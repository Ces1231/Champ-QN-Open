# Roadmap — CHAMP-QN Crypto Readiness Scanner

This roadmap covers the public, open-source **Crypto Readiness Scanner**
component of this repository. It does not describe the private CHAMP-QN
platform's roadmap, which is not disclosed here.

Status legend:

- **Available now** — implemented, tested, and shipped in this repository today.
- **In development** — actively being worked on; not yet merged/released.
- **Planned** — committed direction, not yet started.
- **Research concept** — an idea under consideration; may change significantly
  or not ship at all.

## Phase 1 — Crypto inventory reference scanner

**Available now.**

- Free-text algorithm/protocol detection across RSA, ECDSA, ECDH,
  Diffie-Hellman, AES, SHA-1/2/3, TLS versions, X.509 mentions, ML-KEM
  (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and hybrid combinations.
- JSON and YAML inventory upload, bundled sample inventory, and REST API.
- 0–100 readiness scoring and JSON/Markdown report generation.
- Informational mappings to NIST PQC standards, NSA CNSA 2.0, CISA
  guidance, and NIST CSF categories.

## Phase 2 — Certificate and TLS metadata import

**Planned.**

- Direct import of PEM/DER certificate chains and structured TLS scan
  output (e.g. from common TLS scanning tool output formats) instead of
  requiring pre-summarized algorithm strings.
- Certificate expiry and chain-validity awareness alongside algorithm
  classification.

## Phase 3 — Policy-as-code evaluation

**Planned.**

- User-supplied policy definitions (e.g. "no SHA-1 in production tier
  assets") evaluated against inventory results, producing pass/fail policy
  findings alongside the existing algorithm findings.

## Phase 4 — Hybrid cryptography readiness

**Planned.**

- Deeper hybrid-configuration analysis: detecting partial hybrid rollouts,
  flagging inconsistent hybrid pairings, and tracking hybrid-to-PQC-only
  migration progress over time.

## Phase 5 — Network and asset-platform integrations

**Research concept.**

- Optional, explicitly opt-in import adapters for common asset-inventory
  and network-discovery tool export formats. Any such integration would
  remain read-only and would not perform live network scanning itself.

## Phase 6 — Evidence bundles and compliance mappings

**Research concept.**

- Signed, exportable evidence bundles summarizing an organization's
  crypto-readiness posture over time, with expanded (still informational,
  non-certifying) mappings to additional frameworks.

## Phase 7 — Distributed quantum-network simulation interfaces

**Research concept.**

- An optional read-only bridge allowing this scanner's findings to be
  referenced alongside quantum-network topology and policy data from the
  broader CHAMP-QN platform, for organizations operating both. No
  proprietary CHAMP-QN platform internals would be exposed by such a
  bridge; any interface would be published and versioned independently in
  this public repository.

---

Roadmap items are not commitments to a specific date. Priorities may shift
based on contributor availability and community feedback — open an issue to
discuss any of the above.
