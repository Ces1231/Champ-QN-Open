<p align="center">
  <img src="logo.svg" alt="CHAMP-QN Logo" width="420"/>
</p>

<h1 align="center">CHAMP-QN-public</h1>
<p align="center"><strong>Preparing trust architectures for the post-quantum transition</strong></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"/></a>
  <img src="https://img.shields.io/badge/Stage-Alpha-orange" alt="Stage: Alpha"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform"/>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/NVIDIA-Inception%20Member-76b900?logo=nvidia&logoColor=white" alt="NVIDIA Inception"/>
</p>

<p align="center">
  <em>Built by <a href="https://champtron-systems.com/">Champtron Systems LLC</a></em>
</p>

---

> **Scope of this repository.** CHAMP-QN-public is the sanitized public
> open-source companion to the privately developed CHAMP-QN platform. This
> repository contains independently usable reference components,
> documentation, examples, and implementation guidance without exposing
> proprietary or security-sensitive source code from the private platform.
>
> Everything under `app/`, `tests/`, `examples/`, and `docs/` in this
> repository is real, runnable, independent software — not a mockup of the
> private platform. It demonstrates a practical subset of the CHAMP-QN
> vision (cryptographic inventory and post-quantum readiness assessment) on
> its own merits.

## What's in this repository

| Component | What it is | Status |
|---|---|---|
| **CHAMP-QN Crypto Readiness Scanner** | A runnable, tested, open-source post-quantum cryptography readiness assessment tool | Available now — this repository |
| **CHAMP-QN platform overview** (below) | Public documentation and screenshots describing the privately developed quantum-network control plane | Documentation only — source not included here |

---

# CHAMP-QN Crypto Readiness Scanner

A lightweight, offline, open-source reference tool that scans a
user-supplied inventory of systems and identifies which cryptographic
algorithms and protocols they use, classifies each as quantum-vulnerable,
transition-required, hybrid-ready, post-quantum-ready, or requiring
validation, and produces a 0–100 readiness score with migration guidance.

> This reference tool provides preliminary cryptographic-readiness
> guidance. Results require validation by qualified security and
> cryptographic professionals and do not constitute certification,
> authorization, or formal compliance determination.

## Features

- **Multiple input paths:** JSON upload, YAML upload, a bundled sample
  inventory, or a direct REST API call — no UI required if you'd rather
  script it.
- **Broad algorithm/protocol catalog:** RSA, ECDSA, ECDH, Diffie-Hellman,
  AES (128/192/256), SHA-1, SHA-2, SHA-3, TLS 1.0–1.3, X.509 certificate
  mentions, ML-KEM (Kyber), ML-DSA (Dilithium), SLH-DSA (SPHINCS+), and
  hybrid classical+PQC combinations.
- **Deterministic, documented scoring** — no black box. See
  [`app/scoring/readiness.py`](app/scoring/readiness.py).
- **JSON and Markdown reports**, both generated from the same result object.
- **Informational standards mappings** to NIST FIPS 203/204/205, NIST IR
  8547, NSA CNSA 2.0, CISA quantum-readiness guidance, and NIST CSF 2.0.
- **No required commercial services, no required external AI API, no
  telemetry.** Runs fully offline after the image/dependencies are pulled.
- **Non-destructive by design:** this is a text classifier over data you
  provide — it never scans a network, executes uploaded content, or
  collects credentials. See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md).

## Screenshots

The scanner's browser UI has not yet had screenshots captured for this
README (placeholder — to be added). To capture them yourself:

1. Run the app (see Quick Start below) and open it in a browser.
2. Load the bundled sample inventory via the "Assess sample inventory" button.
3. Screenshot the results panel and save it under `screenshots/` with a
   descriptive filename (e.g. `scanner_results_overview.png`), then add an
   `![...]` reference here.

The screenshots currently in this repository's `screenshots/` directory
belong to the CHAMP-QN platform overview further down this README, not to
the scanner.

## Quick start

```bash
git clone https://github.com/Ces1231/Champ-QN-public.git
cd Champ-QN-public

# Linux / macOS
./scripts/start.sh

# Windows PowerShell
./scripts/start.ps1
```

