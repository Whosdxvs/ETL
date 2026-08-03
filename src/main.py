import os
import sys

# Ensure src is in path if run from other locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract import extract_all_transactions, extract_reference_data
from transform import profile_data, clean_and_harmonize, transform_and_integrate
from load import validate_data, load_data
from queries import run_queries

def main():
    print("====================================")
    print("      STARTING ETL PIPELINE         ")
    print("====================================")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'raw')

    # 1. Extract
    print("\n[1/5] Extracting Data...")
    try:
        sales_df = extract_all_transactions(raw_dir)
        products_df, stores_df, promotions_df, targets_df = extract_reference_data(raw_dir)
        print(f"Extracted {len(sales_df)} transaction records.")
    except Exception as e:
        print(f"CRITICAL ERROR during Extraction: {e}")
        sys.exit(1)

    # 2. Profile
    print("\n[2/5] Profiling Data...")
    profile_data(sales_df)

    # 3. Clean and Harmonize
    print("\n[3/5] Cleaning and Harmonizing Data...")
    try:
        clean_sales_df = clean_and_harmonize(sales_df)
        print(f"Rows after cleaning: {len(clean_sales_df)} (Removed {len(sales_df) - len(clean_sales_df)} invalid/duplicate rows)")
    except Exception as e:
        print(f"CRITICAL ERROR during Cleaning: {e}")
        sys.exit(1)

    # 4. Transform and Integrate
    print("\n[4/5] Transforming and Integrating Data...")
    try:
        integrated_df = transform_and_integrate(clean_sales_df, products_df, stores_df, promotions_df)
        print(f"Integrated dataset created with {len(integrated_df.columns)} columns.")
    except Exception as e:
        print(f"CRITICAL ERROR during Transformation: {e}")
        sys.exit(1)

    # 5. Validate and Load
    print("\n[5/5] Validating and Loading Data...")
    try:
        validate_data(integrated_df)
        load_data(integrated_df, targets_df, base_dir)
    except Exception as e:
        print(f"CRITICAL ERROR during Validation/Loading: {e}")
        sys.exit(1)

    print("\n====================================")
    print("     ETL PIPELINE COMPLETED         ")
    print("====================================")

    # Run analytical queries automatically
    run_queries(base_dir)

if __name__ == "__main__":
    main()
