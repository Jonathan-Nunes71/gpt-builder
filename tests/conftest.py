from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest


@pytest.fixture
def sample_html() -> Callable[[str], str]:
    fixtures_dir = Path(__file__).parent / "fixtures"

    def _load(name: str) -> str:
        return (fixtures_dir / name).read_text(encoding="utf-8")

    return _load
