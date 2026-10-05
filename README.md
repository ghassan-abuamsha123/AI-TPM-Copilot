# AI TPM Copilot

**AI-powered technical program management assistant for turning engineering updates into actionable program intelligence.**

AI TPM Copilot demonstrates how AI can help a technical program manager identify actions, dependencies, priorities, schedule risks, performance gaps, and hidden project-health issues from unstructured engineering updates.

> **Important:** Project Phoenix and all included data are fictional. No AMD, employer, or confidential project data is used.

## The problem

Technical programs generate information across engineering meetings, status updates, metrics, defects, and multiple teams. A program can look **GREEN** at the headline level while schedule slips, dependencies, defects, or performance gaps are developing underneath.

This project calls that a **watermelon condition**: green on the outside, red/yellow underneath.

## Demo

The fictional Project Phoenix update reports **GREEN**, while the underlying notes contain:

- Firmware integration slipped from Tuesday to Thursday.
- Driver validation depends on firmware integration.
- Driver validation is also scheduled for Thursday, compressing the dependency.
- System validation remains Friday.
- Two P1 software defects remain open.
- AI inference is 44 tokens/sec against a 50 tokens/sec target.

AI TPM Copilot converts those notes into structured data and applies deterministic program-health logic to expose the hidden risk.

## How It Works

The AI Technical Program Manager Copilot separates AI-based interpretation from deterministic program analysis.

### 1. Unstructured Project Update
The user provides a natural-language project or engineering update containing information such as milestones, risks, dependencies, performance metrics, action items, and priority issues.

### 2. AI-Powered Extraction
The application uses an LLM through the OpenAI API to interpret the update and convert the unstructured text into structured program data.

The model extracts information including:
- Reported program status
- Risks and priority issues
- Action items and owners
- Milestones and schedule changes
- Technical dependencies
- Performance metrics

The LLM is used for interpretation rather than making the final program-health decision.

### 3. Deterministic Program Analysis
The structured data is passed to a Python-based analysis layer.

Instead of asking the LLM to decide whether a program is GREEN, YELLOW, or RED, deterministic rules evaluate signals such as:
- Schedule slips
- Performance gaps
- Open priority issues
- Technical dependencies
- Program risks

This separation makes the program-health assessment more consistent, explainable, and repeatable.

### 4. Program Intelligence
The application converts the analysis into a TPM-focused dashboard showing:
- Reported vs. evidence-based program health
- Risk score
- Reasons behind the status
- Dependency chains
- Performance against targets
- Action items
- Priority issues
- Recommended corrective actions

The application can also identify a "watermelon" condition: a program reported as GREEN while underlying evidence indicates material risk.

### 5. Human-in-the-Loop Decision Making
The system does not autonomously make the final program decision.

AI helps identify and organize important signals, while deterministic logic supports consistent analysis. The Technical Program Manager remains responsible for reviewing the evidence, approving actions, escalating risks, and making the final decision.

> **Design principle:** AI accelerates interpretation. Deterministic logic supports consistency. Human judgment owns the decision.

---

## Technical Architecture

```text
Weekly Engineering Update
          |
          v
     OpenAI API / LLM
          |
          v
 Structured Program Data
          |
          v
 Deterministic Python Analyzer
          |
          v
 Program Health + Risks + Dependencies
          |
          v
   Streamlit Dashboard
          |
          v
      TPM Review

## Architecture

```text
Unstructured Engineering Update
             |
             v
     AI / LLM Extraction
             |
             v
   Structured Program JSON
             |
             v
 Deterministic Python Engine
     |        |        |
     |        |        +--> Performance gap
     |        +-----------> Dependency risk
     +--------------------> Schedule / priority risk
             |
             v
     Watermelon Detector
             |
             v
 Corrective-Action Recommendations
             |
             v
       Human TPM Review
             |
             v
          Dashboard
```

### Core design decision

The application separates **probabilistic AI interpretation** from **deterministic analysis**.

An LLM is useful for interpreting messy human language, but schedule calculations, metric comparisons, and explicit risk rules should be repeatable and auditable. Final decisions remain with a human TPM.

## Run locally

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in Terminal.

### Interview-safe mode

The default **Reliable demo** mode requires no API key or internet connection. It uses a deterministic extractor for the fictional Project Phoenix scenario so the live presentation cannot fail because of an API/network issue.

### Optional live LLM mode

Copy the environment template:

```bash
cp .env.example .env
```

Add your API key to `.env`, then select **Live LLM** in the dashboard. `.env` is excluded by `.gitignore`; never commit API keys.

## Test

```bash
pytest
```

The tests verify that the Project Phoenix scenario detects:

- the watermelon condition,
- the 12% inference-performance gap,
- the compressed firmware → driver dependency.

## Repository structure

```text
AI-TPM-Copilot/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── engineering_update.txt
├── output/
├── src/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── demo_extractor.py
│   └── llm_extractor.py
└── tests/
    └── test_analyzer.py
```

## What this project demonstrates

- AI/LLM application architecture
- Human-in-the-loop AI design
- Technical program management thinking
- Requirements and structured-data extraction
- Dependency and schedule-risk analysis
- Program-health reporting
- P1 defect awareness and prioritization
- AI workload performance tracking
- Testable, modular Python design

## Disclaimer

This is a portfolio/demo project built with fictional data for educational and interview purposes.
