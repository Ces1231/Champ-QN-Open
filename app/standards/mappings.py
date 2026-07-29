"""Informational mappings to public post-quantum cryptography standards and guidance.

These mappings are paraphrased summaries with links to authoritative sources.
They are provided for orientation only and do not represent formal compliance
determinations, certifications, or legal advice. Always consult the primary
source documents and a qualified security/cryptography professional.
"""

from __future__ import annotations

from app.models.inventory import Classification, StandardsReference

_NIST_PQC = StandardsReference(
    source="NIST",
    reference="FIPS 203 / 204 / 205 — Post-Quantum Cryptography Standards",
    url="https://csrc.nist.gov/pubs/fips/203/final",
    note=(
        "NIST finalized ML-KEM (FIPS 203), ML-DSA (FIPS 204), and SLH-DSA (FIPS 205) "
        "as the first standardized post-quantum algorithms. Migration guidance is "
        "informational; consult the published FIPS documents for authoritative detail."
    ),
)

_NIST_MIGRATION = StandardsReference(
    source="NIST",
    reference="NIST IR 8547 — Transition to Post-Quantum Cryptography Standards",
    url="https://csrc.nist.gov/pubs/ir/8547/ipd",
    note=(
        "NIST guidance on deprecating vulnerable algorithms (RSA, finite-field "
        "Diffie-Hellman, ECDH, ECDSA) on a defined transition timeline."
    ),
)

_CNSA_2 = StandardsReference(
    source="NSA",
    reference="Commercial National Security Algorithm Suite 2.0 (CNSA 2.0)",
    url="https://www.nsa.gov/Cybersecurity/Post-Quantum-Cybersecurity-Resources/",
    note=(
        "NSA guidance for National Security Systems specifying required algorithms "
        "(CNSA 2.0 favors ML-KEM, ML-DSA, and AES-256) and adoption timelines. "
        "Applicability depends on system classification and mission context."
    ),
)

_CISA_ROADMAP = StandardsReference(
    source="CISA",
    reference="Post-Quantum Cryptography Initiative",
    url="https://www.cisa.gov/quantum",
    note=(
        "CISA guidance for critical infrastructure organizations on cryptographic "
        "inventory, risk prioritization, and migration planning ahead of "
        "cryptographically relevant quantum computers."
    ),
)

_NIST_CSF = StandardsReference(
    source="NIST",
    reference="NIST Cybersecurity Framework (CSF) 2.0 — Identify / Protect functions",
    url="https://www.nist.gov/cyberframework",
    note=(
        "Cryptographic inventory and migration planning map to the CSF Identify "
        "(asset/risk management) and Protect (data security) functions."
    ),
)

# Classification -> ordered list of relevant references.
CLASSIFICATION_REFERENCES: dict[Classification, list[StandardsReference]] = {
    Classification.QUANTUM_VULNERABLE: [_NIST_MIGRATION, _CNSA_2, _CISA_ROADMAP, _NIST_CSF],
    Classification.TRANSITION_REQUIRED: [_NIST_MIGRATION, _CISA_ROADMAP, _NIST_CSF],
    Classification.HYBRID_READY: [_NIST_PQC, _CNSA_2],
    Classification.POST_QUANTUM_READY: [_NIST_PQC, _CNSA_2],
    Classification.UNKNOWN: [_CISA_ROADMAP, _NIST_CSF],
}


def references_for(classifications: set[Classification]) -> list[StandardsReference]:
    """Deduplicated, stable-ordered list of references relevant to the given classifications."""
    seen: dict[str, StandardsReference] = {}
    for classification in (
        Classification.QUANTUM_VULNERABLE,
        Classification.TRANSITION_REQUIRED,
        Classification.HYBRID_READY,
        Classification.POST_QUANTUM_READY,
        Classification.UNKNOWN,
    ):
        if classification not in classifications:
            continue
        for ref in CLASSIFICATION_REFERENCES[classification]:
            seen[ref.reference] = ref
    return list(seen.values())
