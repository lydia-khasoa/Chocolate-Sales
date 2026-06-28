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
## 🗂️ Queries

```sql

SECTION 1 — OVERVIEW KPIs
-- 1.1  Executive summary — single-row snapshot
SELECT
    COUNT(*)                                              AS total_transactions,
    ROUND(SUM(amount), 2)                                 AS total_revenue,
    ROUND(AVG(amount), 2)                                 AS avg_order_value,
    ROUND(MIN(amount), 2)                                 AS min_order_value,
    ROUND(MAX(amount), 2)                                 AS max_order_value,
    SUM(boxes_shipped)                                    AS total_boxes_shipped,
    ROUND(AVG(boxes_shipped), 1)                          AS avg_boxes_per_transaction,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2) AS overall_revenue_per_box,
    MIN(sale_date)                                        AS earliest_sale,
    MAX(sale_date)                                        AS latest_sale,
    COUNT(DISTINCT country)                               AS countries_active,
    COUNT(DISTINCT product)                               AS products_active,
    COUNT(DISTINCT CONCAT(first_name, ' ', last_name))    AS total_salespersons
FROM sales;

-- 1.2  High-value vs low-value order classification
--      (mirrors the workbook's "Classification" column)
SELECT
    CASE
        WHEN amount >= 8000 THEN 'High Sale Value'
        ELSE 'Low Sale Value'
    END                             AS sale_classification,
    COUNT(*)                        AS transaction_count,
    ROUND(SUM(amount), 2)           AS total_revenue,
    ROUND(AVG(amount), 2)           AS avg_order_value,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1
    )                               AS pct_of_transactions
FROM sales
GROUP BY sale_classification
ORDER BY total_revenue DESC;

 SECTION 2 — REVENUE BY COUNTRY
-- 2.1  Revenue, transactions, and market share by country
SELECT
    country,
    COUNT(*)                                                      AS transactions,
    ROUND(SUM(amount), 2)                                         AS total_revenue,
    ROUND(AVG(amount), 2)                                         AS avg_order_value,
    SUM(boxes_shipped)                                            AS total_boxes,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2)         AS revenue_per_box,
    ROUND(
        SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 1
    )                                                             AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(amount) DESC)                       AS revenue_rank
FROM sales
GROUP BY country
ORDER BY total_revenue DESC;

-- 2.2  Country concentration risk — top 2 markets vs rest
SELECT
    CASE
        WHEN country IN (
            SELECT country
            FROM sales
            GROUP BY country
            ORDER BY SUM(amount) DESC
            LIMIT 2
        ) THEN country
        ELSE 'All Other Markets'
    END                             AS market_group,
    ROUND(SUM(amount), 2)           AS total_revenue,
    ROUND(
        SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 1
    )                               AS revenue_share_pct
FROM sales
GROUP BY market_group
ORDER BY total_revenue DESC;

 SECTION 3 — PRODUCT PERFORMANCE

-- 3.1  Full product performance table
SELECT
    product,
    COUNT(*)                                                  AS transactions,
    ROUND(SUM(amount), 2)                                     AS total_revenue,
    ROUND(AVG(amount), 2)                                     AS avg_order_value,
    SUM(boxes_shipped)                                        AS total_boxes,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2)     AS revenue_per_box,
    ROUND(
        SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 1
    )                                                         AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(amount) DESC)                   AS revenue_rank
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;

-- 3.2  Top 5 products by revenue
SELECT
    product,
    ROUND(SUM(amount), 2)  AS total_revenue,
    COUNT(*)               AS transactions,
    SUM(boxes_shipped)     AS total_boxes
FROM sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 5;

-- 3.3  Bottom 5 products — portfolio pruning candidates
SELECT
    product,
    ROUND(SUM(amount), 2)                                 AS total_revenue,
    COUNT(*)                                              AS transactions,
    SUM(boxes_shipped)                                    AS total_boxes,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2) AS revenue_per_box
FROM sales
GROUP BY product
ORDER BY total_revenue ASC
LIMIT 5;

-- 3.4  Product efficiency — revenue per box (logistics value)
SELECT
    product,
    SUM(boxes_shipped)                                        AS total_boxes,
    ROUND(SUM(amount), 2)                                     AS total_revenue,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2)     AS revenue_per_box,
    RANK() OVER (
        ORDER BY SUM(amount) / NULLIF(SUM(boxes_shipped), 0) DESC
    )                                                         AS efficiency_rank
FROM sales
GROUP BY product
ORDER BY revenue_per_box DESC;

-- 3.5  Products sold in multiple markets (breadth indicator)
SELECT
    product,
    COUNT(DISTINCT country)  AS markets_present_in,
    ROUND(SUM(amount), 2)    AS total_revenue,
    COUNT(*)                 AS total_transactions
FROM sales
GROUP BY product
HAVING COUNT(DISTINCT country) > 1
ORDER BY markets_present_in DESC, total_revenue DESC;

SECTION 4 — SALESPERSON PERFORMANCE
-- 4.1  Salesperson revenue ranking — full leaderboard
SELECT
    CONCAT(
        INITCAP(TRIM(first_name)), ' ',
        INITCAP(TRIM(last_name))
    )                                                          AS salesperson,
    COUNT(*)                                                   AS transactions,
    ROUND(SUM(amount), 2)                                      AS total_revenue,
    ROUND(AVG(amount), 2)                                      AS avg_order_value,
    SUM(boxes_shipped)                                         AS total_boxes,
    ROUND(
        SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 1
    )                                                          AS revenue_share_pct,
    RANK() OVER (ORDER BY SUM(amount) DESC)                    AS revenue_rank
FROM sales
GROUP BY first_name, last_name
ORDER BY total_revenue DESC;

-- 4.2  Performance gap — top vs bottom rep
WITH rep_summary AS (
    SELECT
        CONCAT(TRIM(first_name), ' ', TRIM(last_name)) AS salesperson,
        ROUND(SUM(amount), 2)                           AS total_revenue
    FROM sales
    GROUP BY first_name, last_name
)
SELECT
    MAX(total_revenue)                                    AS top_rep_revenue,
    MIN(total_revenue)                                    AS bottom_rep_revenue,
    ROUND(MAX(total_revenue) / NULLIF(MIN(total_revenue), 0), 1) AS performance_gap_ratio,
    ROUND(AVG(total_revenue), 2)                          AS avg_rep_revenue,
    ROUND(STDDEV(total_revenue), 2)                       AS revenue_std_dev
FROM rep_summary;

-- 4.3  Salesperson performance vs team average (above/below average flag)
WITH rep_totals AS (
    SELECT
        CONCAT(TRIM(first_name), ' ', TRIM(last_name)) AS salesperson,
        ROUND(SUM(amount), 2)                           AS total_revenue
    FROM sales
    GROUP BY first_name, last_name
),
team_avg AS (
    SELECT ROUND(AVG(total_revenue), 2) AS avg_revenue FROM rep_totals
)
SELECT
    r.salesperson,
    r.total_revenue,
    t.avg_revenue                                              AS team_avg_revenue,
    ROUND(r.total_revenue - t.avg_revenue, 2)                  AS variance_from_avg,
    CASE
        WHEN r.total_revenue >= t.avg_revenue THEN 'Above Average'
        ELSE 'Below Average'
    END                                                        AS performance_flag
FROM rep_totals r
CROSS JOIN team_avg t
ORDER BY r.total_revenue DESC;

-- 4.4  Country coverage per salesperson
SELECT
    CONCAT(TRIM(first_name), ' ', TRIM(last_name))  AS salesperson,
    COUNT(DISTINCT country)                          AS countries_covered,
    COUNT(DISTINCT product)                          AS products_sold,
    COUNT(*)                                         AS total_transactions,
    ROUND(SUM(amount), 2)                            AS total_revenue
FROM sales
GROUP BY first_name, last_name
ORDER BY countries_covered DESC, total_revenue DESC;

SECTION 5 — MONTHLY REVENUE TREND
-- 5.1  Monthly revenue, volume, and transaction count
SELECT
    TO_CHAR(sale_date, 'YYYY-MM')           AS month,           -- MySQL: DATE_FORMAT(sale_date, '%Y-%m')
    TO_CHAR(sale_date, 'Month YYYY')        AS month_label,
    COUNT(*)                                AS transactions,
    ROUND(SUM(amount), 2)                   AS monthly_revenue,
    SUM(boxes_shipped)                      AS boxes_shipped,
    ROUND(AVG(amount), 2)                   AS avg_order_value
FROM sales
GROUP BY TO_CHAR(sale_date, 'YYYY-MM'), TO_CHAR(sale_date, 'Month YYYY')
ORDER BY month;

-- 5.2  Month-over-month revenue change (trend analysis)
WITH monthly AS (
    SELECT
        TO_CHAR(sale_date, 'YYYY-MM')  AS month,
        ROUND(SUM(amount), 2)          AS monthly_revenue
    FROM sales
    GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
)
SELECT
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month)        AS prior_month_revenue,
    ROUND(
        monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month),
        2
    )                                                 AS mom_change,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month))
        * 100.0 / NULLIF(LAG(monthly_revenue) OVER (ORDER BY month), 0),
        1
    )                                                 AS mom_change_pct
FROM monthly
ORDER BY month;

-- 5.3  Identify months with abnormally low revenue (flag: below 50% of avg)
WITH monthly AS (
    SELECT
        TO_CHAR(sale_date, 'YYYY-MM') AS month,
        ROUND(SUM(amount), 2)         AS monthly_revenue,
        COUNT(*)                      AS transactions
    FROM sales
    GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
),
avg_monthly AS (
    SELECT ROUND(AVG(monthly_revenue), 2) AS avg_revenue FROM monthly
)
SELECT
    m.month,
    m.monthly_revenue,
    a.avg_revenue,
    ROUND(m.monthly_revenue * 100.0 / a.avg_revenue, 1) AS pct_of_avg,
    CASE
        WHEN m.monthly_revenue < a.avg_revenue * 0.5 THEN '⚠ Anomaly — Below 50% of Average'
        WHEN m.monthly_revenue < a.avg_revenue        THEN 'Below Average'
        ELSE 'At or Above Average'
    END                                                  AS revenue_flag
FROM monthly m
CROSS JOIN avg_monthly a
ORDER BY m.month;

 SECTION 6 — REVENUE PER BOX (PRODUCT EFFICIENCY)
-- 6.1  Revenue per box by product — ranked
SELECT
    product,
    SUM(boxes_shipped)                                        AS total_boxes,
    ROUND(SUM(amount), 2)                                     AS total_revenue,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2)     AS revenue_per_box,
    NTILE(4) OVER (
        ORDER BY SUM(amount) / NULLIF(SUM(boxes_shipped), 0)
    )                                                         AS efficiency_quartile  -- 4 = top
FROM sales
GROUP BY product
ORDER BY revenue_per_box DESC;

-- 6.2  Revenue per box by country
SELECT
    country,
    SUM(boxes_shipped)                                        AS total_boxes,
    ROUND(SUM(amount), 2)                                     AS total_revenue,
    ROUND(SUM(amount) / NULLIF(SUM(boxes_shipped), 0), 2)     AS revenue_per_box
FROM sales
GROUP BY country
ORDER BY revenue_per_box DESC;

SECTION 7 — SHIPPING METHOD ANALYSIS
-- Note: shipping method is derived from boxes_shipped thresholds
-- matching the workbook's Classification lookup table:
--   0   → Pickup   | 20  → Road    | 40  → Courier
--   70  → Air      | 90  → Sea     | 150 → Truck

-- 7.1  Classify shipments and summarise
SELECT
    CASE
        WHEN boxes_shipped < 20  THEN 'Pickup'
        WHEN boxes_shipped < 40  THEN 'Road'
        WHEN boxes_shipped < 70  THEN 'Courier'
        WHEN boxes_shipped < 90  THEN 'Air'
        WHEN boxes_shipped < 150 THEN 'Sea'
        ELSE 'Truck'
    END                                                    AS shipping_method,
    COUNT(*)                                               AS shipment_count,
    ROUND(SUM(amount), 2)                                  AS total_revenue,
    SUM(boxes_shipped)                                     AS total_boxes,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1
    )                                                      AS pct_of_shipments
FROM sales
GROUP BY shipping_method
ORDER BY shipment_count DESC;

-- 7.2  Shipping method by country
SELECT
    country,
    CASE
        WHEN boxes_shipped < 20  THEN 'Pickup'
        WHEN boxes_shipped < 40  THEN 'Road'
        WHEN boxes_shipped < 70  THEN 'Courier'
        WHEN boxes_shipped < 90  THEN 'Air'
        WHEN boxes_shipped < 150 THEN 'Sea'
        ELSE 'Truck'
    END                         AS shipping_method,
    COUNT(*)                    AS shipment_count,
    ROUND(SUM(amount), 2)       AS total_revenue
FROM sales
GROUP BY country, shipping_method
ORDER BY country, shipment_count DESC;

SECTION 8 — ADVANCED / COMBINED INSIGHTS
-- 8.1  Running cumulative revenue (by date — growth curve)
SELECT
    sale_date,
    ROUND(SUM(amount), 2)                                 AS daily_revenue,
    ROUND(SUM(SUM(amount)) OVER (ORDER BY sale_date), 2)  AS cumulative_revenue
FROM sales
GROUP BY sale_date
ORDER BY sale_date;

-- 8.2  Pareto analysis — which products make up 80% of revenue
WITH product_revenue AS (
    SELECT
        product,
        ROUND(SUM(amount), 2) AS total_revenue
    FROM sales
    GROUP BY product
),
ranked AS (
    SELECT
        product,
        total_revenue,
        ROUND(
            SUM(total_revenue) OVER (ORDER BY total_revenue DESC)
            * 100.0 / SUM(total_revenue) OVER (),
            1
        ) AS cumulative_revenue_pct
    FROM product_revenue
)
SELECT
    product,
    total_revenue,
    cumulative_revenue_pct,
    CASE
        WHEN cumulative_revenue_pct <= 80 THEN 'Top 80% Revenue Drivers'
        ELSE 'Tail Products'
    END AS pareto_category
FROM ranked
ORDER BY total_revenue DESC;

-- 8.3  Cross-tabulation — product × country revenue heatmap base
SELECT
    product,
    SUM(CASE WHEN country = 'UK'          THEN amount ELSE 0 END) AS uk,
    SUM(CASE WHEN country = 'USA'         THEN amount ELSE 0 END) AS usa,
    SUM(CASE WHEN country = 'Australia'   THEN amount ELSE 0 END) AS australia,
    SUM(CASE WHEN country = 'India'       THEN amount ELSE 0 END) AS india,
    SUM(CASE WHEN country = 'Canada'      THEN amount ELSE 0 END) AS canada,
    SUM(CASE WHEN country = 'New Zealand' THEN amount ELSE 0 END) AS new_zealand,
    ROUND(SUM(amount), 2)                                          AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;

-- 8.4  Salesperson × product matrix — who sells what best
SELECT
    CONCAT(TRIM(first_name), ' ', TRIM(last_name))  AS salesperson,
    product,
    COUNT(*)                                         AS transactions,
    ROUND(SUM(amount), 2)                            AS revenue
FROM sales
GROUP BY first_name, last_name, product
ORDER BY salesperson, revenue DESC;

-- 8.5  Best product per country
WITH ranked_products AS (
    SELECT
        country,
        product,
        ROUND(SUM(amount), 2)                             AS total_revenue,
        RANK() OVER (
            PARTITION BY country
            ORDER BY SUM(amount) DESC
        )                                                 AS rank_in_country
    FROM sales
    GROUP BY country, product
)
SELECT
    country,
    product         AS top_product,
    total_revenue
FROM ranked_products
WHERE rank_in_country = 1
ORDER BY total_revenue DESC;

-- 8.6  Best salesperson per country
WITH ranked_reps AS (
    SELECT
        country,
        CONCAT(TRIM(first_name), ' ', TRIM(last_name)) AS salesperson,
        ROUND(SUM(amount), 2)                           AS total_revenue,
        RANK() OVER (
            PARTITION BY country
            ORDER BY SUM(amount) DESC
        )                                               AS rank_in_country
    FROM sales
    GROUP BY country, first_name, last_name
)
SELECT
    country,
    salesperson     AS top_salesperson,
    total_revenue
FROM ranked_reps
WHERE rank_in_country = 1
ORDER BY total_revenue DESC;

-- 8.7  Transaction-level detail with all derived metrics
--      (useful as a base view for dashboards / BI tools)
SELECT
    sale_id,
    CONCAT(TRIM(INITCAP(first_name)), ' ', TRIM(INITCAP(last_name))) AS salesperson,
    country,
    product,
    sale_date,
    TO_CHAR(sale_date, 'YYYY-MM')                                     AS sale_month,
    amount,
    boxes_shipped,
    ROUND(amount / NULLIF(boxes_shipped, 0), 2)                       AS revenue_per_box,
    CASE
        WHEN amount >= 8000 THEN 'High Sale Value'
        ELSE 'Low Sale Value'
    END                                                               AS sale_classification,
    CASE
        WHEN boxes_shipped < 20  THEN 'Pickup'
        WHEN boxes_shipped < 40  THEN 'Road'
        WHEN boxes_shipped < 70  THEN 'Courier'
        WHEN boxes_shipped < 90  THEN 'Air'
        WHEN boxes_shipped < 150 THEN 'Sea'
        ELSE 'Truck'
    END                                                               AS shipping_method,
    amount * boxes_shipped                                            AS grand_total,
    ROUND(
        SUM(amount) OVER (
            PARTITION BY TO_CHAR(sale_date, 'YYYY-MM')
        ), 2
    )                                                                 AS month_total_revenue,
    ROUND(
        amount * 100.0 / SUM(amount) OVER (
            PARTITION BY TO_CHAR(sale_date, 'YYYY-MM')
        ), 1
    )                                                                 AS pct_of_month_revenue
FROM sales
ORDER BY sale_date, amount DESC;
```
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
