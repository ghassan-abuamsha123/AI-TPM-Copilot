"""OpenAI-backed extraction layer.

The LLM converts unstructured project updates into structured program data.
The deterministic analyzer evaluates that structured data separately.
"""

import json
import os

from openai import OpenAI


SCHEMA_INSTRUCTIONS = """
Extract technical program-management information from the project update.

Return ONLY valid JSON.

The JSON MUST have exactly these top-level fields:

{
    "project": "",
    "reported_status": "UNKNOWN",
    "actions": [],
    "risks": [],
    "dependencies": [],
    "milestones": [],
    "metrics": [],
    "priority_issues": []
}

Required formats:

actions:
[
    {
        "owner": "string",
        "action": "string",
        "deadline": "string"
    }
]

risks:
[
    {
        "id": "string",
        "description": "string",
        "severity": "LOW | MEDIUM | HIGH | CRITICAL"
    }
]

dependencies:
[
    {
        "upstream": "string",
        "downstream": "string"
    }
]

milestones:
[
    {
        "name": "string",
        "planned": "string",
        "current": "string",
        "schedule_status": "ON_SCHEDULE | DELAYED | EARLY | UNKNOWN"
    }
]

metrics:
[
    {
        "name": "string",
        "actual": number,
        "target": number,
        "unit": "string",
        "lower_is_better": boolean
    }
]

priority_issues:
[
    {
        "description": "string",
        "priority": "P0 | P1 | P2 | P3 | HIGH | MEDIUM | LOW | UNKNOWN"
    }
]

Rules:

1. Do not invent information.

2. Only extract facts explicitly supported by the project update.

3. The input may describe software, hardware, construction, manufacturing,
   infrastructure, research, operations, or another type of technical program.
   Do not assume the project is a software project.

4. Dependencies MUST be JSON objects containing "upstream" and "downstream".
   Never return dependencies as plain strings.

5. Metrics MUST contain numeric actual and target values.

6. For latency, defect rate, error rate, power consumption, cost, or similar
   metrics where smaller values are better, set "lower_is_better" to true.

7. For throughput, performance, completion rate, productivity, or similar
   metrics where larger values are better, set "lower_is_better" to false.

8. Only create a milestone when the update contains meaningful schedule
   information about that milestone.

9. A milestone is DELAYED only when the update explicitly indicates that its
   current schedule is later than its original/planned schedule.

10. If an update says something "remains scheduled" for a date or time,
    classify it as ON_SCHEDULE. Do not treat this as a schedule slip.

11. If only the current date is known and the original planned date is not
    provided, set planned to "UNKNOWN" and schedule_status to "UNKNOWN".
    Do NOT infer that UNKNOWN -> current date represents a delay.

12. If the update says a milestone was completed on schedule, use the same
    meaningful planned/current schedule value when available and classify it
    as ON_SCHEDULE.

13. Do not use words such as "completed", "finished", or "in progress" as
    substitute dates in the planned or current fields.

14. Priority issues are significant unresolved problems explicitly described
    in the update. Examples may include P0/P1 defects, safety deficiencies,
    critical blockers, severe quality issues, or other high-priority problems.

15. Do not convert a non-software issue into a software defect.

16. If the update explicitly states a count of P1 issues, represent those
    issues in priority_issues when enough information is available. Do not
    invent descriptions that were not provided.

17. Risks should capture explicitly supported threats to schedule, quality,
    performance, safety, cost, delivery, or other program objectives.

18. Actions must represent actual assigned or requested work. A statement
    describing a schedule change by itself is NOT an action item unless
    someone is explicitly responsible for taking an action.

19. If information is unavailable, use an empty list or "UNKNOWN".

20. Return JSON only. Do not include Markdown, commentary, or explanation.
"""


def extract_with_llm(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env file."
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        input=[
            {
                "role": "system",
                "content": (
                    "You are a technical program-management data extraction "
                    "assistant. Extract facts conservatively and never invent "
                    "missing schedule, priority, ownership, or project data.\n\n"
                    + SCHEMA_INSTRUCTIONS
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )

    raw_output = response.output_text.strip()

    # Remove accidental Markdown code fences.
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")

        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        data = json.loads(raw_output)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"LLM returned invalid JSON: {raw_output}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            "LLM output must be a JSON object."
        )

    # ---------------------------------------------------------
    # GUARANTEE REQUIRED FIELDS
    # ---------------------------------------------------------

    defaults = {
        "project": "Unknown Project",
        "reported_status": "UNKNOWN",
        "actions": [],
        "risks": [],
        "dependencies": [],
        "milestones": [],
        "metrics": [],
        "priority_issues": [],
    }

    for key, default_value in defaults.items():
        if key not in data or data[key] is None:
            data[key] = default_value

    # ---------------------------------------------------------
    # VALIDATE LIST FIELDS
    # ---------------------------------------------------------

    list_fields = [
        "actions",
        "risks",
        "dependencies",
        "milestones",
        "metrics",
        "priority_issues",
    ]

    for field in list_fields:
        if not isinstance(data[field], list):
            data[field] = []

    # ---------------------------------------------------------
    # REMOVE MALFORMED OBJECTS
    # ---------------------------------------------------------

    data["actions"] = [
        item
        for item in data["actions"]
        if isinstance(item, dict)
        and item.get("action")
    ]

    data["risks"] = [
        item
        for item in data["risks"]
        if isinstance(item, dict)
        and item.get("description")
    ]

    data["dependencies"] = [
        item
        for item in data["dependencies"]
        if isinstance(item, dict)
        and item.get("upstream")
        and item.get("downstream")
    ]

    data["milestones"] = [
        item
        for item in data["milestones"]
        if isinstance(item, dict)
        and item.get("name")
    ]

    data["metrics"] = [
        item
        for item in data["metrics"]
        if isinstance(item, dict)
        and item.get("name")
        and item.get("actual") is not None
        and item.get("target") is not None
    ]

    data["priority_issues"] = [
        item
        for item in data["priority_issues"]
        if isinstance(item, dict)
        and item.get("description")
    ]

    # ---------------------------------------------------------
    # NORMALIZE MILESTONES
    # ---------------------------------------------------------

    valid_schedule_statuses = {
        "ON_SCHEDULE",
        "DELAYED",
        "EARLY",
        "UNKNOWN",
    }

    for milestone in data["milestones"]:
        milestone.setdefault("planned", "UNKNOWN")
        milestone.setdefault("current", "UNKNOWN")

        status = str(
            milestone.get("schedule_status", "UNKNOWN")
        ).upper()

        if status not in valid_schedule_statuses:
            status = "UNKNOWN"

        milestone["schedule_status"] = status

    # ---------------------------------------------------------
    # NORMALIZE REPORTED STATUS
    # ---------------------------------------------------------

    data["reported_status"] = str(
        data.get("reported_status", "UNKNOWN")
    ).upper()

    return data