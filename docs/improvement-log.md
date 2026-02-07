# Improvement Log

Use this log after each report to capture repeatable process improvements.

| Date | Area | Observation | Action |
| --- | --- | --- | --- |
| 2026-02-06 | Bootstrap | Initial workflow created with templates, prompts, and DCF model. | Run PEP report and refine assumptions based on gaps. |
| 2026-02-07 | Valuation inputs | Auto-bootstrap assumptions lacked explicit base-year fields and did not persist scenario outputs for auditability. | Standardized `valuation/inputs.yaml` with base-year revenue/net debt/shares and wrote `valuation/outputs.json`; cited both files directly in the report. |
| 2026-02-07 | Valuation methodology | Five-year two-stage DCF compressed durable-advantage economics and could understate long-duration value. | Switched the skill reference to a three-stage DCF (competitive-advantage period, fade, terminal), added CAP/fade quality checks, and re-ran ASML with explicit stage-length assumptions. |
| 2026-02-07 | Evidence quality | Third-party transcript files can include editorial summaries mixed with management remarks. | Prioritize SEC filings for core financial/forecast claims and use transcript files mainly for color commentary with explicit source labeling. |
| 2026-02-07 | Cyclical normalization | Peak-cycle commodity earnings can overstate steady-state cash generation when margins are supply-shock-driven. | For CALM, anchored stage-1 DCF margins below FY2025 peak, cited explicit volatility/customer-risk factors from filings, and documented net-debt/share assumptions in valuation inputs. |
| 2026-02-07 | Quality-of-earnings normalization | Cash flow and net income can be temporarily boosted by large non-cash tax items, distorting steady-state margin assumptions. | For UPWK, tied valuation margins to operating trajectory and macro/GSV signals rather than one-year reported net income, and documented the normalization rationale in valuation notes and report text. |
| 2026-02-07 | Pre-10K coverage | Newly public companies can have strong growth but distorted GAAP margins and incomplete annual normalized exports, which can break comparability. | For FIG, anchored valuation to annualized run-rate revenue plus scenario margins, marked ROIC/leverage as not meaningful where appropriate, and cited 10-Q/S-1 limitations explicitly. |
