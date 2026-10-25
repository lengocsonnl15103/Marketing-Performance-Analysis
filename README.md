# Marketing Campaign Performance & Attribution Analytics

End-to-end marketing analytics project: SQL + Python data pipeline, four-model attribution
comparison (including statistical validation), CAC:LTV analysis, K-Means segmentation, A/B
testing, and a 5-page interactive Power BI dashboard with a native DAX-driven budget simulator.

## Business Problem

Which channels actually drive conversions, what's the true cost of acquiring a customer per
channel, and how should budget be reallocated to improve ROI?

## Key Findings

- **Attribution methodology has minimal practical impact on this dataset**: four independent
  models (Last-Touch, First-Touch, Linear, Markov Chain) converge to a 15–18% credit band per
  channel; confirmed statistically via chi-square test (χ²=2.03, p=0.845).
- **A high-risk campaign segment**, identified via K-Means clustering: 17,133 campaigns (8.6%),
  $245.7M in spend, CAC 8.4x the portfolio average — confirmed _not_ concentrated in any single
  channel, location, or audience (campaign-level driver, not systemic).
- **Search vs. Email A/B test**: statistically significant (p=0.0003) but practically trivial
  (0.03 percentage point gap) — a deliberate example of distinguishing statistical from
  practical significance.
- **Budget reallocation simulator**: validated in both Python and live Power BI DAX (matching
  to the cent) — projects modest 0.02–0.08% revenue lift given near-uniform channel ROI (4.99–5.01).

## Dashboard

5-page interactive Power BI dashboard — see `/screenshots` for page-by-page previews.

1. Executive Summary
2. Channel, Campaign & Geographic Performance
3. Attribution & CAC:LTV
4. Customer Segmentation
5. Budget Simulator & Recommendations (native What-If parameter, DAX-driven)

## Tech Stack

Python (Pandas, NumPy, Scikit-learn, SciPy) · PostgreSQL · SQLAlchemy · Power BI (DAX, star
schema, built via direct MCP integration) · reportlab (PDF reporting)
