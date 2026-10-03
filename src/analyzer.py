"""Deterministic program-health analysis.

The LLM interprets unstructured project language.
This module performs repeatable calculations and explicit program-health rules.
"""


def _safe_list(value):
    """Return value only if it is a list."""
    return value if isinstance(value, list) else []


def _safe_float(value):
    """Convert a value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def analyze_program(data: dict) -> dict:
    """Analyze structured program data and return deterministic program health."""

    if not isinstance(data, dict):
        data = {}

    findings = []
    recommendations = []
    dependency_warnings = []
    metric_results = []

    score = 0

    # =========================================================
    # 1. METRIC ANALYSIS
    # =========================================================

    for metric in _safe_list(data.get("metrics")):

        if not isinstance(metric, dict):
            continue

        actual = _safe_float(metric.get("actual"))
        target = _safe_float(metric.get("target"))

        if actual is None or target is None:
            continue

        name = str(metric.get("name") or "Metric")
        unit = str(metric.get("unit") or "")
        lower_is_better = bool(
            metric.get("lower_is_better", False)
        )

        off_target = False
        gap_pct = 0.0

        if target != 0:

            if lower_is_better:

                off_target = actual > target

                if off_target:
                    gap_pct = (
                        (actual - target)
                        / abs(target)
                        * 100.0
                    )

            else:

                off_target = actual < target

                if off_target:
                    gap_pct = (
                        (target - actual)
                        / abs(target)
                        * 100.0
                    )

        if off_target:

            score += 2

            direction = (
                "above"
                if lower_is_better
                else "below"
            )

            findings.append(
                f"{name} is {abs(gap_pct):.1f}% "
                f"{direction} target "
                f"({actual:g} vs {target:g} {unit})."
            )

            recommendations.append(
                f"Create a recovery plan for the "
                f"{name.lower()} gap and assign "
                f"an owner for corrective action."
            )

        metric_results.append(
            {
                **metric,
                "actual": actual,
                "target": target,
                "gap_pct": round(abs(gap_pct), 1),
                "below_target": (
                    off_target
                    and not lower_is_better
                ),
                "off_target": off_target,
            }
        )

    # =========================================================
    # 2. MILESTONE / SCHEDULE ANALYSIS
    # =========================================================

    milestones = []

    for milestone in _safe_list(data.get("milestones")):

        if not isinstance(milestone, dict):
            continue

        name = str(
            milestone.get("name") or ""
        ).strip()

        if not name:
            continue

        planned = str(
            milestone.get("planned") or "UNKNOWN"
        ).strip()

        current = str(
            milestone.get("current") or "UNKNOWN"
        ).strip()

        schedule_status = str(
            milestone.get("schedule_status") or "UNKNOWN"
        ).upper().strip()

        if schedule_status not in {
            "ON_SCHEDULE",
            "DELAYED",
            "EARLY",
            "UNKNOWN",
        }:
            schedule_status = "UNKNOWN"

        clean_milestone = {
            "name": name,
            "planned": planned,
            "current": current,
            "schedule_status": schedule_status,
        }

        milestones.append(clean_milestone)

        # IMPORTANT:
        # We no longer infer a delay simply because
        # planned != current.
        #
        # The extractor must explicitly classify it
        # as DELAYED.
        if schedule_status == "DELAYED":

            score += 2

            if (
                planned.upper() != "UNKNOWN"
                and current.upper() != "UNKNOWN"
            ):

                findings.append(
                    f"{name} slipped from "
                    f"{planned} to {current}."
                )

            else:

                findings.append(
                    f"{name} is reported as delayed."
                )

            recommendations.append(
                f"Confirm the root cause, recovery owner, "
                f"and recovery plan for the {name} "
                f"schedule delay."
            )

    # =========================================================
    # 3. PRIORITY ISSUE ANALYSIS
    # =========================================================

    priority_issues = []

    for issue in _safe_list(
        data.get("priority_issues")
    ):

        if not isinstance(issue, dict):
            continue

        description = str(
            issue.get("description") or ""
        ).strip()

        priority = str(
            issue.get("priority") or "UNKNOWN"
        ).upper().strip()

        if not description:
            continue

        priority_issues.append(
            {
                "description": description,
                "priority": priority,
            }
        )

    # Score serious priority issues.
    serious_issues = [
        issue
        for issue in priority_issues
        if issue["priority"] in {
            "P0",
            "P1",
            "HIGH",
            "CRITICAL",
        }
    ]

    if serious_issues:

        # Cap contribution so issue count does not
        # overwhelm the entire health assessment.
        score += min(
            len(serious_issues) * 2,
            4,
        )

        for issue in serious_issues:

            findings.append(
                f'{issue["priority"]} issue: '
                f'{issue["description"]}'
            )

        recommendations.append(
            "Review high-priority open issues for "
            "program impact, ownership, mitigation, "
            "and closure dates."
        )

    # =========================================================
    # 4. DEPENDENCY ANALYSIS
    # =========================================================

    dependencies = []

    for dep in _safe_list(
        data.get("dependencies")
    ):

        if not isinstance(dep, dict):
            continue

        upstream = dep.get("upstream")
        downstream = dep.get("downstream")

        if not upstream or not downstream:
            continue

        dependencies.append(
            {
                "upstream": str(upstream).strip(),
                "downstream": str(downstream).strip(),
            }
        )

    milestone_by_name = {
        milestone["name"].lower(): milestone
        for milestone in milestones
    }

    for dep in dependencies:

        upstream_name = dep["upstream"]
        downstream_name = dep["downstream"]

        up = milestone_by_name.get(
            upstream_name.lower()
        )

        down = milestone_by_name.get(
            downstream_name.lower()
        )

        if not up or not down:
            continue

        up_current = str(
            up.get("current") or ""
        ).strip()

        down_current = str(
            down.get("current") or ""
        ).strip()

        # Only perform same-time schedule compression
        # analysis when both schedules are actually known.
        if (
            up_current
            and down_current
            and up_current.upper() != "UNKNOWN"
            and down_current.upper() != "UNKNOWN"
            and up_current.lower()
            == down_current.lower()
        ):

            score += 2

            warning = (
                f"{downstream_name} depends on "
                f"{upstream_name}, but both are "
                f"currently scheduled for "
                f"{up_current}, leaving little "
                f"or no schedule buffer."
            )

            dependency_warnings.append(
                warning
            )

            findings.append(
                warning
            )

            recommendations.append(
                f"Re-baseline the dependency between "
                f"{upstream_name} and "
                f"{downstream_name} and determine "
                f"whether downstream work can begin "
                f"before full upstream completion."
            )

    # =========================================================
    # 5. EXTRACTED RISK SIGNALS
    # =========================================================

    severe_risk_count = 0

    for risk in _safe_list(
        data.get("risks")
    ):

        if not isinstance(risk, dict):
            continue

        severity = str(
            risk.get("severity") or ""
        ).upper()

        if severity in {
            "HIGH",
            "CRITICAL",
        }:
            severe_risk_count += 1

    # Risk contribution is intentionally capped.
    if severe_risk_count:

        score += min(
            severe_risk_count,
            2,
        )

    # =========================================================
    # 6. DETERMINE PROGRAM HEALTH
    # =========================================================

    if score >= 7:

        assessed_status = "RED"
        health_label = "CRITICAL"

    elif score >= 3:

        assessed_status = "YELLOW"
        health_label = "AT RISK"

    else:

        assessed_status = "GREEN"
        health_label = "ON TRACK"

    reported_status = str(
        data.get(
            "reported_status",
            "UNKNOWN",
        )
        or "UNKNOWN"
    ).upper()

    # =========================================================
    # 7. WATERMELON DETECTION
    # =========================================================

    watermelon = (
        reported_status == "GREEN"
        and assessed_status
        in {"YELLOW", "RED"}
    )

    if watermelon:

        recommendations.append(
            "Update the program status so leadership "
            "sees the underlying program risk rather "
            "than a green headline."
        )

    # =========================================================
    # 8. REMOVE DUPLICATE RECOMMENDATIONS
    # =========================================================

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )

    # =========================================================
    # 9. RETURN ANALYSIS
    # =========================================================

    return {
        "reported_status": reported_status,
        "assessed_status": assessed_status,
        "health_label": health_label,
        "risk_score": score,
        "watermelon": watermelon,
        "findings": findings,
        "dependency_warnings": dependency_warnings,
        "metric_results": metric_results,
        "priority_issues": priority_issues,
        "recommendations": recommendations,
    }