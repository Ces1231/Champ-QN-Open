import pytest

from app.models.inventory import Classification, Inventory
from app.reporting.report import InventoryTooLargeError, assess_inventory, render_markdown


def _inventory(assets):
    return Inventory.model_validate({"inventory_name": "Test Inventory", "assets": assets})


def test_assess_inventory_end_to_end():
    inv = _inventory(
        [
            {"id": "host-a", "algorithms": ["RSA-2048", "SHA-1"]},
            {"id": "host-b", "algorithms": ["ML-KEM-768", "ML-DSA-65", "AES-256-GCM"]},
        ]
    )
    result = assess_inventory(inv)
    assert result.asset_count == 2
    assert result.finding_count == 5
    assert result.overall_classification == Classification.QUANTUM_VULNERABLE
    assert len(result.assets) == 2
    assert result.assets[0].asset_id == "host-a"
    assert result.assets[0].asset_classification == Classification.QUANTUM_VULNERABLE
    assert result.assets[1].asset_classification == Classification.POST_QUANTUM_READY
    assert "preliminary" in result.disclaimer.lower()


def test_assess_inventory_with_no_assets():
    inv = _inventory([])
    result = assess_inventory(inv)
    assert result.asset_count == 0
    assert result.finding_count == 0
    assert result.overall_score == 0
    assert result.overall_classification == Classification.UNKNOWN


def test_assess_inventory_asset_with_no_algorithms():
    inv = _inventory([{"id": "empty-host", "algorithms": []}])
    result = assess_inventory(inv)
    assert result.assets[0].asset_score == 0
    assert result.assets[0].asset_classification == Classification.UNKNOWN


def test_standards_references_present_for_vulnerable_findings():
    inv = _inventory([{"id": "host-a", "algorithms": ["RSA-2048"]}])
    result = assess_inventory(inv)
    assert len(result.standards_references) > 0
    sources = {ref.source for ref in result.standards_references}
    assert "NIST" in sources


def test_too_many_assets_raises(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "max_assets", 1)
    inv = _inventory([{"id": "a", "algorithms": []}, {"id": "b", "algorithms": []}])
    with pytest.raises(InventoryTooLargeError):
        assess_inventory(inv)


def test_too_many_algorithms_per_asset_raises(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "max_algorithms_per_asset", 2)
    inv = _inventory([{"id": "a", "algorithms": ["RSA", "AES", "SHA-256"]}])
    with pytest.raises(InventoryTooLargeError):
        assess_inventory(inv)


def test_render_markdown_contains_key_sections():
    inv = _inventory([{"id": "host-a", "algorithms": ["RSA-2048"]}])
    result = assess_inventory(inv)
    md = render_markdown(result)
    assert "# CHAMP-QN Crypto Readiness Report" in md
    assert "host-a" in md
    assert "Overall readiness score" in md
    assert "Standards and guidance references" in md
    assert result.disclaimer in md
