"""封装企业微信机器人 Webhook 推送。"""

import json
import logging

import requests

from config.config import config

logger = logging.getLogger(__name__)


def push_text(content: str) -> bool:
    """推送文本消息到企业微信群机器人。

    Args:
        content: 消息文本（支持 Markdown 语法子集）。

    Returns:
        True 表示推送成功。
    """
    if not config.wework_webhook_url:
        logger.error("未配置 WEWORK_WEBHOOK_URL")
        return False

    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    try:
        resp = requests.post(
            config.wework_webhook_url,
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("errcode") == 0:
            logger.info("企业微信推送成功")
            return True
        else:
            logger.error("企业微信推送失败: %s", result)
            return False
    except Exception as e:
        logger.error("企业微信推送异常: %s", e)
        return False


def push_newsletter(summary: str, news_list: list[dict]) -> bool:
    """推送完整的每日简报（含摘要 + 来源链接）。

    Args:
        summary: Claude 生成的总结文本。
        news_list: 原始新闻列表（用于生成来源链接）。

    Returns:
        True 表示推送成功。
    """
    # Markdown 正文
    lines = [
        "# 📊 每日金融简报",
        "",
        f"📅 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %A')}",
        "",
        summary,
        "",
        "---",
        "**📰 主要来源**",
    ]

    # 展示各来源的条目数
    source_count: dict[str, int] = {}
    for n in news_list:
        src = n.get("source", "其他")
        source_count[src] = source_count.get(src, 0) + 1

    lines.append(
        " | ".join(f"{src} {cnt}条" for src, cnt in source_count.items())
    )

    # 前 5 条链接
    lines.append("")
    lines.append("**🔗 快速链接**")
    for n in news_list[:5]:
        title = n.get("title", "")
        url = n.get("url", "")
        if url:
            lines.append(f"- [{title}]({url})")
        else:
            lines.append(f"- {title}")

    content = "\n".join(lines)
    return push_text(content)
