# LLM Context Pack: CB

As of: 2026-02-06

## Company Profile (companies/<TICKER>/data/company_profile.csv)
```json
{
  "symbol": "CB",
  "price": 331.89,
  "marketCap": 129800000000.00002,
  "beta": 0.49,
  "lastDividend": 3.88,
  "range": "263.14 - 335.34",
  "change": NaN,
  "changePercentage": NaN,
  "volume": 523531.0,
  "companyName": "Chubb Ltd",
  "currency": "USD",
  "cik": 896159,
  "isin": "CH0044328745",
  "cusip": "H1467J104",
  "exchangeFullName": "New York Stock Exchange",
  "exchange": "NYSE",
  "industry": "Insurance - Property & Casualty",
  "website": "https://chubb.com",
  "ceo": "Evan Greenberg",
  "sector": "Financials",
  "country": "Switzerland",
  "fullTimeEmployees": 43000,
  "phone": "41 43 456 76 00",
  "address": "Barengasse 32",
  "city": "Zurich, Switzerland Ch-8001",
  "state": NaN,
  "zip": NaN,
  "ipoDate": NaN,
  "isEtf": false,
  "isActivelyTrading": true,
  "isAdr": false
}
```

## Key Metrics (computed)
```json
{
  "latest_year": 2024,
  "latest_revenue": 55753000000.0,
  "latest_ebit": 11455000000.0,
  "latest_fcf": 16182000000.0,
  "latest_net_debt": 11830000000.0,
  "avg_revenue_growth": 0.10357988742126537,
  "avg_ebit_margin": 0.17632589619948005,
  "avg_fcf_margin": 0.2557046781787926,
  "avg_roic": 0.09293702336805303,
  "avg_reinvestment_rate": NaN,
  "avg_leverage": 1.808472025053227
}
```

## Financial Summary Table (last 4 years)
| Fiscal Year | Revenue ($m) | EBIT ($m) | EBIT Margin | FCF ($m) | FCF Margin | Net Debt ($m) | ROIC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 40963.0 | 9816.0 | 24.0% | 11149.0 | 27.2% | 13510.0 | 11.7% |
| 2022 | 43166.0 | 6568.0 | 15.2% | 11243.0 | 26.0% | 12390.0 | 8.4% |
| 2023 | 49735.0 | 9526.0 | 19.2% | 12632.0 | 25.4% | 10414.0 | 12.2% |
| 2024 | 55753.0 | 11455.0 | 20.5% | 16182.0 | 29.0% | 11830.0 | 12.0% |

## Model Assumptions (assumptions.yaml)
```yaml
forecast_years: 5
notes: Auto-generated using analyst revenue forecasts (StockAnalysis) for FY2027 (CAGR
  from FY2024 over 3 years) and recent financial averages. Review and adjust before
  making decisions.
scenarios:
  base:
    revenue_growth: -0.011815559308003931
    fcf_margin: 0.15
    discount_rate: 0.1
    terminal_growth: 0.02
  bull:
    revenue_growth: 0.0050385726818780174
    fcf_margin: 0.16999999999999998
    discount_rate: 0.09
    terminal_growth: 0.025
  bear:
    revenue_growth: -0.04017315428379453
    fcf_margin: 0.12
    discount_rate: 0.11
    terminal_growth: 0.015
```

## Valuation Outputs
```json
{
  "inputs": {
    "latest_revenue": 55753000000.0,
    "net_debt": 11830000000.0,
    "shares_outstanding": 391093434.5716955,
    "current_price": 331.89
  },
  "scenarios": {
    "base": {
      "enterprise_value": 93052362271.14702,
      "equity_value": 81222362271.14702,
      "per_share_value": 207.68019887650985,
      "margin_of_safety": -0.598082059798813,
      "assumptions": {
        "revenue_growth": -0.011815559308003931,
        "fcf_margin": 0.15,
        "discount_rate": 0.1,
        "terminal_growth": 0.02
      }
    },
    "bull": {
      "enterprise_value": 137006209169.09726,
      "equity_value": 125176209169.09726,
      "per_share_value": 320.067273198241,
      "margin_of_safety": -0.03693825577236159,
      "assumptions": {
        "revenue_growth": 0.0050385726818780174,
        "fcf_margin": 0.16999999999999998,
        "discount_rate": 0.09,
        "terminal_growth": 0.025
      }
    },
    "bear": {
      "enterprise_value": 56645837147.060814,
      "equity_value": 44815837147.060814,
      "per_share_value": 114.5911262768722,
      "margin_of_safety": -1.8962975649449128,
      "assumptions": {
        "revenue_growth": -0.04017315428379453,
        "fcf_margin": 0.12,
        "discount_rate": 0.11,
        "terminal_growth": 0.015
      }
    }
  },
  "valuation_table": "| Scenario | Implied Value/Share | Margin of Safety |\n| --- | --- | --- |\n| Base | $207.68 | -59.8% |\n| Bull | $320.07 | -3.7% |\n| Bear | $114.59 | -189.6% |"
}
```

