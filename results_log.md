# Results Log — Verified Numbers for CV / Report Use

## Scope
- Campaign dataset: 200,000 campaigns, 5 channels, full year 2021
- Touchpoint dataset: 10,000 touchpoints, 2,847 unique customer journeys, 6 channels

## Headline KPIs (whole dataset, verified in both Python and Power BI DAX)
- Total Spend: $2,500,878,608
- Total Revenue: $15,018,267,282.24
- ROAS: 6.01 (mathematically = 1 + spend-weighted avg ROI, since Revenue was derived from ROI)
- Blended CAC: $284.04
- Conversion Rate: 8.01%

## Attribution Modeling
- Baseline simulated conversion rate (Markov): 83.79%
- Removal effects range: 23.4% (Search Ads) – 26.2% (Display Ads)
- Final attribution range across all 4 models: 14.7% – 18.0% per channel (narrow, converged)
- Chi-square test (Last-Touch vs First-Touch): χ² = 2.03, dof = 5, p = 0.845 (not significant)

## CAC & LTV by Channel (Markov-adjusted)
| Channel | Naive CAC | Markov CAC | LTV | CAC:LTV Ratio | Status |
|---|---|---|---|---|---|
| Direct Traffic | $281.93 | $287.02 | $1,694.67 | 0.169 | Healthy |
| Display Ads | $284.75 | $288.06 | $1,708.81 | 0.169 | Healthy |
| Email | $283.34 | $278.25 | $1,699.61 | 0.164 | Healthy |
| Search Ads | $285.22 | $272.26 | $1,713.55 | 0.159 | Healthy |
| Social Media | $284.51 | $287.84 | $1,708.89 | 0.168 | Healthy |
- Channels flagged CAC ≥ LTV risk: 0 (all Healthy)

## K-Means Segmentation
| Segment | Campaigns | % of Total | Spend | Weighted CAC | vs. Overall |
|---|---|---|---|---|---|
| Inefficient / High-Risk Spend | 17,133 | 8.6% | $245,713,480 | $2,377.44 | 8.4x higher |
| High-Value Engaged Champions | 81,339 | 40.7% | $1,001,362,921 | $267.54 | better |
| Efficient Converters, Low Engagement | 81,429 | 40.7% | $1,003,907,624 | $268.65 | better |
| High-CTR Efficient Spenders | 20,099 | 10.1% | $249,894,583 | $204.54 | best |
- High-risk segment concentration check: none found by channel (8.43-8.65%), location
  (8.39-8.69%), customer_segment (8.37-8.77%), or campaign_type (8.25-8.76%) — risk is
  campaign-level, not systemic.

## A/B Test — Search vs Email
- Search: 1,764,235 / 22,032,144 clicks = 8.0076%
- Email: 1,747,009 / 21,897,902 clicks = 7.9780%
- Z-statistic: 3.6143, P-value: 0.000301 (statistically significant)
- Effect size: 0.03 percentage points (practically negligible given sample size)

## Time-Lag Correlation (spend vs conversions)
- Same-month correlation across channels: r = 0.86 – 0.98 (strong)
- Lag-1/lag-2 correlations unstable, likely artifact of only 12 months of data

## Budget Reallocation Simulator (Display Ads → Direct Traffic)
| Shift % | Shift Amount | Revenue Lift ($) | Revenue Lift (%) |
|---|---|---|---|
| 10% | $41,677,858 | $833,557.16 | 0.0167% |
| 20% | $83,355,716 | $1,667,114.33 | 0.0333% |
| 30% | $125,033,575 | $2,500,671.49 | 0.0500% |
| 50% | $208,389,291 | $4,167,785.82 | 0.0834% |
- Verified matching exactly (to the cent) between Python and live Power BI DAX evaluation.