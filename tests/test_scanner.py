from app.models.inventory import Classification
from app.scanners.crypto_scanner import classify_algorithm, classify_algorithms


def test_rsa_is_quantum_vulnerable():
    finding = classify_algorithm("RSA-2048")
    assert finding.classification == Classification.QUANTUM_VULNERABLE
    assert "RSA" in finding.matched_name


def test_ecdsa_is_quantum_vulnerable():
    finding = classify_algorithm("ECDSA-P256")
    assert finding.classification == Classification.QUANTUM_VULNERABLE


def test_ecdh_is_quantum_vulnerable():
    finding = classify_algorithm("ECDHE")
    assert finding.classification == Classification.QUANTUM_VULNERABLE


def test_diffie_hellman_is_quantum_vulnerable():
    finding = classify_algorithm("Diffie-Hellman")
    assert finding.classification == Classification.QUANTUM_VULNERABLE


def test_sha1_is_quantum_vulnerable():
    finding = classify_algorithm("SHA-1")
    assert finding.classification == Classification.QUANTUM_VULNERABLE


def test_aes_128_requires_transition():
    finding = classify_algorithm("AES-128-CBC")
    assert finding.classification == Classification.TRANSITION_REQUIRED


def test_aes_256_is_post_quantum_ready():
    finding = classify_algorithm("AES-256-GCM")
    assert finding.classification == Classification.POST_QUANTUM_READY


def test_aes_unspecified_size_is_unknown():
    finding = classify_algorithm("AES")
    assert finding.classification == Classification.UNKNOWN


def test_ml_kem_is_post_quantum_ready():
    finding = classify_algorithm("ML-KEM-768")
    assert finding.classification == Classification.POST_QUANTUM_READY
    assert finding.category == "Key Encapsulation Mechanism (KEM)"


def test_kyber_alias_matches_ml_kem_rule():
    finding = classify_algorithm("Kyber768")
    assert finding.classification == Classification.POST_QUANTUM_READY
    assert "ML-KEM" in finding.matched_name


def test_ml_dsa_is_post_quantum_ready():
    finding = classify_algorithm("ML-DSA-65")
    assert finding.classification == Classification.POST_QUANTUM_READY


def test_dilithium_alias_matches_ml_dsa_rule():
    finding = classify_algorithm("Dilithium3")
    assert finding.classification == Classification.POST_QUANTUM_READY
    assert "ML-DSA" in finding.matched_name


def test_slh_dsa_is_post_quantum_ready():
    finding = classify_algorithm("SLH-DSA-SHA2-128s")
    assert finding.classification == Classification.POST_QUANTUM_READY


def test_sphincs_alias_matches_slh_dsa_rule():
    finding = classify_algorithm("SPHINCS+")
    assert finding.classification == Classification.POST_QUANTUM_READY
    assert "SLH-DSA" in finding.matched_name


def test_hybrid_classical_plus_pqc_is_hybrid_ready():
    finding = classify_algorithm("X25519+ML-KEM-768")
    assert finding.classification == Classification.HYBRID_READY


def test_hybrid_keyword_with_both_markers():
    finding = classify_algorithm("Hybrid ECDHE and Kyber key exchange")
    assert finding.classification == Classification.HYBRID_READY


def test_sha256_is_post_quantum_ready():
    finding = classify_algorithm("SHA-256")
    assert finding.classification == Classification.POST_QUANTUM_READY


def test_sha3_is_post_quantum_ready():
    finding = classify_algorithm("SHA3-256")
    assert finding.classification == Classification.POST_QUANTUM_READY


def test_tls_1_0_is_quantum_vulnerable():
    finding = classify_algorithm("TLS1.0")
    assert finding.classification == Classification.QUANTUM_VULNERABLE


def test_tls_1_2_requires_transition():
    finding = classify_algorithm("TLS1.2")
    assert finding.classification == Classification.TRANSITION_REQUIRED


def test_x509_without_algorithm_is_unknown():
    finding = classify_algorithm("X.509")
    assert finding.classification == Classification.UNKNOWN


def test_unrecognized_algorithm_is_unknown():
    finding = classify_algorithm("AcmeProto-CipherX")
    assert finding.classification == Classification.UNKNOWN
    assert finding.matched_name == "Unrecognized algorithm/protocol reference"


def test_classify_algorithms_skips_blank_entries():
    findings = classify_algorithms(["RSA-2048", "  ", "", "AES-256"])
    assert len(findings) == 2
