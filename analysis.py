import pandas as pd

orders   = pd.read_csv("orders.csv", parse_dates=["order_date"])
products = pd.read_csv("products.csv")
mkt      = pd.read_csv("marketing_spend.csv")

print(orders.shape, products.shape, mkt.shape)


tol = 0.015
brief = orders.product_cost + orders.shipping_cost + orders.platform_fee
print((brief - orders.total_costs).abs().gt(tol).sum())                           # 2000
print((brief + orders.transaction_fee - orders.total_costs).abs().gt(tol).sum())  # 0


# ================= STEP 2: CATEGORY PROFITABILITY =================

# Part 1: helper column (1 = order was returned, 0 = not returned)
orders["returned_flag"] = (orders.returned == "Yes").astype(int)

# Part 2: profit table by category
cat = orders.groupby("primary_category").agg(
    orders=("order_id", "count"),
    gross_revenue=("gross_revenue", "sum"),
    net_revenue=("net_revenue", "sum"),
    total_costs=("total_costs", "sum"),
    profit=("profit", "sum"),
    return_rate=("returned_flag", "mean"),
)
cat["margin_gross"] = cat.profit / cat.gross_revenue
cat["margin_net"] = cat.profit / cat.net_revenue
cat = cat.sort_values("margin_gross", ascending=False)
print(cat.round(3))

print("Most profitable:", cat.index[0], f"{cat.margin_gross.iloc[0]:.1%}")
print("Least profitable:", cat.index[-1], f"{cat.margin_gross.iloc[-1]:.1%}")

# Part 3: what drives the differences (each cost as % of gross revenue)
cols = ["gross_revenue", "discount_amount", "refund_amount", "product_cost",
        "shipping_cost", "platform_fee", "transaction_fee"]
sums = orders.groupby("primary_category")[cols].sum()

pct = sums.div(sums.gross_revenue, axis=0).drop(columns="gross_revenue")
pct["profit"] = cat.margin_gross
pct = pct.loc[cat.index]
print(pct.round(3))

# Sanity check: every row should add up to 1.0 (100% of revenue)
print(pct.sum(axis=1).round(6))

# Compare the worst category against the best
best, worst = cat.index[0], cat.index[-1]
gap = (pct.loc[worst] - pct.loc[best]).round(3)
print(gap)
print("Shipping share of gap:", round(gap.shipping_cost / -gap.profit, 2))



# ================= STEP 3: CHANNEL ANALYSIS =================

# Part 1: main channel table
ch = orders.groupby("channel").agg(
    orders=("order_id", "count"),
    gross_revenue=("gross_revenue", "sum"),
    refunds=("refund_amount", "sum"),
    platform_fees=("platform_fee", "sum"),
    total_costs=("total_costs", "sum"),
    profit=("profit", "sum"),
    return_rate=("returned_flag", "mean"),
)
ch["avg_order_value"] = ch.gross_revenue / ch.orders
ch["profit_per_order"] = ch.profit / ch.orders
ch["margin_gross"] = ch.profit / ch.gross_revenue
ch = ch.sort_values("profit_per_order", ascending=False)
print(ch.round(3))

print("Best:", ch.index[0], round(ch.profit_per_order.iloc[0], 2))
print("Worst:", ch.index[-1], round(ch.profit_per_order.iloc[-1], 2))

# Part 2: how much do platform fees matter?
ch["platform_fee_per_order"] = ch.platform_fees / ch.orders
ch["platform_fee_pct_gross"] = ch.platform_fees / ch.gross_revenue
ch["profit_per_order_before_fee"] = (ch.profit + ch.platform_fees) / ch.orders
print(ch[["profit_per_order", "platform_fee_per_order",
          "profit_per_order_before_fee", "platform_fee_pct_gross"]].round(3))

# Part 3: where does an average order's money go, by channel?
per_order = orders.groupby("channel")[["gross_revenue", "discount_amount", "refund_amount",
            "product_cost", "shipping_cost", "platform_fee", "transaction_fee", "profit"]].mean()
