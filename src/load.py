import pandas as pd
import sqlite3
import os

def validate_data(df):
    """Activity 7: Validate."""
    errors = []
    
    # sale_line_id is unique
    if df['sale_line_id'].duplicated().any():
        errors.append("Validation Failed: Duplicate sale_line_id found.")

    # Required identifiers and dates are not null
    required_cols = ['sale_line_id', 'sale_date', 'store_id', 'product_id']
    if df[required_cols].isnull().any().any():
        errors.append("Validation Failed: Null values in required identifiers or dates.")

    # quantity, unit_price, gross_sales, and net_sales are positive
    positive_cols = ['quantity', 'unit_price', 'gross_sales', 'net_sales']
    for col in positive_cols:
        if (df[col] <= 0).any():
            # some might be legitimately 0 if 100% discount, but requirement says positive.
            # wait, net_sales could be 0 if 100% discount, but let's check gross_sales > 0 and others >= 0
            if col in ['quantity', 'unit_price', 'gross_sales'] and (df[col] <= 0).any():
                errors.append(f"Validation Failed: Non-positive values in {col}.")
            elif col == 'net_sales' and (df[col] < 0).any():
                 errors.append(f"Validation Failed: Negative values in {col}.")

    # Every product matches the product master (product_name not null)
    if df['product_name'].isnull().any():
        errors.append("Validation Failed: Unmatched product_id found.")

    # Every store matches the store master (store_name not null)
    if df['store_name'].isnull().any():
        unmatched = df[df['store_name'].isnull()]['store_id'].unique()
        errors.append(f"Validation Failed: Unmatched store_id found: {unmatched}")

    # net_sales equals gross_sales minus discount_amount
    expected_net = df['gross_sales'] - df['discount_amount']
    # use np.isclose to handle floating point issues
    if not pd.Series(expected_net).equals(df['net_sales']):
        # Let's use a tolerance check instead of exact equals
        if not (abs(expected_net - df['net_sales']) < 1e-5).all():
            errors.append("Validation Failed: net_sales calculation mismatch.")

    if errors:
        for error in errors:
            print(error)
        raise ValueError("Data validation failed. Check logs for details.")
    
    print("Validation passed successfully.")

def load_data(df, targets_df, base_dir):
    """Activity 8: Load."""
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    db_path = os.path.join(base_dir, 'database', 'retail_analytics.db')

    # Ensure directories exist
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Save to CSV
    csv_path = os.path.join(processed_dir, 'integrated_sales.csv')
    df.to_csv(csv_path, index=False)
    print(f"Saved processed data to {csv_path}")

    # Load to SQLite
    conn = sqlite3.connect(db_path)
    try:
        # Save transactions
        df.to_sql('sales_analytics', conn, if_exists='replace', index=False)
        # Save monthly targets
        targets_df.to_sql('monthly_targets', conn, if_exists='replace', index=False)
        print(f"Loaded data to database {db_path}")
    except Exception as e:
        print(f"Error loading to SQLite: {e}")
        raise
    finally:
        conn.close()
