#!/usr/bin/env python3
"""
Generate `hardtech-live-data.json` from whitelisted sites for hard-tech topics.

What this version fixes:
- Preserves a multi-day archive instead of overwriting with only one date.
- Supports backfilling recent days so the date selector has real history.
- Filters out shallow market/stock snippets.
- Decodes Google News RSS links back to source articles.
- Pulls deeper summaries from article metadata and正文段落.

Usage:
  python3 scripts/generate_live_data_from_whitelist.py --out ../hardtech-live-data.json
  python3 scripts/generate_live_data_from_whitelist.py --out ../hardtech-live-data.json --backfill-days 5
  python3 scripts/generate_live_data_from_whitelist.py --out ../hardtech-live-data.json --date 2026-03-10
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path


WHITELIST_SITES = [
    "eastmoney.com",
    "myqcloud.com",
    "wallstreetcn.com",
    "caijing.com.cn",
    "163.com",
    "huxiu.com",
    "cnfol.com",
]

TOPIC_KEYWORDS = {
    "AI": ["大模型", "AI", "Agentic AI", "智能体", "推理", "模型应用"],
    "Chip": ["芯片", "半导体", "台积电", "2nm", "5nm", "算力"],
    "Robotics": ["机器人", "人形机器人", "具身智能", "标准体系"],
    "EV": ["新能源汽车", "电池", "快充", "比亚迪", "智能驾驶", "闪充"],
}

TAG_BY_SECTOR = {
    "AI": "AI",
    "Chip": "芯片",
    "Robotics": "机器人",
    "EV": "新能源车",
}

SOURCE_PRIORITY = {
    "华尔街见闻": 4.0,
    "虎嗅网": 3.8,
    "虎嗅": 3.8,
    "东方财富": 1.8,
    "腾讯云": 3.0,
    "网易": 2.0,
    "中金在线": 1.8,
    "财经网": 2.2,
}

SITE_LABELS = {
    "wallstreetcn.com": "华尔街见闻",
    "huxiu.com": "虎嗅网",
    "eastmoney.com": "东方财富",
    "163.com": "网易",
    "myqcloud.com": "腾讯云",
    "cnfol.com": "中金在线",
    "caijing.com.cn": "财经网",
}

NEGATIVE_PATTERNS = [
    "股吧",
    "股市直播",
    "涨停",
    "跌停",
    "ETF",
    "回购",
    "概念股",
    "资金流",
    "主力资金",
    "盘中",
    "尾盘",
    "收评",
    "午评",
    "早评",
    "开盘",
    "异动",
    "研报",
    "评级",
    "题材",
    "快讯",
    "公告",
    "股东",
    "港股",
    "A股",
    "美股",
    "财富号",
    "主题挖掘",
    "板块",
    "走高",
    "流入",
    "流出",
    "中概股",
    "跌幅",
    "涨超",
    "异动拉升",
    "概念再度活跃",
]

BOILERPLATE_PATTERNS = [
    "首页",
    "打开APP",
    "版权声明",
    "广告",
    "联系我们",
    "用户协议",
    "隐私政策",
    "免责声明",
    "登录",
    "注册",
    "下载客户端",
    "Comprehensive up-to-date news coverage",
]

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

SHANGHAI_TZ = dt.timezone(dt.timedelta(hours=8))


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    summary: str
    published: dt.datetime
    sector: str
    quote: str = ""
    score: float = 0.0
    discovery_link: str = ""


def build_google_rss_url(site: str, keywords: list[str], target_date: dt.date) -> str:
    joined = " OR ".join(keywords)
    window_start = (target_date - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    window_end = target_date.strftime("%Y-%m-%d")
    query = f"site:{site} ({joined}) after:{window_start} before:{window_end}"
    params = {
        "q": query,
        "hl": "zh-CN",
        "gl": "CN",
        "ceid": "CN:zh-Hans",
    }
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)


def http_get(url: str, timeout: int = 4, headers: dict[str, str] | None = None) -> str:
    req_headers = {"User-Agent": USER_AGENT}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def http_post(url: str, data: str, timeout: int = 4, headers: dict[str, str] | None = None) -> str:
    req_headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data.encode("utf-8"), headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "ignore")


def parse_pubdate(text: str) -> dt.datetime:
    try:
        value = email.utils.parsedate_to_datetime(text)
        if value.tzinfo is None:
            return value.replace(tzinfo=dt.timezone.utc)
        return value
    except Exception:
        return dt.datetime.now(dt.timezone.utc)


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<script[\\s\\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\\s\\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", strip_html(text)).lower()


def clean_title(title: str, source: str) -> str:
    title = strip_html(title)
    title = re.sub(r"\s*-\s*(网易|华尔街见闻|虎嗅网?|东方财富|中金在线|腾讯云|财经网|cnfol|163\.com)$", "", title, flags=re.I)
    title = re.sub(r"_股市直播_市场_中金在线$", "", title)
    title = re.sub(r"_新车上市_汽车_中金在线$", "", title)
    title = re.sub(r"\s*[-|丨]\s*[^-丨|]{1,16}$", lambda m: "" if source and source in m.group(0) else m.group(0), title)
    return title.strip(" -_|")


def is_low_quality_candidate(title: str, summary: str, source: str) -> bool:
    text = f"{title} {summary} {source}"
    return any(token in text for token in NEGATIVE_PATTERNS)


def keyword_score(text: str, sector: str) -> float:
    score = 0.0
    for kw in TOPIC_KEYWORDS[sector]:
        if kw.lower() in text.lower():
            score += 1.6
    return score


def source_score(source: str) -> float:
    for label, score in SOURCE_PRIORITY.items():
        if label in source:
            return score
    return 1.5


def score_candidate(title: str, summary: str, source: str, sector: str, published: dt.datetime) -> float:
    text = f"{title} {summary}"
    score = source_score(source)
    score += keyword_score(text, sector)
    score += min(len(strip_html(summary)) / 80, 2.2)
    age_hours = max((dt.datetime.now(dt.timezone.utc) - published).total_seconds() / 3600, 0)
    score += max(0, 2.0 - age_hours / 12)
    if "标准" in text or "发布会" in text or "量产" in text or "融资" in text or "营收" in text:
        score += 1.2
    if is_low_quality_candidate(title, summary, source):
        score -= 8
    return score


def sentence_split(text: str) -> list[str]:
    cleaned = strip_html(text)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[。！？!?；;])", cleaned)
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part[-1] not in "。！？!?；;":
            part += "。"
        out.append(part)
    return out


def dedupe_sentences(parts: list[str]) -> list[str]:
    seen = set()
    out = []
    for part in parts:
        key = normalize_text(part)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(part)
    return out


def extract_meta_content(raw_html: str, key: str, value: str) -> str:
    pattern = rf'<meta[^>]+{key}=["\']{re.escape(value)}["\'][^>]+content=["\']([^"\']+)["\']'
    alt_pattern = rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+{key}=["\']{re.escape(value)}["\']'
    for pat in (pattern, alt_pattern):
        match = re.search(pat, raw_html, re.I)
        if match:
            return strip_html(match.group(1))
    return ""


def extract_json_ld_text(raw_html: str) -> list[str]:
    matches = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', raw_html, re.I)
    snippets: list[str] = []
    for block in matches:
        block = block.strip()
        if not block:
            continue
        try:
            data = json.loads(block)
        except Exception:
            continue

        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key in ("description", "articleBody"):
                    value = node.get(key)
                    if isinstance(value, str):
                        snippets.append(strip_html(value))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    return [text for text in snippets if len(text) >= 40]


def extract_paragraphs(raw_html: str) -> list[str]:
    paragraphs = re.findall(r"<p[^>]*>([\\s\\S]*?)</p>", raw_html, re.I)
    cleaned: list[str] = []
    for part in paragraphs:
        text = strip_html(part)
        if len(text) < 28:
            continue
        if any(bad in text for bad in BOILERPLATE_PATTERNS):
            continue
        cleaned.append(text)
    return dedupe_sentences(cleaned)[:8]


def build_deep_summary(title: str, rss_summary: str, article_bits: list[str]) -> tuple[str, str]:
    candidates = []
    candidates.extend(sentence_split(rss_summary))
    for bit in article_bits:
        candidates.extend(sentence_split(bit))
    candidates = dedupe_sentences(candidates)

    summary_parts: list[str] = []
    total_len = 0
    for part in candidates:
        plain = strip_html(part)
        if normalize_text(plain) == normalize_text(title):
            continue
        if len(plain) < 20:
            continue
        if any(bad in plain for bad in BOILERPLATE_PATTERNS):
            continue
        summary_parts.append(plain)
        total_len += len(plain)
        if len(summary_parts) >= 4 and total_len >= 130:
            break

    if not summary_parts:
        fallback = strip_html(rss_summary) or title
        summary_parts = sentence_split(fallback)[:3] or [fallback]

    summary = "".join(summary_parts)

    quote_parts: list[str] = []
    quote_len = 0
    for part in summary_parts:
        quote_parts.append(part)
        quote_len += len(part)
        if quote_len >= 60:
            break
    quote = "".join(quote_parts) if quote_parts else summary[:80]
    return summary, quote


def decode_google_news_url(source_url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(source_url)
        if parsed.hostname != "news.google.com":
            return source_url

        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            return source_url
        base64_str = path_parts[-1]

        raw_html = http_get(f"https://news.google.com/articles/{base64_str}")
        if "data-n-a-sg" not in raw_html:
            raw_html = http_get(f"https://news.google.com/rss/articles/{base64_str}")

        sig_match = re.search(r'data-n-a-sg="([^"]+)"', raw_html)
        ts_match = re.search(r'data-n-a-ts="([^"]+)"', raw_html)
        if not sig_match or not ts_match:
            return source_url

        payload = [[
            [
                "Fbv4je",
                (
                    '["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,'
                    'null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],'
                    f'"{base64_str}",{ts_match.group(1)},"{sig_match.group(1)}"]'
                ),
            ]
        ]]
        body = "f.req=" + urllib.parse.quote(json.dumps(payload))
        raw_resp = http_post("https://news.google.com/_/DotsSplashUi/data/batchexecute", body)
        parsed_resp = json.loads(raw_resp.split("\n\n", 1)[1])[:-2]
        decoded_url = json.loads(parsed_resp[0][2])[1]
        return decoded_url or source_url
    except Exception:
        return source_url


def extract_article_content(url: str) -> tuple[str, list[str]]:
    try:
        raw_html = http_get(url)
    except Exception:
        return "", []

    meta_candidates = [
        extract_meta_content(raw_html, "property", "og:description"),
        extract_meta_content(raw_html, "name", "description"),
        extract_meta_content(raw_html, "name", "twitter:description"),
        extract_meta_content(raw_html, "itemprop", "description"),
    ]
    meta_candidates.extend(extract_json_ld_text(raw_html))
    meta_candidates = [text for text in meta_candidates if len(text) >= 30]
    paragraphs = extract_paragraphs(raw_html)
    description = meta_candidates[0] if meta_candidates else ""
    return description, paragraphs


def prettify_source(source: str, final_url: str) -> str:
    cleaned = strip_html(source)
    if cleaned and cleaned not in {"Google 新闻", "Google News"}:
        return cleaned
    domain = urllib.parse.urlparse(final_url).netloc.lower().replace("www.", "")
    for site, label in SITE_LABELS.items():
        if site in domain:
            return label
    return domain or cleaned or "原文"


def fetch_sector_news(sector: str, sites: list[str], target_date: dt.date, timeout: int = 4) -> list[NewsItem]:
    keywords = TOPIC_KEYWORDS[sector]
    results: list[NewsItem] = []

    for site in sites:
        url = build_google_rss_url(site, keywords, target_date)
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                raw = resp.read()
            root = ET.fromstring(raw)
        except Exception:
            continue

        for item in root.findall("./channel/item"):
            raw_title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub = parse_pubdate(item.findtext("pubDate") or "")
            desc = strip_html(item.findtext("description") or "")
            src = item.find("source")
            source = (src.text.strip() if src is not None and src.text else SITE_LABELS.get(site, site))
            title = clean_title(raw_title, source)
            if not title or not link:
                continue
            if is_low_quality_candidate(title, desc, source):
                continue
            summary = desc if len(desc) >= 28 else title
            score = score_candidate(title, summary, source, sector, pub)
            results.append(
                NewsItem(
                    title=title,
                    link=link,
                    source=source,
                    summary=summary,
                    published=pub,
                    sector=sector,
                    score=score,
                    discovery_link=link,
                )
            )

    return results


def dedupe_and_rank(items: list[NewsItem], limit: int) -> list[NewsItem]:
    best_by_title: dict[str, NewsItem] = {}
    for item in items:
        key = normalize_text(item.title)
        existing = best_by_title.get(key)
        if not existing or (item.score, item.published) > (existing.score, existing.published):
            best_by_title[key] = item
    ranked = sorted(best_by_title.values(), key=lambda item: (item.score, item.published), reverse=True)
    return ranked[:limit]


def select_top_items(items: list[NewsItem], limit: int) -> list[NewsItem]:
    ranked = dedupe_and_rank(items, limit=max(limit * 4, 40))
    picked: list[NewsItem] = []
    source_counts: Counter[str] = Counter()
    sector_counts: Counter[str] = Counter()

    for item in ranked:
        if source_counts[item.source] >= 3:
            continue
        if sector_counts[item.sector] >= 4:
            continue
        picked.append(item)
        source_counts[item.source] += 1
        sector_counts[item.sector] += 1
        if len(picked) >= limit:
            return picked

    for item in ranked:
        if item in picked:
            continue
        picked.append(item)
        if len(picked) >= limit:
            break
    return picked[:limit]


def enrich_items(items: list[NewsItem]) -> list[NewsItem]:
    enriched: list[NewsItem] = []
    for item in items:
        final_url = decode_google_news_url(item.link)
        description, paragraphs = extract_article_content(final_url)
        article_bits = []
        if description:
            article_bits.append(description)
        article_bits.extend(paragraphs[:3])
        summary, quote = build_deep_summary(item.title, item.summary, article_bits)
        final_source = prettify_source(item.source, final_url)
        score = item.score
        if final_url != item.link:
            score += 2.4
        if len(summary) >= 120:
            score += 1.8
        if paragraphs:
            score += 1.4
        enriched.append(
            replace(
                item,
                link=final_url,
                source=final_source,
                summary=summary,
                quote=quote,
                score=score,
            )
        )
        time.sleep(0.15)
    return enriched


def choose_breakthroughs(items: list[NewsItem]) -> list[dict]:
    sector_counts = Counter(item.sector for item in items)
    text_all = " ".join(f"{item.title} {item.summary}" for item in items)
    mapping = {
        "AI": ("模型与应用突破", "Agentic AI、语音交互和企业级落地继续推高 AI 应用价值密度。"),
        "Chip": ("芯片与算力突破", "先进制程、算力供给和关键器件价格预期继续牵引产业链。"),
        "Robotics": ("机器人落地突破", "人形机器人与具身智能正在从概念验证走向标准体系和交付能力竞争。"),
        "EV": ("新能源车技术突破", "快充、电池和智驾协同升级，整车竞争回到系统能力。"),
    }
    ordered = [sector for sector, _ in sector_counts.most_common()]
    if "标准" in text_all and "Robotics" not in ordered:
        ordered.insert(0, "Robotics")
    if "台积电" in text_all and "Chip" not in ordered:
        ordered.insert(0, "Chip")
    if "比亚迪" in text_all and "EV" not in ordered:
        ordered.insert(0, "EV")

    out = []
    for sector in ordered[:3]:
        title, text = mapping.get(sector, ("技术突破", "关键赛道出现了值得跟进的新变量。"))
        out.append({"title": title, "text": text})
    while len(out) < 3:
        out.append({"title": "产业链进展", "text": "核心赛道正在从新闻热度转向真实交付与商业兑现。"})
    return out


def build_copy(items: list[NewsItem]) -> dict:
    text_all = " ".join(f"{item.title} {item.summary}" for item in items)
    sector_counts = Counter(item.sector for item in items)
    lead_sector = sector_counts.most_common(1)[0][0] if sector_counts else "AI"
    opening_map = {
        "AI": "今天的主线很明确：AI 不只是在卷模型能力，已经开始卷交互方式、组织执行和商业落地速度。",
        "Chip": "今天最硬的信号来自芯片链，先进制程、器件价格和算力供给一起在抬高行业预期。",
        "Robotics": "今天机器人赛道不是热闹而已，标准、零部件通用化和场景交付已经开始变成真问题。",
        "EV": "今天车圈继续上强度，快充、电池和智驾一起卷，用户感知会被直接拉高。",
    }
    insights = [
        "🤖 AI：模型竞争正在外溢到交互体验、Agent 执行链和企业采购决策。",
        "🧠 芯片：先进制程、关键器件和算力供给仍是最确定的主线。",
        "🦾 机器人：标准体系和关键部件通用化，是商业化速度的前置条件。",
        "🚗 新能源车：补能效率、整车电气架构和智驾体验正在合并成同一场竞争。",
    ]
    if "台积电" in text_all:
        insights[1] = "🧠 芯片：台积电报价和先进制程景气度，继续决定算力链条的利润分配。"
    if "比亚迪" in text_all or "闪充" in text_all:
        insights[3] = "🚗 新能源车：比亚迪等厂商把竞争从单车参数，推向补能网络和全栈架构。"
    if "标准" in text_all and "机器人" in text_all:
        insights[2] = "🦾 机器人：国家级标准体系落地后，行业会加速从展示型产品转向工程交付。"

    return {
        "title": "震惊！硬科技今天信息量爆炸🤯 10 条干货看完就知道钱和趋势往哪走（建议收藏）",
        "open": opening_map.get(lead_sector, "今天硬科技四条主线同时有动静，信息量很大，但底层逻辑都在指向系统能力竞争。"),
        "insights": insights,
    }


def build_day_payload(items: list[NewsItem], target_date: dt.date) -> dict:
    generated_at = dt.datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d %H:%M")
    sector_count = Counter(item.sector for item in items)
    total = max(len(items), 1)
    sectors = [
        {"name": "AI", "ratio": round(sector_count["AI"] * 100 / total), "color": "#39c2ff"},
        {"name": "Chip", "ratio": round(sector_count["Chip"] * 100 / total), "color": "#8b93ff"},
        {"name": "Robotics", "ratio": round(sector_count["Robotics"] * 100 / total), "color": "#42d392"},
        {"name": "EV", "ratio": round(sector_count["EV"] * 100 / total), "color": "#ffb347"},
    ]
    delta = 100 - sum(item["ratio"] for item in sectors)
    sectors[0]["ratio"] += delta

    return {
        "updatedAt": f"{generated_at} (Asia/Shanghai)",
        "breakthroughs": choose_breakthroughs(items),
        "sectors": sectors,
        "heatmap": {
            "cols": ["近1季度", "中期1年", "长期3年"],
            "rows": [
                {"name": "AI", "scores": [9, 8, 7]},
                {"name": "Chip", "scores": [8, 8, 9]},
                {"name": "Robotics", "scores": [7, 8, 8]},
                {"name": "EV", "scores": [8, 9, 8]},
            ],
        },
        "news": [
            {
                "tag": TAG_BY_SECTOR.get(item.sector, item.sector),
                "title": item.title,
                "summary": item.summary,
                "quote": item.quote,
                "source": item.source,
                "link": item.link,
            }
            for item in items
        ],
        "copy": build_copy(items),
    }


def load_archive(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def prune_archive(archive: dict, keep_days: int) -> dict:
    ordered_keys = sorted(archive.keys(), reverse=True)
    keep = ordered_keys[:keep_days]
    return {key: archive[key] for key in keep}


def generate_for_date(target_date: dt.date, limit: int) -> dict | None:
    all_items: list[NewsItem] = []
    for sector in TOPIC_KEYWORDS:
        all_items.extend(fetch_sector_news(sector, WHITELIST_SITES, target_date))

    if not all_items:
        return None

    candidates = dedupe_and_rank(all_items, limit=max(limit + 4, 14))
    enriched = enrich_items(candidates[:4])
    ranked = select_top_items(enriched + candidates, limit=limit)
    return build_day_payload(ranked, target_date)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="hardtech-live-data.json", help="Output JSON path")
    parser.add_argument("--limit", type=int, default=10, help="Top N news")
    parser.add_argument("--date", help="Target date in YYYY-MM-DD, defaults to today Asia/Shanghai")
    parser.add_argument("--backfill-days", type=int, default=1, help="Generate archive for N days ending at --date/today")
    parser.add_argument("--archive-days", type=int, default=7, help="Keep latest N days in archive")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_date = dt.datetime.now(SHANGHAI_TZ).date()
    if args.date:
        target_date = dt.datetime.strptime(args.date, "%Y-%m-%d").date()

    out_path = Path(args.out)
    archive = load_archive(out_path)
    updated_dates: list[str] = []

    for offset in range(max(args.backfill_days, 1) - 1, -1, -1):
        day = target_date - dt.timedelta(days=offset)
        day_key = day.strftime("%Y-%m-%d")
        payload = generate_for_date(day, args.limit)
        if payload:
            archive[day_key] = payload
            updated_dates.append(day_key)

    if not updated_dates and not archive:
        raise SystemExit("No news found from whitelist. Check network or site coverage.")

    archive = prune_archive(archive, args.archive_days)
    out_path.write_text(json.dumps(archive, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated: {out_path} | updated_dates={','.join(updated_dates) or 'none'} | archive_days={len(archive)}")


if __name__ == "__main__":
    main()
