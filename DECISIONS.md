# Project Decisions & Assumptions Log

## Data Sourcing
- Combined two Kaggle datasets: campaign-level spend data (no customer IDs)
  and touchpoint-level journey data (no spend data). Joined only at channel
  level -- realistic scenario, mirrors how marketing spend data and web
  analytics data live in separate systems in real companies.
- Dataset 1 (campaign_clean.csv): 200,000 rows, 5 channels, full year 2021.
- Dataset 2 (touchpoints_clean.csv): 10,000 touchpoint rows, 2,847 unique
  users, 6 channels, spans only 2 days (Feb 10-11, 2025) -- too short a
  window for time-based journey analysis, but sufficient for attribution
  modeling since that needs journeys, not time depth.

## Channel Mapping (documented assumption)
- Facebook + Instagram -> Social Media
- YouTube -> Display Ads
- Google Ads -> Search Ads
- Website -> Direct Traffic
- Email -> Email
- Referral: no paid-spend equivalent in campaign dataset, left unmapped
  (exists only in touchpoint/attribution data, not in campaign_with_segments)
- WHY: the two datasets used different channel taxonomies; this mapping
  groups conceptually similar channels for consistent cross-dataset analysis.

## Revenue Estimation
- Campaign dataset had ROI but no Revenue column.
- Used: Revenue = Spend * (1 + ROI)
- WHY: standard ROI formula rearranged; documented since every downstream
  KPI (CAC, ROAS, LTV) depends on this assumption.
- Confirmed via Power BI DAX that ROAS is mathematically equivalent to
  1 + spend-weighted average ROI as a direct consequence of this formula --
  not an independent metric, since Revenue was constructed from ROI.

## Customer Journey Construction
- Discovered 'converted' flag was inconsistent per user (67.6% of users had
  mixed Yes/No across their touchpoints) -- meaning it's a per-touch flag,
  not a per-user flag as first assumed.
- FIX: truncated each journey at the FIRST conversion touchpoint; touches
  after that point are dropped (they can't have caused a conversion that
  already happened).
- Result: average path length dropped from 3.51 -> 1.7 touches/journey.
- Final conversion rate: 83.63% (high vs real-world funnels -- see Data
  Quality note below).

## Data Quality / Synthetic Data Caveat
- Campaign ROI distribution (min 2.0, max 8.0, mean ~5.0, tight std) looks
  synthetically generated, not organic.
- Touchpoint "where customers go after Start" was nearly uniform
  (15.8%-17.3% across all 6 channels) -- real customer journeys usually
  show clearer channel-role patterns (some channels open journeys,
  others close them).
- CONSEQUENCE: all 4 attribution models converged to a narrow 15-18% band
  per channel; CAC:LTV ratios came out uniformly "Healthy" across every
  channel; budget reallocation simulator showed minimal upside (0.02-0.08%)
  since channel ROI is nearly identical (4.99-5.01). These are legitimate,
  honestly-reported findings, not analysis failures.

## Attribution Modeling
- Last-touch: 100% credit to final channel before conversion
- First-touch: 100% credit to first channel in the journey
- Linear: equal credit split across every channel in the journey
- Markov chain (removal effect): simulate 20,000 random journeys through
  a transition-probability map; remove each channel one at a time; the
  % drop in conversion rate becomes that channel's attributed credit.
  Baseline conversion rate: 83.79%. Removal effects ranged 23.4%-26.2%.
- All 4 models' final credit range: 14.7%-18.0% per channel -- narrow,
  consistent with the uniform underlying transition data.

## Chi-Square Test: Attribution Model Agreement
- Chi-square test of homogeneity comparing Last-Touch vs First-Touch channel-
  credit distributions (6 channels, real integer counts, not percentages).
- Chi2 = 2.03, dof = 5, p = 0.845 -- NOT statistically significant.
- Statistically confirms the qualitative observation from attribution
  modeling: all 4 models converge to a narrow band, consistent with the
  dataset's near-uniform channel transition probabilities. Ties together
  every "flat/synthetic" finding across the project into one coherent,
  statistically grounded conclusion.

