"""CLI helper to run the Scrapy spider programmatically."""
from __future__ import annotations

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from app.config import load_environment
from app.observability.logs import configure_logging
from app.spiders.source_spider import SourceSpider


def main() -> None:
    env = load_environment()
    configure_logging(env.log_level)

    settings = get_project_settings()
    settings.set("LOG_LEVEL", env.log_level)
    settings.set("HTTPPROXY_ENABLED", bool(env.http_proxy))
    if env.http_proxy:
        settings.set("HTTP_PROXY", env.http_proxy)

    process = CrawlerProcess(settings=settings)
    process.crawl(SourceSpider)
    process.start()


if __name__ == "__main__":
    main()
