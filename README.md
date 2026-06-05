# Defect-Triage-RCA-Stand-alone

A simple Python-based AI Defect Triage & RCA demo project.

## Features

The Gradio app accepts:
- Jira defect link
- Optional notes

It displays:
- Defect summary
- Predicted owner team
- Predicted subsystem
- Probable root causes
- Similar historical defects
- Recommended next action
- RCA summary

## Quick Start

1. Create and activate a virtual environment (optional but recommended)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open the Gradio URL shown in your terminal.

## Sample Input

Use `sample_input.json` as an example payload.