The launcher finds a free host port starting at 8080, brings the stack up
with `docker compose`, and prints the URL, e.g.:

```text
CHAMP-QN Crypto Readiness Scanner is available at:
http://localhost:8080
```

## Docker installation (manual)

```bash
docker compose up --build
```

By default this publishes the app on host port 8080 (override with the
`CHAMPQN_HOST_PORT` environment variable). See `.env.example` for all
configuration options.

## Local installation (without Docker)

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000`.

## API examples

Interactive API docs are always available at `/docs` (Swagger UI).

**Health and status:**

```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/status
```

**Assess the bundled sample inventory:**

```bash
curl -X POST http://localhost:8080/api/v1/assess/sample
```

**Assess a JSON body directly:**

```bash
curl -X POST http://localhost:8080/api/v1/assess \
  -H "Content-Type: application/json" \
  -d '{
        "inventory_name": "Example",
        "assets": [
          {"id": "web-01", "algorithms": ["RSA-2048", "TLS1.2", "SHA-1"]}
        ]
      }'
```

**Upload a JSON or YAML file:**

```bash
curl -X POST http://localhost:8080/api/v1/assess/upload \
  -F "file=@examples/sample-inventory.yaml"
```

**Get a Markdown report instead of JSON:**

```bash
curl -X POST "http://localhost:8080/api/v1/assess/sample?format=markdown"
```

## Sample inventory

See [`examples/sample-inventory.json`](examples/sample-inventory.json) and
[`examples/sample-inventory.yaml`](examples/sample-inventory.yaml) — the
same illustrative inventory in both supported formats, covering a legacy
RSA/TLS1.2/SHA-1 web server, an ECDSA/ECDHE VPN gateway, a hybrid
X25519+ML-KEM-768 gateway, a pure post-quantum file service, and an
unrecognized vendor-proprietary protocol.

## Sample output

Running the sample inventory (verified output, `POST /api/v1/assess/sample`):

```json
{
  "overall_score": 60,
  "overall_classification": "Quantum-vulnerable",
  "asset_count": 8,
  "finding_count": 23,
  "findings_by_severity": {"Critical": 7, "High": 0, "Medium": 4, "Low": 2, "Info": 10},
  "assets": [
    {
      "asset_id": "legacy-web-01.example.internal",
      "asset_classification": "Quantum-vulnerable",
      "asset_score": 30
    }
  ]
}
```

(Truncated — the full response includes per-finding guidance and standards
references for every asset.) Run it yourself to see the complete report.

## Architecture overview

```
app/
├── main.py          FastAPI app, security headers, static/template mounting
├── api/routes.py     /health, /api/v1/status, /api/v1/assess*, /api/v1/sample
├── models/           Pydantic schemas: Inventory, AssessmentResult, findings
├── scanners/         Free-text algorithm/protocol pattern-matching catalog
├── scoring/          0-100 scoring + overall classification ("worst wins")
├── standards/        Informational NIST/CNSA 2.0/CISA/CSF reference mappings
├── reporting/        Orchestration + JSON/Markdown rendering
├── templates/        Jinja2 browser UI
└── static/           Vanilla JS/CSS (no framework, no build step)
```

No network calls, no database, no external service dependency. Everything
runs in a single process.

## Supported algorithms

| Family | Examples detected | Typical classification |
|---|---|---|
| RSA | `RSA-2048`, `RSA-4096` | Quantum-vulnerable |
| ECDSA / ECDH(E) | `ECDSA-P256`, `ECDHE` | Quantum-vulnerable |
| Diffie-Hellman | `DHE`, `Diffie-Hellman` | Quantum-vulnerable |
| AES | `AES-128`, `AES-256-GCM` | Transition required (128) / Post-quantum-ready (192/256) |
| SHA-1 | `SHA-1` | Quantum-vulnerable (deprecated) |
| SHA-2 / SHA-3 | `SHA-256`, `SHA3-256` | Post-quantum-ready (≥256-bit output) |
| TLS | `TLS1.0`–`TLS1.3` | Quantum-vulnerable (1.0/1.1) / Transition required (1.2/1.3) |
| X.509 | `X.509` (algorithm unspecified) | Unknown — requires validation |
| ML-KEM (Kyber) | `ML-KEM-768`, `Kyber1024` | Post-quantum-ready |
| ML-DSA (Dilithium) | `ML-DSA-65`, `Dilithium3` | Post-quantum-ready |
| SLH-DSA (SPHINCS+) | `SLH-DSA-SHA2-128s`, `SPHINCS+` | Post-quantum-ready |
| Hybrid combinations | `X25519+ML-KEM-768` | Hybrid-ready |

Standardized NIST names (ML-KEM, ML-DSA, SLH-DSA) are matched alongside
their legacy/marketing names (Kyber, Dilithium, SPHINCS+) so both are
recognized. Full rule catalog:
[`app/scanners/crypto_scanner.py`](app/scanners/crypto_scanner.py).

## Standards references

Informational only — not a compliance determination. See
[`app/standards/mappings.py`](app/standards/mappings.py) for the full list
with links:

- NIST FIPS 203 / 204 / 205 (ML-KEM, ML-DSA, SLH-DSA)
- NIST IR 8547 (transition guidance)
- NSA Commercial National Security Algorithm Suite 2.0 (CNSA 2.0)
- CISA Post-Quantum Cryptography Initiative
- NIST Cybersecurity Framework (CSF) 2.0

## Security model

See [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) for the full threat
model. Summary: this is a passive text-classification tool with no network
scanning, no code execution of uploaded content, safe-YAML-only parsing,
enforced upload size/count limits, no persistence by default, a non-root
container user, and a read-only-compatible container filesystem.

## Known limitations

- Detection is pattern/keyword matching on free text, not a cryptographic
  protocol analyzer — it can't inspect a live certificate or connection itself.
- The 0–100 score is a simple, documented average, not a risk-weighted or
  asset-criticality-aware score.
- No authentication layer in this reference version — see the threat
  model's rate-limiting guidance before exposing this beyond local/offline use.
- Full details: [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md#known-limitations).

## Roadmap summary

Phase 1 (this scanner) is available now. Phases 2–4 (certificate/TLS
import, policy-as-code, deeper hybrid analysis) are planned. Phases 5–7
(asset-platform integrations, evidence bundles, quantum-network simulation
interfaces) are research concepts, not commitments. Full detail:
[`ROADMAP.md`](ROADMAP.md).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup, branch/commit
conventions, the PR process, and rules around AI-assisted contributions and
sensitive-material restrictions. Please review
[`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
[`SECURITY.md`](SECURITY.md) (for vulnerability reports specifically —
do not file those as public issues).

