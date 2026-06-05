# Defect-Triage-RCA-Stand-alone

AI-powered defect triage and root cause analysis tool that uses Jira defect input to predict owner team, subsystem, probable root causes, similar historical defects, and RCA summary.

## Overview
This repository contains a proof-of-concept for faster Jira-based defect investigation. The tool accepts a Jira defect link and optional notes, then provides a guided triage output to help teams begin investigation more quickly.

## Key capabilities
- Jira defect link intake
- Predicted owner team
- Predicted subsystem
- Probable root cause suggestions
- Similar historical defects view
- Recommended next action
- AI-generated RCA summary

## Planned repository contents
- `app.py` - Gradio demo application
- `requirements.txt` - Python dependencies
- `sample_inputs.txt` - Example Jira links and notes
- `offline_demo/` - Browser-openable HTML demo
- `presentation/` - Presentation deck
- `screenshots/` - Application screenshots

## Getting started
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```

## Notes
This is a stand-alone demo/POC intended for review and presentation purposes.
