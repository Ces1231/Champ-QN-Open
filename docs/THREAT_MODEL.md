# Threat Model — CHAMP-QN Crypto Readiness Scanner

This document describes the security posture of the reference Crypto
Readiness Scanner component. It is scoped to this application only, not to
the private CHAMP-QN platform.

## What this tool is, and is not

This is a **passive, offline, text-classification tool**. It reads
user-supplied inventory data (JSON or YAML describing assets and the
algorithm/protocol names associated with them) and returns a classification
and score. It does not:

- Connect to any network host.
- Scan, probe, fingerprint, or otherwise interact with live systems.
- Execute, evaluate, or interpret uploaded content as code.
- Collect credentials of any kind.
- Send data anywhere outside the process handling the request (no
  telemetry, no external API calls).

## Protected assets

- **Integrity of the classification/scoring logic** — the rule catalog and
  scoring model must not be silently alterable by request input.
- **Confidentiality of submitted inventory data** — since this data may
  describe a real organization's cryptographic posture, it must not be
  persisted, logged in full, or leaked to third parties by default.
- **Availability of the service** — a single malicious or malformed request
  should not crash the process or consume unbounded resources.
- **Integrity of the host running the container** — the application must
  not be usable as a pivot point into the host filesystem or other
  containers.

## Trust boundaries

```
┌──────────────┐      HTTP (JSON/YAML body, file upload)      ┌─────────────────────┐
│   Browser /  │ ───────────────────────────────────────────▶ │  FastAPI application │
│   API client │ ◀─────────────────────────────────────────── │  (this container)    │
└──────────────┘        JSON / Markdown report response        └─────────────────────┘
```

The only trust boundary crossed is the HTTP request/response between an
untrusted client and this application. There is no database, no outbound
network call, and no second internal service in this reference
implementation.

## Expected users

- Security engineers, architects, and compliance staff performing a
  preliminary, self-service assessment of a cryptographic inventory they
  already control or have legitimate access to.
- Developers evaluating the tool locally before integrating it into a
  larger workflow.

This tool is **not** intended for, and provides no functionality for,
assessing systems the operator does not control or have authorization to
inventory.

## Abuse cases considered

| Abuse case | Mitigation |
|---|---|
| Upload a very large file to exhaust memory/disk | `CHAMPQN_MAX_UPLOAD_BYTES` enforced before parsing (default 2 MiB); request rejected with HTTP 413. |
| Upload an inventory with an extreme number of assets/algorithms to exhaust CPU | `CHAMPQN_MAX_ASSETS` and `CHAMPQN_MAX_ALGORITHMS_PER_ASSET` enforced; request rejected with HTTP 413. |
| Upload YAML containing a Python-object constructor tag (e.g. `!!python/object/apply:os.system`) to achieve code execution | `yaml.safe_load` is used exclusively; the default (unsafe) `yaml.load` is never called. Tested in `tests/test_api.py::test_assess_upload_unsafe_yaml_is_rejected`. |
| Path traversal via a crafted filename in a multipart upload | The uploaded filename is used only to guess the JSON/YAML parser to use (by extension) and is never used to construct a filesystem path. |
| Reflected/stored XSS via attacker-controlled inventory content (asset IDs, algorithm strings, notes) rendered in the browser UI | The browser UI renders all user-controlled values via `textContent`, never `innerHTML` string concatenation. Markdown reports are returned as `text/markdown`, not rendered as HTML by the server. |
| Container escape / host pivot | Container runs as a non-root user (uid 10001); `docker-compose.yml` sets `read_only: true` with a `tmpfs` mount for `/tmp` and `no-new-privileges`. |
| Data exfiltration of submitted inventories | No outbound network calls are made by the application. No persistence occurs by default (`CHAMPQN_PERSIST_UPLOADS=false`); this reference version has no write path for uploaded content even when the flag is toggled — see `SECURITY.md` and `app/config.py`. |
| Dependency supply-chain compromise | Dependencies are version-range pinned in `pyproject.toml`; CI runs `pip-audit` and Trivy container scanning; Dependabot is configured for pip, Docker base image, and GitHub Actions updates. |

## Security assumptions

- The container is deployed behind normal network controls appropriate to
  its exposure (see "Rate-limiting guidance" below for production use).
- Operators do not disable the safe-YAML-only parsing path or the upload
  size limits in a production deployment.
- TLS termination (HTTPS) is handled by a reverse proxy or load balancer in
  front of this application in any production deployment; this reference
  container serves plain HTTP internally.

## Known limitations

- The algorithm classification is **pattern/keyword matching on free text**,
  not a cryptographic protocol analyzer. It can be fooled by unusual
  naming, and it cannot detect algorithms that are not named in the input
  at all (e.g. a certificate's actual key algorithm, if the inventory only
  says "certificate" with no further detail).
- The 0–100 score is a simple, documented average-of-findings model (see
  `app/scoring/readiness.py`), not a risk-weighted or asset-criticality-aware
  score. Two inventories with very different real-world risk can produce
  similar scores if their algorithm mix is similar.
- Standards mappings are informational summaries only and are not a
  substitute for reading the primary source documents or consulting a
  qualified professional.
- There is no authentication/authorization layer in this reference version
  — anyone who can reach the HTTP endpoint can submit inventory data and
  receive a report. See "Rate-limiting guidance" below.

## Rate-limiting guidance for production deployments

This reference implementation does not include application-level rate
limiting. Operators deploying this beyond local/offline use should place it
behind a reverse proxy (e.g. nginx, Envoy, or a cloud load balancer) that
enforces:

- Per-IP request rate limits on `/api/v1/assess*` endpoints.
- A request body size limit at the proxy layer in addition to this
  application's own `CHAMPQN_MAX_UPLOAD_BYTES` check.
- TLS termination.

## Out-of-scope threats

- Threats specific to the private CHAMP-QN platform's quantum-network
  orchestration, mTLS node authentication, or audit-chain implementation
  are out of scope for this document and this public repository.
- Physical security, cloud provider infrastructure security, and
  organizational security policy are out of scope.
- This tool does not claim to detect every possible cryptographic
  weakness in a real deployment; it is a preliminary reference aid, as
  stated in the in-app disclaimer.
