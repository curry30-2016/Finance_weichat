"""采集引擎：依次调用各源、合并去重。"""

import logging

from src.collector.sources import (
    fetch_cls,
    fetch_eastmoney_indices,
    fetch_sina,
    fetch_wallstreetcn,
)

logger = logging.getLogger(__name__)

SOURCES = [
    ("新浪财经", fetch_sina),
    ("华尔街见闻", fetch_wallstreetcn),
    ("财联社", fetch_cls),
    ("行情数据", fetch_eastmoney_indices),
]


def collect(max_total: int = 30, per_source: int = 10) -> list[dict]:
    """采集所有源，按标题去重后返回。

    Returns:
        list[dict]: [{title, url, summary, source}, ...]
    """
    all_news: list[dict] = []
    seen_titles: set[str] = set()

    for name, fetcher in SOURCES:
        logger.info("正在采集: %s", name)
        try:
            items = fetcher(limit=per_source) if name != "行情数据" else fetcher()
        except Exception as e:
            logger.error("采集器 %s 异常: %s", name, e)
            continue

        for item in items:
            key = item["title"][:30]
            if key in seen_titles:
                continue
            seen_titles.add(key)
            all_news.append(item)

        logger.info("  %s 采集到 %d 条", name, len(items))

    logger.info("去重后共 %d 条新闻", len(all_news))
    return all_news[:max_total]
