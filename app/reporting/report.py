"""Assessment orchestration and report rendering.

`assess_inventory` is the single entry point that turns a validated
`Inventory` into a full `AssessmentResult`. It performs no I/O, no network
access, and no persistence -- it is pure computation over the data already
supplied in the request.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app import __version__
from app.config import settings
from app.models.inventory import (
    AssessmentResult,
    AssetFinding,
    Inventory,
)
from app.scanners.crypto_scanner import classify_algorithms
from app.scoring.readiness import overall_classification, score_findings, severity_counts
from app.standards.mappings import references_for

DISCLAIMER = (
    "This reference tool provides preliminary cryptographic-readiness guidance. "
    "Results require validation by qualified security and cryptographic "
    "professionals and do not constitute certification, authorization, or "
    "formal compliance determination."
)


class InventoryTooLargeError(ValueError):
    """Raised when an inventory exceeds configured size limits."""


def _validate_limits(inventory: Inventory) -> None:
    if len(inventory.assets) > settings.max_assets:
        raise InventoryTooLargeError(
            f"inventory contains {len(inventory.assets)} assets, "
            f"exceeding the limit of {settings.max_assets}"
        )
    for asset in inventory.assets:
        if len(asset.algorithms) > settings.max_algorithms_per_asset:
            raise InventoryTooLargeError(
                f"asset '{asset.id}' has {len(asset.algorithms)} algorithm entries, "
                f"exceeding the limit of {settings.max_algorithms_per_asset}"
            )


def assess_inventory(inventory: Inventory, *, now: datetime | None = None) -> AssessmentResult:
    """Run the full crypto-readiness assessment over an inventory."""
    _validate_limits(inventory)

    asset_results: list[AssetFinding] = []
    all_findings = []

    for asset in inventory.assets:
        findings = classify_algorithms(asset.algorithms)
        all_findings.extend(findings)
        asset_results.append(
            AssetFinding(
                asset_id=asset.id,
                asset_category=asset.category,
                findings=findings,
                asset_classification=overall_classification(findings),
                asset_score=score_findings(findings),
            )
        )

    classifications_present = {f.classification for f in all_findings}

    return AssessmentResult(
        inventory_name=inventory.inventory_name,
        generated_at=(now or datetime.now(UTC)).isoformat(),
        scanner_version=__version__,
        asset_count=len(inventory.assets),
        finding_count=len(all_findings),
        overall_score=score_findings(all_findings),
        overall_classification=overall_classification(all_findings),
        findings_by_severity=severity_counts(all_findings),
        assets=asset_results,
        standards_references=references_for(classifications_present),
        disclaimer=DISCLAIMER,
    )


def render_markdown(result: AssessmentResult) -> str:
    """Render a human-readable Markdown report from an assessment result."""
    lines: list[str] = []
    title = result.inventory_name or "Untitled inventory"
    lines.append(f"# CHAMP-QN Crypto Readiness Report — {title}")
    lines.append("")
    lines.append(f"*Generated: {result.generated_at} · Scanner version {result.scanner_version}*")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Overall readiness score:** {result.overall_score} / 100")
    lines.append(f"- **Overall classification:** {result.overall_classification.value}")
    lines.append(f"- **Assets assessed:** {result.asset_count}")
    lines.append(f"- **Findings identified:** {result.finding_count}")
    lines.append("")
    lines.append("### Findings by severity")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---|")
    for severity, count in result.findings_by_severity.items():
        lines.append(f"| {severity} | {count} |")
    lines.append("")
    lines.append("## Assets")
    lines.append("")
    for asset in result.assets:
        lines.append(f"### {asset.asset_id}")
        if asset.asset_category:
            lines.append(f"*Category: {asset.asset_category}*")
        lines.append("")
        lines.append(
            f"Asset score: **{asset.asset_score}/100** · "
            f"Classification: **{asset.asset_classification.value}**"
        )
        lines.append("")
        if asset.findings:
            lines.append("| Detected value | Matched algorithm | Classification | Guidance |")
            lines.append("|---|---|---|---|")
            for finding in asset.findings:
                lines.append(
                    f"| `{finding.raw_value}` | {finding.matched_name} | "
                    f"{finding.classification.value} | {finding.guidance} |"
                )
        else:
            lines.append("_No algorithms listed for this asset._")
        lines.append("")
    lines.append("## Standards and guidance references (informational)")
    lines.append("")
    for ref in result.standards_references:
        lines.append(f"- **{ref.source} — {ref.reference}**: {ref.note} ([source]({ref.url}))")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"> {result.disclaimer}")
    lines.append("")
    return "\n".join(lines)
