"""Cryptographic algorithm/protocol identification.

Matches free-text algorithm identifier strings (as supplied in an inventory
asset's ``algorithms`` list) against a fixed catalog of known patterns and
returns a classified finding for each. This is pattern/keyword matching
against user-supplied text -- it is not live network scanning, does not
connect to any host, and does not execute or evaluate the input in any way.

Rules are evaluated in order; the first match wins. Hybrid combinations are
checked first so that e.g. "X25519+ML-KEM-768" is classified as Hybrid-ready
rather than falling through to a plain classical-algorithm rule.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.inventory import AlgorithmFinding, Classification, Severity

_CLASSICAL_KEX_MARKERS = re.compile(
    r"\b(RSA|ECDH|ECDHE|DH|DHE|DIFFIE-?HELLMAN|X25519|X448|ECDSA)\b", re.IGNORECASE
)
_PQC_MARKERS = re.compile(
    r"\b(ML-?KEM|KYBER|ML-?DSA|DILITHIUM|SLH-?DSA|SPHINCS\+?)\b", re.IGNORECASE
)


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    category: str
    classification: Classification
    severity: Severity
    guidance: str


def _hybrid_predicate(text: str) -> bool:
    has_classical = bool(_CLASSICAL_KEX_MARKERS.search(text))
    has_pqc = bool(_PQC_MARKERS.search(text))
    has_hybrid_word = "hybrid" in text.lower() or "+" in text
    return has_classical and has_pqc and has_hybrid_word


# Rules are checked top-to-bottom; the hybrid check is special-cased separately
# in `classify_algorithm` because it depends on the *combination* of markers
# rather than a single pattern.
RULES: list[Rule] = [
    Rule(
        name="ML-KEM (Kyber)",
        pattern=re.compile(r"\bML-?KEM(-?\d{3,4})?\b|\bKYBER(-?\d{3,4})?\b", re.IGNORECASE),
        category="Key Encapsulation Mechanism (KEM)",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "ML-KEM (FIPS 203, formerly known as Kyber) is a NIST-standardized "
            "post-quantum key encapsulation mechanism. No action required beyond "
            "keeping parameter sets current with NIST/CNSA 2.0 guidance."
        ),
    ),
    Rule(
        name="ML-DSA (Dilithium)",
        pattern=re.compile(r"\bML-?DSA(-?\d{2,3})?\b|\bDILITHIUM\d*\b", re.IGNORECASE),
        category="Digital Signature",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "ML-DSA (FIPS 204, formerly Dilithium) is a NIST-standardized "
            "post-quantum digital signature algorithm. No action required beyond "
            "keeping parameter sets current."
        ),
    ),
    Rule(
        name="SLH-DSA (SPHINCS+)",
        pattern=re.compile(r"\bSLH-?DSA\b|\bSPHINCS\+?\b", re.IGNORECASE),
        category="Digital Signature (stateless hash-based)",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "SLH-DSA (FIPS 205, formerly SPHINCS+) is a NIST-standardized "
            "stateless hash-based post-quantum signature scheme. Note its larger "
            "signature size relative to ML-DSA when evaluating fit for constrained "
            "environments."
        ),
    ),
    Rule(
        name="RSA",
        pattern=re.compile(r"\bRSA(-?\d{3,5})?\b", re.IGNORECASE),
        category="Asymmetric encryption / signature",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "RSA key establishment and signatures are broken by Shor's algorithm "
            "on a cryptographically relevant quantum computer. Plan migration to "
            "ML-KEM (key establishment) and ML-DSA or SLH-DSA (signatures), or a "
            "hybrid classical+PQC configuration as an interim step."
        ),
    ),
    Rule(
        name="ECDSA",
        pattern=re.compile(r"\bEC-?DSA\b", re.IGNORECASE),
        category="Digital Signature (elliptic curve)",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "ECDSA is broken by Shor's algorithm on a cryptographically relevant "
            "quantum computer. Plan migration to ML-DSA or SLH-DSA, or a hybrid "
            "signature scheme as an interim step."
        ),
    ),
    Rule(
        name="ECDH",
        pattern=re.compile(r"\bECDHE?\b", re.IGNORECASE),
        category="Key Exchange (elliptic curve)",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "ECDH/ECDHE key exchange is broken by Shor's algorithm on a "
            "cryptographically relevant quantum computer. Plan migration to "
            "ML-KEM or a hybrid ECDHE+ML-KEM configuration as an interim step."
        ),
    ),
    Rule(
        name="Diffie-Hellman (finite field)",
        pattern=re.compile(r"\bDIFFIE-?HELLMAN\b|\bDHE?\b", re.IGNORECASE),
        category="Key Exchange (finite field)",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "Finite-field Diffie-Hellman key exchange is broken by Shor's "
            "algorithm on a cryptographically relevant quantum computer. Plan "
            "migration to ML-KEM or a hybrid configuration as an interim step."
        ),
    ),
    Rule(
        name="AES-128",
        pattern=re.compile(r"\bAES-?128\b", re.IGNORECASE),
        category="Symmetric encryption",
        classification=Classification.TRANSITION_REQUIRED,
        severity=Severity.MEDIUM,
        guidance=(
            "Grover's algorithm reduces AES-128's effective security margin to "
            "roughly 64 bits against a quantum adversary. NSA CNSA 2.0 and NIST "
            "guidance recommend AES-256 for long-lived protection needs."
        ),
    ),
    Rule(
        name="AES-256/192",
        pattern=re.compile(r"\bAES-?(192|256)\b", re.IGNORECASE),
        category="Symmetric encryption",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "AES-256 retains an estimated ~128-bit effective security margin "
            "against Grover's algorithm and is considered quantum-resistant with "
            "adequate margin by NIST and NSA CNSA 2.0 guidance."
        ),
    ),
    Rule(
        name="AES (unspecified key size)",
        pattern=re.compile(r"\bAES\b", re.IGNORECASE),
        category="Symmetric encryption",
        classification=Classification.UNKNOWN,
        severity=Severity.MEDIUM,
        guidance=(
            "AES was referenced without a specific key size. Confirm the actual "
            "key length in use -- AES-256 is recommended for long-lived "
            "protection needs; AES-128 requires a documented risk acceptance or "
            "migration plan."
        ),
    ),
    Rule(
        name="SHA-1",
        pattern=re.compile(r"\bSHA-?1\b", re.IGNORECASE),
        category="Hash function",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "SHA-1 is deprecated due to practical classical collision attacks "
            "and offers reduced margin under Grover's algorithm. Migrate to "
            "SHA-256 or stronger without delay."
        ),
    ),
    Rule(
        name="SHA-3",
        pattern=re.compile(r"\bSHA-?3(-?\d{3})?\b|\bSHA3-?\d{3}\b", re.IGNORECASE),
        category="Hash function",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "SHA-3 with a 256-bit or larger output is considered quantum-resistant "
            "with adequate margin under Grover's algorithm."
        ),
    ),
    Rule(
        name="SHA-2 (256/384/512)",
        pattern=re.compile(r"\bSHA-?(256|384|512)\b", re.IGNORECASE),
        category="Hash function",
        classification=Classification.POST_QUANTUM_READY,
        severity=Severity.INFO,
        guidance=(
            "SHA-2 variants of 256 bits or larger output are considered "
            "quantum-resistant with adequate margin under Grover's algorithm."
        ),
    ),
    Rule(
        name="SHA-2 (unspecified or short output)",
        pattern=re.compile(r"\bSHA-?2\b|\bSHA-?224\b", re.IGNORECASE),
        category="Hash function",
        classification=Classification.TRANSITION_REQUIRED,
        severity=Severity.MEDIUM,
        guidance=(
            "SHA-2 was referenced without a sufficient output length specified. "
            "Confirm the actual digest size in use -- SHA-256 or larger is "
            "recommended."
        ),
    ),
    Rule(
        name="TLS 1.0 / 1.1",
        pattern=re.compile(r"\bTLS ?1\.[01]\b|\bSSLv?[23]\b", re.IGNORECASE),
        category="Transport protocol",
        classification=Classification.QUANTUM_VULNERABLE,
        severity=Severity.CRITICAL,
        guidance=(
            "TLS 1.0/1.1 (and any SSL version) are deprecated protocols with "
            "known classical weaknesses in addition to quantum-vulnerable key "
            "exchange. Migrate to TLS 1.3 with a hybrid PQC key exchange."
        ),
    ),
    Rule(
        name="TLS 1.2",
        pattern=re.compile(r"\bTLS ?1\.2\b", re.IGNORECASE),
        category="Transport protocol",
        classification=Classification.TRANSITION_REQUIRED,
        severity=Severity.MEDIUM,
        guidance=(
            "TLS 1.2 is still widely supported but its key exchange is "
            "typically classical (ECDHE/RSA). Plan migration to TLS 1.3 with a "
            "hybrid PQC key exchange (e.g. X25519+ML-KEM-768)."
        ),
    ),
    Rule(
        name="TLS 1.3",
        pattern=re.compile(r"\bTLS ?1\.3\b", re.IGNORECASE),
        category="Transport protocol",
        classification=Classification.TRANSITION_REQUIRED,
        severity=Severity.LOW,
        guidance=(
            "TLS 1.3 is the current protocol version, but its default key "
            "exchange is still classical unless explicitly configured with a "
            "hybrid PQC key exchange group (e.g. X25519+ML-KEM-768). Confirm the "
            "negotiated group in use."
        ),
    ),
    Rule(
        name="X.509 certificate (algorithm unspecified)",
        pattern=re.compile(r"\bX\.?509\b|\bCERTIFICATE\b", re.IGNORECASE),
        category="Certificate",
        classification=Classification.UNKNOWN,
        severity=Severity.MEDIUM,
        guidance=(
            "An X.509 certificate was referenced without its key or signature "
            "algorithm specified. Inspect the certificate's public key algorithm "
            "and signature algorithm directly and re-assess."
        ),
    ),
]

_FALLBACK = Rule(
    name="Unrecognized algorithm/protocol reference",
    pattern=re.compile(r".*"),
    category="Unclassified",
    classification=Classification.UNKNOWN,
    severity=Severity.MEDIUM,
    guidance=(
        "This entry did not match any pattern in the reference scanner's "
        "catalog. It may be a vendor-specific name, an abbreviation, or a "
        "non-cryptographic value. Manual review by a qualified professional is "
        "recommended."
    ),
)


def classify_algorithm(raw_value: str) -> AlgorithmFinding:
    """Classify a single free-text algorithm/protocol identifier string."""
    text = raw_value.strip()

    if _hybrid_predicate(text):
        return AlgorithmFinding(
            raw_value=raw_value,
            matched_name="Hybrid classical + post-quantum combination",
            category="Hybrid Key Exchange / Signature",
            classification=Classification.HYBRID_READY,
            severity=Severity.LOW,
            guidance=(
                "A hybrid classical+post-quantum combination was detected. This "
                "is a widely recommended transition strategy: the classical "
                "component provides a fallback while the PQC component provides "
                "quantum resistance. Plan eventual migration to PQC-only once "
                "ecosystem support matures."
            ),
        )

    for rule in RULES:
        if rule.pattern.search(text):
            return AlgorithmFinding(
                raw_value=raw_value,
                matched_name=rule.name,
                category=rule.category,
                classification=rule.classification,
                severity=rule.severity,
                guidance=rule.guidance,
            )

    return AlgorithmFinding(
        raw_value=raw_value,
        matched_name=_FALLBACK.name,
        category=_FALLBACK.category,
        classification=_FALLBACK.classification,
        severity=_FALLBACK.severity,
        guidance=_FALLBACK.guidance,
    )


def classify_algorithms(values: list[str]) -> list[AlgorithmFinding]:
    """Classify a list of free-text algorithm/protocol identifier strings."""
    return [classify_algorithm(v) for v in values if v.strip()]
