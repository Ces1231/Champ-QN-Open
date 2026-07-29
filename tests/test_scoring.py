from app.models.inventory import Classification
from app.scanners.crypto_scanner import classify_algorithms
from app.scoring.readiness import overall_classification, score_findings, severity_counts


def test_empty_findings_score_zero():
    assert score_findings([]) == 0


def test_empty_findings_classification_is_unknown():
    assert overall_classification([]) == Classification.UNKNOWN


def test_all_quantum_vulnerable_scores_low():
    findings = classify_algorithms(["RSA-2048", "SHA-1", "ECDSA-P256"])
    assert score_findings(findings) == 10
    assert overall_classification(findings) == Classification.QUANTUM_VULNERABLE


def test_all_post_quantum_ready_scores_100():
    findings = classify_algorithms(["ML-KEM-1024", "ML-DSA-87", "AES-256-GCM", "SHA3-256"])
    assert score_findings(findings) == 100
    assert overall_classification(findings) == Classification.POST_QUANTUM_READY


def test_single_vulnerable_finding_dominates_overall_classification():
    # Many post-quantum-ready findings plus a single quantum-vulnerable one:
    # the overall classification must reflect the worst finding, not an average.
    findings = classify_algorithms(
        ["ML-KEM-768", "ML-DSA-65", "AES-256-GCM", "SHA3-256", "RSA-2048"]
    )
    assert overall_classification(findings) == Classification.QUANTUM_VULNERABLE
    # But the score is still an average, not a floor -- it should sit between
    # the pure-vulnerable (10) and pure-ready (100) extremes.
    assert 10 < score_findings(findings) < 100


def test_mixed_hybrid_and_ready_has_no_vulnerable_or_transition():
    findings = classify_algorithms(["X25519+ML-KEM-768", "ML-DSA-65", "AES-256-GCM"])
    assert overall_classification(findings) == Classification.HYBRID_READY


def test_severity_counts_includes_zero_count_levels():
    findings = classify_algorithms(["RSA-2048"])
    counts = severity_counts(findings)
    assert counts["Critical"] == 1
    assert counts["Info"] == 0  # present with zero count, not omitted


def test_score_is_clamped_to_valid_range():
    findings = classify_algorithms(["ML-KEM-768"])
    score = score_findings(findings)
    assert 0 <= score <= 100
