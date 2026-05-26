import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    wework_webhook_url: str = os.getenv("WEWORK_WEBHOOK_URL", "")
    news_limit_per_source: int = int(os.getenv("NEWS_LIMIT_PER_SOURCE", "10"))
    max_news_total: int = int(os.getenv("MAX_NEWS_TOTAL", "30"))
    log_dir: Path = Path(__file__).resolve().parent.parent / "logs"

    @property
    def is_valid(self) -> bool:
        return bool(self.deepseek_api_key) and bool(self.wework_webhook_url)


config = Config()
