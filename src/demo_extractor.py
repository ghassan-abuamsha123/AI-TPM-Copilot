"""Deterministic extractor for the fictional Project Phoenix demo.

This provides an interview-safe offline workflow that does not require
network access or an API key.

The output intentionally follows the same schema as the Live LLM extractor,
allowing both extraction methods to feed the same deterministic analyzer.
"""


def extract_program_data(text: str) -> dict:
    """Return structured program data for the Project Phoenix demo."""

    return {
        "project": "Project Phoenix",
        "reported_status": "GREEN",

        "actions": [
            {
                "owner": "Sarah",
                "action": "Prepare system validation environment",
                "deadline": "Wednesday",
            },
            {
                "owner": "Firmware Team",
                "action": "Provide updated integration status",
                "deadline": "Thursday morning",
            },
        ],

        "risks": [
            {
                "id": "R1",
                "description": (
                    "Firmware integration slipped from Tuesday "
                    "to Thursday"
                ),
                "severity": "HIGH",
            },
            {
                "id": "R2",
                "description": (
                    "Two high-priority software defects remain open"
                ),
                "severity": "HIGH",
            },
        ],

        "dependencies": [
            {
                "upstream": "Firmware Integration",
                "downstream": "Driver Validation",
            },
            {
                "upstream": "Driver Validation",
                "downstream": "System Validation",
            },
        ],

        "milestones": [
            {
                "name": "Firmware Integration",
                "planned": "Tuesday",
                "current": "Thursday",
            },
            {
                "name": "Driver Validation",
                "planned": "Thursday",
                "current": "Thursday",
            },
            {
                "name": "System Validation",
                "planned": "Friday",
                "current": "Friday",
            },
        ],

        "metrics": [
            {
                "name": "Inference Performance",
                "actual": 44.0,
                "target": 50.0,
                "unit": "tokens/sec",
                "lower_is_better": False,
            }
        ],

        "priority_issues": [
            {
                "priority": "P1",
                "description": (
                    "Software defect affecting driver validation"
                ),
            },
            {
                "priority": "P1",
                "description": (
                    "Software defect affecting system validation"
                ),
            },
        ],
    }