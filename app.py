from __future__ import annotations

import json

import gradio as gr

from triage_engine import triage_defect


def _format_result(jira_link: str, notes: str) -> tuple[str, str, str, str, str, str, str, str]:
    if not jira_link.strip():
        msg = "Please provide a Jira defect link."
        return msg, "", "", "", "[]", "", "", ""

    result = triage_defect(jira_link=jira_link, notes=notes)
    return (
        result["defect_summary"],
        result["predicted_owner_team"],
        result["predicted_subsystem"],
        "\n".join(f"- {cause}" for cause in result["probable_root_causes"]),
        json.dumps(result["similar_historical_defects"], indent=2),
        result["recommended_next_action"],
        result["rca_summary"],
        json.dumps(result, indent=2),
    )


with gr.Blocks(title="AI Defect Triage & RCA Demo") as demo:
    gr.Markdown("# AI Defect Triage & RCA Demo")
    gr.Markdown(
        "Enter a Jira defect link and optional notes to generate triage and RCA insights."
    )

    jira_link = gr.Textbox(label="Jira Defect Link", placeholder="https://jira.example.com/browse/APP-123")
    notes = gr.Textbox(label="Optional Notes", lines=5)

    submit = gr.Button("Analyze Defect")
    defect_summary = gr.Textbox(label="Defect Summary")
    owner_team = gr.Textbox(label="Predicted Owner Team")
    subsystem = gr.Textbox(label="Predicted Subsystem")
    root_causes = gr.Textbox(label="Probable Root Causes", lines=4)
    similar_defects = gr.Code(label="Similar Historical Defects", language="json")
    next_action = gr.Textbox(label="Recommended Next Action", lines=3)
    rca_summary = gr.Textbox(label="RCA Summary", lines=3)
    raw_output = gr.Code(label="Raw Combined Output", language="json")

    submit.click(
        fn=_format_result,
        inputs=[jira_link, notes],
        outputs=[
            defect_summary,
            owner_team,
            subsystem,
            root_causes,
            similar_defects,
            next_action,
            rca_summary,
            raw_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()
