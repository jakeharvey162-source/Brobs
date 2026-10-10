"""Optional provenance-aware news risk guard for local paper runners.

GDELT provides metadata about indexed publisher coverage. Passing this guard
does NOT verify the truth of articles, predict prices, or establish strategy
profitability. Only independently sourced, recent English headlines are used.
No article bodies or secrets are downloaded. Fail closed on missing evidence.
"""
from datetime import datetime, timezone
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from collections import Counter
import json
import re

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
ASSETS = {
    "BTC_USDT": ("Bitcoin", r"\\b(?:bitcoin|btc)\\b"),
    "ETH_USDT": ("Ethereum", r"\\b(?:ethereum|ether|eth)\\b"),
    "AAPL": ("Apple", r"\\b(?:apple|aapl|iphone)\\b"),
    "MSFT": ("Microsoft", r"\\b(?:microsoft|msft)\\b"),
}
# Whitelisted *publisher hosts*, not proof that every article is true.
PUBLISHERS = frozenset({
    "reuters.com", "apnews.com", "bbc.com", "cnbc.com", "ft.com",
    "wsj.com", "bloomberg.com", "marketwatch.com", "coindesk.com",
    "finance.yahoo.com", "theguardian.com",
})
NEGATIVE = frozenset({
    "fraud", "fraudulent", "hack", "hacked", "breach", "bankrupt", "bankruptcy",
    "crash", "crashes", "plunge", "plunges", "plunged", "lawsuit", "lawsuits",
    "collapse", "collapses", "collapsed", "liquidation", "liquidations",
    "investigation", "investigated", "scam", "scandal",
})
POSITIVE = frozenset({
    "surge", "surges", "rally", "rallies", "record", "rebound", "rebounds",
    "recovery", "recovers", "upgrade", "upgraded", "growth", "profit", "profits",
})
class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("GDELT endpoint redirect refused")

def _utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("Timezone-aware datetime required")
    return value.astimezone(timezone.utc)

def _seen(value):
    if not isinstance(value, str):
        raise ValueError("Missing GDELT seen timestamp")
    if re.fullmatch(r"\\d{8}T\\d{6}Z", value):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    return _utc(value)

def _host(domain, url):
    if not isinstance(url, str) or len(url) > 2048:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.port:
            return None
        host = parsed.hostname.lower().rstrip(".")
        domain = str(domain).lower().rstrip(".")
        if not domain or domain != host or not any(host == allowed or host.endswith("." + allowed) for allowed in PUBLISHERS):
            return None
        return host
    except ValueError:
        return None

def _fetch(url):
    request = Request(url, headers={"User-Agent": "BROBS-paper-news-research/1.0", "Accept": "application/json"})
    with build_opener(_NoRedirect()).open(request, timeout=8) as response:
        raw = response.read(400001)
        if len(raw) > 400000:
            raise ValueError("News response too large")
        return raw

def evaluate_articles(symbol, articles, now):
    """Validate GDELT provenance; classify only relevant distinct publishers."""
    if symbol not in ASSETS:
        return dict(status="unsupported", sentiment="unknown", reason="Symbol has no verified news mapping", articles=[])
    now = _utc(now)
    if not isinstance(articles, list):
        raise ValueError("GDELT article list must be an array")
    seen_urls = set()
    retained = []
    for item in articles[:150]:
        if not isinstance(item, dict):
            continue
        url = item.get("url")
        host = _host(item.get("domain"), url)
        title = item.get("title")
        if not host or not isinstance(title, str) or not 10 <= len(title) <= 240:
            continue
        if url in seen_urls:
            continue
        if item.get("language", "").lower() != "english":
            continue
        if not re.search(ASSETS[symbol][1], title, re.IGNORECASE):
            continue
        try:
            age = (now - _seen(item.get("seendate"))).total_seconds()
        except (ValueError, TypeError, OverflowError):
            continue
        if not 0 <= age <= 24 * 3600:
            continue
        seen_urls.add(url)
        words = set(re.findall(r"[a-z]+", title.lower()))
        negatives = words & NEGATIVE
        positives = words & POSITIVE
        label = "negative" if negatives and not positives else "positive" if positives and not negatives else "neutral"
        retained.append(dict(publisher=host, title=title, url=url, seendate=item["seendate"], headline_signal=label))
    by_publisher = {}
    for article in retained:
        publisher = next((domain for domain in PUBLISHERS if article["publisher"] == domain or article["publisher"].endswith("." + domain)), article["publisher"])
        if publisher not in by_publisher:
            by_publisher[publisher] = article
    unique = list(by_publisher.values())
    if len(unique) < 2:
        return dict(status="insufficient", sentiment="unknown", reason="Fewer than two recent independent allowed publishers", articles=unique)
    votes = Counter(item["headline_signal"] for item in unique)
    if votes["negative"] >= 2:
        sentiment = "negative"
    elif votes["positive"] >= 2 and votes["negative"] == 0:
        sentiment = "positive"
    elif votes["negative"] and votes["positive"]:
        sentiment = "mixed"
    else:
        sentiment = "neutral"
    return dict(status="verified_metadata", sentiment=sentiment,
                reason="GDELT coverage metadata passed timestamp, URL, language, relevance and publisher-diversity checks; article truth NOT verified",
                articles=unique)

def get_news_review(symbol, now, fetch=None):
    """Fetch no more than 35 indexed articles for a fixed, whitelisted asset."""
    if symbol not in ASSETS:
        return dict(status="unsupported", sentiment="unknown", reason="Asset not supported for news risk guard", articles=[])
    params = {"query": '"' + ASSETS[symbol][0] + '" sourcelang:english',
              "mode": "artlist", "format": "json", "maxrecords": "35", "timespan": "1d", "sort": "datedesc"}
    url = GDELT_URL + "?" + urlencode(params)
    try:
        raw = (fetch or _fetch)(url)
        if not isinstance(raw, (bytes, bytearray)) or len(raw) > 400000:
            raise ValueError("Invalid provider response")
        data = json.loads(raw)
        return evaluate_articles(symbol, data.get("articles"), now)
    except (OSError, ValueError, TypeError, KeyError, TimeoutError) as exc:
        return dict(status="unavailable", sentiment="unknown", reason="Fresh verified publisher metadata unavailable: " + type(exc).__name__, articles=[])

def guard_entry(signal, symbol, now, fetch=None):
    """Fail closed for NEW paper entries only; no effect on existing exits or stops."""
    review = get_news_review(symbol, now, fetch=fetch)
    votes = list(signal.get("votes", []))
    votes.append(dict(agent="news_provenance", action="veto" if review["status"] != "verified_metadata" or review["sentiment"] in ("negative", "mixed") else "clear",
                      reason=review["reason"], sentiment=review["sentiment"],
                      publisher_count=len(review["articles"]),
                      sources=[{"publisher":x["publisher"], "title":x["title"], "url":x["url"], "seendate":x["seendate"]} for x in review["articles"]]))
    allow = votes[-1]["action"] == "clear"
    # Positive coverage never forces a buy: other signals and risk gates still decide.
    return {**signal, "action":signal["action"] if allow else "hold", "votes":votes}
