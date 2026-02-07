# Improvement Log

Use this log after each report to capture repeatable process improvements.

| Date | Area | Observation | Action |
| --- | --- | --- | --- |
| 2026-02-06 | Bootstrap | Initial workflow created with templates, prompts, and DCF model. | Run PEP report and refine assumptions based on gaps. |
| 2026-02-07 | Valuation inputs | Auto-bootstrap assumptions lacked explicit base-year fields and did not persist scenario outputs for auditability. | Standardized `valuation/inputs.yaml` with base-year revenue/net debt/shares and wrote `valuation/outputs.json`; cited both files directly in the report. |
| 2026-02-07 | Valuation methodology | Five-year two-stage DCF compressed durable-advantage economics and could understate long-duration value. | Switched the skill reference to a three-stage DCF (competitive-advantage period, fade, terminal), added CAP/fade quality checks, and re-ran ASML with explicit stage-length assumptions. |
| 2026-02-07 | Evidence quality | Third-party transcript files can include editorial summaries mixed with management remarks. | Prioritize SEC filings for core financial/forecast claims and use transcript files mainly for color commentary with explicit source labeling. |
