import os
import sys
import logging
from datetime import datetime

# Ensure src is in path if run from other locations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extract import extract_all_transactions, extract_reference_data
from transform import profile_data, clean_and_harmonize, transform_and_integrate
from load import validate_data, load_data
from queries import run_queries

def setup_logging(base_dir):
    """Configure logging to write to both console and a log file."""
    logs_dir = os.path.join(base_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, 'pipeline.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_path, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger = setup_logging(base_dir)

    logger.info("====================================")
    logger.info("      STARTING ETL PIPELINE         ")
    logger.info("====================================")

    raw_dir = os.path.join(base_dir, 'raw')

    # 1. Extract
    logger.info("[1/5] Extracting Data...")
    try:
        sales_df = extract_all_transactions(raw_dir)
        products_df, stores_df, promotions_df, targets_df = extract_reference_data(raw_dir)
        logger.info(f"Extracted {len(sales_df)} transaction records.")
    except Exception as e:
        logger.error(f"CRITICAL ERROR during Extraction: {e}")
        sys.exit(1)

    # 2. Profile
    logger.info("[2/5] Profiling Data...")
    profile_data(sales_df)

    # 3. Clean and Harmonize
    logger.info("[3/5] Cleaning and Harmonizing Data...")
    try:
        clean_sales_df = clean_and_harmonize(sales_df)
        logger.info(f"Rows after cleaning: {len(clean_sales_df)} (Removed {len(sales_df) - len(clean_sales_df)} invalid/duplicate rows)")
    except Exception as e:
        logger.error(f"CRITICAL ERROR during Cleaning: {e}")
        sys.exit(1)

    # 4. Transform and Integrate
    logger.info("[4/5] Transforming and Integrating Data...")
    try:
        integrated_df = transform_and_integrate(clean_sales_df, products_df, stores_df, promotions_df, targets_df)
        logger.info(f"Integrated dataset created with {len(integrated_df.columns)} columns.")
    except Exception as e:
        logger.error(f"CRITICAL ERROR during Transformation: {e}")
        sys.exit(1)

    # 5. Validate and Load
    logger.info("[5/5] Validating and Loading Data...")
    try:
        validate_data(integrated_df)
        load_data(integrated_df, targets_df, base_dir)
        logger.info("Validation passed successfully.")
    except Exception as e:
        logger.error(f"CRITICAL ERROR during Validation/Loading: {e}")
        sys.exit(1)

    logger.info("====================================")
    logger.info("     ETL PIPELINE COMPLETED         ")
    logger.info("====================================")

    # Run analytical queries automatically
    run_queries(base_dir)

if __name__ == "__main__":
    main()