print(per_order.loc[ch.index].round(2))

# Part 4: category x channel (profit per order, and how many orders each cell has)
heat = orders.pivot_table(index="primary_category", columns="channel",
                          values="profit", aggfunc="mean")
print(heat.round(2))

counts = orders.pivot_table(index="primary_category", columns="channel",
                            values="order_id", aggfunc="count")
print(counts)




# ================= STEP 4: RETURNS =================
from scipy.stats import chi2_contingency

# Part 1: return rates
print("Overall return rate:", round(orders.returned_flag.mean(), 3))
print("Returned orders:", orders.returned_flag.sum(), "of", len(orders))

by_cat = orders.groupby("primary_category").agg(
    orders=("order_id", "count"),
    returned_orders=("returned_flag", "sum"),
    return_rate=("returned_flag", "mean"),
    refunds=("refund_amount", "sum"),
).sort_values("return_rate", ascending=False)
print(by_cat.round(3))

by_ch = orders.groupby("channel").agg(
    orders=("order_id", "count"),
    returned_orders=("returned_flag", "sum"),
    return_rate=("returned_flag", "mean"),
    refunds=("refund_amount", "sum"),
).sort_values("return_rate", ascending=False)
print(by_ch.round(3))

# Part 2: category x channel grid (return rate in %)
rate_grid = orders.pivot_table(index="primary_category", columns="channel",
                               values="returned_flag", aggfunc="mean")
print((rate_grid * 100).round(1))

# Part 3: revenue lost to returns
gross = orders.gross_revenue.sum()
discounts = orders.discount_amount.sum()
refunds = orders.refund_amount.sum()
print("Revenue lost to returns:", round(refunds))
print("  as % of gross revenue:", round(refunds / gross * 100, 1))
print("  as % of revenue after discounts:", round(refunds / (gross - discounts) * 100, 1))

# Part 4: profit impact
profit = orders.profit.sum()
profit_no_returns = profit + refunds
print("Actual profit:", round(profit), "| margin:", round(profit / gross * 100, 1))
print("Profit with no returns:", round(profit_no_returns), "| margin:", round(profit_no_returns / gross * 100, 1))
print("Share of potential profit lost:", round(refunds / profit_no_returns * 100, 1))

# Part 5: costs already spent on returned orders
returned = orders[orders.returned_flag == 1]
print("Product cost on returned orders:", round(returned.product_cost.sum()))
print("Shipping on returned orders:", round(returned.shipping_cost.sum()))
print("Fees on returned orders:", round((returned.platform_fee + returned.transaction_fee).sum()))
print("Profit on returned orders:", round(returned.profit.sum()))

# Part 6: are the differences real or chance?
for col in ["primary_category", "channel"]:
    table = pd.crosstab(orders[col], orders.returned_flag)
    chi2, p, dof, expected = chi2_contingency(table)
    print(col, "p-value:", round(p, 2))


    # ================= STEP 5: MARKETING ROI =================

# Part 1: platform scorecard
plat = mkt.groupby("platform").agg(
   spend=("spend", "sum"),
    impressions=("impressions", "sum"),
    clicks=("clicks", "sum"),
    conversions=("conversions", "sum"),
    revenue=("revenue_attributed", "sum"),
)
plat["roas"] = plat.revenue / plat.spend
plat["cpa"] = plat.spend / plat.conversions
plat["cpc"] = plat.spend / plat.clicks
plat["ctr"] = plat.clicks / plat.impressions
plat["conv_rate"] = plat.conversions / plat.clicks
plat["share_of_spend"] = plat.spend / plat.spend.sum()
plat = plat.sort_values("roas", ascending=False)
print(plat.round(3))

print("Total spend:", round(mkt.spend.sum()))
print("Overall ROAS:", round(mkt.revenue_attributed.sum() / mkt.spend.sum(), 2))