## Analyst Revenue Forecasts (analyst_estimates.csv)
```csv
metric,fiscalYear,high,avg,low,source,retrieved
revenue,2026,54000000000.0,51400000000.0,47600000000.0,https://stockanalysis.com/stocks/cb/forecast/,2026-02-06
revenue,2027,56600000000.0,53800000000.0,49300000000.0,https://stockanalysis.com/stocks/cb/forecast/,2026-02-06

```

Source: https://stockanalysis.com/stocks/cb/forecast/

## 10-K Business Section (10-K-2025-02-27-0000896159-25-000004.md)
Chubb Limited is the Swiss-incorporated holding company of the Chubb Group of Companies. Chubb Limited, which is headquartered in Zurich, Switzerland, and its direct and indirect subsidiaries (collectively, the Chubb Group of Companies, Chubb, we, us, or our) are a global insurance and reinsurance organization, serving the needs of a diverse group of clients worldwide. At December 31, 2024, we had total assets of $247 billion and total Chubb shareholders’ equity, which excludes noncontrolling interests, of $64 billion. Chubb was incorporated in 1985 at which time it opened its first business office in Bermuda and continues to maintain operations in Bermuda. We have grown our business through increased premium volume, expansio n of product offerings and geographic reach, and the acquisition of other companies, to become a global property and casualty (P&C) leader. We expanded our personal accident and supplemental health (A&H), and life insurance business with the acquisition of Cigna's business in several Asian markets in 2022. We further advanced our goal of greater product, customer, and geographical diversification with incremental purchases that led to a controlling majority interest in Huatai Insurance Group Co. Ltd (Huatai Group), a Chinese financial services holding company with separate P&C, life, and asset management subsidiaries (collectively, Huatai) on July 1, 2023. At December 31, 2024, our ownership interest in Huatai Group was approximately 85.5 percent. Refer to Note 2 to the Consolidated Financial Statements for additional information on our acquisitions.

With operations in 54 countries and territories, Chubb provides commercial and consumer P&C insurance, A&H, reinsurance, and life insurance to a diverse group of clients. We provide commercial insurance products and service offerings such as risk management programs, loss control, and engineering and complex claims management. We provide specialized insurance products ranging from Directors & Officers (D&O) and financial lines to various specialty-casualty and umbrella and excess casualty lines to niche areas such as aviation and energy. We also offer consumer lines insurance coverage including homeowners, automobile, valuables, umbrella liability, and recreational marine products. In addition, we supply A&H and life insurance to individuals in select countries.

We serve multinational corporations, mid-size and small businesses with property and casualty insurance and risk engineering services; affluent and high net worth individuals with substantial assets to protect; individuals purchasing life, personal accident, supplemental health, homeowners, automobile in certain international markets and for high net worth individuals in the U.S., and specialty personal insurance coverage; companies and affinity groups providing or offering accident and health insurance programs and life insurance to their employees or members; and insurers managing exposures with reinsurance coverage.

We make available free of charge through our website (investors.chubb.com, under Financials) our annual report on Form 10-K, quarterly reports on Form 10-Q, current reports on Form 8-K, and amendments to those reports, if any, filed or furnished pursuant to Section 13(a) or 15(d) of the Exchange Act as soon as reasonably practicable after they have been electronically filed with or furnished to the U.S. Securities and Exchange Commission (SEC). Also available through our website (under Investor Relations / Corporate Governance) are our Corporate Governance Guidelines, Code of Conduct, and Charters for the Committees of the Board of Directors (the Board). Printed documents are available by contacting our Investor Relations Department (Telephone: +1 (212) 827-4445, E-mail: investorrelations@chubb.com).

We also use our website as a means of disclosing material, non-public information and for complying with our disclosure obligations under SEC Regulation FD (Fair Disclosure). Accordingly, investors should monitor the Investor Relations portion of our website, in addition to following our press releases, SEC filings, and public conference calls and webcasts. The information contained on, or that may be accessed through, our website is not incorporated by reference into, and is not a part of, this report. The SEC maintains an Internet site (www.sec.gov) that contains reports, proxy and information statements, and other information regarding issuers that file with the SEC.

