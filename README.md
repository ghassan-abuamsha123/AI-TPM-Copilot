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

## 2-minute demo flow

1. Show the weekly engineering update and its reported **GREEN** status.
2. Click **Analyze Program**.
3. Reveal the **WATERMELON CONDITION**.
4. Explain firmware → driver → system-validation dependencies.
5. Show the 44 vs 50 tokens/sec performance gap and open P1 defects.
6. Show recommended corrective actions and human review.
7. Close with the design principle: **AI accelerates interpretation; deterministic logic and human judgment protect the decision.**

## Disclaimer

This is a portfolio/demo project built with fictional data for educational and interview purposes.
