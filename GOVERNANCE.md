# Governance

This document describes how decisions are made in this repository today,
and how that is expected to evolve as the project matures.

## Current model: founder-led (pre-1.0)

CHAMP-QN-public is currently maintained by its founder, **Carnell E. Smith**
(Champtron Systems LLC), as the sole maintainer. This is typical for an
early-stage open-source project and is expected to change as the
contributor base grows — see "Future maintainer expansion" below.

## Maintainer responsibilities

The maintainer is responsible for:

- Triaging issues and pull requests in a reasonable timeframe.
- Reviewing contributions for correctness, security, licensing, and fit
  with the project's scope.
- Cutting releases and maintaining `CHANGELOG.md`.
- Enforcing the `CODE_OF_CONDUCT.md`.
- Making final decisions on scope disputes (e.g., whether a proposed
  feature belongs in this public repository — see the private/public
  boundary described in `README.md`).

## Decision-making process

- **Routine changes** (bug fixes, documentation, dependency updates, test
  improvements): maintainer approval via normal PR review.
- **Non-trivial features**: discussed in an issue before implementation.
  The maintainer decides whether a feature fits this repository's scope as
  the sanitized public companion to the private CHAMP-QN platform.
- **Breaking changes** (API, schema, or CLI behavior changes): called out
  explicitly in the PR description and the changelog, following semantic
  versioning.

## Contribution review

All contributions are reviewed by the maintainer (or a delegated reviewer,
once any exist) before merge. Review covers functional correctness, test
coverage, security implications, and consistency with existing
documentation. See `CONTRIBUTING.md` for the practical checklist.

## Release authority

Releases are cut by the maintainer. Version numbers follow semantic
versioning once the project reaches 1.0; pre-1.0 versions (`0.x.y`) may
include breaking changes between minor versions, called out in
`CHANGELOG.md`.

## Security-sensitive changes

Changes touching authentication, input parsing (especially YAML/JSON
deserialization), file handling, or container security posture receive
additional scrutiny and, where practical, are tested against the scenarios
described in `docs/THREAT_MODEL.md` before merge.

## Conflict resolution

Disagreements about design direction are first discussed in the relevant
issue or PR. If consensus isn't reached, the maintainer makes the final
call, with reasoning documented in the issue/PR thread. As the project
grows a broader maintainer group, this document will be updated to
describe a voting or consensus-seeking process among maintainers.

## Future maintainer expansion

As the contributor base grows, the intent is to:

1. Identify frequent, trusted contributors and offer commit/triage access.
2. Move from founder-led decisions toward documented maintainer consensus.
3. Update this document publicly before any such transition takes effect,
   rather than changing governance silently.

## Neutral treatment of vendors and cryptographic implementations

This project aims to be vendor-neutral. The scanner's algorithm catalog and
standards mappings are based on publicly published, non-proprietary
cryptographic and standards terminology (NIST, NSA, CISA). Contributions
that would bias detection or recommendations toward or against a specific
commercial vendor's product, without a citable public standards basis, will
be declined.
