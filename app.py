import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.analyzer import analyze_program
from src.demo_extractor import extract_program_data


# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI TPM Copilot",
    page_icon="🧠",
    layout="wide",
)

st.title("AI Technical Program Manager Copilot")
st.caption("From project updates to actionable program intelligence")


# ---------------------------------------------------------
# Load default engineering update
# ---------------------------------------------------------

default_path = Path("data/engineering_update.txt")

if default_path.exists():
    default_text = default_path.read_text(encoding="utf-8")
else:
    default_text = ""


# ---------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------

with st.sidebar:

    st.header("Demo Controls")

    extraction_mode = st.radio(
        "Extraction mode",
        ["Reliable demo", "Live LLM"],
        help=(
            "Reliable demo requires no API key. "
            "Live LLM uses OPENAI_API_KEY from .env."
        ),
    )

    st.markdown("---")

    st.markdown(
        "**Design:** AI interprets unstructured language; "
        "deterministic Python evaluates program health."
    )

    st.markdown(
        "**Safety:** Recommendations require human TPM review."
    )


# ---------------------------------------------------------
# Project update input
# ---------------------------------------------------------

notes = st.text_area(
    "Weekly project update",
    value=default_text,
    height=280,
)


# ---------------------------------------------------------
# Analyze program
# ---------------------------------------------------------

if st.button(
    "Analyze Program",
    type="primary",
    use_container_width=True,
):

    if not notes.strip():
        st.warning("Add a project update first.")
        st.stop()

    with st.spinner("Analyzing project update..."):

        # -------------------------------------------------
        # Extraction layer
        # -------------------------------------------------

        if extraction_mode == "Live LLM":

            try:
                from src.llm_extractor import extract_with_llm

                structured = extract_with_llm(notes)

            except Exception as exc:

                st.error(
                    f"Live LLM extraction failed: {exc}"
                )

                st.info(
                    "Switch to Reliable demo mode for the "
                    "interview-safe offline workflow."
                )

                st.stop()

        else:

            structured = extract_program_data(notes)

        # -------------------------------------------------
        # Deterministic analysis layer
        # -------------------------------------------------

        analysis = analyze_program(structured)

    # Store results so Streamlit keeps them
    st.session_state["structured"] = structured
    st.session_state["analysis"] = analysis


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