## CAC Calculation Fix (Python)
- Initial approach mixed touchpoint-dataset conversions (2,847 users, 2
  days) directly with campaign-dataset spend (200K campaigns, full year)
  -> produced meaningless CAC in the millions due to scale mismatch
  between datasets.
- FIX: kept spend/conversions in campaign dataset's native scale; used the
  Markov vs last-touch percentage ratio only as a relative adjustment
  factor applied to campaign-scale conversions. Preserves the attribution
  *signal* without importing the touchpoint dataset's tiny sample size.
- Referral has no CAC (no paid campaign spend maps to it -- organic channel).

## CAC:LTV Analysis
- CAC:LTV ratio calculated as cac_markov_adjusted / ltv per channel.
- Risk thresholds: >=0.5 High Risk, >=0.33 Watch, else Healthy (LTV >=3x CAC).
- Result: all 5 channels came out "Healthy" (ratios 0.159-0.169, i.e. ~6:1
  LTV:CAC) -- consistent with the dataset's low cross-channel variance.
  No channel is genuinely at risk in this dataset.
- Later added CAC (Naive) as a comparison measure alongside CAC (Markov-
  Adjusted) in Power BI -- real differences are small (-4.5% to +1.8% per
  channel), demonstrating methodology rather than revealing a dramatic swing.

## K-Means Customer Segmentation
- Features used: conversion_rate, roi, ctr, engagement_score, cac (all
  numeric, standardized via StandardScaler before clustering).
- Elbow method showed no sharp bend (smooth, gradual decline) -- consistent
  with homogeneous/synthetic underlying data. Chose k=4 for business
  interpretability, not because of a clear mathematical elbow.
- Segments identified and named:
  1. Inefficient / High-Risk Spend -- 17,133 campaigns (8.6%), $245.7M
     spend, weighted CAC $2,377.44 (8.4x the $284.04 portfolio average).
     Lowest conversion rate and CTR of any segment.
  2. Efficient Converters, Low Engagement -- 81,429 campaigns, decent
     conversion, lowest engagement score.
  3. High-Value Engaged Champions -- 81,339 campaigns, best all-around
     (high conversion, highest engagement, low CAC).
  4. High-CTR Efficient Spenders -- 20,099 campaigns, standout CTR (0.46
     vs 0.07-0.11 elsewhere), lowest CAC of all segments.
- NOTE: the $2,377.44 weighted CAC (SUM(spend)/SUM(conversions)) differs
  from an earlier-reported $3,007.69, which was a simple/naive AVERAGE of
  the per-row cac column -- exactly the "averaging a ratio" mistake this
  project otherwise avoids. The $2,377.44 figure is the mathematically
  correct one and is what's used everywhere downstream (CV, dashboard).

## Segmentation Concentration Deep-Dive
- Checked whether the high-risk segment concentrates in any channel,
  location, customer_segment, or campaign_type.
- Result: NO concentration found in any dimension -- all four checked
  within 0.2-0.5 percentage points of the 8.6% overall rate.
- CONCLUSION: risk is driven by individual campaign-level performance
  (low CTR + high CAC), not a systemic channel/market/audience issue.
  Recommendation reframed accordingly: per-campaign monitoring thresholds
  instead of blanket channel or market budget cuts.

## A/B Test: Search vs Email Conversion Rate
- Two-proportion z-test: p = 0.0003 (statistically significant).
- BUT effect size is tiny: 8.0076% vs 7.9780% (0.03 percentage point gap).
- Large sample size (22M+ clicks/group) makes even trivial differences
  statistically detectable. Recommendation: do NOT reallocate budget on
  this result alone -- statistical significance without meaningful effect
  size shouldn't drive business decisions.
- This A/B test and the attribution modeling are separate, parallel
  analyses on the same dataset -- not a sequential/dependent pipeline.
  The z-test does not "validate" the attribution models; they measure
  unrelated things (campaign-variant conversion rates vs. channel credit).

## Time-Lag Effect
- Cross-correlated monthly channel spend against conversions at lag 0, 1,
  and 2 months.
