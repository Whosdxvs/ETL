import sqlite3
import pandas as pd
import os

def run_queries(base_dir):
    """Activity 9: Analytical Queries"""
    db_path = os.path.join(base_dir, 'database', 'retail_analytics.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Run pipeline first.")
        return

    conn = sqlite3.connect(db_path)
    
    queries = {
        "1. Total Revenue by Month": {
            "sql": """
                SELECT month, SUM(net_sales) as total_revenue
                FROM sales_analytics
                GROUP BY month
                ORDER BY month;
            """,
            "explanation": "Business Question: How is overall revenue trending across the quarter? This tracks total sales performance over time, satisfying the 'Total Revenue by Month' requirement."
        },
        "2. Top-selling Products": {
            "sql": """
                SELECT product_name, SUM(quantity) as total_units_sold, SUM(net_sales) as total_revenue
                FROM sales_analytics
                GROUP BY product_name
                ORDER BY total_revenue DESC
                LIMIT 5;
            """,
            "explanation": "Business Question: Which products generate the most revenue? Identifies the highest-grossing products to guide inventory and marketing decisions."
        },
        "3. Product Performance (Sales by Category)": {
            "sql": """
                SELECT category, SUM(net_sales) as total_revenue, COUNT(sale_line_id) as total_transactions
                FROM sales_analytics
                GROUP BY category
                ORDER BY total_revenue DESC;
            """,
            "explanation": "Business Question: Which product categories drive the most revenue? Helps understand category-level performance for purchasing and promotion strategy."
        },
        "4. Sales by Region and Store": {
            "sql": """
                SELECT region, store_name, SUM(net_sales) as total_revenue
                FROM sales_analytics
                GROUP BY region, store_name
                ORDER BY region, total_revenue DESC;
            """,
            "explanation": "Business Question: How does performance compare across branches? Provides a geographic breakdown of revenue by region and store."
        },
        "5. Store Target Performance (vs Monthly Targets)": {
            "sql": """
                SELECT 
                    s.month, 
                    s.store_id,
                    MAX(s.store_name) as store_name,
                    SUM(s.net_sales) as actual_revenue,
                    MAX(t.sales_target) as target_revenue,
                    (SUM(s.net_sales) - MAX(t.sales_target)) as difference,
                    CASE 
                        WHEN SUM(s.net_sales) >= MAX(t.sales_target) THEN 'Met/Exceeded' 
                        ELSE 'Missed' 
                    END as target_status
                FROM sales_analytics s
                LEFT JOIN monthly_targets t ON s.store_id = t.store_id AND s.month = t.month
                GROUP BY s.month, s.store_id
                ORDER BY s.month, s.store_id;
            """,
            "explanation": "Business Question: Which stores met or missed their monthly sales targets? Compares actual revenue against targets to evaluate store performance."
        },
        "6. Sales Trend Over Time (Weekly)": {
            "sql": """
                SELECT week, SUM(net_sales) as weekly_revenue
                FROM sales_analytics
                GROUP BY week
                ORDER BY week;
            """,
            "explanation": "Business Question: How do sales fluctuate week to week? Offers a granular view of weekly progress to spot short-term trends."
        }
    }

    print("\n" + "="*50)
    print("ANALYTICAL QUERIES RESULTS")
    print("="*50)

    for title, content in queries.items():
        print(f"\n{title}")
        print("-" * len(title))
        print(content["explanation"])
        try:
            df = pd.read_sql(content["sql"], conn)
            if df.empty:
                print("No data returned.")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f"Error running query: {e}")

    conn.close()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    run_queries(base_dir)