## License

This repository is licensed under the [MIT License](LICENSE) (copyright
Carnell Smith, in place before this scanner component was added). MIT
permits both commercial and non-commercial use while retaining the
original copyright notice. We considered Apache License 2.0 for this new
component specifically, for its explicit patent-grant clause, but chose to
keep the repository on its existing, deliberately-chosen MIT license rather
than introduce a second license into one repository without dedicated
owner review. This can be revisited by the maintainer. See
[`NOTICE`](NOTICE) for third-party dependency attributions.

## Maintainer

**Carnell E. Smith — Champtron Systems LLC**
[carnell.smith@champtron-systems.com](mailto:carnell.smith@champtron-systems.com)

---

# CHAMP-QN Platform Overview

*The remainder of this README describes the privately developed CHAMP-QN
platform. Its source code is not included in this repository — see the
scope statement at the top of this document.*

## Overview

Classical networking infrastructure cannot manage entanglement scheduling,
fidelity-aware routing, or the cryptographic evidence chains required for
quantum-safe compliance. CHAMP-QN fills that gap.

CHAMP-QN is a production-quality orchestration platform that enforces a
Zero Trust security posture across every node, job, and key exchange in a
distributed quantum network. It ships as a fully containerized 13-service
stack — deployable in minutes, auditable by design.

---

## Core Capabilities