For most commercial and personal lines of business we offer, insureds typically use the services of an insurance broker or agent. An insurance broker acts as an agent for the insureds, offering advice on the types and amount of insurance to purchase, and assists in the negotiation of price and terms and conditions. We obtain business from the local and major international insurance brokers and typically pay a commission to brokers for any business accepted and bound. Loss of all or a substantial portion of the business provided by one or more of these brokers could have a material adverse effect on our business. In our

opinion, no material part of our business is dependent upon a single insured or group of insureds. We do not believe that the loss of any one insured would have a material adverse effect on our financial condition or results of operations.

Competition in the insurance and reinsurance marketplace is substantial. We compete on an international and regional basis with major U.S., Bermuda, European, and other international insurers and reinsurers and with underwriting syndicates, some of which have greater financial, technological, marketing, distribution and management resources than we do. In addition, capital market participants have created alternative products that are intended to compete with reinsurance products. We also compete with new companies and existing companies that move into the insurance and reinsurance markets. Competitors include other stock companies, mutual companies, alternative risk sharing groups (such as group captives and catastrophe pools), and other underwriting organizations. Competitors sell through various distribution channels and business models, across a broad array of product lines, and with a high level of variation regarding geographic, marketing, and customer segmentation. We compete for business not only on the basis of price but also on the basis of availability of coverage desired by customers and quality of service. We also compete in China for assets under management (AUM) with investment management firms, banks, and other financial institutions that offer products that are similar to those offered by Huatai's asset management companies.

The insurance industry is changing rapidly. Our ability to compete is dependent on a number of factors, particularly our ability to maintain the appropriate financial strength ratings as assigned by independent rating agencies and effectively using digital capabilities, including the growth of new digital-based distribution models, in an everchanging competitive landscape and incorporating, among other things, climate and environmental changes into our insurance processes, products, and services. Our broad market capabilities in personal, commercial, specialty, and A&H lines made available by our underwriting expertise, business infrastructure, and global presence, help define our competitive advantage. Our superior claims service is a significant asset to our business, our business partners and customers, and is unique in the industry. Our strong balance sheet is attractive to businesses, and our strong capital position and global platform affords us opportunities for growth not available to smaller, less diversified insurance companies. Refer to “Segment Information” for competitive environment by segment.

## 10-K Risk Factors Section (10-K-2025-02-27-0000896159-25-000004.md)
Factors that could have a material impact on our results of operations or financial condition are outlined below. Additional risks not presently known to us or that we currently deem insignificant may also impair our business or results of operations as they become known or as facts and circumstances change. Any of the risks described below could result in a material adverse effect on our results of operations or financial condition.

Our results of operations or financial condition could be adversely affected by the occurrence of natural and man-made disasters.

We have substantial exposure to losses resulting from natural disasters, man-made catastrophes, such as terrorism or cyber-attack, and other catastrophic events. This could impact a variety of our businesses, including our commercial and personal lines, and life and accident and health (A&H) products. Catastrophes can be caused by various events, including hurricanes, typhoons, earthquakes, hailstorms, droughts, explosions, severe winter weather, fires, war, acts of terrorism, nuclear accidents, political instability, and other natural or man-made disasters, including a global or other wide-impact pandemic or a significant cyber-attack. The incidence and severity of catastrophes are inherently unpredictable and our losses from catastrophes could be substantial. In addition, climate change and resulting changes in global temperatures, weather patterns, and sea levels may both increase the frequency and severity of natural catastrophes and the resulting losses in the future and impact our risk modeling assumptions. We cannot predict the impact that changing climate conditions, if any, may have on our results of operations or our financial condition. We cannot predict how legal, regulatory or social responses to concerns around global climate change and the resulting impact on various sectors of the economy may impact our business. In addition, exposure to cyber risk is increasing systematically due to greater digital dependence, which may increase possible losses due to a catastrophic cyber event. Cyber catastrophic scenarios are not bound by time or geographic limitations and cyber catastrophic perils do not have well-established definitions or fundamental physical properties. Rather, cyber risks are engineered by human actors and thus are continuously evolving, often in ways that are engineered specifically to evade established loss mitigation controls. The occurrence of claims from catastrophic events could result in substantial volatility in our results of operations or financial condition for any fiscal quarter or year. Although we attempt to manage our exposure to such events through the use of underwriting controls, risk models, and the purchase of third-party reinsurance, catastrophic events are inherently unpredictable and the actual nature of such events, when they occur, could be more frequent or severe than contemplated in our pricing and risk management expectations. As a result, the occurrence of one or more catastrophic events could have an adverse effect on our results of operations and financial condition.