# Part 2: break-even ROAS
margin = orders.profit.sum() / orders.gross_revenue.sum()
breakeven = 1 / margin
print("Blended margin:", round(margin, 3), "| break-even ROAS:", round(breakeven, 2))

# Part 3: platform vs break-even
plat["roas_vs_breakeven"] = plat.roas / breakeven
plat["profitable"] = plat.roas > breakeven
print(plat[["roas", "roas_vs_breakeven", "profitable"]].round(2))

# Part 4: month-by-month consistency
mkt["below_1"] = mkt.roas < 1
mkt["below_breakeven"] = mkt.roas < breakeven
months = mkt.groupby("platform").agg(
    months=("month", "count"),
    months_below_1=("below_1", "sum"),
    months_below_breakeven=("below_breakeven", "sum"),
    min_roas=("roas", "min"),
    median_roas=("roas", "median"),
    max_roas=("roas", "max"),
).loc[plat.index]
print(months.round(2))
print(mkt[mkt.below_1][["month", "platform", "spend", "revenue_attributed", "roas"]])

# Part 5: reality check against the orders file
print("Marketing attributed revenue:", round(mkt.revenue_attributed.sum()))
print("Orders gross revenue:", round(orders.gross_revenue.sum()))
print("Ratio:", round(mkt.revenue_attributed.sum() / orders.gross_revenue.sum(), 1))
print("Spend vs order gross revenue:", round(mkt.spend.sum() / orders.gross_revenue.sum(), 2))

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)



# ================= STEP 6: CUT 20% OF MARKETING SPEND =================

# Part 1: the target
margin = orders.profit.sum() / orders.gross_revenue.sum()
total_spend = mkt.spend.sum()
target = 0.20 * total_spend
print("Total spend:", round(total_spend), "| amount to cut:", round(target))

# Part 2: rank platform-months by ROAS and decide how much to cut from each
plan = mkt.sort_values(["roas", "month"]).reset_index(drop=True)
plan["cum_spend"] = plan.spend.cumsum()
plan["spend_cut"] = (target - (plan.cum_spend - plan.spend)).clip(lower=0, upper=plan.spend)
plan["revenue_lost"] = plan.spend_cut * plan.roas

cut = plan[plan.spend_cut > 0]
print("Platform-months touched:", len(cut), "| fully cut:", (cut.spend_cut == cut.spend).sum())
print("Spend cut:", round(cut.spend_cut.sum()))
print(cut[["month", "platform", "spend", "roas", "spend_cut"]].head(15).round(2))

# Part 3: summary by platform
by_platform = cut.groupby("platform").agg(
    months_touched=("month", "count"),
    spend_cut=("spend_cut", "sum"),
    revenue_lost=("revenue_lost", "sum"),
)
by_platform["platform_budget"] = mkt.groupby("platform").spend.sum()
by_platform["pct_of_budget_cut"] = by_platform.spend_cut / by_platform.platform_budget
by_platform = by_platform.sort_values("spend_cut", ascending=False)
print(by_platform.round(2))

# Part 4: targeted cut vs equal cut
lost_targeted = cut.revenue_lost.sum()
lost_equal = 0.20 * mkt.revenue_attributed.sum()
print("Revenue lost, targeted cut:", round(lost_targeted))
print("Revenue lost, equal 20% cut:", round(lost_equal))
print("ROAS of dollars cut:", round(lost_targeted / target, 1))
print("ROAS of budget kept:", round((mkt.revenue_attributed.sum() - lost_targeted) / (total_spend - target), 1))
print("Profit effect, targeted:", round(target - lost_targeted * margin))
print("Profit effect, equal cut:", round(target - lost_equal * margin))

# Part 5: which months?
by_month = cut.groupby("month").spend_cut.sum().sort_values(ascending=False)
print(by_month.head(8).round(0))
print(by_month.round(0).sort_index().to_string())