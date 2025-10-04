"""Data models for scraped items and validation."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductItem(BaseModel):
    """Represents a single product extracted from the target website."""

    source: str = Field(..., description="Human readable label of the data source")
    url: str = Field(..., description="Canonical URL of the product detail page")
    titre: str = Field(..., description="Titre du produit")
    prix: Decimal = Field(..., description="Prix TTC du produit en devise locale")
    disponibilite: Optional[str] = Field(
        default=None, description="Texte décrivant la disponibilité du produit"
    )
    crawled_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp UTC de l'extraction",
    )

    @field_validator("titre")
    @classmethod
    def strip_title(cls, value: str) -> str:  # noqa: D401
        """Normalize the title by stripping extra whitespace."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Le titre ne peut pas être vide")
        return cleaned

    @field_validator("prix")
    @classmethod
    def positive_price(cls, value: Decimal) -> Decimal:  # noqa: D401
        """Ensure prices are positive."""
        if value <= 0:
            raise ValueError("Le prix doit être positif")
        return value
