"""各新闻源适配器。每个源封装为一个独立函数，互不影响。"""

import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_TIMEOUT = 15
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}


# ---------------------------------------------------------------------------
# 1. 新浪财经 — 滚动新闻（按分类）
# ---------------------------------------------------------------------------
def fetch_sina(limit: int = 10) -> list[dict]:
    """新浪财经 — 综合、国内、国际三个分类滚动新闻"""
    categories = [
        (2516, "综合"),
        (2517, "国内财经"),
        (2519, "国际财经"),
    ]
    news = []
    per_cat = max(1, limit // len(categories))
    for lid, label in categories:
        try:
            resp = requests.get(
                "https://feed.sina.com.cn/api/roll/get",
                params={"pageid": 153, "lid": lid, "num": per_cat, "versionNumber": 1},
                headers=_HEADERS,
                timeout=_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            for item in (data.get("result", {}).get("data") or []):
                title = (item.get("title") or "").strip()
                if not title:
                    continue
                news.append({
                    "title": _clean(title),
                    "url": item.get("url") or item.get("link") or "",
                    "summary": _clean(item.get("summary", item.get("intro", ""))),
                    "source": "新浪财经",
                })
        except Exception as e:
            logger.warning("新浪财经(lid=%s)采集失败: %s", lid, e)
    return news[:limit]


# ---------------------------------------------------------------------------
# 2. 华尔街见闻 — 全球快讯
# ---------------------------------------------------------------------------
def fetch_wallstreetcn(limit: int = 10) -> list[dict]:
    news = []
    try:
        resp = requests.get(
            "https://api-one.wallstcn.com/apiv1/content/lives",
            params={"channel": "global-channel", "limit": limit},
            headers={**_HEADERS, "Origin": "https://wallstreetcn.com"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        for item in (resp.json().get("data", {}).get("items", [])):
            title = (item.get("title") or item.get("content_text") or "").strip()
            if not title:
                continue
            news.append({
                "title": _clean(title[:120]),
                "url": item.get("uri", "") or "https://wallstreetcn.com/live/global",
                "summary": _clean((item.get("content_text") or "")[:200]),
                "source": "华尔街见闻",
            })
    except Exception as e:
        logger.warning("华尔街见闻采集失败: %s", e)
    return news[:limit]


# ---------------------------------------------------------------------------
# 3. 财联社 — 电报
# ---------------------------------------------------------------------------
def fetch_cls(limit: int = 10) -> list[dict]:
    """爬取财联社电报页面 HTML"""
    news = []
    try:
        resp = requests.get(
            "https://www.cls.cn/telegraph",
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        for div in soup.select("div.telegraph-content-box"):
            txt = div.text.strip()
            if not txt:
                continue
            title = txt[:120]
            # 跳过非新闻元素
            if any(skip in title for skip in ("关于我们", "网站声明", "联系方式")):
                continue
            news.append({
                "title": _clean(title),
                "url": "https://www.cls.cn/telegraph",
                "summary": "",
                "source": "财联社",
            })
    except Exception as e:
        logger.warning("财联社采集失败: %s", e)
    return news[:limit]


# ---------------------------------------------------------------------------
# 4. 东方财富 — 主要指数行情
# ---------------------------------------------------------------------------
def fetch_eastmoney_indices() -> list[dict]:
    """主要指数实时行情（非新闻，作为市场背景补充）"""
    news = []
    try:
        resp = requests.get(
            "https://push2.eastmoney.com/api/qt/ulist.np/get",
            params={
                "fltt": 2,
                "fields": "f2,f3,f4,f12,f14",
                "secids": "1.000001,0.399001,0.399006,1.000300,0.399300,0.688001",
            },
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        diff = (resp.json().get("data") or {}).get("diff") or {}
        if isinstance(diff, dict):
            name_map = {
                "1.000001": "上证指数",
                "0.399001": "深证成指",
                "0.399006": "创业板指",
                "1.000300": "沪深300",
                "0.399300": "沪深300",
                "0.688001": "科创50",
            }
            for secid, item in diff.items():
                name = name_map.get(secid, secid)
                price = item.get("f2", "-")
                pct = item.get("f3", "-")
                if price == "-" or pct == "-":
                    continue
                sign = "📈" if float(pct) >= 0 else "📉"
                news.append({
                    "title": f"{sign} {name} {price} ({pct}%)",
                    "url": "https://quote.eastmoney.com/",
                    "summary": f"{name} 当前 {price}，涨跌幅 {pct}%",
                    "source": "行情数据",
                })
    except Exception as e:
        logger.warning("东方财富行情获取失败: %s", e)
    return news


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()
