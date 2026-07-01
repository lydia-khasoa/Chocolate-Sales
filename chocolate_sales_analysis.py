"""
================================================================
  CHOCOLATE SALES ANALYSIS — Python Visualization Script
  Author  : Lydia Wafula
  Dataset : 3,282 transactions | 6 countries | 22 products
            25 sales reps | Jan 2022 – Aug 2024
  Output  : 8 publication-ready PNG charts
================================================================
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

# ── Output folder ─────────────────────────────────────────────
OUTPUT_DIR = "charts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Colour palette ────────────────────────────────────────────
PALETTE      = ["#4B2E2A", "#7B4F3E", "#B07D6A", "#D4A98A", "#E8CDB5", "#F5EBE0"]
ACCENT       = "#4B2E2A"   # deep cocoa
HIGHLIGHT    = "#B07D6A"   # warm caramel
LIGHT_BG     = "#FDF6F0"   # cream
GRID_COLOR   = "#E8D9CC"

def apply_style(ax, title, xlabel="", ylabel=""):
    """Shared axis styling helper."""
    ax.set_facecolor(LIGHT_BG)
    ax.set_title(title, fontsize=13, fontweight="bold", color=ACCENT, pad=12)
    ax.set_xlabel(xlabel, fontsize=10, color="#555")
    ax.set_ylabel(ylabel, fontsize=10, color="#555")
    ax.tick_params(colors="#555", labelsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color(GRID_COLOR)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)


# ════════════════════════════════════════════════════════════
#  1. LOAD & CLEAN DATA
# ════════════════════════════════════════════════════════════
print("📦 Loading data...")
df = pd.read_csv("Chocolate_Sales__2_.csv")
df["Amount"]  = df["Amount"].replace(r"[\$,]", "", regex=True).astype(float)
df["Date"]    = pd.to_datetime(df["Date"], format="%d/%m/%Y")
df["Month"]   = df["Date"].dt.to_period("M")
df["Year"]    = df["Date"].dt.year
df["YearMonth"] = df["Date"].dt.to_period("M").dt.to_timestamp()
df["Revenue_per_Box"] = (df["Amount"] / df["Boxes Shipped"]).round(2)

print(f"   ✓ {len(df):,} records loaded | {df['Date'].min().date()} → {df['Date'].max().date()}\n")


# ════════════════════════════════════════════════════════════
#  2. KPI CALCULATIONS
# ════════════════════════════════════════════════════════════
total_revenue   = df["Amount"].sum()
total_orders    = len(df)
total_boxes     = df["Boxes Shipped"].sum()
avg_order_value = df["Amount"].mean()
rev_per_box     = total_revenue / total_boxes

# Country
country_rev  = df.groupby("Country")["Amount"].sum().sort_values(ascending=False)
country_ord  = df.groupby("Country")["Amount"].count().reindex(country_rev.index)

# Product
product_rev  = df.groupby("Product")["Amount"].sum().sort_values(ascending=False)
product_eff  = df.groupby("Product").apply(
    lambda g: g["Amount"].sum() / g["Boxes Shipped"].sum()
).sort_values(ascending=False)
product_ntile = product_rev.rank(pct=True).apply(
    lambda x: "Q1 – Top" if x >= 0.75 else ("Q2" if x >= 0.50 else ("Q3" if x >= 0.25 else "Q4 – Bottom"))
)

# Sales reps
rep_rev  = df.groupby("Sales Person")["Amount"].sum().sort_values(ascending=False)
rep_mean = rep_rev.mean()

# Monthly
monthly = df.groupby("YearMonth").agg(Revenue=("Amount","sum"), Orders=("Amount","count")).reset_index()
monthly["Rolling3"] = monthly["Revenue"].rolling(3, min_periods=1).mean()
monthly["MoM_Growth"] = monthly["Revenue"].pct_change() * 100

# Country best-sellers
best_by_country = (
    df.groupby(["Country","Product"])["Amount"].sum()
    .reset_index()
    .sort_values("Amount", ascending=False)
    .drop_duplicates("Country")
    .set_index("Country")
)

# Heatmap: country × product
heatmap_data = df.groupby(["Country","Product"])["Amount"].sum().unstack(fill_value=0)

print("📊 KPIs computed. Generating charts...\n")


# ════════════════════════════════════════════════════════════
#  CHART 1 — TOP-LINE KPI SUMMARY CARD
# ════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 5, figsize=(16, 3.2))
fig.patch.set_facecolor(LIGHT_BG)
kpis = [
    ("Total Revenue",     f"${total_revenue/1e6:.2f}M"),
    ("Total Orders",      f"{total_orders:,}"),
    ("Boxes Shipped",     f"{total_boxes:,}"),
    ("Avg Order Value",   f"${avg_order_value:,.0f}"),
    ("Revenue / Box",     f"${rev_per_box:.2f}"),
]
for ax, (label, value) in zip(axes, kpis):
    ax.set_facecolor(ACCENT)
    ax.axis("off")
    ax.text(0.5, 0.60, value, ha="center", va="center",
            fontsize=22, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.25, label, ha="center", va="center",
            fontsize=10, color="#D4A98A", transform=ax.transAxes)
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.suptitle("🍫  Chocolate Sales — Top-Line KPIs  (Jan 2022 – Aug 2024)",
             fontsize=14, fontweight="bold", color=ACCENT, y=1.04)
plt.tight_layout(pad=1.2)
fig.savefig(f"{OUTPUT_DIR}/01_kpi_summary.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 1  — KPI Summary Card")


# ════════════════════════════════════════════════════════════
#  CHART 2 — REVENUE BY COUNTRY (bar + share donut)
# ════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor(LIGHT_BG)

bars = ax1.barh(country_rev.index[::-1], country_rev.values[::-1],
                color=PALETTE[:len(country_rev)], edgecolor="white", height=0.6)
for bar, val in zip(bars, country_rev.values[::-1]):
    ax1.text(bar.get_width() + 20000, bar.get_y() + bar.get_height()/2,
             f"${val/1e6:.2f}M", va="center", fontsize=9, color=ACCENT)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M"))
apply_style(ax1, "Revenue by Country", "Total Revenue", "Country")
ax1.grid(axis="x", color=GRID_COLOR, linewidth=0.7, linestyle="--")
ax1.grid(axis="y", visible=False)

wedges, texts, autotexts = ax2.pie(
    country_rev.values, labels=country_rev.index,
    colors=PALETTE[:len(country_rev)], autopct="%1.1f%%",
    startangle=140, pctdistance=0.8,
    wedgeprops=dict(width=0.55, edgecolor="white", linewidth=1.5)
)
for t in autotexts:
    t.set_fontsize(8)
    t.set_color("white")
ax2.set_title("Revenue Share by Country", fontsize=13, fontweight="bold",
              color=ACCENT, pad=12)
ax2.set_facecolor(LIGHT_BG)

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/02_revenue_by_country.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 2  — Revenue by Country")


# ════════════════════════════════════════════════════════════
#  CHART 3 — TOP & BOTTOM 10 PRODUCTS BY REVENUE
# ════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.patch.set_facecolor(LIGHT_BG)

top10    = product_rev.head(10)
bottom10 = product_rev.tail(10)

ax1.barh(top10.index[::-1], top10.values[::-1],
         color=ACCENT, edgecolor="white", height=0.65)
for i, (idx, val) in enumerate(zip(top10.index[::-1], top10.values[::-1])):
    ax1.text(val + 5000, i, f"${val:,.0f}", va="center", fontsize=8, color=ACCENT)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
apply_style(ax1, "Top 10 Products by Revenue", "Revenue (USD)", "Product")
ax1.grid(axis="x", color=GRID_COLOR, linewidth=0.7, linestyle="--")
ax1.grid(axis="y", visible=False)

ax2.barh(bottom10.index[::-1], bottom10.values[::-1],
         color=HIGHLIGHT, edgecolor="white", height=0.65)
for i, (idx, val) in enumerate(zip(bottom10.index[::-1], bottom10.values[::-1])):
    ax2.text(val + 3000, i, f"${val:,.0f}", va="center", fontsize=8, color=ACCENT)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
apply_style(ax2, "Bottom 10 Products by Revenue", "Revenue (USD)", "")

plt.suptitle("Product Revenue Performance", fontsize=14, fontweight="bold",
             color=ACCENT, y=1.01)
plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/03_product_revenue.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 3  — Product Revenue (Top & Bottom 10)")


# ════════════════════════════════════════════════════════════
#  CHART 4 — REVENUE PER BOX (Product Efficiency)
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(LIGHT_BG)

top_eff = product_eff.head(15)
colors  = [ACCENT if v >= product_eff.median() else HIGHLIGHT for v in top_eff.values]
bars = ax.barh(top_eff.index[::-1], top_eff.values[::-1],
               color=colors[::-1], edgecolor="white", height=0.65)
ax.axvline(product_eff.median(), color=HIGHLIGHT, linestyle="--",
           linewidth=1.5, label=f"Median ${product_eff.median():.2f}")
for bar, val in zip(bars, top_eff.values[::-1]):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"${val:.2f}", va="center", fontsize=9, color=ACCENT)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
apply_style(ax, "Revenue per Box Shipped — Product Efficiency",
            "Revenue per Box (USD)", "Product")
ax.grid(axis="x", color=GRID_COLOR, linewidth=0.7, linestyle="--")
ax.grid(axis="y", visible=False)
ax.legend(fontsize=9)

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/04_revenue_per_box.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 4  — Revenue per Box (Product Efficiency)")


# ════════════════════════════════════════════════════════════
#  CHART 5 — SALES REP LEADERBOARD + BENCHMARK LINE
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 8))
fig.patch.set_facecolor(LIGHT_BG)

colors = [ACCENT if v >= rep_mean else HIGHLIGHT for v in rep_rev.values]
bars = ax.barh(rep_rev.index[::-1], rep_rev.values[::-1],
               color=colors[::-1], edgecolor="white", height=0.65)
ax.axvline(rep_mean, color="#D4A98A", linestyle="--", linewidth=2,
           label=f"Company Avg ${rep_mean:,.0f}")
for bar, val in zip(bars, rep_rev.values[::-1]):
    ax.text(bar.get_width() + 3000, bar.get_y() + bar.get_height()/2,
            f"${val/1e3:.0f}K", va="center", fontsize=8, color=ACCENT)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
apply_style(ax, "Sales Rep Leaderboard — Total Revenue vs Company Average",
            "Total Revenue (USD)", "Sales Person")
ax.grid(axis="x", color=GRID_COLOR, linewidth=0.7, linestyle="--")
ax.grid(axis="y", visible=False)
ax.legend(fontsize=9, loc="lower right")

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/05_sales_rep_leaderboard.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 5  — Sales Rep Leaderboard")


# ════════════════════════════════════════════════════════════
#  CHART 6 — MONTHLY REVENUE TREND + 3-MONTH ROLLING AVG
# ════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
fig.patch.set_facecolor(LIGHT_BG)

# Revenue bars
ax1.bar(monthly["YearMonth"], monthly["Revenue"], width=25,
        color=HIGHLIGHT, alpha=0.75, label="Monthly Revenue", zorder=2)
ax1.plot(monthly["YearMonth"], monthly["Rolling3"], color=ACCENT,
         linewidth=2.5, marker="o", markersize=4, label="3-Month Rolling Avg", zorder=3)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e3:.0f}K"))
apply_style(ax1, "Monthly Revenue Trend with 3-Month Rolling Average",
            "", "Revenue (USD)")
ax1.legend(fontsize=9)

# MoM growth
colors_mom = [ACCENT if v >= 0 else "#C0392B" for v in monthly["MoM_Growth"].fillna(0)]
ax2.bar(monthly["YearMonth"], monthly["MoM_Growth"].fillna(0),
        width=25, color=colors_mom, alpha=0.85)
ax2.axhline(0, color=ACCENT, linewidth=1, linestyle="-")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
apply_style(ax2, "Month-over-Month Revenue Growth (%)",
            "Month", "MoM Growth (%)")
ax2.set_facecolor(LIGHT_BG)

import matplotlib.dates as mdates
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
plt.xticks(fontsize=8)

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/06_monthly_trend.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 6  — Monthly Revenue Trend & MoM Growth")


# ════════════════════════════════════════════════════════════
#  CHART 7 — COUNTRY × PRODUCT REVENUE HEATMAP
# ════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(16, 5))
fig.patch.set_facecolor(LIGHT_BG)

sns.heatmap(
    heatmap_data / 1e3,
    ax=ax,
    cmap=sns.light_palette(ACCENT, as_cmap=True),
    linewidths=0.5,
    linecolor="white",
    annot=True,
    fmt=".0f",
    annot_kws={"size": 7.5},
    cbar_kws={"label": "Revenue ($K)"}
)
ax.set_title("Country × Product Revenue Heatmap  (USD '000s)",
             fontsize=13, fontweight="bold", color=ACCENT, pad=12)
ax.set_xlabel("Product", fontsize=10, color="#555")
ax.set_ylabel("Country", fontsize=10, color="#555")
ax.tick_params(axis="x", rotation=45, labelsize=8)
ax.tick_params(axis="y", rotation=0, labelsize=9)

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/07_heatmap_country_product.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 7  — Country × Product Heatmap")


# ════════════════════════════════════════════════════════════
#  CHART 8 — YEARLY REVENUE COMPARISON (grouped bar)
# ════════════════════════════════════════════════════════════
yearly_country = (
    df.groupby(["Year","Country"])["Amount"]
    .sum()
    .reset_index()
    .pivot(index="Country", columns="Year", values="Amount")
)

fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor(LIGHT_BG)

x     = range(len(yearly_country.index))
years = yearly_country.columns.tolist()
width = 0.25
offsets = [-width, 0, width] if len(years) == 3 else [i*width for i in range(len(years))]
bar_colors = [ACCENT, HIGHLIGHT, "#D4A98A"]

for i, (year, offset, color) in enumerate(zip(years, offsets, bar_colors)):
    vals = yearly_country[year].values
    bars = ax.bar([xi + offset for xi in x], vals, width=width*0.9,
                  label=str(year), color=color, edgecolor="white")

ax.set_xticks(x)
ax.set_xticklabels(yearly_country.index, fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
apply_style(ax, "Annual Revenue by Country (Year-over-Year)", "Country", "Revenue (USD)")
ax.legend(title="Year", fontsize=9)

plt.tight_layout()
fig.savefig(f"{OUTPUT_DIR}/08_yearly_country_comparison.png", dpi=150, bbox_inches="tight",
            facecolor=LIGHT_BG)
plt.close()
print("   ✓ Chart 8  — Yearly Revenue by Country\n")


# ════════════════════════════════════════════════════════════
#  DONE
# ════════════════════════════════════════════════════════════
print("=" * 55)
print(f"  ✅  All 8 charts saved to → ./{OUTPUT_DIR}/")
print("=" * 55)
print()
print("📁  Files generated:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    size = os.path.getsize(f"{OUTPUT_DIR}/{f}") // 1024
    print(f"    {f}  ({size} KB)")
