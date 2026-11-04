CREATE DATABASE brightcart;

USE brighcart;

-- 1. Check the load (expect 2000, 2000, 0)
SELECT COUNT(*) AS orders,
       COUNT(DISTINCT order_id) AS distinct_orders,
       SUM(ABS(product_cost + shipping_cost + platform_fee + transaction_fee - total_costs) > 0.015) AS cost_mismatches
FROM orders;

-- 2. Q1: category profitability
SELECT primary_category,
       COUNT(*) AS orders,
       ROUND(SUM(profit), 0) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(gross_revenue), 1) AS margin_pct_gross,
       ROUND(100.0 * SUM(shipping_cost) / SUM(gross_revenue), 1) AS shipping_pct
FROM orders
GROUP BY primary_category
ORDER BY margin_pct_gross DESC;

-- 3. Q2: channel profit per order
SELECT channel,
       COUNT(*) AS orders,
       ROUND(AVG(gross_revenue), 2) AS avg_order_value,
       ROUND(AVG(profit), 2) AS profit_per_order,
       ROUND(AVG(profit + platform_fee), 2) AS profit_before_platform_fee,
       ROUND(100.0 * SUM(CASE WHEN returned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM orders
GROUP BY channel
ORDER BY profit_per_order DESC;

-- 4. Q3: return rate by category
SELECT primary_category,
       COUNT(*) AS orders,
       SUM(CASE WHEN returned = 'Yes' THEN 1 ELSE 0 END) AS returned_orders,
       ROUND(100.0 * SUM(CASE WHEN returned = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM orders
GROUP BY primary_category
ORDER BY return_rate_pct DESC;

-- 5. Q3: revenue lost to returns and profit impact
SELECT ROUND(SUM(refund_amount), 0) AS revenue_lost,
       ROUND(100.0 * SUM(refund_amount) / SUM(gross_revenue), 1) AS pct_of_gross,
       ROUND(SUM(profit), 0) AS actual_profit,
       ROUND(SUM(profit + refund_amount), 0) AS profit_if_no_returns,
       ROUND(100.0 * SUM(refund_amount) / SUM(profit + refund_amount), 1) AS pct_potential_profit_lost
FROM orders;


USE brightcart;

-- Q4: ROAS, CPA, CPC and break-even check by platform
SELECT m.platform,
       ROUND(SUM(m.spend), 0)                               AS spend,
       ROUND(SUM(m.revenue_attributed) / SUM(m.spend), 2)   AS roas,
       ROUND(SUM(m.spend) / SUM(m.conversions), 2)          AS cpa,
       ROUND(SUM(m.spend) / SUM(m.clicks), 3)               AS cpc,
       ROUND(b.breakeven_roas, 2)                           AS breakeven_roas,
       SUM(CASE WHEN m.roas < b.breakeven_roas THEN 1 ELSE 0 END) AS months_below_breakeven,
       SUM(CASE WHEN m.roas < 1 THEN 1 ELSE 0 END)          AS months_below_1
FROM marketing_spend m
CROSS JOIN (SELECT SUM(gross_revenue) / SUM(profit) AS breakeven_roas FROM orders) b
GROUP BY m.platform, b.breakeven_roas
ORDER BY roas DESC;

-- Q5: cut 20% of spend, starting with the lowest-ROAS platform-months
WITH ranked AS (
    SELECT month, platform, spend, revenue_attributed,
           revenue_attributed / spend AS roas,
           SUM(spend) OVER (ORDER BY revenue_attributed / spend, month, platform) AS cum_spend
    FROM marketing_spend
),
target AS (
    SELECT 0.20 * SUM(spend) AS cut_target FROM marketing_spend
),
plan AS (
    SELECT r.*,
           CASE WHEN r.cum_spend <= t.cut_target THEN r.spend
                WHEN r.cum_spend - r.spend < t.cut_target THEN t.cut_target - (r.cum_spend - r.spend)
                ELSE 0 END AS spend_cut
    FROM ranked r CROSS JOIN target t
)
SELECT platform,
       ROUND(SUM(spend_cut), 0)            AS spend_cut,
       ROUND(SUM(spend_cut * roas), 0)     AS attributed_revenue_lost,
       SUM(CASE WHEN spend_cut > 0 THEN 1 ELSE 0 END) AS months_touched
FROM plan
GROUP BY platform
ORDER BY spend_cut DESC;