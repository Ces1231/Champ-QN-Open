# Changelog

All notable changes to the CHAMP-QN Crypto Readiness Scanner (the public
reference component of this repository) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/) once
it reaches 1.0.0. Prior to 1.0.0, minor versions may include breaking changes.

## [Unreleased]

### Planned
- See `ROADMAP.md` for planned and research-concept items beyond Phase 1.

## [0.1.0] — Initial public release of the Crypto Readiness Scanner

### Added
- FastAPI application with a browser interface (`/`) and REST API
  (`/health`, `/api/v1/status`, `/api/v1/assess`, `/api/v1/assess/upload`,
  `/api/v1/assess/sample`, `/api/v1/sample`, `/docs`).
- Cryptographic algorithm/protocol detection covering RSA, ECDSA, ECDH,
  Diffie-Hellman, AES (128/192/256), SHA-1, SHA-2, SHA-3, TLS 1.0–1.3,
  X.509 certificate mentions, ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA
  (SPHINCS+), and hybrid classical+PQC combinations.
- Classification into Quantum-vulnerable, Transition required,
  Hybrid-ready, Post-quantum-ready, and Unknown/requires-validation.
- 0–100 readiness scoring with a documented, deterministic scoring model.
- JSON and Markdown report generation.
- Informational mappings to NIST FIPS 203/204/205, NIST IR 8547, NSA CNSA
  2.0, CISA quantum-readiness guidance, and NIST CSF 2.0.
- Bundled sample inventory (JSON and YAML) for immediate try-out.
- Docker image (non-root user, read-only-compatible root filesystem) and
  `docker-compose.yml`.
- Cross-platform launcher scripts (`scripts/start.sh`, `scripts/start.ps1`)
  that select a free host port automatically.
- Test suite covering scanner classification, scoring boundaries, report
  generation, and API behavior (valid/invalid JSON and YAML, oversized
  input, missing required fields, no-persistence-by-default).
- GitHub Actions CI: formatting, linting, type checking, `bandit`,
  `pip-audit`, unit tests, Docker build, container health check, and SBOM
  generation.
- Open-source governance documentation: `CONTRIBUTING.md`, `SECURITY.md`,
  `ROADMAP.md`, `GOVERNANCE.md`, `CODE_OF_CONDUCT.md`, `NOTICE`,
  `REPOSITORY_SETTINGS.md`.
- `docs/THREAT_MODEL.md` documenting protected assets, trust boundaries,
  abuse cases, and known limitations.

[Unreleased]: https://github.com/Ces1231/Champ-QN-public/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ces1231/Champ-QN-public/releases/tag/v0.1.0
