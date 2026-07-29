# Contributing to CHAMP-QN-public

Thank you for your interest in contributing. This document covers the
practical mechanics of contributing to the **CHAMP-QN Crypto Readiness
Scanner** and the rest of this public repository.

## Scope reminder

This repository is the sanitized, independently usable open-source
companion to the privately developed CHAMP-QN platform. Contributions
should improve *this* repository's own code, documentation, and reference
components — not attempt to add proprietary functionality from the private
platform. See the README for the full scope statement.

## Development environment setup

```bash
git clone https://github.com/Ces1231/Champ-QN-public.git
cd Champ-QN-public
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Run the app locally without Docker:

```bash
uvicorn app.main:app --reload --port 8000
```

## Branch naming

Use a short, descriptive prefix:

- `feature/<short-description>` — new functionality
- `fix/<short-description>` — bug fixes
- `docs/<short-description>` — documentation only
- `chore/<short-description>` — tooling, CI, dependency updates

## Commit conventions

Prefer [Conventional Commits](https://www.conventionalcommits.org/)-style
messages: `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`. Keep the
subject line under ~72 characters; explain *why*, not just *what*, in the
body when the reason isn't obvious from the diff.

## Pull request process

1. Open an issue first for anything beyond a small fix, so the approach can
   be discussed before you invest significant time.
2. Fork the repository and branch from `main`.
3. Make your change, including tests and documentation updates.
4. Ensure CI passes locally before opening the PR (see "Testing
   requirements" below).
5. Fill out the pull request template completely.
6. A maintainer will review; expect at least one round of feedback for
   non-trivial changes. See `GOVERNANCE.md` for release/merge authority.

## Testing requirements

All new behavior must include test coverage in `tests/`. Before opening a
PR, run:

```bash
ruff check .
black --check .
mypy app
bandit -r app -x tests
pytest --cov=app
```

CI runs the same checks plus a Docker build, container health check, and
SBOM generation.

## Documentation expectations

Update `README.md`, relevant files under `docs/`, and docstrings whenever
behavior, endpoints, or configuration change. Do not leave documentation
describing removed or renamed functionality.

## Issue reporting

Use the provided issue templates. **Do not include classified, controlled,
export-controlled, customer-confidential, or government-sensitive material
in any issue, PR, discussion, or commit message in this public repository.**
If you are unsure whether something is sensitive, do not post it — ask a
maintainer privately first (see `SECURITY.md` for the private contact
channel).

## Coding standards

- Python 3.11+, type-annotated, formatted with `black`, linted with `ruff`.
- Prefer small, focused functions over large ones; the scanning/scoring/
  reporting layers are intentionally separated (see `docs/` architecture
  notes) — keep new logic in the matching layer rather than mixing concerns.
- No shell execution based on user input. No arbitrary file execution. No
  network calls to unexpected destinations from application code.

## Developer Certificate of Origin

By submitting a contribution, you certify that you wrote the contribution
yourself, or otherwise have the right to submit it under the project's
license, per the [Developer Certificate of Origin](https://developercertificate.org/).
Sign off your commits with `git commit -s` where practical.

## AI-assisted contributions

AI-assisted contributions (including those written with Claude, Copilot, or
similar tools) are welcome, subject to the same review bar as any other
contribution. If you use an AI tool:

- You are responsible for the correctness, security, and licensing of the
  resulting code, exactly as if you had written it by hand.
- Do not submit AI output you have not personally reviewed and tested.
- Do not paste proprietary, classified, or customer-confidential material
  into a third-party AI tool as part of preparing a contribution to this
  public repository.
- Disclose significant AI assistance in the PR description when it materially
  shaped the design, not just line-completion — this helps reviewers focus.

## Restrictions

Do not submit:

- Classified or controlled information (e.g., CUI, ITAR/EAR-controlled material).
- Proprietary source code, configuration, or documentation from the private
  CHAMP-QN development repository.
- Customer names, deployment details, or government-sensitive information.
- Secrets, credentials, tokens, or internal infrastructure details of any kind.

Contributions violating these restrictions will be rejected and, if already
merged, reverted.
