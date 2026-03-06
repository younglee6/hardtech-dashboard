#!/usr/bin/env python3
"""
Generate `hardtech-live-data.json` from whitelisted sites for hard-tech topics.

Approach:
- Query Google News RSS with `site:` filters + topic keywords + `when:1d`
- Keep top 10 deduplicated results
- Map to dashboard schema consumed by `hardtech-web-dashboard-demo.html`

Usage:
  python3 scripts/generate_live_data_from_whitelist.py \
    --out ../hardtech-live-data.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass


WHITELIST_SITES = [
    "eastmoney.com",       # 东方财富
    "myqcloud.com",        # 腾讯云
    "wallstreetcn.com",    # 华尔街见闻
    "caijing.com.cn",      # 财富系站点兜底
    "163.com",             # 网易
    "huxiu.com",           # 虎嗅
    "cnfol.com",           # 中金在线
]

TOPIC_KEYWORDS = {
    "AI": ["大模型", "AI", "Agentic AI", "智能体", "推理"],
    "Chip": ["芯片", "半导体", "台积电", "2nm", "5nm"],
    "Robotics": ["机器人", "人形机器人", "具身智能"],
    "EV": ["新能源汽车", "电池", "快充", "比亚迪", "智能驾驶"],
}

TAG_BY_SECTOR = {
    "AI": "AI",
    "Chip": "芯片",
    "Robotics": "机器人",
    "EV": "新能源车",
}


@dataclass
class NewsItem:
    title: str
    link: str
    source: str
    summary: str
    published: dt.datetime
    sector: str


def build_google_rss_url(site: str, keywords: list[str]) -> str:
    # query example: site:wallstreetcn.com (AI OR 大模型 OR ... ) when:1d
    joined = " OR ".join(keywords)
    query = f"site:{site} ({joined}) when:1d"
    params = {
        "q": query,
        "hl": "zh-CN",
        "gl": "CN",
        "ceid": "CN:zh-Hans",
    }
    return "https://news.google.com/rss/search?" + urllib.parse.urlencode(params)


def parse_pubdate(text: str) -> dt.datetime:
    try:
        t = email.utils.parsedate_to_datetime(text)
        if t.tzinfo is None:
            return t.replace(tzinfo=dt.timezone.utc)
        return t
    except Exception:
        return dt.datetime.now(dt.timezone.utc)


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", text).strip()


def fetch_sector_news(sector: str, sites: list[str], timeout: int = 12) -> list[NewsItem]:
    keywords = TOPIC_KEYWORDS[sector]
    results: list[NewsItem] = []

    for site in sites:
        url = build_google_rss_url(site, keywords)
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                raw = resp.read()
            root = ET.fromstring(raw)
        except Exception:
            continue

        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub = parse_pubdate(item.findtext("pubDate") or "")
            desc = strip_html(item.findtext("description") or "")
            src = item.find("source")
            source = (src.text.strip() if src is not None and src.text else site)
            if not title or not link:
                continue
            summary = desc if len(desc) >= 30 else f"{title}（来源：{source}）"
            results.append(
                NewsItem(
                    title=title,
                    link=link,
                    source=source,
                    summary=summary,
                    published=pub,
                    sector=sector,
                )
            )

    return results


def dedupe_and_rank(items: list[NewsItem], limit: int = 10) -> list[NewsItem]:
    seen = set()
    uniq: list[NewsItem] = []
    for x in sorted(items, key=lambda i: i.published, reverse=True):
        key = re.sub(r"\s+", "", x.title.lower())
        if key in seen:
            continue
        seen.add(key)
        uniq.append(x)
    return uniq[:limit]


def choose_breakthroughs(items: list[NewsItem]) -> list[dict]:
    c = Counter(i.sector for i in items)
    ordered = [k for k, _ in c.most_common(3)] or ["AI", "Chip", "EV"]
    mapping = {
        "AI": ("模型与应用突破", "AI 工具形态和交互方式持续升级，实用性进一步提升。"),
        "Chip": ("芯片与算力突破", "先进制程与算力供给成为产业链核心关注变量。"),
        "Robotics": ("机器人落地突破", "人形机器人与具身智能向标准化和商业化推进。"),
        "EV": ("新能源车技术突破", "电池、快充与智驾能力继续推动整车体验升级。"),
    }
    out = []
    for s in ordered[:3]:
        title, text = mapping.get(s, ("技术突破", "关键赛道出现进展。"))
        out.append({"title": title, "text": text})
    return out


def build_dashboard_json(items: list[NewsItem], tz: str = "Asia/Shanghai") -> dict:
    now = dt.datetime.now()
    date_key = now.strftime("%Y-%m-%d")
    updated_at = now.strftime("%Y-%m-%d %H:%M") + f" ({tz})"

    sector_count = Counter(i.sector for i in items)
    total = max(len(items), 1)

    sectors = [
        {"name": "AI", "ratio": round(sector_count["AI"] * 100 / total), "color": "#39c2ff"},
        {"name": "Chip", "ratio": round(sector_count["Chip"] * 100 / total), "color": "#8b93ff"},
        {"name": "Robotics", "ratio": round(sector_count["Robotics"] * 100 / total), "color": "#42d392"},
        {"name": "EV", "ratio": round(sector_count["EV"] * 100 / total), "color": "#ffb347"},
    ]

    # ensure sum == 100 for visual consistency
    delta = 100 - sum(s["ratio"] for s in sectors)
    sectors[0]["ratio"] += delta

    news = []
    for i in items:
        news.append(
            {
                "tag": TAG_BY_SECTOR.get(i.sector, i.sector),
                "title": i.title,
                "summary": i.summary,
                "quote": i.summary[:120],
                "source": i.source,
                "link": i.link,
            }
        )

    top_sector = sector_count.most_common(1)[0][0] if sector_count else "AI"
    top_text = {
        "AI": "AI 应用进入效率与治理并重阶段。",
        "Chip": "芯片与先进制程持续牵引行业预期。",
        "Robotics": "机器人标准化与场景化落地加速。",
        "EV": "新能源车技术竞争转向系统能力。",
    }.get(top_sector, "硬科技多赛道同步推进。")

    payload = {
        date_key: {
            "updatedAt": updated_at,
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
            "news": news,
            "copy": {
                "title": "震惊！硬科技今日高能速览🤯 10条干货建议收藏",
                "open": f"今天硬科技的核心变化是：{top_text} 从单点技术走向系统化能力比拼。",
                "insights": [
                    "🤖 AI：应用体验、组织稳定与治理要求同步上升。",
                    "🧠 芯片：先进制程与供给能力仍是产业主线。",
                    "🦾 机器人：标准体系与场景化交付成为关键分水岭。",
                    "🚗 新能源车：补能与智能化协同推动体验升级。",
                ],
            },
        }
    }
    return payload


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="hardtech-live-data.json", help="Output JSON path")
    p.add_argument("--limit", type=int, default=10, help="Top N news")
    args = p.parse_args()

    all_items: list[NewsItem] = []
    for sector in TOPIC_KEYWORDS.keys():
        all_items.extend(fetch_sector_news(sector, WHITELIST_SITES))

    ranked = dedupe_and_rank(all_items, limit=args.limit)
    if not ranked:
        raise SystemExit("No news found from whitelist. Check network or site coverage.")

    data = build_dashboard_json(ranked)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated: {args.out} | items={len(ranked)}")


if __name__ == "__main__":
    main()