If actual claims exceed our loss reserves, our financial results could be adversely affected.

Our results of operations and financial condition depend upon our ability to accurately assess the potential losses associated with the risks that we insure and reinsure. We establish reserves for unpaid losses and loss expenses, which are estimates of future payments of reported and unreported claims for losses and related expenses, with respect to insured events that have occurred at or prior to the balance sheet date. The process of establishing reserves can be highly complex and is subject to considerable variability as it requires the use of informed estimates and judgments.

Actuarial staff in each of our segments regularly evaluates the levels of loss reserves. Such evaluations could result in future changes in estimates of losses or reinsurance recoverables and would be reflected in our results of operations in the period in which the estimates are changed. Losses and loss expenses are charged to income as incurred. During the loss settlement period, which can be many years in duration for some of our lines of business, additional facts regarding individual claims and trends often will become known, which may result in a change in overall reserves. In addition, application of statistical and actuarial methods may require the adjustment of overall reserves upward or downward from time to time.

We include in our loss reserves liabilities for latent claims, such as asbestos and environmental (A&E), which are principally related to claims arising from remediation costs associated with hazardous waste sites and bodily-injury claims related to exposure to asbestos products and environmental hazards. At December 31, 2024, gross A&E liabilities represented approximately 1.6 percent of our gross loss reserves. The estimation of these liabilities is subject to many complex variables including: the current legal environment; specific settlements that may be used as precedents to settle future claims; assumptions regarding trends with respect to claim severity and the frequency of higher severity claims; assumptions regarding the ability to allocate liability among defendants (including bankruptcy trusts) and other insurers; the ability of a claimant to bring a claim in a state in which it has no residency or exposure; the ability of a policyholder to claim the right to non-products coverage; whether high-level excess policies have the potential to be accessed given the policyholder's claim trends and liability situation; payments to unimpaired claimants; and the potential liability of peripheral defendants. Accordingly, the ultimate settlement of losses, arising from either latent or non-latent causes, may be significantly greater or less than the loss and loss

expense reserves held at the balance sheet date. In addition, the amount and timing of the settlement of our P&C liabilities are uncertain and our actual payments could be higher than contemplated in our loss reserves owing to the impacts of insurance, judicial decisions, and social inflation. If our loss reserves are determined to be inadequate, we may be required to increase loss reserves at the time of the determination and our net income and capital may be reduced.

The effects of emerging claim and coverage issues on our business are uncertain.

As industry practices and legislative, regulatory, judicial, social, financial, technological and other environmental conditions change, unexpected and unintended issues related to claims and coverage may emerge. These issues may adversely affect our business by either extending coverage beyond our underwriting intent or by increasing the frequency and severity of claims. For example, "reviver" legislation in certain states allows civil claims relating to molestation to be asserted against policyholders that would otherwise be barred by statutes of limitations. As a result, the full extent of liability under our insurance or reinsurance contracts may not be known for many years after issuance.

The failure of any of the loss limitation methods we use could have an adverse effect on our results of operations and financial condition.

## 10-K MD&A Section (10-K-2025-02-27-0000896159-25-000004.md)
The following is a discussion of our financial condition and results of operations for the years ended December 31, 2024 and 2023, and comparisons between 2024 and 2023. This discussion should be read in conjunction with the Consolidated Financial Statements and related Notes, under Item 8 of this Form 10-K. Comparisons between 2023 and 2022 have been omitted from this Form 10-K, but can be found in "Management's Discussion and Analysis of Financial Condition and Results of Operations" in Part II, Item 7 of our Form 10-K for the year ended December 31, 2023.

All comparisons in this discussion are to the prior year unless otherwise indicated. All dollar amounts are rounded. However, percent changes and ratios are calculated using whole dollars. Accordingly, calculations using rounded dollars may differ.

