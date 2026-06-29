"""
Common market schema shared across platforms.

Polymarket and Kalshi expose very different payloads and orderbook encodings.
Everything downstream (price impact, matching, scoring, reporting) operates on
the platform-neutral structures defined here. Collectors are responsible for
translating their raw payloads into these types via :func:`build_orderbook`.

Price convention: all prices are expressed as an implied probability in [0, 1]
for the YES / affirmative outcome, and all sizes are a number of shares /
contracts (each contract pays $1 on resolution). This makes Polymarket shares
and Kalshi contracts directly comparable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class OrderLevel:
    """A single price level on one side of the book."""

    price: float   # implied probability, 0..1
    size: float    # number of contracts/shares resting at this price

    @property
    def notional(self) -> float:
        """USD required to take this level (price per contract * contracts)."""
        return self.price * self.size


@dataclass
class OrderBook:
    """A canonicalised two-sided book for the YES outcome.

    ``bids`` are sorted best-first (descending price); ``asks`` are sorted
    best-first (ascending price).
    """

    bids: List[OrderLevel] = field(default_factory=list)
    asks: List[OrderLevel] = field(default_factory=list)

    # -- top of book -------------------------------------------------------
    def best_bid(self) -> Optional[float]:
        return self.bids[0].price if self.bids else None

    def best_ask(self) -> Optional[float]:
        return self.asks[0].price if self.asks else None

    def mid_price(self) -> Optional[float]:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return (bb + ba) / 2.0

    def spread(self) -> Optional[float]:
        bb, ba = self.best_bid(), self.best_ask()
        if bb is None or ba is None:
            return None
        return ba - bb

    # -- depth -------------------------------------------------------------
    def ask_notional(self) -> float:
        """Total USD of resting liquidity on the ask side."""
        return sum(level.notional for level in self.asks)

    def bid_notional(self) -> float:
        return sum(level.notional for level in self.bids)

    def is_two_sided(self) -> bool:
        return bool(self.bids) and bool(self.asks)


@dataclass
class NormalizedMarket:
    """A single tradable YES outcome on one platform, plus its book."""

    platform: str                 # "Polymarket" | "Kalshi"
    market_id: str                # conditionId (Polymarket) | ticker (Kalshi)
    question: str                 # human-readable question / outcome description
    outcome: str = "Yes"          # affirmative outcome label
    category: str = "Unknown"     # macro bucket, assigned by the matcher
    end_date: Optional[str] = None
    volume: float = 0.0           # lifetime traded volume (USD or contracts)
    liquidity: float = 0.0        # resting liquidity reported by the platform
    displayed_prob: Optional[float] = None  # platform-displayed implied probability
    url: Optional[str] = None
    # Native platform identifiers, carried through to matched pairs so the UI can
    # deep-link to each venue's trade page.
    polymarket_slug: Optional[str] = None   # Polymarket Gamma `slug`
    kalshi_ticker: Optional[str] = None      # Kalshi market `ticker`
    book: Optional[OrderBook] = None
    extra: Dict[str, object] = field(default_factory=dict)

    @property
    def has_book(self) -> bool:
        return self.book is not None and self.book.is_two_sided()


def build_orderbook(
    raw_bids: Sequence[Tuple[float, float]],
    raw_asks: Sequence[Tuple[float, float]],
) -> OrderBook:
    """Canonicalise ``(price, size)`` pairs into a sorted, validated OrderBook.

    Invalid levels (non-positive size, out-of-range price) are dropped rather
    than raising, so one malformed level never discards an entire book.
    """
    bids = _clean_levels(raw_bids)
    asks = _clean_levels(raw_asks)
    bids.sort(key=lambda lvl: lvl.price, reverse=True)  # best bid first
    asks.sort(key=lambda lvl: lvl.price)                # best ask first
    return OrderBook(bids=bids, asks=asks)


def _clean_levels(raw: Sequence[Tuple[float, float]]) -> List[OrderLevel]:
    levels: List[OrderLevel] = []
    for item in raw:
        try:
            price = float(item[0])
            size = float(item[1])
        except (TypeError, ValueError, IndexError):
            continue
        if size <= 0:
            continue
        if not (0.0 < price < 1.0):
            # Prices outside (0,1) are not valid implied probabilities.
            continue
        levels.append(OrderLevel(price=price, size=size))
    return levels
