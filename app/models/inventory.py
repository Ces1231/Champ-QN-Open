"""Pydantic models for inventory input and assessment output.

The inventory schema is intentionally simple and free-text-tolerant: each
asset carries a list of algorithm/protocol identifier strings (e.g.
"RSA-2048", "TLS1.2", "AES-256-GCM", "ML-KEM-768"). This keeps the reference
scanner usable against hand-written inventories, spreadsheet exports, or
lightweight discovery tool output without requiring a heavyweight schema.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

MAX_STRING_LENGTH = 256
MAX_ALGORITHM_STRING_LENGTH = 128


class Classification(str, Enum):
    QUANTUM_VULNERABLE = "Quantum-vulnerable"
    TRANSITION_REQUIRED = "Transition required"
    HYBRID_READY = "Hybrid-ready"
    POST_QUANTUM_READY = "Post-quantum-ready"
    UNKNOWN = "Unknown or requires validation"


class Severity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


class InventoryAsset(BaseModel):
    """A single system, service, certificate, or network element being assessed."""

    id: str = Field(..., min_length=1, max_length=MAX_STRING_LENGTH)
    category: str | None = Field(default=None, max_length=MAX_STRING_LENGTH)
    algorithms: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=1024)

    @field_validator("algorithms")
    @classmethod
    def _validate_algorithms(cls, value: list[str]) -> list[str]:
        cleaned = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("each algorithm entry must be a string")
            item = item.strip()
            if not item:
                continue
            if len(item) > MAX_ALGORITHM_STRING_LENGTH:
                raise ValueError(
                    f"algorithm string exceeds {MAX_ALGORITHM_STRING_LENGTH} characters"
                )
            cleaned.append(item)
        return cleaned


class Inventory(BaseModel):
    """A named collection of assets submitted for assessment."""

    inventory_name: str | None = Field(default=None, max_length=MAX_STRING_LENGTH)
    assets: list[InventoryAsset] = Field(default_factory=list)


class AlgorithmFinding(BaseModel):
    """A single detected algorithm/protocol reference within one asset."""

    raw_value: str
    matched_name: str
    category: str
    classification: Classification
    severity: Severity
    guidance: str


class AssetFinding(BaseModel):
    """All findings for one asset, plus the asset's own rollup classification."""

    asset_id: str
    asset_category: str | None = None
    findings: list[AlgorithmFinding]
    asset_classification: Classification
    asset_score: int = Field(ge=0, le=100)


class StandardsReference(BaseModel):
    source: str
    reference: str
    url: str
    note: str


class AssessmentResult(BaseModel):
    """Full assessment output — the machine-readable report body."""

    inventory_name: str | None = None
    generated_at: str
    scanner_version: str
    asset_count: int
    finding_count: int
    overall_score: int = Field(ge=0, le=100)
    overall_classification: Classification
    findings_by_severity: dict[str, int]
    assets: list[AssetFinding]
    standards_references: list[StandardsReference]
    disclaimer: str