| Capability | Description |
|---|---|
| **Entanglement-aware routing** | Routes quantum workloads in real time based on live fidelity and latency measurements; automatically reroutes around degraded links |
| **BB84 Quantum Key Distribution** | End-to-end QKD with basis reconciliation, sifted key extraction, and visual proof of quantum key exchange |
| **Zero Trust control plane** | Every node authenticates via mTLS certificate fingerprint and API key on every request — no implicit trust, no exceptions |
| **Tamper-evident audit chain** | Every policy decision, job execution, and node registration is HMAC-SHA256 signed and chain-linked; deletion or reordering is immediately detectable |
| **Signed evidence capsules** | Each job produces a cryptographically signed proof-of-execution ready for compliance audits |
| **Live topology dashboard** | Real-time SVG network canvas with node health, fidelity/latency overlays, active job particles, and self-heal reroute visualization |
| **Policy engine** | Configurable fidelity thresholds, degraded node avoidance, and backend mode — with a per-decision audit trace |
| **Digital Twin Control Plane** | Intent-based scheduling, chaos injection, and scenario simulation without mutating live state |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Dashboard                         │
│         (real-time topology · job pipeline · audit)         │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS + JWT
┌─────────────────────▼───────────────────────────────────────┐
│                      Orchestrator                            │
│   job routing · policy engine · QKD · evidence capsules     │
│   mTLS node auth · audit log · SQLite · Prometheus metrics  │
└──────┬──────────────┬──────────────────────┬────────────────┘
       │ mTLS         │ mTLS                  │ mTLS
┌──────▼──────┐ ┌─────▼──────┐        ┌──────▼──────────────┐
│  Link Sim   │ │ Audit Log  │        │   Quantum Nodes      │
│ entanglement│ │ HMAC chain │        │  qnode01 – qnode06   │
│ fidelity/ms │ │ tamper-    │        │  Qiskit Aer / IBM Q  │
│             │ │ evident    │        │  local circuit exec  │
└─────────────┘ └────────────┘        └─────────────────────┘
                                       (6 independent agents)

