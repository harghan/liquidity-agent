"""
Central configuration for liquidity-agent (v2 — full rebuild).

Every tunable parameter — API endpoints, HTTP behaviour, market selection,
the five price-impact order sizes, Liquidity Quality Index weights, per-category
NLP matching thresholds, the Anthropic model, the PDF design system, and the
academic grounding text — lives here. The report's methodology section is derived
directly from these constants.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "liquidity_agent.log"

load_dotenv(ROOT_DIR / ".env")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

# ---------------------------------------------------------------------------
# HTTP client behaviour
# ---------------------------------------------------------------------------
HTTP_TIMEOUT = 25
HTTP_MAX_RETRIES = 3
HTTP_BACKOFF_BASE = 1.5
HTTP_USER_AGENT = "liquidity-agent/2.0 (+research; cross-platform liquidity intelligence)"
INTER_REQUEST_SLEEP = 0.06

# ---------------------------------------------------------------------------
# Collection targets
# ---------------------------------------------------------------------------
TARGET_MARKETS_PER_PLATFORM = 300

# ---- Polymarket (Gamma + CLOB), keyless --------------------------------
POLYMARKET_GAMMA_MARKETS = "https://gamma-api.polymarket.com/markets"
POLYMARKET_CLOB_BOOK = "https://clob.polymarket.com/book"
POLYMARKET_PAGE_SIZE = 100
POLYMARKET_MAX_PAGES = 14            # scan up to ~1400 markets to find 300 categorizable
POLYMARKET_MIN_LIQUIDITY = 2_000.0   # USD resting liquidity (Gamma `liquidityNum`)

# ---- Kalshi (external-api), keyless ------------------------------------
KALSHI_BASE = "https://external-api.kalshi.com/trade-api/v2"
KALSHI_MARKETS = KALSHI_BASE + "/markets"
KALSHI_ORDERBOOK = KALSHI_BASE + "/markets/{ticker}/orderbook"
KALSHI_PER_SERIES_LIMIT = 80

# Macro / crypto / politics / sports series, pulled round-robin so no single
# high-cardinality series crowds out the others.
KALSHI_MACRO_SERIES = [
    "KXFED", "KXFEDDECISION",        # Fed decisions / rate thresholds
    "KXCPIYOY", "KXCPI",             # CPI / inflation
    "KXRECSSNBER",                   # NBER recession
    "KXGDP", "KXGDPYEAR",            # GDP growth
    "KXU3", "KXU3MAX",               # unemployment
    "KXBTC", "KXBTCD", "KXETH", "KXETHD",  # crypto price thresholds
    "KXPRESPERSON", "KXPRESPARTY",   # presidential election
    "KXWCGAME",                      # World Cup 2026 match winners
    "KXMLBGAME", "KXNBA", "KXNHL",   # other active sports (best-effort)
]

# Authoritative category for each Kalshi series (overrides text classification).
KALSHI_SERIES_CATEGORY = {
    "KXFED": "Fed / Rates", "KXFEDDECISION": "Fed / Rates",
    "KXCPIYOY": "Inflation", "KXCPI": "Inflation",
    "KXRECSSNBER": "Recession",
    "KXGDP": "GDP", "KXGDPYEAR": "GDP",
    "KXU3": "Unemployment", "KXU3MAX": "Unemployment",
    "KXBTC": "Crypto", "KXBTCD": "Crypto", "KXETH": "Crypto", "KXETHD": "Crypto",
    "KXPRESPERSON": "Presidential Election", "KXPRESPARTY": "Party Election",
    "KXWCGAME": "World Cup",
    "KXMLBGAME": "Sports", "KXNBA": "Sports", "KXNHL": "Sports",
}

# ---------------------------------------------------------------------------
# Category taxonomy & NLP matching vocabulary
# ---------------------------------------------------------------------------
# Ordered text-classification rules: (category, any-of includes, none-of excludes).
# First match wins, so specific categories precede broad ones. Used for
# Polymarket (no series) and as a fallback for Kalshi.
CATEGORY_RULES = [
    ("Crypto", ("bitcoin", "btc", "ethereum", "solana", "dogecoin", "crypto"), ()),
    ("World Cup", ("world cup", "fifa"), ()),
    ("Primary / Nomination", ("nomination", "nominee", "primary"), ()),
    ("Presidential Election", ("president", "presidential", "presidency"),
     ("nomination", "nominee", "primary")),
    ("Party Election", ("which party", "party win", "presidency in",
                        "republican party", "democratic party"), ()),
    ("Fed / Rates", ("federal reserve", "fomc", "rate cut", "rate hike",
                     "interest rate", "basis point", "bps", "fed funds",
                     "federal funds", "fed "), ()),
    ("Inflation", ("cpi", "inflation", "pce"), ()),
    ("Recession", ("recession",), ()),
    ("GDP", ("gdp", "gross domestic"), ()),
    ("Unemployment", ("unemployment", "jobless", "u-3", "u3", "payroll", "nonfarm"), ()),
    ("Sports", (" vs ", "vs.", " beat ", "to advance", "o/u", "moneyline"), ()),
]

# Categories whose subject is a person/candidate — held to the stricter threshold.
PERSON_CATEGORIES = {"Presidential Election", "Primary / Nomination"}

# Categories actually matched across platforms (others are collected for context
# but have no realistic counterpart). "GDP"/"Unemployment" stay matchable too.
# "Party Election" is intentionally excluded: Polymarket's party markets are
# about Congressional control while Kalshi's are about the Presidency, so they
# match on the party name alone and produce false positives.
MATCHABLE_CATEGORIES = {
    "Presidential Election", "Primary / Nomination",
    "Fed / Rates", "Inflation", "Recession", "GDP", "Unemployment",
    "Crypto", "World Cup", "Sports",
}

# Semantic-conflict guards. Two markets in the same category are rejected if one
# expresses an "up" direction and the other a "down" direction, or if both name
# a numeric threshold and those thresholds disagree beyond tolerance.
DIRECTION_UP = {"increase", "hike", "hikes", "rise", "rises", "higher", "above",
                "up", "gain", "over", "exceed", "reach", "hit"}
DIRECTION_DOWN = {"decrease", "cut", "cuts", "lower", "fall", "falls", "drop",
                  "drops", "below", "decline", "under", "beneath"}
NUMERIC_THRESHOLD_TOLERANCE = 0.05  # 5% relative tolerance for "same" threshold

# 2026 FIFA World Cup nations — lets a Polymarket "[A] vs [B]" market be
# recognised as World Cup (its text rarely says "World Cup") so it can match
# Kalshi's KXWCGAME per-match contracts.
WORLD_CUP_TEAMS = {
    "argentina", "france", "spain", "england", "brazil", "portugal", "germany",
    "netherlands", "belgium", "croatia", "uruguay", "usa", "united states",
    "mexico", "canada", "morocco", "japan", "south korea", "korea", "senegal",
    "switzerland", "denmark", "colombia", "ecuador", "italy", "ivory coast",
    "nigeria", "ghana", "cameroon", "australia", "egypt", "algeria", "tunisia",
    "poland", "serbia", "austria", "norway", "sweden", "qatar", "iran", "iraq",
    "saudi arabia", "peru", "chile", "paraguay", "panama", "jamaica",
    "costa rica", "south africa", "new zealand", "turkey", "ukraine", "wales",
    "scotland", "greece", "czech", "hungary", "romania",
}

# Tokens removed before keyword extraction so the distinguishing entity (a
# candidate name, a rate threshold, an asset, a team) dominates the comparison.
# Years are KEPT (they separate recession-2026 from recession-2027).
STOPWORDS = {
    "will", "the", "a", "an", "be", "to", "of", "in", "on", "for", "by", "at",
    "is", "are", "and", "or", "before", "after", "than", "this", "that", "with",
    "what", "which", "who", "whom", "us", "u.s.", "usa", "united", "states",
    "market", "resolve", "resolves", "yes", "no", "there", "be",
    "win", "wins", "winner", "won", "next", "become", "becomes",
    "president", "presidential", "presidency", "election", "elections",
    "federal", "reserve", "rate", "rates", "following", "above", "below",
    "upper", "bound", "target", "funds", "increase", "rise", "year", "ending",
    "price", "range", "at", "more", "less", "high", "get", "happen",
}

# ---------------------------------------------------------------------------
# Matching thresholds
# ---------------------------------------------------------------------------
MATCH_FUZZY_WEIGHT = 0.5
MATCH_KEYWORD_WEIGHT = 0.5
MATCH_THRESHOLD_PERSON = 0.75    # candidate / person markets
MATCH_THRESHOLD_DEFAULT = 0.65   # all other categories
MATCH_ENTITY_FLOOR = 0.45        # hard gate: distinguishing entities must align

# ---------------------------------------------------------------------------
# Price-impact methodology — FIVE order sizes
# ---------------------------------------------------------------------------
ORDER_SIZES_USD = [500.0, 2_000.0, 10_000.0, 50_000.0, 100_000.0]
DEPTH_REFERENCE_SIZE = 2_000.0          # LQI depth component
PRICE_IMPACT_REFERENCE_SIZE = 10_000.0  # LQI impact component & headline
INSTITUTIONAL_SIZE = 50_000.0
FUND_SIZE = 100_000.0

# ---------------------------------------------------------------------------
# Liquidity Quality Index (LQI) — composite 0..100
# Weights follow standard market-microstructure practitioner convention:
# mid-book depth (40%) is primary for institutional participants, with spread
# and large-size impact at 30% each.
# ---------------------------------------------------------------------------
LQI_WEIGHTS = {"spread": 0.30, "depth": 0.40, "impact": 0.30}
LQI_SPREAD_CAP = 0.10        # 10c spread -> 0 on spread component
LQI_DEPTH_IMPACT_CAP = 0.10  # 10c slippage on $2k -> 0 on depth
LQI_IMPACT_CAP = 0.15        # 15c slippage on $10k -> 0 on impact

# ---------------------------------------------------------------------------
# Anthropic report-writing model (user-specified: Sonnet 4.6)
# ---------------------------------------------------------------------------
ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_MAX_TOKENS = 16_000

# ---------------------------------------------------------------------------
# PDF design system
# ---------------------------------------------------------------------------
COLOR_DARK = "#0a0a0a"
COLOR_GOLD = "#c8a951"
COLOR_ROW_ALT = "#f7f7f7"
COLOR_WHITE = "#ffffff"
COLOR_MUTED = "#666666"
COLOR_MUTED_FOOTER = "#888888"
COLOR_DANGER = "#c1121f"
COLOR_SAFE = "#2d6a4f"
FONT_BODY = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

AUTHOR_CREDIT_LINE_1 = "Research concept and design: Harsha Ghandikota, Duke University (MEM 2026)"
AUTHOR_CREDIT_LINE_2 = "Critical review and commentary: Sohan & Nitin"
AUTHOR_CREDIT_LINE_3 = "Autonomous analysis and report generation: Claude Sonnet (Anthropic)"
DATA_SOURCE = "Polymarket (Gamma + CLOB) & Kalshi (trade-api v2)"
REPORT_DISCLAIMER = ("This memo is generated autonomously by the Liquidity Agent. "
                     "It does not constitute investment advice.")

PHANTOM_LIQUIDITY_DISCLAIMER = (
    "Displayed limit orders may be cancelled on approach in live markets. All "
    "figures represent displayed depth, not guaranteed execution. This caveat "
    "affects both platforms equally and does not bias the cross-platform "
    "comparison."
)

# Academic grounding for the LQI / price-impact methodology.
ACADEMIC_REFERENCES = [
    ("Kyle, A. S. (1985).", "Continuous Auctions and Insider Trading. "
     "Econometrica, 53(6), 1315–1335.",
     "Source of the linear price-impact coefficient (lambda) relating order "
     "flow to price movement; our VWAP-vs-mid impact is its empirical analogue."),
    ("Amihud, Y. (2002).", "Illiquidity and Stock Returns: Cross-Section and "
     "Time-Series Effects. Journal of Financial Markets, 5(1), 31–56.",
     "Precedent for a volume-normalized illiquidity ratio; motivates measuring "
     "impact per dollar of notional rather than from quoted spread alone."),
    ("Roll, R. (1984).", "A Simple Implicit Measure of the Effective Bid-Ask "
     "Spread in an Efficient Market. Journal of Finance, 39(4), 1127–1139.",
     "Prior art for inferring effective transaction cost as a liquidity "
     "measure, supporting spread as one LQI component."),
]


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure logging to stdout and a timestamped file. Idempotent."""
    logger = logging.getLogger("liquidity_agent")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stream = logging.StreamHandler()
    stream.setFormatter(fmt)
    logger.addHandler(stream)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.propagate = False
    return logger