if "analysis" in st.session_state:

    structured = st.session_state["structured"]
    analysis = st.session_state["analysis"]

    # -----------------------------------------------------
    # Program health summary
    # -----------------------------------------------------

    st.divider()

    project_name = structured.get("project", "Unknown Project")

    if project_name and project_name != "Unknown Project":
        st.caption(f"Analysis: {project_name}")

    st.subheader("Program Health")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Reported Status",
        analysis["reported_status"],
    )

    c2.metric(
        "Evidence-Based Status",
        analysis["assessed_status"],
    )

    c3.metric(
        "Risk Score",
        analysis["risk_score"],
    )

    priority_issues = analysis.get(
        "priority_issues",
        []
    )

    serious_issue_count = sum(
        1
        for issue in priority_issues
        if str(
            issue.get("priority", "")
        ).upper()
        in {
            "P0",
            "P1",
            "HIGH",
            "CRITICAL",
        }
    )

    c4.metric(
        "Priority Issues",
        serious_issue_count,
    )

    # -----------------------------------------------------
    # Watermelon detection
    # -----------------------------------------------------

    if analysis["watermelon"]:

        st.error(
            "🍉 WATERMELON CONDITION DETECTED — "
            "The program is reported GREEN, but underlying "
            "project signals indicate material risk."
        )

    elif analysis["assessed_status"] == "GREEN":

        st.success(
            "Program health is consistent with the "
            "reported GREEN status."
        )

    else:

        st.warning(
            f'Program assessed as {analysis["health_label"]}.'
        )

    # -----------------------------------------------------
    # Risk explanation
    # -----------------------------------------------------

    st.subheader("Why the Status Changed")

    findings = analysis.get("findings", [])

    if findings:

        for finding in findings:
            st.write(f"• {finding}")

    else:

        st.write(
            "No material program-health concerns were detected."
        )

    # -----------------------------------------------------
    # Two-column program intelligence section
    # -----------------------------------------------------

    left, right = st.columns(2)

    # -----------------------------------------------------
    # LEFT COLUMN
    # -----------------------------------------------------

    with left:

        st.subheader("Dependency Chain")

        dependencies = structured.get(
            "dependencies",
            []
        )

        valid_dependencies = [
            dep
            for dep in dependencies
            if isinstance(dep, dict)
            and dep.get("upstream")
            and dep.get("downstream")
        ]

        if valid_dependencies:

            for dep in valid_dependencies:

                st.code(
                    f'{dep["upstream"]}  →  '
                    f'{dep["downstream"]}',
                    language=None,
                )

        else:

            st.caption(
                "No explicit dependencies identified."
            )

        st.subheader("Performance")

        metric_results = analysis.get(
            "metric_results",
            []
        )

        if metric_results:

            for metric in metric_results:

                actual = metric.get("actual", 0)
                unit = metric.get("unit", "")
                gap_pct = metric.get("gap_pct", 0.0)
                off_target = metric.get(
                    "off_target",
                    False,
                )

                lower_is_better = bool(
                    metric.get(
                        "lower_is_better",
                        False,
                    )
                )

                if off_target:

                    if lower_is_better:
                        delta_text = (
                            f'+{gap_pct:.1f}% above target'
                        )
                    else:
                        delta_text = (
                            f'-{gap_pct:.1f}% below target'
                        )

                    delta_color = "inverse"

                else:

                    delta_text = "On target"
                    delta_color = "normal"

                st.metric(
                    metric.get(
                        "name",
                        "Metric",
                    ),
                    f"{actual:g} {unit}",
                    delta=delta_text,
                    delta_color=delta_color,
                )

        else:

            st.caption(
                "No quantitative performance metrics identified."
            )

        # -------------------------------------------------
        # Priority issues
        # -------------------------------------------------

        st.subheader("Priority Issues")

        if priority_issues:

            for issue in priority_issues:

                priority = issue.get(
                    "priority",
                    "UNKNOWN",
                )

                description = issue.get(
                    "description",
                    "",
                )

                st.markdown(
                    f"**{priority}** — {description}"
                )

        else:

            st.caption(
                "No priority issues identified."
            )

    # -----------------------------------------------------
    # RIGHT COLUMN
    # -----------------------------------------------------

    with right:

        st.subheader("Action Items")

        actions = structured.get(
            "actions",
            []
        )

        valid_actions = [
            action
            for action in actions
            if isinstance(action, dict)
        ]

        if valid_actions:

            for action in valid_actions:

                owner = action.get(
                    "owner",
                    "Unknown owner",
                )

                action_text = action.get(
                    "action",
                    "Action not specified",
                )

                deadline = action.get(
                    "deadline",
                    "Not specified",
                )

                st.markdown(
                    f"**{owner}** — "
                    f"{action_text}  \n"
                    f"Deadline: `{deadline}`"
                )

        else:

            st.caption(
                "No explicit action items identified."
            )

        st.subheader(
            "Recommended Corrective Actions"
        )

        recommendations = analysis.get(
            "recommendations",
            []
        )

        if recommendations:

            for i, recommendation in enumerate(
                recommendations,
                start=1,
            ):

                st.write(
                    f"{i}. {recommendation}"
                )

        else:

            st.success(
                "No corrective actions currently required."
            )

    # -----------------------------------------------------
    # Human review
    # -----------------------------------------------------

    st.divider()

    st.subheader("Human-in-the-Loop Review")

    st.caption(
        "AI identifies signals and recommends actions; "
        "the TPM remains accountable for the final decision."
    )

    approve_col, review_col = st.columns(2)

    with approve_col:

        if st.button(
            "Approve Recommendations",
            use_container_width=True,
        ):

            st.success(
                "Recommendations approved for TPM follow-up."
            )

    with review_col:

        if st.button(
            "Needs Further Review",
            use_container_width=True,
        ):

            st.warning(
                "Recommendations flagged for further "
                "project review."
            )

    # -----------------------------------------------------
    # Structured AI output
    # -----------------------------------------------------

    with st.expander(
        "View Structured Program Data (JSON)"
    ):

        st.json(structured)

    # -----------------------------------------------------
    # Save report
    # -----------------------------------------------------

    output_dir = Path("output")

    output_dir.mkdir(
        exist_ok=True
    )

    report = {
        "extracted": structured,
        "analysis": analysis,
    }

    report_json = json.dumps(
        report,
        indent=2,
    )

    report_path = (
        output_dir / "program_status.json"
    )

    report_path.write_text(
        report_json,
        encoding="utf-8",
    )

    # -----------------------------------------------------
    # Download report
    # -----------------------------------------------------

    st.download_button(
        "Download Analysis JSON",
        data=report_json,
        file_name="program_status.json",
        mime="application/json",
    )


# ---------------------------------------------------------
# Initial state
# ---------------------------------------------------------

else:

    st.info(
        "Click **Analyze Program** to analyze "
        "the project update."
    )