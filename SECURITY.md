# Security Policy

## Scope

This policy covers the code in this public repository — primarily the
**CHAMP-QN Crypto Readiness Scanner** reference component. It does not
cover the privately developed CHAMP-QN platform, which has its own,
separate security process not disclosed here.

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x (current) | Yes |
| Pre-release / main branch | Best-effort |

This project is in early alpha. Until a 1.0 release, only the latest
tagged release and `main` branch receive security attention.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report privately to:

> **carnell.smith@champtron-systems.com** — confirmed monitored mailbox.

If GitHub's private vulnerability reporting feature
(Security → Advisories → Report a vulnerability) is enabled for this
repository, that is the preferred channel.

Please include:

- A description of the vulnerability and its potential impact.
- Steps to reproduce, including a minimal example if possible.
- The version/commit affected.
- Whether you intend to publicly disclose, and any timeline you have in mind.

## Expected acknowledgment timeline

- **Acknowledgment:** within 5 business days of receipt.
- **Initial assessment:** within 10 business days of acknowledgment.
- **Resolution timeline:** communicated once severity is assessed; critical
  issues are prioritized.

These are targets for a small open-source maintainer team, not contractual
SLAs.

## Disclosure coordination

We follow a coordinated disclosure model:

1. You report privately.
2. We confirm, assess severity, and develop a fix.
3. We agree with you on a disclosure date, generally once a fix is
   available and users have had reasonable time to update.
4. We publish a security advisory and, where applicable, credit the
   reporter (with permission).

Please do not publish vulnerability details (including in public issues,
pull requests, or commit messages) before coordinated disclosure.

## Scope of accepted reports

In scope:

- The Crypto Readiness Scanner application code (`app/`), its API, and its
  Docker packaging.
- Supply-chain issues in this repository's declared dependencies.
- Documentation that could lead to insecure deployment if followed as written.

Out of scope:

- The private CHAMP-QN platform and its infrastructure.
- Third-party services referenced only informationally (e.g., standards
  body websites linked from documentation).
- Denial of service achieved purely by resource exhaustion against a
  deliberately under-resourced local deployment.

## Testing rules — safe harbor

We support good-faith security research against your **own local instance**
of this software. When testing:

- **Do not** perform destructive testing, denial-of-service testing, or
  testing against any deployment you do not own or control.
- **Do not** attempt to access, modify, or exfiltrate data belonging to
  others.
- **Do not** publish zero-day details in public issues, forums, or social
  media before coordinated disclosure.

Good-faith research conducted consistent with this policy, limited to your
own local instance, and reported through the private channel above will not
be treated as a hostile act by the maintainers of this repository. This is
a project-level statement of intent, not a legal indemnification, and does
not bind third parties or any organization other than this project's
maintainers.
