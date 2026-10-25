-- ===========================================================
-- QUERY 1: Total spend and conversions by channel
-- Purpose: baseline view — where does money go, what comes back
-- ===========================================================
SELECT
    channel_standardized,
    COUNT(*) AS num_campaigns,
    SUM(spend) AS total_spend,
    SUM(conversions) AS total_conversions,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(roi)::numeric, 2) AS avg_roi
FROM campaigns
GROUP BY channel_standardized
ORDER BY total_spend DESC;


-- ===========================================================
-- QUERY 2: Month-over-month ROI trend using CTE + LAG()
-- Purpose: is ROI improving or declining month to month, per channel
-- LAG() looks at the "previous row" (previous month) without a self-join
-- ===========================================================
WITH monthly_roi AS (
    SELECT
        channel_standardized,
        month,
        ROUND(AVG(roi)::numeric, 2) AS avg_monthly_roi
    FROM campaigns
    GROUP BY channel_standardized, month
)
SELECT
    channel_standardized,
    month,
    avg_monthly_roi,
    LAG(avg_monthly_roi) OVER (
        PARTITION BY channel_standardized ORDER BY month
    ) AS prev_month_roi,
    ROUND(
        avg_monthly_roi - LAG(avg_monthly_roi) OVER (
            PARTITION BY channel_standardized ORDER BY month
        ), 2
    ) AS roi_change
FROM monthly_roi
ORDER BY channel_standardized, month;


-- ===========================================================
-- QUERY 3: Top 10 campaigns per channel by revenue, using RANK()
-- Purpose: identify standout campaigns worth studying/replicating
-- RANK() (not ROW_NUMBER) so ties share the same rank
-- ===========================================================
WITH ranked_campaigns AS (
    SELECT
        campaign_id,
        company,
        channel_standardized,
        revenue,
        roi,
        RANK() OVER (
            PARTITION BY channel_standardized ORDER BY revenue DESC
        ) AS revenue_rank
    FROM campaigns
)
SELECT *
FROM ranked_campaigns
WHERE revenue_rank <= 10
ORDER BY channel_standardized, revenue_rank;


-- ===========================================================
-- QUERY 4: Channels performing below the overall average ROI
-- Purpose: flag underperformers as budget-cut candidates
-- Subquery calculates the benchmark; outer query compares against it
-- ===========================================================
SELECT
    channel_standardized,
    ROUND(AVG(roi)::numeric, 2) AS channel_avg_roi,
    (SELECT ROUND(AVG(roi)::numeric, 2) FROM campaigns) AS overall_avg_roi
FROM campaigns
GROUP BY channel_standardized
HAVING AVG(roi) < (SELECT AVG(roi) FROM campaigns)
ORDER BY channel_avg_roi ASC;


-- ===========================================================
-- QUERY 5: Running total of monthly revenue (window function)
-- Purpose: cumulative revenue growth across the year, company-wide
-- ===========================================================
WITH monthly_revenue AS (
    SELECT
        month,
        SUM(revenue) AS monthly_revenue
    FROM campaigns
    GROUP BY month
)
SELECT
    month,
    monthly_revenue,
    SUM(monthly_revenue) OVER (ORDER BY month) AS running_total_revenue
FROM monthly_revenue
ORDER BY month;