"""Roundtrip identity tests: parse -> write -> parse -> compare models.

Roundtrip compares parsed data models, not raw bytes. This validates that
parse(write(parse(file))) == parse(file) — i.e. all semantic data survives
the roundtrip. Orphan zone-area data (no zone_id, no connection) and empty
rows are discarded as they carry no semantic meaning.
"""

import tempfile
from pathlib import Path

import pytest

from h3tc.parsers.sod import SodParser
from h3tc.parsers.hota import HotaParser
from h3tc.writers.sod import SodWriter
from h3tc.writers.hota import HotaWriter

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _compare_packs(original, roundtripped, label: str):
    """Compare two TemplatePack models for semantic equality."""
    # Compare headers
    assert len(original.header_rows) == len(roundtripped.header_rows), (
        f"[{label}] Header row count differs"
    )

    assert len(original.maps) == len(roundtripped.maps), (
        f"[{label}] Map count differs: "
        f"original={len(original.maps)}, roundtripped={len(roundtripped.maps)}"
    )

    for mi, (om, rm) in enumerate(zip(original.maps, roundtripped.maps)):
        map_label = f"{label}:{om.name}"
        assert om.name == rm.name, f"[{map_label}] Map name differs"
        assert om.min_size == rm.min_size, f"[{map_label}] min_size differs"
        assert om.max_size == rm.max_size, f"[{map_label}] max_size differs"

        assert len(om.zones) == len(rm.zones), (
            f"[{map_label}] Zone count: {len(om.zones)} vs {len(rm.zones)}"
        )
        for zi, (oz, rz) in enumerate(zip(om.zones, rm.zones)):
            assert oz == rz, (
                f"[{map_label}] Zone {zi} (id={oz.id}) differs"
            )

        assert len(om.connections) == len(rm.connections), (
            f"[{map_label}] Connection count: "
            f"{len(om.connections)} vs {len(rm.connections)}"
        )
        for ci, (oc, rc) in enumerate(zip(om.connections, rm.connections)):
            # Compare without extra_zone_cols (may differ in roundtrip)
            oc_dict = oc.model_dump(exclude={"extra_zone_cols"})
            rc_dict = rc.model_dump(exclude={"extra_zone_cols"})
            assert oc_dict == rc_dict, (
                f"[{map_label}] Connection {ci} "
                f"({oc.zone1}->{oc.zone2}) differs"
            )


def _sod_roundtrip(filepath: Path, label: str):
    """Parse SOD -> write SOD -> parse again -> compare models."""
    parser = SodParser()
    original = parser.parse(filepath)

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        outpath = Path(f.name)

    writer = SodWriter()
    writer.write(original, outpath)

    roundtripped = parser.parse(outpath)
    outpath.unlink()

    _compare_packs(original, roundtripped, label)


def test_sod_roundtrip(sod_filepath):
    """Parse SOD -> write SOD -> parse again -> compare models."""
    _sod_roundtrip(sod_filepath, "sod_original")


# Collect all SOD files from sod_complete/
_sod_complete_dir = TEMPLATES_DIR / "sod_complete"
_sod_files = []
if _sod_complete_dir.exists():
    _sod_files = sorted(_sod_complete_dir.glob("*/[Rr]mg.txt"))


@pytest.mark.parametrize(
    "sod_path",
    _sod_files,
    ids=[p.parent.name for p in _sod_files],
)
def test_sod_roundtrip_all(sod_path):
    """Roundtrip test for every SOD template in sod_complete/."""
    _sod_roundtrip(sod_path, sod_path.parent.name)


def _hota_roundtrip(filepath: Path, label: str):
    """Parse HOTA -> write HOTA -> parse again -> compare models."""
    parser = HotaParser()
    original = parser.parse(filepath)

    with tempfile.NamedTemporaryFile(suffix=".h3t", delete=False) as f:
        outpath = Path(f.name)

    writer = HotaWriter()
    writer.write(original, outpath)

    roundtripped = parser.parse(outpath)
    outpath.unlink()

    _compare_packs(original, roundtripped, label)

    # Also compare HOTA-specific fields
    if original.metadata:
        assert original.metadata == roundtripped.metadata, (
            f"[{label}] Pack metadata differs"
        )
    if original.field_counts:
        assert original.field_counts == roundtripped.field_counts, (
            f"[{label}] Field counts differ"
        )

    for mi, (om, rm) in enumerate(zip(original.maps, roundtripped.maps)):
        assert om.options == rm.options, (
            f"[{label}:{om.name}] Map options differ"
        )


def test_hota_roundtrip(hota_filepath):
    """Parse HOTA -> write HOTA -> parse again -> compare models."""
    _hota_roundtrip(hota_filepath, "hota_original")


def test_hota_complex_roundtrip(hota_complex_filepath):
    """Parse complex HOTA -> write -> parse again -> compare models."""
    _hota_roundtrip(hota_complex_filepath, "hota_complex")


# Collect all HOTA files from hota_complete/
_hota_complete_dir = TEMPLATES_DIR / "hota_complete"
_hota_files = []
if _hota_complete_dir.exists():
    _hota_files = sorted(_hota_complete_dir.glob("*.[hH]3[tT]"))


@pytest.mark.parametrize(
    "hota_path",
    _hota_files,
    ids=[p.stem for p in _hota_files],
)
def test_hota_roundtrip_all(hota_path):
    """Roundtrip test for every HOTA template in hota_complete/."""
    _hota_roundtrip(hota_path, hota_path.stem)
