"""Parsing helpers for the placeholder source."""
from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

from parsel import Selector

from app.models.items import ProductItem


@dataclass(slots=True)
class SourceParser:
    """Encapsulates parsing logic for the target website."""

    currency: str = "EUR"

    def extract_list_urls(self, html: str) -> List[str]:
        """Extract product detail URLs from a listing page."""
        selector = Selector(text=html)
        links = selector.xpath("//a[contains(@class, 'product-card')]/@href").getall()
        normalized = [self._normalize_url(link) for link in links if link]
        return [url for url in normalized if url]

    def parse_detail(self, html: str, *, source: str, url: str) -> ProductItem:
        """Parse a product detail page into a :class:`ProductItem`."""
        selector = Selector(text=html)

        titre = self._extract_title(selector)
        prix = self._extract_price(selector)
        disponibilite = self._extract_availability(selector)

        return ProductItem(
            source=source,
            url=url,
            titre=titre,
            prix=prix,
            disponibilite=disponibilite,
        )

    def _normalize_url(self, url: str) -> str:
        if url.startswith("//"):
            return f"https:{url}"
        return url.strip()

    def _extract_title(self, selector: Selector) -> str:
        title = selector.xpath("//h1/text()").get()
        if title:
            return title.strip()
        # fallback to meta
        meta_title = selector.xpath("//meta[@property='og:title']/@content").get()
        if meta_title:
            return meta_title.strip()
        raise ValueError("Titre introuvable dans la page")

    def _extract_price(self, selector: Selector) -> Decimal:
        price_text = selector.xpath("//span[contains(@class, 'price')]/text()").get()
        if not price_text:
            price_text = self._extract_price_from_jsonld(selector)
        if not price_text:
            raise ValueError("Prix introuvable dans la page")
        normalized = (
            price_text.replace("\xa0", " ")
            .replace("€", "")
            .replace("EUR", "")
            .replace(",", ".")
            .strip()
        )
        return Decimal(normalized)

    def _extract_price_from_jsonld(self, selector: Selector) -> str | None:
        scripts = selector.xpath("//script[@type='application/ld+json']/text()").getall()
        for script in scripts:
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and data.get("@type") == "Product":
                offers = data.get("offers")
                if isinstance(offers, dict):
                    price = offers.get("price")
                    if isinstance(price, str):
                        return price
                    if isinstance(price, (int, float)):
                        return str(price)
        return None

    def _extract_availability(self, selector: Selector) -> str | None:
        availability = selector.xpath(
            "//div[contains(@class, 'availability')]/text()"
        ).get()
        if availability:
            return availability.strip()
        return None


def map_listing_urls(html_pages: Iterable[str], parser: SourceParser) -> List[str]:
    """Flatten all listing pages into a list of unique product URLs."""
    seen: set[str] = set()
    results: List[str] = []
    for html in html_pages:
        for url in parser.extract_list_urls(html):
            if url not in seen:
                seen.add(url)
                results.append(url)
    return results
