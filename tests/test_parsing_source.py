from __future__ import annotations

from decimal import Decimal

import pytest
import requests
import vcr

from app.parsers.source_parser import SourceParser, map_listing_urls


@pytest.fixture
def parser() -> SourceParser:
    return SourceParser()


def test_extract_list_urls(parser: SourceParser, sample_html):
    html = sample_html("listing.html")
    urls = parser.extract_list_urls(html)
    assert urls == [
        "https://<<exemple.com>>/produit/1",
        "https://<<exemple.com>>/produit/2",
    ]


@pytest.mark.parametrize(
    "fixture,expected",
    [
        (
            "detail.html",
            {
                "titre": "Produit 1",
                "prix": Decimal("12.99"),
                "disponibilite": "En stock",
            },
        ),
    ],
)
def test_parse_detail(parser: SourceParser, sample_html, fixture: str, expected: dict):
    html = sample_html(fixture)
    item = parser.parse_detail(html, source="<<Source 1>>", url="https://<<exemple.com>>/produit/1")
    assert item.titre == expected["titre"]
    assert item.prix == expected["prix"]
    assert item.disponibilite == expected["disponibilite"]


def test_map_listing_urls(parser: SourceParser, sample_html):
    html = sample_html("listing.html")
    urls = map_listing_urls([html, html], parser)
    assert len(urls) == 2
    assert urls[0].startswith("https://")


def test_vcr_example(tmp_path):
    cassette_path = "tests/cassettes/example.yaml"
    session = requests.Session()
    session.trust_env = False
    with vcr.use_cassette(cassette_path):
        response = session.get("https://example.com/", proxies={"http": None, "https": None})
    assert response.status_code == 200