- Result: strong same-month correlation across all channels (r=0.86-0.98).
  Lag-1 correlations were unstable, some strongly negative (e.g. Social
  Media -0.727) -- likely an artifact of only having 12 months of data,
  not a genuine delayed-effect signal. No reliable evidence of "slow-burn"
  channels in this dataset.

## Budget Reallocation Simulator
- Bug found and fixed: initial version compared actual summed revenue
  (old) against formula-reconstructed revenue (new) -- an apples-to-oranges
  mismatch that produced a false negative lift. Fixed by using the same
  Spend*(1+ROI) formula on both sides of the comparison.
- Result: shifting budget from Display Ads (ROI 4.99) to Direct Traffic
  (ROI 5.01) projects only 0.02-0.08% revenue lift even at 50% shift --
  expected, given how close ROI is across all channels in this dataset.
- Framed explicitly as an estimate: assumes constant ROI as spend scales,
  ignoring real-world diminishing returns.

## Power BI Modeling (via direct MCP integration)
- Fixed attribution_comparison table: Column1 (unlabeled index from pandas
  export) renamed to channel_standardized; verified exact spelling/casing
  match against campaign_with_segments before creating the relationship;
  confirmed direction via real row counts (6 rows = one per channel,
  dimension-style table) rather than assuming.
- Removed duplicate auto-generated date tables (Power BI's Auto Date/Time
  had created two separate hidden calendars); built one proper shared
  Date table via DAX CALENDAR(), marked as the official model date table.
- A later leftover DateTableTemplate_ object (Auto Date/Time's internal
  template, persists while the Desktop setting stays on) was found and
  deleted directly via the modeling tool; the Desktop-level "Auto
  date/time" option itself still needs manual disabling in File Options
  since no modeling tool can toggle that application setting.
- All ratio/rate measures (CAC, ROAS, Conversion Rate) recomputed from
  underlying SUMs rather than averaging pre-existing per-row ratio columns
  -- averaging a ratio across rows of different sizes is mathematically
  wrong and would misstate blended figures under any filter/slicer.
- CAC (Naive) added as a comparison measure alongside CAC (Markov-Adjusted)
  per interview-value suggestion -- shows methodology (naive vs. adjusted)
  rather than a dramatic swing, since real differences are small.
- Native What-If Parameter built for the budget simulator (GENERATESERIES-
  based calculated table + SELECTEDVALUE-driven DAX measures) rather than
  importing static Python scenario output -- genuinely live/interactive,
  not a CSV import.
- Found and fixed a ~2% discrepancy between the DAX budget simulator and
  the Python-validated figures: Python's simulate_reallocation() used
  ROUNDED avg_roi (5.01/4.99, rounded to 2 decimals) as displayed, while
  initial DAX used full-precision averages. Since the lift calculation is
  a difference of two very large, very close numbers, this small rounding
  difference got amplified into a real percentage-level gap. Fixed by
  applying ROUND(...,2) to ROI in DAX, matching Python exactly to the cent
  at every tested shift level (10%/20%/30%/50%).
- All measures verified via explicit Get calls confirming state="Ready"
  (not just assumed from successful Create calls), plus live DAX
  evaluation of actual values -- compiling clean is not the same as
  returning correct values, as demonstrated by the CAC scale-mismatch and
  ROI-rounding bugs above.

## Dashboard Structure
- Originally planned as 6 pages; consolidated to 5 to avoid redundancy
  (merged Geographic/Device performance into Channel/Campaign page since
  no device column existed; split Attribution+CAC:LTV+Segmentation across
  two pages once segmentation was identified as the strongest, most
  quotable finding and given its own dedicated page).
- Page 3 (Attribution & CAC:LTV) deliberately has no Date/Channel slicer
  rail: attribution_comparison and cac_ltv_analysis are static, Python-
  precomputed per-channel tables connected via one-directional
  relationships (dimension -> fact only). A fact-side slicer cannot filter
  them, and forcing bidirectional filtering would misleadingly imply these
  values recalculate live for a filtered subset, which they do not.