# GPT Builder Scraper

## Présentation

Ce dépôt propose une architecture Scrapy prête pour un projet de collecte conforme et responsable. Elle implémente l'intégralité du cahier des charges fourni, avec configuration TOML/ENV, modèles Pydantic, pipelines de persistance, exports multi-formats, tests Pytest + VCR.py, observabilité et conteneurisation.

## Configuration

1. Copier `.env.example` vers `.env` et ajuster les variables.
2. Adapter `configs/settings.toml` avec les informations du projet cible.
3. Vérifier le respect des contraintes légales (robots.txt, ToS, RGPD) avant toute exécution.

## Installation

```bash
poetry install
poetry run pre-commit install  # optionnel si vous ajoutez pre-commit
```

## Exécution

```bash
poetry run python scripts/run_spider.py
```

Le spider `SourceSpider` se base sur la configuration TOML pour déterminer les URLs de pagination et de détail. Les données valides sont insérées dans SQLite puis exportables via les utilitaires d'`ExportManager`.

## Tests

```bash
poetry run pytest
```

Les tests vérifient les sélecteurs, la normalisation des champs et la reproductibilité via VCR.py.

## Observabilité

* Logs JSON structurés (`app/observability/logs.py`).
* Collecteur de métriques simple (`app/observability/metrics.py`) exportant un fichier JSON.

## Conformité

* Respect `robots.txt` et délais entre requêtes (`AUTOTHROTTLE`, `DOWNLOAD_DELAY`).
* Limitation des retries et prise en compte des codes 429/5xx.
* Pas de contournement de CAPTCHA ni de paywall.
* Journaux structurés incluant user-agent explicite.

## Table de mapping (exemple)

| champ           | sélecteur                                        | type    | post-traitement              | obligatoire |
| --------------- | ------------------------------------------------ | ------- | ---------------------------- | ----------- |
| `titre`         | `//h1/text()`                                    | string  | `strip()`                    | oui         |
| `prix`          | `//span[contains(@class,'price')]/text()`        | decimal | `normalize_price('EUR')`    | oui         |
| `disponibilite` | `//div[contains(@class,'availability')]/text()`  | string  | `strip()`                    | non         |

## Docker

```bash
make docker-build
make docker-run
```

## Checklist d'audit

- [x] Respect robots.txt / délais
- [x] Modèles Pydantic
- [x] Tests Pytest + VCR.py
- [x] Export JSONL/CSV/Parquet
- [x] Observabilité (logs + métriques)
- [x] Dockerfile + CI

## Roadmap

1. Support JSON-LD enrichi et découverte sitemap.
2. Intégration Playwright pour contenu dynamique.
3. Partitionnement Parquet par date.
