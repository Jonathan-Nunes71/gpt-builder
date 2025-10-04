"""Scrapy spider orchestrating crawling for the configured source."""
from __future__ import annotations

import itertools
from typing import Iterable

import scrapy
from scrapy import Request

from app.config import load_environment, load_settings
from app.parsers.source_parser import SourceParser
from app.storage.repository import Repository
from app.utils.fingerprint import fingerprint_url


def _paginate(pattern: str) -> Iterable[str]:
    """Expand the {1..N} syntax into incremental URLs until missing."""
    if "{1.." not in pattern:
        yield pattern
        return

    prefix, range_part = pattern.split("{1..", 1)
    end_str, suffix = range_part.split("}", 1)
    end = int(end_str.replace("N", "100"))  # sensible upper bound placeholder
    for page in itertools.count(1):
        if page > end:
            break
        yield f"{prefix}{page}{suffix}"


class SourceSpider(scrapy.Spider):
    """Spider that navigates catalogue listings and detail pages."""

    name = "source_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DOWNLOAD_DELAY": 2,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 5,
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],
        "USER_AGENT": "gpt-builder-scraper/1.0 (+https://example.com/conformite)",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings_model = load_settings()
        self.env = load_environment()
        self.parser = SourceParser()
        self.repository = Repository(self.env.database_url)
        self.repository.ensure_schema()

    def start_requests(self):  # noqa: D401
        """Kick-off crawl using the configured listing patterns."""
        target = self.settings_model.cibles[0]
        for page in target.pages:
            if page.type != "liste":
                continue
            for url in _paginate(page.pattern):
                yield Request(url=url, callback=self.parse_listing, errback=self.on_error)

    def parse_listing(self, response: scrapy.http.Response):  # type: ignore[override]
        urls = self.parser.extract_list_urls(response.text)
        for url in urls:
            yield Request(url=url, callback=self.parse_detail, errback=self.on_error)

    def parse_detail(self, response: scrapy.http.Response):  # type: ignore[override]
        target = self.settings_model.cibles[0]
        item = self.parser.parse_detail(
            response.text, source=target.label, url=response.url
        )
        if self.repository.is_duplicate(fingerprint_url(response.url), item):
            self.logger.debug("Duplicate detected %s", response.url)
            return
        self.repository.save_item(item)
        yield item.dict()

    def on_error(self, failure):
        self.logger.error("Request failed: %s", failure)
        self.crawler.stats.inc_value("taux_erreur_http", 1)

    def closed(self, reason: str):
        self.repository.close()
        super().closed(reason)
