# Chubb Ltd (CB) Research Report (LLM)

_As of 2026-02-06_

## Executive Summary
- Chubb is a global insurance and reinsurance group headquartered in Zurich, operating across six segments including North America Commercial and Personal P&C, Overseas General, Global Reinsurance, and Life Insurance. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- FY2024 revenue was $55.8b with operating cash flow of $16.2b; FCF margin was ~29.0%. (Source: `companies/CB/data/income_statement_annual.csv`, `companies/CB/data/cash_flow_statement_annual.csv`)
- Revenue grew at ~10.8% CAGR from FY2021–FY2024, but analyst forecasts imply a flatter 2026–2027 revenue path versus FY2024. (Source: `companies/CB/data/income_statement_annual.csv`, `companies/CB/data/analyst_estimates.csv`)
- Capital intensity is low (FCF roughly tracks operating cash flow due to limited capex disclosure), enabling steady shareholder returns, though buybacks are subject to Swiss legal constraints. (Source: `companies/CB/data/cash_flow_statement_annual.csv`, `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- DCF using current assumptions implies ~$206.25/share base case versus a current price of $332.73, resulting in a negative margin of safety. (Source: `companies/CB/model/assumptions.yaml`, `companies/CB/data/company_profile.csv`, `companies/CB/data/balance_sheet_annual.csv`)
- Key risks are catastrophe exposure, reserve estimation error, market/investment volatility, and regulatory/cyber requirements. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

## Business Overview
Chubb Limited is a global insurance and reinsurance organization headquartered in Zurich with operations across North America, overseas markets, reinsurance, and life insurance. The 10-K describes six operating segments—North America Commercial P&C, North America Personal P&C, North America Agricultural, Overseas General, Global Reinsurance, and Life Insurance—with consolidated net premiums earned of $49.8b in 2024. The company also consolidates Huatai Group as of mid‑2023, adding P&C and life exposure in China. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

Chubb distributes most commercial and personal lines through brokers and agents, relying on major intermediaries to originate and place risk. This model emphasizes underwriting discipline, product breadth, and claims service across a global client base, rather than direct-to-consumer scale. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

## Competitive Position
Competition is intense across global P&C and reinsurance markets. The 10-K highlights that financial strength ratings and digital capabilities are critical competitive factors, alongside underwriting expertise, a broad product set, and global distribution. Chubb’s scale and diversification across multiple lines and geographies, combined with claims service and underwriting infrastructure, are its stated differentiators. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

From a financial lens, Chubb’s cash generation is strong (average FCF margin ~26.9% over FY2021–FY2024), supporting balance sheet resilience. However, EBIT and ROIC metrics are not available from the current EDGAR‑derived dataset, limiting quantitative peer comparisons on underwriting profitability. (Source: `companies/CB/data/cash_flow_statement_annual.csv`, `companies/CB/data/income_statement_annual.csv`)

## Financial Quality
Revenue expanded at ~10.8% CAGR from FY2021–FY2024, reaching $55.8b in FY2024. Net income margin averaged ~17.0% over the last four years, indicating healthy profitability for a P&C‑heavy insurer. (Source: `companies/CB/data/income_statement_annual.csv`)

Operating cash flow was $16.2b in FY2024 and has been consistently strong; reported FCF is roughly equal to operating cash flow due to missing capex data in the EDGAR export. This suggests cash conversion is high, but a full earnings‑quality assessment requires complete capex and underwriting margin disclosures. (Source: `companies/CB/data/cash_flow_statement_annual.csv`)

## Capital Allocation
Chubb’s cash generation supports dividends and potential buybacks. The most recent dividend per share is listed at $3.88. Share repurchases are subject to Swiss legal constraints that require periodic shareholder approval for capital reductions or repurchase authorizations. (Source: `companies/CB/data/company_profile.csv`, `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

Net debt was approximately $12.4b based on FY2022 balance sheet data; cash figures for FY2023–FY2024 are missing, so leverage trends should be confirmed directly from the latest statutory disclosures. (Source: `companies/CB/data/balance_sheet_annual.csv`)

## Growth Opportunities
Growth levers include expansion within commercial and specialty P&C lines, overseas general insurance, and life insurance—especially in markets added through Huatai Group. Global distribution and broker relationships enable product cross‑sell across regions and customer segments. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

Analyst revenue forecasts show a modest trajectory into 2026–2027 versus FY2024, implying that sustained growth will likely require a mix of rate, underwriting mix shifts, and expansion in higher‑growth overseas or specialty lines. (Source: `companies/CB/data/analyst_estimates.csv`)

## Key Risks
- Catastrophe exposure (natural disasters, terrorism, cyber events) can drive large loss volatility across commercial, personal, and A&H lines. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- Reserve adequacy is judgment‑driven; adverse development or model error can materially impact earnings and capital. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- Market and macro volatility affects investment returns, reinsurance availability, and demand for coverage. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- Counterparty and reinsurance credit risk can impair recoverables and liquidity under stress scenarios. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)
- Regulatory and cybersecurity requirements increase compliance costs and raise operational risk. (Source: `companies/CB/data/10-K-2025-02-27-0000896159-25-000004.md`)

## Valuation
The DCF model applies the current base/bull/bear assumptions from the model file (negative to low‑single‑digit revenue growth and 12–17% FCF margins). Using FY2024 revenue, market‑implied shares outstanding, and FY2022 net debt, the implied per‑share values are approximately:
- Base: $206.25/share
- Bull: $318.63/share
- Bear: $113.16/share

These values are sensitive to net debt and cash data gaps for FY2023–FY2024, and should be refreshed once balance‑sheet cash and underwriting profitability are fully captured. (Source: `companies/CB/model/assumptions.yaml`, `companies/CB/data/company_profile.csv`, `companies/CB/data/balance_sheet_annual.csv`)

## Margin of Safety
At a current price of $332.73, the base‑case margin of safety is -61.3%, and even the bull case implies -4.4%. Upside requires either stronger growth than analyst forecasts imply or higher sustainable FCF margins than embedded in the current assumptions. (Source: `companies/CB/model/assumptions.yaml`, `companies/CB/data/company_profile.csv`, `companies/CB/data/analyst_estimates.csv`)

## Conclusion
Based on the current model inputs and available data, Chubb appears overvalued versus intrinsic value, with a negative margin of safety even in the bull case. Before making a firm call, the analysis should be upgraded by: (1) fixing missing EBIT and cash line items in the EDGAR export, (2) validating underwriting profitability and combined ratios through statutory disclosures, and (3) reviewing catastrophe exposure and reinsurance protections in recent disclosures.
