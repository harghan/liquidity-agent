"""
Kalshi collector — external-api.kalshi.com, no auth required for market data.

Markets are pulled per macro/economic series (Fed, CPI, recession, growth,
unemployment, elections) because the unfiltered feed is dominated by
short-dated sports markets. The orderbook endpoint returns Kalshi's
``orderbook_fp`` format, which encodes resting interest as YES bids
(``yes_dollars``) and NO bids (``no_dollars``); a NO bid at price ``q`` is
economically a YES ask at ``1 - q``, so we fold both sides into a single YES
book to match Polymarket's convention.

Run standalone to smoke-test the collector in isolation:

    python -m collectors.kalshi
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional, Tuple

import config
from collectors.http_client import get_json
from core.normalizer import NormalizedMarket, OrderBook, build_orderbook

logger = logging.getLogger("liquidity_agent.kalshi")

PLATFORM = "Kalshi"


def _fetch_series_markets(series_ticker: str) -> List[dict]:
    params = {
        "series_ticker": series_ticker,
        "status": "open",
        "limit": config.KALSHI_PER_SERIES_LIMIT,
    }
    data = get_json(
        config.KALSHI_MARKETS,
        params=params,
        context=f"kalshi markets series={series_ticker}",
    )
    if not isinstance(data, dict):
        return []
    markets = data.get("markets")
    if not isinstance(markets, list):
        return []
    # Tag each market with its source series so the normalizer can attach the
    # authoritative category hint.
    for m in markets:
        if isinstance(m, dict):
            m["_series"] = series_ticker
    return markets


def _fetch_orderbook(ticker: str) -> Optional[OrderBook]:
    url = config.KALSHI_ORDERBOOK.format(ticker=ticker)
    data = get_json(url, context=f"kalshi orderbook {ticker}")
    if not isinstance(data, dict):
        return None
    # New "orderbook_fp" (dollar-denominated) format; tolerate the legacy
    # "orderbook" (cent-denominated) shape as a fallback.
    fp = data.get("orderbook_fp")
    if isinstance(fp, dict):
        yes_levels = fp.get("yes_dollars") or []
        no_levels = fp.get("no_dollars") or []
        scale = 1.0
    else:
        legacy = data.get("orderbook") or {}
        yes_levels = legacy.get("yes") or []
        no_levels = legacy.get("no") or []
        scale = 0.01  # legacy prices are in cents

    raw_bids: List[Tuple[float, float]] = []
    for lvl in yes_levels:
        price, size = _level(lvl)
        if price is not None:
            raw_bids.append((price * scale, size))

    # NO bid at q  <=>  YES ask at (1 - q)
    raw_asks: List[Tuple[float, float]] = []
    for lvl in no_levels:
        price, size = _level(lvl)
        if price is not None:
            raw_asks.append((1.0 - price * scale, size))

    return build_orderbook(raw_bids, raw_asks)


def _level(lvl) -> Tuple[Optional[float], float]:
    """Parse a ``[price, size]`` pair (strings or numbers) from the book."""
    try:
        return float(lvl[0]), float(lvl[1])
    except (TypeError, ValueError, IndexError):
        return None, 0.0


def _build_question(market: dict) -> str:
    """Compose a descriptive question from the title and the YES outcome label."""
    title = str(market.get("title") or "").strip()
    sub = str(market.get("yes_sub_title") or market.get("subtitle") or "").strip()
    if sub and sub.lower() not in ("yes", "no") and sub.lower() not in title.lower():
        return f"{title} — {sub}".strip(" —")
    return title


def _normalize(market: dict) -> NormalizedMarket:
    def _f(key: str) -> float:
        try:
            return float(market.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0

    displayed = None
    for key in ("last_price_dollars", "last_price"):
        val = market.get(key)
        if val is not None:
            try:
                displayed = float(val)
                if key == "last_price":  # cents → dollars
                    displayed /= 100.0
                break
            except (TypeError, ValueError):
                continue

    ticker = str(market.get("ticker") or "unknown")
    return NormalizedMarket(
        platform=PLATFORM,
        market_id=ticker,
        question=_build_question(market),
        outcome=str(market.get("yes_sub_title") or "Yes"),
        end_date=market.get("close_time") or market.get("expiration_time"),
        volume=_f("volume"),
        liquidity=_f("liquidity"),
        displayed_prob=displayed,
        url=f"https://kalshi.com/markets/{market.get('event_ticker') or ticker}",
        kalshi_ticker=ticker,
        book=None,  # populated lazily by fetch_book()
        extra={
            "event_ticker": market.get("event_ticker"),
            "yes_sub_title": market.get("yes_sub_title"),
            "series": market.get("_series"),
            "category_hint": config.KALSHI_SERIES_CATEGORY.get(market.get("_series", "")),
        },
    )


def collect_metadata(max_markets: int = config.TARGET_MARKETS_PER_PLATFORM) -> List[NormalizedMarket]:
    """Collect macro Kalshi market metadata (no orderbooks).

    Markets are pulled per series and round-robined so no single
    high-cardinality series crowds out the others. Orderbooks are fetched
    separately (and only for matched markets) via :func:`fetch_book`.
    """
    logger.info("Collecting Kalshi macro metadata across %d series…", len(config.KALSHI_MACRO_SERIES))
    per_series: List[List[dict]] = []
    for series in config.KALSHI_MACRO_SERIES:
        try:
            rows = _fetch_series_markets(series)
            logger.info("Kalshi series %s -> %d markets", series, len(rows))
            if rows:
                per_series.append(rows)
            time.sleep(config.INTER_REQUEST_SLEEP)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to fetch Kalshi series %s: %s", series, exc)

    # Round-robin across series so no single high-cardinality series (e.g. the
    # ~50 Fed strike markets) crowds out CPI, recession, or election coverage.
    candidates: List[dict] = []
    idx = 0
    while len(candidates) < max_markets and per_series:
        progressed = False
        for rows in per_series:
            if idx < len(rows):
                candidates.append(rows[idx])
                progressed = True
                if len(candidates) >= max_markets:
                    break
        if not progressed:
            break
        idx += 1
    results: List[NormalizedMarket] = []
    for m in candidates:
        try:
            if not m.get("ticker"):
                continue
            results.append(_normalize(m))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Skipping malformed Kalshi market: %s", exc)

    logger.info("Kalshi: %d macro markets in universe", len(results))
    return results


def fetch_book(market: NormalizedMarket) -> bool:
    """Populate ``market.book`` from the orderbook. Returns True if two-sided."""
    book = _fetch_orderbook(market.market_id)
    time.sleep(config.INTER_REQUEST_SLEEP)
    if book is None or not book.is_two_sided():
        logger.info("Kalshi %s has no two-sided book", market.market_id)
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
    logger.info("Kalshi: collected %d markets with live books", len(out))
    return out


if __name__ == "__main__":
    config.configure_logging()
    markets = collect(max_markets=30)
    print(f"\nCollected {len(markets)} Kalshi markets:\n")
    for mk in markets:
        b = mk.book
        print(
            f"  • {mk.question[:60]:<60} "
            f"bid={b.best_bid()} ask={b.best_ask()} "
            f"spread={round(b.spread(), 4) if b.spread() is not None else None}"
        )
