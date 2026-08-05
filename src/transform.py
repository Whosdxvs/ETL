import pandas as pd
import numpy as np

def profile_data(df):
    """Activity 4: Profile the combined transaction data."""
    print("--- Profiling Summary ---")
    print(f"Row count: {len(df)}")
    print("\nColumns and Data Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nDuplicate sale_line_id values:")
    print(df['sale_line_id'].duplicated().sum())
    print("-------------------------\n")

def clean_and_harmonize(df):
    """Activity 5: Clean and harmonize data."""
    df = df.copy()

    # Trim whitespace and standardize to uppercase for ID columns
    str_cols = ['sale_line_id', 'store_id', 'product_id', 'promotion_code']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # payment_method needs to be Title case
    if 'payment_method' in df.columns:
        df['payment_method'] = df['payment_method'].astype(str).str.strip()

    # Standardize text casing
    df['payment_method'] = df['payment_method'].str.title()
    
    # Parse dates
    # We have different formats: YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY
    # Dates were already parsed per-source in extract.py using their correct format
    df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')

    # Convert quantity and unit_price to numeric
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')

    # Filter out invalid records
    df = df.dropna(subset=['sale_date', 'quantity', 'unit_price'])
    df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)]

    # Remove duplicated sale_line_id records, keeping the first
    df = df.drop_duplicates(subset=['sale_line_id'], keep='first')

    # Represent missing promotion codes consistently
    # Some might be "nan", "None", "", "N/A"
    invalid_promos = ['nan', 'None', '', 'N/A']
    df['promotion_code'] = df['promotion_code'].replace(invalid_promos, 'None')
    df['promotion_code'] = df['promotion_code'].fillna('None')

    return df

def transform_and_integrate(sales_df, products_df, stores_df, promotions_df):
    """Activity 6: Transform and integrate."""
    # Ensure references are trimmed and uppercase
    products_df['product_id'] = products_df['product_id'].str.strip().str.upper()
    stores_df['store_id'] = stores_df['store_id'].str.strip().str.upper()
    promotions_df['promotion_code'] = promotions_df['promotion_code'].str.strip().str.upper()

    # Merge products
    merged = pd.merge(sales_df, products_df[['product_id', 'product_name', 'category']], on='product_id', how='left')

    # Merge stores
    merged = pd.merge(merged, stores_df[['store_id', 'store_name', 'city', 'region']], on='store_id', how='left')

    # Merge promotions
    # Promotions table has promotion_code, discount_pct, campaign_name
    merged = pd.merge(merged, promotions_df[['promotion_code', 'discount_pct', 'campaign_name']], on='promotion_code', how='left')

    # Default missing discount_pct to 0
    merged['discount_pct'] = merged['discount_pct'].fillna(0)

    # Calculate fields
    merged['gross_sales'] = merged['quantity'] * merged['unit_price']
    merged['discount_amount'] = merged['gross_sales'] * merged['discount_pct']
    merged['net_sales'] = merged['gross_sales'] - merged['discount_amount']

    # Date components
    # month format YYYY-MM
    merged['month'] = merged['sale_date'].dt.to_period('M').astype(str)
    # week format e.g. 2026-W05
    merged['week'] = merged['sale_date'].dt.strftime('%G-W%V')
    merged['day_name'] = merged['sale_date'].dt.day_name()

    return merged
