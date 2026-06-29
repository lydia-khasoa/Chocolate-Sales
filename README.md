# 🍫 Chocolate Sales Analysis — SQL Portfolio

> Comprehensive SQL query portfolio analyzing chocolate sales data across 6 countries, 22 products & 23 salespersons. Covers revenue KPIs, product efficiency, salesperson rankings, trend analysis, Pareto classification & shipping insights. Built for PostgreSQL.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Dataset Summary](#-dataset-summary)
- [Database Schema](#-database-schema)
- [Query Sections](#-query-sections)
- [Key KPIs Covered](#-key-kpis-covered)
- [Key Insights from the Data](#-key-insights-from-the-data)
- [How to Use](#-how-to-use)
- [Tools & Compatibility](#-tools--compatibility)
- [Author](#-author)

---

## 📋 Project Overview

This project is part of my **Data Analytics Portfolio** and demonstrates practical SQL skills applied to a real-world chocolate sales dataset. The goal is to extract meaningful business intelligence that can inform stakeholder decisions — covering everything from top-line revenue summaries to granular salesperson and product-level performance.

The queries are structured as a portfolio file, progressing from basic aggregations through to advanced window functions, CTEs, and cross-tabulations — mimicking how a data analyst would approach a full sales analysis brief.

---

## 📊 Dataset Summary

| Attribute | Detail |
|---|---|
| **Period covered** | January – August 2022 |
| **Total transactions** | 49 |
| **Total revenue** | $267,428 |
| **Countries** | UK, USA, Australia, India, Canada, New Zealand |
| **Products** | 22 chocolate product lines |
| **Salespersons** | 23 |
| **Total boxes shipped** | 8,082 |
| **Average order value** | $5,458 |

---

## 🗂️ Database Schema

```sql
CREATE TABLE sales (
    sale_id       SERIAL PRIMARY KEY,
    first_name    VARCHAR(50),
    last_name     VARCHAR(50),
    country       VARCHAR(50),
    product       VARCHAR(100),
    sale_date     DATE,
    amount        NUMERIC(12, 2),
    boxes_shipped INT
);
```

> **Note:** The `salesperson` field is derived at query time using `CONCAT(first_name, ' ', last_name)` rather than stored as a separate column.

---

## 🗃️ Query Sections

The portfolio is organized into **8 sections** covering **25 queries**:

```
chocolate_sales_analysis.sql
│
├── Section 0 — Table Setup (DDL)
├── Section 1 — Overview KPIs
├── Section 2 — Revenue by Country
├── Section 3 — Product Performance
├── Section 4 — Salesperson Performance
├── Section 5 — Monthly Revenue Trend
├── Section 6 — Revenue per Box (Efficiency)
├── Section 7 — Shipping Method Analysis
└── Section 8 — Advanced / Combined Insights
```

### Section details

| # | Section | Queries | Highlights |
|---|---|---|---|
| 0 | Table Setup | 1 | DDL — schema creation |
| 1 | Overview KPIs | 2 | Executive snapshot, High/Low sale value classification |
| 2 | Revenue by Country | 2 | Market share %, concentration risk flag |
| 3 | Product Performance | 5 | Top/bottom products, efficiency ranking, market breadth |
| 4 | Salesperson Performance | 4 | Leaderboard, performance gap ratio, above/below average flag |
| 5 | Monthly Trend | 3 | MoM change with `LAG()`, anomaly detection |
| 6 | Revenue per Box | 2 | Efficiency quartiles with `NTILE(4)` |
| 7 | Shipping Method | 2 | Method classification, country breakdown |
| 8 | Advanced Insights | 4 | Pareto 80/20, pivot table, best rep/product per country, BI-ready detail view |

---

## 📈 Key KPIs Covered

- **Total Revenue & Growth** — monthly and cumulative
- **Average Order Value (AOV)** — overall and by segment
- **Revenue per Box Shipped** — product logistics efficiency
- **Market Share %** — by country and product
- **High vs Low Sale Value Classification** — transaction quality split
- **Month-over-Month (MoM) Change** — trend direction and magnitude
- **Salesperson Revenue Ranking** — individual contribution and team variance
- **Performance Gap Ratio** — top vs bottom salesperson
- **Pareto 80/20 Analysis** — which products drive 80% of revenue
- **Shipping Method Distribution** — logistics mode breakdown

---

## 💡 Key Insights from the Data

Here are the standout findings surfaced by the queries:

| Flag | Insight |
|---|---|
| 🔴 Concentration Risk | UK + USA = **45.6%** of total revenue — over-reliance on two markets |
| 🟡 Revenue Anomaly | March revenue collapsed to **$9,786** (only 3 transactions) vs $57K in February |
| 🟢 Star Product | **Peanut Butter Cubes** — top revenue generator at $46,081 across 5 transactions |
| 🔴 Underperformer | **Fruit & Nut Bars** — $168 total revenue, $0.52 per box, 1 transaction only |
| 🔵 Efficiency Leader | **Orange Choco** — highest revenue per box at $337, though low volume |
| 🟡 Rep Disparity | Top rep earns **26×** more than the bottom rep ($28,798 vs $1,085) |
| 🔵 Logistics | **Truck** dominates at 51% of all shipments — single-mode dependency risk |

---

## 🚀 How to Use

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/chocolate-sales-sql.git
cd chocolate-sales-sql
```

### 2. Set up the database
```bash
# PostgreSQL example
psql -U your_username -d your_database
```

### 3. Create the table and load data
```sql
-- Run the DDL from Section 0
\i chocolate_sales_analysis.sql
```

### 4. Run individual queries
Each section is clearly labelled with comments. Jump to any section directly, or run the full file sequentially to reproduce all results.

> 💡 **Tip:** Use a GUI like **pgAdmin**, **DBeaver**, or **TablePlus** for a visual query experience.

---

## 🛠️ Tools & Compatibility

| Tool | Status |
|---|---|
| PostgreSQL 13+ | ✅ Fully compatible |
| MySQL 8+ | ✅ Compatible (minor syntax notes included in file) |
| SQL Server | ✅ Compatible |
| SQLite | ⚠️ Partial — window functions limited |
| DBeaver / pgAdmin | ✅ Recommended for visual exploration |
| Power BI / Tableau | ✅ Section 8 detail view is BI-tool ready |

### SQL features used
- `GROUP BY` with aggregate functions
- Window functions — `RANK()`, `LAG()`, `NTILE()`, `SUM() OVER()`
- Common Table Expressions (CTEs) — `WITH` clauses
- `CASE WHEN` classification logic
- `PARTITION BY` for grouped rankings
- `CROSS JOIN` for team-level benchmarks
- `NULLIF()` for safe division

---

## 👩🏽‍💻 Author

**Lydia Wafula**
*Business Analyst | Data Analytics | Certified Virtual Assistant*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/lydiawafula)
[![Portfolio](https://img.shields.io/badge/Portfolio-View-lightgrey?logo=google)](https://sites.google.com/view/lydiawafula)

> *"Data without direction is just noise — the goal is always the insight that drives the next decision."*

---
*Part of Lydia Wafula's Data Analytics Portfolio — SQL | Excel | Power BI | Python*
