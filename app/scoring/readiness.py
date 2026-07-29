"""Readiness scoring: turns a list of algorithm findings into a 0-100 score
and an overall classification.

Scoring model (intentionally simple and documented, not a black box):

- Each finding contributes a fixed point value based on its classification.
- The overall score is the average of all finding contributions, rounded to
  the nearest integer, clamped to [0, 100].
- An inventory or asset with zero findings scores 0 -- "no identifiable
  cryptography" cannot be asserted as ready.
- The overall *classification* is the most severe classification present
  ("most-conservative-wins"), not an average -- a single quantum-vulnerable
  finding should not be hidden by many post-quantum-ready ones.
"""

from __future__ import annotations

from app.models.inventory import AlgorithmFinding, Classification, Severity

_FINDING_POINTS: dict[Classification, int] = {
    Classification.POST_QUANTUM_READY: 100,
    Classification.HYBRID_READY: 85,
    Classification.TRANSITION_REQUIRED: 50,
    Classification.UNKNOWN: 40,
    Classification.QUANTUM_VULNERABLE: 10,
}

# Most severe first -- used to pick the overall classification.
_SEVERITY_ORDER: list[Classification] = [
    Classification.QUANTUM_VULNERABLE,
    Classification.TRANSITION_REQUIRED,
    Classification.UNKNOWN,
    Classification.HYBRID_READY,
    Classification.POST_QUANTUM_READY,
]


def score_findings(findings: list[AlgorithmFinding]) -> int:
    """Average per-finding point value, clamped to [0, 100]. 0 if no findings."""
    if not findings:
        return 0
    total = sum(_FINDING_POINTS[f.classification] for f in findings)
    avg = round(total / len(findings))
    return max(0, min(100, avg))


def overall_classification(findings: list[AlgorithmFinding]) -> Classification:
    """Most severe classification present. UNKNOWN if there are no findings."""
    if not findings:
        return Classification.UNKNOWN
    present = {f.classification for f in findings}
    for classification in _SEVERITY_ORDER:
        if classification in present:
            return classification
    return Classification.UNKNOWN  # unreachable in practice; defensive default


def severity_counts(findings: list[AlgorithmFinding]) -> dict[str, int]:
    """Count of findings per severity level, including zero-count levels."""
    counts: dict[str, int] = {s.value: 0 for s in Severity}
    for f in findings:
        counts[f.severity.value] += 1
    return counts
