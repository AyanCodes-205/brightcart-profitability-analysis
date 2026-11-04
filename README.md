# BrightCart E-Commerce Profitability Analysis

An end-to-end profitability analysis of 2,000 orders from BrightCart, an online retailer selling across eight product categories (January 2024 – January 2026), combined with 24 months of marketing spend (January 2024 – December 2025). The project explores category and channel profitability, the cost of returns, advertising return on ad spend (ROAS), and where a 20% marketing cut should land. Every result is built in pandas, SQL and Excel so the three methods cross-check one another.

**Tools:** Python (pandas, scipy) · SQL (MySQL) · Excel · Statistical Testing


## Analysis Preview

The following previews showcase the key analytical outputs from the BrightCart E-Commerce Profitability Analysis. The analysis is presented through Excel dashboards, summary tables, profitability comparisons, return analysis and marketing performance visualizations.

### 1. Executive Summary
A consolidated overview of BrightCart's overall business performance, highlighting revenue, profit, profit margins, return rates and key business findings.

![Executive Summary](images/executive_summary.png)

### 2. Category Profitability Analysis
Compares revenue, product costs, shipping expenses and profit margins across eight product categories to identify the strongest and weakest performers.

![Category Profitability](images/category_profitability.png)

### 3. Sales Channel Analysis
Evaluates profitability across Website, Mobile App, Marketplace and Social Commerce, including the impact of platform fees on profit per order.

![Channel Analysis](images/channel_analysis.png)

### 4. Returns Analysis
Examines return rates, refunded revenue and the financial impact of returned orders on overall business profitability.

![Returns Analysis](images/returns_analysis.png)

### 5. Marketing Performance & Budget Optimization
Compares advertising ROAS across marketing platforms and demonstrates how a 20% marketing budget reduction can be allocated to minimize potential revenue loss.

![Marketing Analysis](images/marketing_analysis.png)



## Business Questions Answered

- Which product categories are the most and least profitable, and what drives the difference?
- How does profit per order differ across the website, mobile app, marketplace and social commerce, after platform fees?
- What is the return rate by category and channel, and how much revenue is lost to returns?
- Which advertising platform delivers the best ROAS, and is any platform losing money?
- If marketing spend were cut by 20%, which platforms and months should be reduced?

## Key Business Insights

- **Category performance:** Electronics is the most profitable category (26.4% margin) and Books the least (10.0%). Shipping explains about 88% of the gap, while product cost is roughly 40% of revenue in every category.
- **Channel performance:** Mobile App earns the most profit per order ($36.32) and Marketplace the least ($15.40). Average order value is nearly identical across channels, and Marketplace's 13.8% platform fee more than halves its profit per order.
- **Returns:** 7.2% of orders were returned, refunding $20,582 (7.4% of gross revenue). Returns cut the profit margin from 27.7% to 20.3%, removing about 27% of potential profit. Differences in return rate between categories and channels are not statistically significant (chi-square p = 0.83 and 0.68).
- **Marketing return:** TikTok Ads has the best ROAS (24.0x) and Email Marketing the worst (4.8x), which is below the 4.93x break-even implied by the 20.3% profit margin.
- **Budget cut:** Cutting $100.7K (20%) from the lowest-ROAS platform-months puts about $449K of attributed revenue at risk, versus $1.63M for an equal cut. The recommended cut is about 69% of Email's budget, 31% of Facebook's, 17% of Influencer's, 14% of Google's, 13% of Instagram's and 8% of TikTok's.

## Recommendations

1. **Cut marketing selectively:** reduce the weakest platform-months first. Estimated profit effect is +$9.8K, against -$229.5K for an equal 20% cut.
2. **Fix shipping:** it costs 18% of revenue, about 1.4x the catalog's standard rates, and orders under $50 lose money. Add a minimum order or shipping fee and audit carrier rates.
3. **Reprice Marketplace and Social Commerce** to cover their fees, and add a restocking or return-shipping fee.

## Technical Implementation

- **Data validation:** Checked for missing values and duplicates, and reconciled costs. Total costs equal product cost + shipping + platform fee + transaction fee, which corrected a mismatch on every row in the original cost formula.
- **Analysis in pandas:** Used `groupby` aggregations for profitability by category and channel, break-even ROAS, and a ranked platform-month budget cut using cumulative spend.
- **Statistical testing:** Applied chi-square tests to check whether return-rate differences are real or random.
- **SQL:** Rebuilt all results with aggregation, `CASE WHEN`, subqueries, CTEs and window functions (running totals).
- **Excel:** Built category, channel, returns, marketing and cut-plan sheets with `SUMIFS`, `COUNTIFS` and charts, all driven by live formulas.

## Dataset & Files

**Dataset:** Three CSV files (`orders.csv`, `products.csv`, `marketing_spend.csv`). The raw data is not included in this repository.

 Dataset & Files

- [analysis.py](analysis.py) — pandas analysis: validation, categories, channels, returns, marketing and the 20% cut.
- [brightcart_queries.sql](brightcart_queries.sql) — the same analysis in SQL (MySQL 8 compatible).
- [BrightCart_Analysis.xlsx](BrightCart_Analysis.xlsx) — Excel workbook with formulas, summary tables and charts.
- [BrightCart_Executive_Summary.csv](BrightCart_Executive_Summary.csv) — headline answers.

## Notes

- Profit margins are calculated on gross revenue (before discounts and refunds) unless stated otherwise.
- Break-even ROAS is total revenue divided by total profit (4.93x), the ROAS needed for ad spend to pay for itself at the current margin.
- Returned orders are treated as full refunds with product, shipping and fee costs unrecovered, as in the source profit field. Reselling returned stock would reduce the loss.
- Platform-attributed revenue ($8.1M) is 29x the revenue in the orders file, so ROAS is used to rank platforms and dollar figures for the cut are indicative.
- The orders file appears to be a sample, and orders fall sharply in late 2025 while ad spend peaks. Verify this before acting on Q4 figures.

## Author

**Ayan**

[LinkedIn Account](https://www.linkedin.com/in/ayanbasit/)
