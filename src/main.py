"""微信金融新闻小助手 — 主入口

流程：采集新闻 → Claude 总结 → 企业微信推送
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 sys.path 中（支持 python src/main.py 和 python -m src.main 两种方式）
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config.config import config
from src.collector.engine import collect
from src.pusher.pusher import push_newsletter
from src.summarizer.summarizer import summarize


def setup_logging():
    log_dir = config.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"finance_{datetime.now():%Y%m%d}.log"

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(fmt)

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # 避免重复 handler
    if not root.handlers:
        root.addHandler(handler)
        root.addHandler(console)

    return log_file


def main():
    log_file = setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("金融新闻小助手启动")
    logger.info("日志文件: %s", log_file)

    # 0. 检查配置
    if not config.is_valid:
        logger.error("配置不完整，请检查 .env 文件中的 DEEPSEEK_API_KEY 和 WEWORK_WEBHOOK_URL")
        sys.exit(1)

    # 1. 采集新闻
    logger.info("Step 1/3: 开始采集新闻...")
    news = collect(max_total=config.max_news_total, per_source=config.news_limit_per_source)
    if not news:
        logger.warning("未采集到任何新闻，流程终止")
        push_newsletter("今日未能成功采集到金融新闻，请检查网络或新闻源。", [])
        return
    logger.info("共采集 %d 条新闻", len(news))

    # 2. 生成摘要
    logger.info("Step 2/3: 调用 Claude 生成摘要...")
    summary = summarize(news)
    logger.info("摘要内容:\n%s", summary)

    # 3. 推送微信
    logger.info("Step 3/3: 推送到企业微信...")
    ok = push_newsletter(summary, news)
    if ok:
        logger.info("全部完成")
    else:
        logger.error("推送失败，摘要已保存在日志中")


if __name__ == "__main__":
    main()
