"""Shared test fixtures."""

from pathlib import Path

import pytest

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@pytest.fixture
def sod_filepath():
    return TEMPLATES_DIR / "sod_original_template_pack.txt"


@pytest.fixture
def hota_filepath():
    return TEMPLATES_DIR / "hota_original_template_pack.h3t"


@pytest.fixture
def hota_complex_filepath():
    return TEMPLATES_DIR / "hota_complex_pack.h3t"
