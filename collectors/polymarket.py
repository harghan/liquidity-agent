"""
Polymarket collector — Gamma (markets) + CLOB (orderbook), no auth required.

Gamma returns market metadata (question, liquidity, the CLOB token ids); the
CLOB ``/book`` endpoint returns the live two-sided orderbook for a token. We
page Gamma by descending volume, keep macro markets with an enabled orderbook,
then pull each book and canonicalise it into the shared schema.

Run standalone to smoke-test the collector in isolation:

    python -m collectors.polymarket
"""

from __future__ import annotations

import json
import logging
import time
from typing import List, Optional, Tuple

import config
from collectors.http_client import get_json
from core.normalizer import NormalizedMarket, OrderBook, build_orderbook

logger = logging.getLogger("liquidity_agent.polymarket")

PLATFORM = "Polymarket"


def _parse_json_field(value, default):
    """Gamma encodes list fields (outcomes, prices, token ids) as JSON strings."""
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return default


def _is_in_scope(question: str) -> bool:
    """Keep any market that classifies into a matchable category (macro,
    crypto, politics, sports, World Cup)."""
    from core.matcher import classify_text  # local import avoids any import cycle
    return classify_text(question) in config.MATCHABLE_CATEGORIES


def _fetch_market_page(offset: int) -> List[dict]:
    params = {
        "active": "true",
        "closed": "false",
        "limit": config.POLYMARKET_PAGE_SIZE,
        "offset": offset,
        "order": "volumeNum",
        "ascending": "false",
    }
    data = get_json(
        config.POLYMARKET_GAMMA_MARKETS,
        params=params,
        context=f"polymarket gamma markets offset={offset}",
    )
    if not isinstance(data, list):
        return []
    return data


def _select_yes_token(market: dict) -> Optional[str]:
    """Return the CLOB token id for the affirmative (YES) outcome."""
    token_ids = _parse_json_field(market.get("clobTokenIds"), [])
    outcomes = _parse_json_field(market.get("outcomes"), [])
    if not token_ids:
        return None
    # Prefer the token aligned with a "Yes" outcome; fall back to the first.
    for idx, outcome in enumerate(outcomes):
        if isinstance(outcome, str) and outcome.strip().lower() == "yes":
            if idx < len(token_ids):
                return str(token_ids[idx])
    return str(token_ids[0])


def _fetch_orderbook(token_id: str) -> Optional[OrderBook]:
    data = get_json(
        config.POLYMARKET_CLOB_BOOK,
        params={"token_id": token_id},
        context=f"polymarket clob book token={token_id[:12]}…",
    )
    if not isinstance(data, dict):
        return None
    raw_bids: List[Tuple[float, float]] = [
        (lvl.get("price"), lvl.get("size")) for lvl in data.get("bids", []) if isinstance(lvl, dict)
    ]
    raw_asks: List[Tuple[float, float]] = [
        (lvl.get("price"), lvl.get("size")) for lvl in data.get("asks", []) if isinstance(lvl, dict)
    ]
    return build_orderbook(raw_bids, raw_asks)


def _normalize(market: dict, token_id: str) -> NormalizedMarket:
    prices = _parse_json_field(market.get("outcomePrices"), [])
    displayed = None
    if prices:
        try:
            displayed = float(prices[0])
        except (TypeError, ValueError):
            displayed = None

    def _f(key: str) -> float:
        try:
            return float(market.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    slug = market.get("slug")
    return NormalizedMarket(
        platform=PLATFORM,
        market_id=str(market.get("conditionId") or market.get("id") or slug or "unknown"),
        question=str(market.get("question") or "").strip(),
        outcome="Yes",
        end_date=market.get("endDate"),
        volume=_f("volumeNum"),
        liquidity=_f("liquidityNum"),
        displayed_prob=displayed,
        url=f"https://polymarket.com/event/{slug}" if slug else None,
        book=None,  # populated lazily by fetch_book()
        extra={
            "gamma_id": market.get("id"),
            "slug": slug,
            "group_item_title": market.get("groupItemTitle"),
            "yes_token_id": token_id,
        },
    )


def collect_metadata(max_markets: int = config.TARGET_MARKETS_PER_PLATFORM) -> List[NormalizedMarket]:
    """Collect in-scope Polymarket market metadata (no orderbooks).

    Cheap: a handful of paged Gamma calls. Orderbooks are fetched separately
    (and only for matched markets) via :func:`fetch_book`. A single bad row is
    logged and skipped, never fatal.
    """
    logger.info("Collecting Polymarket macro metadata (target=%d)…", max_markets)
    results: List[NormalizedMarket] = []

    for page in range(config.POLYMARKET_MAX_PAGES):
        offset = page * config.POLYMARKET_PAGE_SIZE
        rows = _fetch_market_page(offset)
        if not rows:
            break
        for m in rows:
            try:
                question = str(m.get("question") or "")
                if not question or not m.get("enableOrderBook"):
                    continue
                if not _is_in_scope(question):
                    continue
                if float(m.get("liquidityNum") or 0.0) < config.POLYMARKET_MIN_LIQUIDITY:
                    continue
                token_id = _select_yes_token(m)
                if not token_id:
                    continue
                results.append(_normalize(m, token_id))
            except Exception as exc:  # noqa: BLE001 — never let one row break paging
                logger.warning("Skipping malformed Polymarket row: %s", exc)
        if len(results) >= max_markets:
            break

    results = results[:max_markets]
    logger.info("Polymarket: %d macro markets in universe", len(results))
    return results


def fetch_book(market: NormalizedMarket) -> bool:
    """Populate ``market.book`` from the CLOB. Returns True on a two-sided book."""
    token_id = market.extra.get("yes_token_id")
    if not token_id:
        return False
    book = _fetch_orderbook(str(token_id))
    time.sleep(config.INTER_REQUEST_SLEEP)
    if book is None or not book.is_two_sided():
        logger.info("Polymarket %s has no two-sided book", market.market_id)
        return False
    market.book = book
    return True


def collect(max_markets: int = 20) -> List[NormalizedMarket]:
    """Convenience: metadata + orderbooks (used by the standalone smoke test)."""
    meta = collect_metadata(max_markets)
    out: List[NormalizedMarket] = []
    for m in meta:
        if fetch_book(m):
            out.append(m)
    logger.info("Polymarket: collected %d markets with live books", len(out))
    return out


if __name__ == "__main__":
    config.configure_logging()
    markets = collect(max_markets=10)
    print(f"\nCollected {len(markets)} Polymarket markets:\n")
    for mk in markets:
        b = mk.book
        print(
            f"  • {mk.question[:60]:<60} "
            f"bid={b.best_bid()} ask={b.best_ask()} "
            f"spread={b.spread()} liq=${mk.liquidity:,.0f}"
        )
