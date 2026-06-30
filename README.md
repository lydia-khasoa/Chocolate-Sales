# 🍫 Chocolate Sales Analysis — SQL Portfolio Project

A SQL-driven analysis of a global chocolate distribution dataset, uncovering revenue drivers, sales rep performance, product profitability, and seasonal trends across six countries.

![SQL](https://img.shields.io/badge/SQL-PostgreSQL-blue) ![Status](https://img.shields.io/badge/status-complete-brightgreen) ![Rows](https://img.shields.io/badge/records-3%2C282-orange)

---

## 📌 Project Overview

This project analyzes transactional sales data for a chocolate distributor operating across **🇬🇧 UK, 🇺🇸 USA, 🇮🇳 India, 🇦🇺 Australia, 🇨🇦 Canada,** and **🇳🇿 New Zealand**. The goal: turn raw transaction-level data into decision-ready KPIs a sales or operations leader could act on.

| | |
|---|---|
| 📅 **Time period** | Jan 2022 – Aug 2024 |
| 🧾 **Records** | 3,282 transactions |
| 🌍 **Markets** | 6 countries |
| 🍬 **Products** | 22 SKUs |
| 🧑‍💼 **Sales reps** | 25 |
| 💰 **Total revenue** | ~$19.79M |
| 📦 **Total boxes shipped** | ~540,437 |

---

## 🗂️ Repository Structure

```
chocolate-sales-analysis/
│
├── chocolate_sales_clean.csv        # Cleaned dataset (currency & date formatted)
├── chocolate_sales_analysis.sql     # All KPI & analytical SQL queries
└── README.md                        # This file
```

---

## 🧹 Data Cleaning

Raw data required light transformation before analysis:

- 💵 `Amount` converted from text currency (`"$5,320.00"`) → numeric `DECIMAL(12,2)`
- 📆 `Date` parsed from `DD/MM/YYYY` string → proper `DATE` type
- ✅ No duplicate transactions or missing values found in the source file

---

## 📊 Key Insights & KPIs

### 1️⃣ Revenue Performance
- 🏆 **Australia** leads all markets at **$3.65M** in revenue, narrowly ahead of the UK ($3.37M) and India ($3.34M) — the top 3 markets are within ~9% of each other, showing a well-balanced international footprint rather than dependence on a single region.
- 📦 **Smooth Silky Salty**, **50% Dark Bites**, and **White Choc** are the top 3 products by revenue, each generating over $1M — useful for prioritizing inventory and marketing spend.

### 2️⃣ Sales Rep Performance
- 📈 A rep leaderboard (ranked via `RANK()`) surfaces top and bottom performers by total revenue and average deal size — critical for incentive design and coaching priorities.
- ⚖️ Benchmarking each rep's revenue against the **company-wide average** (via window functions) flags reps significantly over- or under-performing peers.

### 3️⃣ Product Profitability
- 💎 Calculating **revenue per box shipped** (rather than raw revenue) separates *high-margin, low-volume* products from *high-volume, low-margin* ones — a more actionable view for pricing and promotion strategy than revenue alone.
- 🥇 `NTILE(4)` buckets products into revenue quartiles, instantly flagging the bottom-quartile SKUs that may be candidates for discontinuation.

### 4️⃣ Time-Series Trends
- 📉📈 Month-over-month growth rates (via `LAG()`) reveal seasonal demand swings — useful for production planning and staffing.
- 🌊 A **3-month rolling average** smooths short-term noise to expose the underlying growth trend across the 2022–2024 window.

### 5️⃣ Market-Specific Bestsellers
- 🗺️ A per-country "best-selling product" query (using `RANK() PARTITION BY country`) shows that consumer preference is **not uniform** — different markets favor different SKUs, which should inform localized merchandising.

### 6️⃣ Shipping & Operational Efficiency
- 🚚 Boxes-per-order and revenue-per-box by country highlight which markets ship efficiently (low cost-to-serve) versus those needing logistics optimization.

---

## 🛠️ SQL Techniques Demonstrated

| Technique | Used For |
|---|---|
| `GROUP BY` + aggregates | Core revenue/orders/boxes summaries |
| `RANK()` | Leaderboards (reps, countries, products) |
| `NTILE(4)` | Quartile segmentation of product performance |
| `LAG()` | Month-over-month growth calculations |
| `Window AVG() OVER()` | Rolling 3-month averages & rep vs. company benchmarking |
| `PARTITION BY` | Best-seller-per-country breakdown |
| `CTE (WITH)` | Multi-step monthly trend & ranking logic |
| `CREATE VIEW` | Reusable BI layer for dashboard/Excel hookup |

---

## 💡 Business Recommendations

1. **Double down on Australia, UK, and India** — the three markets driving over half of total revenue.
2. **Re-evaluate bottom-quartile SKUs** for pricing, bundling, or discontinuation.
3. **Localize product promotion** per country's top-selling SKU rather than a one-size-fits-all catalog push.
4. **Use rep benchmarking** to design targeted coaching for under-performing reps and replicate top performers' approach.
5. **Smooth seasonal swings** in production/staffing using the rolling average trend.

---

## 👩‍💻 About This Project

Built as part of a growing **data analytics portfolio** demonstrating SQL proficiency (CTEs, window functions, ranking, and reusable views) applied to real-world business questions — bridging analytical engineering rigor with practical, decision-ready insight.

📫 Connect with me: [Portfolio](https://sites.google.com/view/lydiawafula) | LinkedIn | GitHub

---
⭐ *If you found this project useful, consider giving the repo a star!*