Observability: Prometheus + Grafana (scraped from all services)
```

### Design Principles

| Principle | Implementation |
|---|---|
| Zero Trust | mTLS cert fingerprint + API key verified on every request — no session reuse |
| Audit-first | All decisions committed to the HMAC chain before acknowledgement |
| Fidelity-aware routing | Real-time rerouting around degraded links; every reroute logged and signed |
| Standards-aligned | ETSI QKD API bridge; QIR/NetQASM translation layer |
| Observable by default | Prometheus metrics on every service; pre-built Grafana dashboard |

---

## Dashboard

### System Health & Node Registry
![Dashboard Overview](screenshots/dashboard_overview.jpg)

### Node Registry & Live Job Pipeline
![Node Registry and Job Pipeline](screenshots/node_registry_distributed_node_simulator.jpg)
*All 6 quantum nodes registered and healthy. Live execution trace shows the 3-phase pipeline: Entanglement → Source Execution → Target Execution.*

### Zero Trust — Node Trust & Policy Posture
![Node Trust Dashboard](screenshots/dashboard_node_trust.jpg)

### Telemetry Event Stream & Policy Decision Trace
![Telemetry and Policy](screenshots/telemetry_event_stream.jpg)
*Live audit timeline showing job completions, node reroutes, and per-request policy allow/block decisions with rule names.*

### AI-Assisted Anomaly Explanation & Certificate Monitor
![AI Anomaly Panel](screenshots/ai_assisted_anomaly_explanation_panel.jpg)
*Incident panel, cert expiry monitor (11 certs tracked), entanglement quality matrix, and application intent prediction.*

### Policy Engine & Scenario Runner
![Policy and Scenario Runner](screenshots/policy_recommendation_operator_review_panel.jpg)
*Hot-reload policy controls, failure injection, per-node job queue counters, and scenario runner with assertions.*

### Signed Evidence Capsule & Audit Chain Integrity
![Evidence and Audit](screenshots/evaluation_audit_evidence_screen.jpg)
*Cryptographically signed proof-of-execution. Any tampered audit entry is detected immediately.*

### Full Dashboard
![Full Dashboard](screenshots/dashboard_full_top.jpg)

---

## Security

- Mutual TLS (mTLS) between all services — certificate fingerprint mapped per node
- JWT authentication with configurable expiry and login lockout
- Role-based access control — admin / operator / viewer
- HMAC-SHA256 signed audit log with chain-of-custody `prev_signature` linking
- Signed evidence capsules per job execution
- Maintenance mode and graceful shutdown

## Quantum Capabilities

- **BB84 QKD** — basis selection, measurement, reconciliation, and sifted key extraction with visual proof
- **Qiskit Aer** local quantum circuit simulation — switchable to IBM Quantum at runtime
- **6-node quantum cluster** — independent agents with heartbeat, auto-recovery, and capability reporting
- Fidelity range: 0.88–0.99 | Latency range: 35–180 ms | Link success rate: 95% (all configurable)

## Observability & Operations

- Prometheus metrics on every service (attempts, success, latency histograms)
- Pre-built Grafana dashboard and live WebSocket event stream to the browser dashboard
- **Failure injection** — mark a node degraded at a configurable severity level; policy engine reacts immediately
- **Scenario runner** — preset scenarios (degraded node reroute, parallel load, BB84 demo) with assertion verification
- **Topology replay** — 15-minute rolling replay window with per-job timeline
- **Hot-reload policy** — update routing policy at runtime without container restart
- **Digital twin** — predict chaos outcomes without mutating live state

---

## Technology Stack

| Layer | Technology |
|---|---|
| Orchestrator | Python 3.12, FastAPI, SQLite, asyncio |
| Node Agents | Python 3.12, FastAPI, Qiskit Aer |
| Link Simulator | Python 3.12, FastAPI |
| Audit Log | Python 3.12, FastAPI, HMAC-SHA256 chain |
| Web Dashboard | Vanilla JS, SVG topology canvas |
| Observability | Prometheus, Grafana |
| Transport Security | mTLS (mutual TLS), self-signed CA |
| Container Runtime | Docker Compose (13-service stack) |
| Quantum Backends | Qiskit Aer (local) · IBM Quantum (optional) |

---

## NVIDIA Inception Program

**Champtron Systems LLC is a member of the NVIDIA Inception Program.**

NVIDIA Inception nurtures startups revolutionizing industries with technology advancements. Membership does not imply endorsement, certification, or funding by NVIDIA.

### GPU Acceleration Roadmap

| Technology | Planned Application |
|---|---|
| **CUDA / cuQuantum** | GPU-accelerated quantum circuit execution — replace Qiskit Aer CPU simulator for high-fidelity multi-qubit entanglement modeling at scale |
| **CUDA-Q** | Port node-agent circuit execution to hybrid classical-quantum workloads on NVIDIA GPUs |
| **RAPIDS** | GPU-accelerated telemetry analytics and entanglement quality time-series processing |
| **TensorRT / Triton** | Accelerated inference for anomaly detection models on live quantum network event streams |
| **NVIDIA NIM** | AI microservices for real-time policy recommendation and intent prediction in the orchestrator |
| **NVIDIA AI Enterprise** | Production-grade AI runtime for zero trust decision support and audit chain analysis |
| **Jetson Edge AI** | Lightweight quantum node agents on Jetson platforms for field-deployable quantum network nodes |

---

## Platform Project Status

| Component | Status |
|---|---|
| Core orchestration | Production-ready demo |
| Zero Trust auth — mTLS + JWT + RBAC | Complete |
| BB84 QKD | Complete |
| Tamper-evident audit chain | Complete |
| Prometheus + Grafana observability | Complete |
| Signed evidence capsules | Complete |
| IBM Quantum integration | Optional — bring your own API key |
| cuQuantum / CUDA-Q integration | Roadmap |
| Multi-tenant / cloud deployment | Roadmap |

---

## Platform Contact & Access

This repository contains the public product overview for the private
platform. Platform source code is available under a private research
license — it is not part of this public repository.

To request access, schedule a demo, or discuss a partnership:

**Carnell Smith — Champtron Systems LLC**
[carnell.smith@champtron-systems.com](mailto:carnell.smith@champtron-systems.com)
