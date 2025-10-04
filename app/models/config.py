"""Configuration models for the scraping project."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PageConfig(BaseModel):
    type: str
    pattern: str


class FieldConfig(BaseModel):
    nom: str
    type: str
    obligatoire: bool = False


class TargetConfig(BaseModel):
    label: str
    domain: str
    pages: List[PageConfig]
    champs: List[FieldConfig]

    @property
    def detail_page(self) -> Optional[PageConfig]:
        for page in self.pages:
            if page.type == "detail":
                return page
        return None


class ProjectConfig(BaseModel):
    nom: str
    description: str
    surface_web_dynamique: bool = False
    volumetrie_cibles_par_jour: int
    delai_max_cycle: str
    donnees_sensibles: bool = False
    zone_juridique: List[str] = Field(default_factory=list)
    contact_dpo: str


class OutputConfig(BaseModel):
    stockage: List[str]
    format_export: List[str]
    bucket: str


class ConstraintConfig(BaseModel):
    respect_robots_txt: bool = True
    respect_tos: bool = True
    taux_req_max_par_domaine: float = 1.0
    concurrence_max: int = 4
    timeouts_secondes: int = 30
    retries_max: int = 3
    backoff: str = "exponentiel_jitter"
    pas_de_captcha_bypass: bool = True
    pas_de_paywall_bypass: bool = True

    @field_validator("taux_req_max_par_domaine")
    @classmethod
    def validate_rate(cls, value: float) -> float:  # noqa: D401
        """Ensure the rate is positive."""
        if value <= 0:
            raise ValueError("Le taux de requêtes par domaine doit être > 0")
        return value

    @field_validator("concurrence_max")
    @classmethod
    def validate_concurrency(cls, value: int) -> int:  # noqa: D401
        """Ensure concurrency is strictly positive."""
        if value <= 0:
            raise ValueError("La concurrence maximale doit être > 0")
        return value


class ObservabilityConfig(BaseModel):
    logs_structures: bool = True
    metriques: List[str] = Field(default_factory=list)


class Settings(BaseModel):
    projet: ProjectConfig
    cibles: List[TargetConfig]
    sortie: OutputConfig
    contraintes: ConstraintConfig
    observabilite: ObservabilityConfig
    settings_path: Optional[Path] = None

    class Config:
        arbitrary_types_allowed = True