| MD&A Index                                                               |     |    | Page | | Forward-Looking Statements                                               |     | 40 |      | | Overview                                                                 |     | 41 |      | | Critical Accounting Estimates                                            |     | 42 |      | | Consolidated Operating Results                                           |     | 52 |      | | Segment Operating Results                                                |     | 56 |      | | Effective Income Tax Rate                                                |     | 64 |      | | Net Realized and Unrealized Gains (Losses)                               |     | 65 |      | | Non-GAAP Reconciliation                                                  |     | 66 |      | | Net Investment Income                                                    |     | 70 |      | | Interest Expense                                                         |     | 70 |      | | Amortization of Purchased Intangibles and Other Amortization             |     | 71 |      | | Investments                                                              |     | 72 |      | | Asbestos and Environmental (A&E)                                         |     | 76 |      | | Catastrophe Management                                                   |     | 77 |      | | Global PropertyCatastrophe Reinsurance Program                           |     | 79 |      | | Political Risk and Credit Insurance                                      |     | 79 |      | | Crop Insurance                                                           |     | 80 |      | | Liquidity                                                                |     | 81 |      | | Capital Resources                                                        |     | 84 |      | | Ratings                                                                  |     | 86 |      | | Information provided in connection with outstanding debt of subsidiaries |     | 87 |      | | Credit Facilities                                                        |     | 88 |      |

The Private Securities Litigation Reform Act of 1995 provides a “safe harbor” for forward-looking statements. Any written or oral statements made by us or on our behalf may include forward-looking statements that reflect our current views with respect to future events and financial performance. These forward-looking statements are subject to certain risks, uncertainties, and other factors that could, should potential events occur, cause actual results to differ materially from such statements. These risks, uncertainties, and other factors, which are described in more detail elsewhere herein and in other documents we file with the SEC, include but are not limited to:

• actual amount of new and renewal business, premium rates, underwriting margins, market acceptance of our products, and risks associated with the introduction of new products and services and entering new markets; the competitive environment in which we operate, including trends in pricing or in policy terms and conditions, which may differ from our projections, and changes in market conditions that could render our business strategies ineffective or obsolete;

• losses arising out of natural or man-made catastrophes; actual loss experience from insured or reinsured events and the timing of claim payments; the uncertainties of the loss-reserving and claims-settlement processes, including the difficulties associated with assessing environmental damage and asbestos-related latent injuries, the impact of aggregate-policy-coverage limits, the impact of bankruptcy protection sought by various asbestos producers and other related businesses, and the timing of loss payments;

• changes in the distribution or placement of risks due to increased consolidation of insurance and reinsurance brokers; material differences between actual and expected assessments for guaranty funds and mandatory pooling arrangements; the ability to collect reinsurance recoverable, credit developments of reinsurers, and any delays with respect thereto and changes in the cost, quality, or availability of reinsurance;

• uncertainties relating to governmental, legislative and regulatory policies, developments, actions, investigations, and treaties; judicial decisions and rulings, new theories of liability, legal tactics, and settlement terms; the effects of data privacy or cyber laws or regulation; global political conditions and possible business disruption or economic contraction that may result from such events;

• the impact of changes in tax laws, guidance and interpretations, such as the implementation of the Organization for Economic Cooperation and Development international tax framework, or the increasing number of challenges from tax authorities in the current global tax environment;

• severity of pandemics and related risks, and their effects on our business operations and claims activity, and any adverse impact to our insureds, brokers, agents, and employees; actual claims may exceed our best estimate of ultimate insurance losses incurred which could change including as a result of, among other things, the impact of legislative or regulatory actions taken in response to a pandemic;

• developments in global financial markets, including changes in interest rates, stock markets, and other financial markets; increased government involvement or intervention in the financial services industry; the cost and availability of financing, and foreign currency exchange rate fluctuations; changing rates of inflation; and other general economic and business conditions, including the depth and duration of potential recession;

• the availability of borrowings and letters of credit under our credit facilities; the adequacy of collateral supporting funded high deductible programs; and the amount of dividends received from subsidiaries;

• changes to our assessment as to whether it is more likely than not that we will be required to sell, or have the intent to sell, available-for-sale fixed maturity investments before their anticipated recovery;

• actions that rating agencies may take from time to time, such as financial strength or credit ratings downgrades or placing these ratings on credit watch negative or the equivalent;

• the effects of public company bankruptcies and accounting restatements, as well as disclosures by and investigations of public companies relating to possible accounting irregularities, and other corporate governance issues;

• acquisitions made performing differently than expected, our failure to realize anticipated expense-related efficiencies or growth from acquisitions, the impact of acquisitions on our pre-existing organization, and risks and uncertainties relating to our planned purchases of additional interests in Huatai Insurance Group Co., Ltd;

• risks associated with being a Swiss corporation, including reduced flexibility with respect to certain aspects of capital management and the potential for additional regulatory burdens; share repurchase plans and share cancellations;