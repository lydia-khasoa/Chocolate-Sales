/* ============================================================
   CHOCOLATE SALES ANALYSIS — SQL PORTFOLIO PROJECT
   Author: Lydia Wafula
   Dataset: 3,282 transactions | 25 sales reps | 6 countries
            22 products | Jan 2022 – Aug 2024
   ============================================================ */

-- ------------------------------------------------------------
-- 0. SCHEMA & STAGING
-- ------------------------------------------------------------
DROP TABLE IF EXISTS chocolate_sales;

CREATE TABLE chocolate_sales (
    sales_person     VARCHAR(100),
    country          VARCHAR(50),
    product          VARCHAR(100),
    sale_date        DATE,
    amount           DECIMAL(12,2),   -- cleaned from "$5,320.00" -> 5320.00
    boxes_shipped    INT
);

-- Example load (Postgres). Adjust for your engine (BULK INSERT / LOAD DATA / COPY).
-- COPY chocolate_sales FROM 'chocolate_sales_clean.csv' DELIMITER ',' CSV HEADER;


-- ------------------------------------------------------------
-- 1. TOP-LINE KPIs
-- ------------------------------------------------------------

-- 1.1 Total revenue, total boxes shipped, total orders
SELECT
    COUNT(*)                       AS total_orders,
    SUM(amount)                    AS total_revenue,
    SUM(boxes_shipped)             AS total_boxes_shipped,
    ROUND(AVG(amount), 2)          AS avg_order_value,
    ROUND(SUM(amount) / SUM(boxes_shipped), 2) AS revenue_per_box
FROM chocolate_sales;

-- 1.2 Revenue & order count by year
SELECT
    EXTRACT(YEAR FROM sale_date)   AS sales_year,
    COUNT(*)                       AS orders,
    SUM(amount)                    AS revenue,
    SUM(boxes_shipped)             AS boxes_shipped
FROM chocolate_sales
GROUP BY 1
ORDER BY 1;


-- ------------------------------------------------------------
-- 2. REVENUE BY COUNTRY / MARKET PERFORMANCE
-- ------------------------------------------------------------

-- 2.1 Revenue, orders and avg order value by country, ranked
SELECT
    country,
    COUNT(*)                                AS orders,
    SUM(amount)                             AS revenue,
    ROUND(AVG(amount), 2)                   AS avg_order_value,
    RANK() OVER (ORDER BY SUM(amount) DESC) AS revenue_rank
FROM chocolate_sales
GROUP BY country
ORDER BY revenue DESC;

-- 2.2 Country's share of total revenue (%)
SELECT
    country,
    SUM(amount) AS revenue,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 2) AS pct_of_total_revenue
FROM chocolate_sales
GROUP BY country
ORDER BY revenue DESC;


-- ------------------------------------------------------------
-- 3. PRODUCT PERFORMANCE
-- ------------------------------------------------------------

-- 3.1 Top 10 products by revenue, with quartile bucketing (NTILE)
SELECT
    product,
    SUM(amount)              AS revenue,
    SUM(boxes_shipped)       AS boxes_shipped,
    ROUND(SUM(amount) / SUM(boxes_shipped), 2) AS revenue_per_box,
    NTILE(4) OVER (ORDER BY SUM(amount) DESC) AS revenue_quartile
FROM chocolate_sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- 3.2 Best-selling product per country (window function + filter)
WITH product_country_sales AS (
    SELECT
        country,
        product,
        SUM(amount) AS revenue,
        RANK() OVER (PARTITION BY country ORDER BY SUM(amount) DESC) AS rnk
    FROM chocolate_sales
    GROUP BY country, product
)
SELECT country, product, revenue
FROM product_country_sales
WHERE rnk = 1
ORDER BY revenue DESC;


-- ------------------------------------------------------------
-- 4. SALES REP PERFORMANCE
-- ------------------------------------------------------------

-- 4.1 Leaderboard: revenue, orders, avg deal size per rep
SELECT
    sales_person,
    COUNT(*)                                AS orders,
    SUM(amount)                             AS revenue,
    ROUND(AVG(amount), 2)                   AS avg_deal_size,
    RANK() OVER (ORDER BY SUM(amount) DESC) AS rank_by_revenue
FROM chocolate_sales
GROUP BY sales_person
ORDER BY revenue DESC;

-- 4.2 Rep performance vs. company average (LAG-style benchmarking using window AVG)
SELECT
    sales_person,
    SUM(amount) AS rep_revenue,
    ROUND(AVG(SUM(amount)) OVER (), 2) AS company_avg_rep_revenue,
    ROUND(SUM(amount) - AVG(SUM(amount)) OVER (), 2) AS variance_from_avg
FROM chocolate_sales
GROUP BY sales_person
ORDER BY rep_revenue DESC;


-- ------------------------------------------------------------
-- 5. TIME-SERIES TRENDS
-- ------------------------------------------------------------

-- 5.1 Monthly revenue trend
SELECT
    DATE_TRUNC('month', sale_date) AS sales_month,
    SUM(amount)                    AS revenue,
    COUNT(*)                       AS orders
FROM chocolate_sales
GROUP BY 1
ORDER BY 1;

-- 5.2 Month-over-month growth (LAG)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', sale_date) AS sales_month,
        SUM(amount) AS revenue
    FROM chocolate_sales
    GROUP BY 1
)
SELECT
    sales_month,
    revenue,
    LAG(revenue) OVER (ORDER BY sales_month) AS prev_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY sales_month))
        / LAG(revenue) OVER (ORDER BY sales_month), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY sales_month;

-- 5.3 3-month rolling average revenue (smoothing seasonality)
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', sale_date) AS sales_month,
        SUM(amount) AS revenue
    FROM chocolate_sales
    GROUP BY 1
)
SELECT
    sales_month,
    revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY sales_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_3mo_avg_revenue
FROM monthly
ORDER BY sales_month;


-- ------------------------------------------------------------
-- 6. OPERATIONAL EFFICIENCY (Boxes Shipped)
-- ------------------------------------------------------------

-- 6.1 Revenue-per-box efficiency by product (identifies high-margin vs. high-volume items)
SELECT
    product,
    SUM(boxes_shipped)                          AS total_boxes,
    SUM(amount)                                 AS total_revenue,
    ROUND(SUM(amount) / SUM(boxes_shipped), 2)  AS revenue_per_box
FROM chocolate_sales
GROUP BY product
ORDER BY revenue_per_box DESC;

-- 6.2 Country shipping efficiency (boxes per order)
SELECT
    country,
    COUNT(*)                                    AS orders,
    SUM(boxes_shipped)                          AS total_boxes,
    ROUND(SUM(boxes_shipped)::DECIMAL / COUNT(*), 1) AS avg_boxes_per_order
FROM chocolate_sales
GROUP BY country
ORDER BY avg_boxes_per_order DESC;


-- ------------------------------------------------------------
-- 7. REUSABLE BI VIEW (for dashboarding tools / Excel hookup)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vw_chocolate_sales_summary AS
SELECT
    sale_date,
    DATE_TRUNC('month', sale_date) AS sales_month,
    sales_person,
    country,
    product,
    amount,
    boxes_shipped,
    ROUND(amount / boxes_shipped, 2) AS revenue_per_box
FROM chocolate_sales;
