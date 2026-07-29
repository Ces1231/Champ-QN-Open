# Recommended GitHub Repository Settings

These are recommendations only. Applying them requires repository owner/admin
access on GitHub and is **not** something that can be done from within the
repository's file contents — hence this separate document.

## Naming — resolved

An earlier draft of this document flagged a naming discrepancy: the task
that produced this repository's initial content referred to it as
`Champ-QN-Open`, while the actual GitHub remote is:

```
https://github.com/Ces1231/Champ-QN-public
```

**Confirmed by the repository owner: the name stays as `Champ-QN-public`.**
No rename is needed. All documentation in this repository (`README.md`,
`NOTICE`, `GOVERNANCE.md`, `CONTRIBUTING.md`, etc.) consistently uses
`CHAMP-QN-public` as the project name.

## Suggested repository description

> Vendor-neutral, open-source reference tooling for the CHAMP-QN Zero
> Trust control plane — starting with the CHAMP-QN Crypto Readiness
> Scanner, a post-quantum cryptography readiness assessment tool.

## Suggested topics

```
post-quantum-cryptography
pqc
cryptography
zero-trust
fastapi
python
security-tools
nist
cnsa2.0
quantum-computing
open-source
crypto-inventory
```

## Suggested settings

- **Features**
  - Enable **Issues**.
  - Enable **Discussions** if community Q&A is desired.
  - Enable **Preserve this repository** only if/when it reaches a stability
    point worth archival protection.
- **Security**
  - Enable **Private vulnerability reporting** (Settings → Security → Private
    vulnerability reporting) so `SECURITY.md`'s preferred channel actually
    exists.
  - Enable **Dependabot alerts** and **Dependabot security updates**.
  - Enable **Secret scanning** and **push protection**.
- **Pull Requests**
  - Require at least one review before merge once there is more than one
    maintainer.
  - Require status checks (the `CI` workflow) to pass before merge.
  - Consider requiring signed commits or DCO sign-off enforcement
    (a DCO GitHub App/Action) to match `CONTRIBUTING.md`'s guidance.
- **Branch protection** on `main`:
  - Require CI to pass.
  - Restrict force-pushes.
  - Require linear history (optional, maintainer preference).

## Before making this repository's existence more widely known

- Contact email (`carnell.smith@champtron-systems.com` in `SECURITY.md` and
  `CODE_OF_CONDUCT.md`) — confirmed by the repository owner as monitored.
- Do a final human pass over `screenshots/` for anything sensitive that an
  automated review might miss (this session's assessment spot-checked
  several screenshots and found nothing sensitive, but a full human review
  before any program submission is still recommended).
- Confirm the license choice (this repository currently keeps its existing
  MIT license rather than switching to Apache-2.0 — see README "License"
  section for the reasoning) matches your intent.
