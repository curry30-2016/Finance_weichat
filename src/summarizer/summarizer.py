"""调用 DeepSeek API 将新闻列表总结为一段每日简报。"""

import logging

from openai import OpenAI

from config.config import config

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = "你是一位专业的金融新闻编辑。你擅长用简洁清晰的中文概括每日市场动态。"


def summarize(news_list: list[dict]) -> str:
    """将新闻列表交给 DeepSeek 总结，返回一段 200~300 字的简报文本。"""
    if not news_list:
        return "今日暂无金融新闻。"

    # 格式化新闻文本
    lines = []
    for i, n in enumerate(news_list, 1):
        title = n.get("title", "")
        summary = n.get("summary", "")
        source = n.get("source", "")
        if summary:
            lines.append(f"{i}. [{source}] {title} — {summary}")
        else:
            lines.append(f"{i}. [{source}] {title}")
    news_text = "\n".join(lines)

    user_msg = (
        "以下是今天采集到的金融新闻列表。请你从中挑选最重要、最有影响力的内容，"
        "整理成一段约 200-300 字的每日金融简报。\n"
        "简报应覆盖：大盘走势、重大政策、市场热点。\n"
        "语言简洁，无需分段，用陈述句连贯成一段话。\n\n"
        f"新闻列表:\n{news_text}"
    )

    try:
        client = OpenAI(
            api_key=config.deepseek_api_key,
            base_url="https://api.deepseek.com",
        )
        resp = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=1024,
            temperature=0.3,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        summary = resp.choices[0].message.content.strip()
        logger.info("DeepSeek 总结完成（%d 字符）", len(summary))
        return summary
    except Exception as e:
        logger.error("DeepSeek API 调用失败: %s", e)
        # 降级：直接拼接标题作为简报
        fallback = "今日金融要闻：\n" + "\n".join(
            f"• {n['title']}" for n in news_list[:10]
        )
        return fallback
