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
        "1. Total Revenue by Month": """
            SELECT month, SUM(net_sales) as total_revenue
            FROM sales_analytics
            GROUP BY month
            ORDER BY month;
        """,
        "2. Top-selling Products": """
            SELECT product_name, SUM(quantity) as total_units_sold, SUM(net_sales) as total_revenue
            FROM sales_analytics
            GROUP BY product_name
            ORDER BY total_revenue DESC
            LIMIT 5;
        """,
        "3. Product Performance (Sales by Category)": """
            SELECT category, SUM(net_sales) as total_revenue, COUNT(sale_line_id) as total_transactions
            FROM sales_analytics
            GROUP BY category
            ORDER BY total_revenue DESC;
        """,
        "4. Sales by Region and Store": """
            SELECT region, store_name, SUM(net_sales) as total_revenue
            FROM sales_analytics
            GROUP BY region, store_name
            ORDER BY region, total_revenue DESC;
        """,
        "5. Store Target Performance (vs Monthly Targets)": """
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
        "6. Sales Trend Over Time (Weekly)": """
            SELECT week, SUM(net_sales) as weekly_revenue
            FROM sales_analytics
            GROUP BY week
            ORDER BY week;
        """
    }

    print("\n" + "="*50)
    print("ANALYTICAL QUERIES RESULTS")
    print("="*50)

    for title, query in queries.items():
        print(f"\n{title}")
        print("-" * len(title))
        try:
            df = pd.read_sql(query, conn)
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
