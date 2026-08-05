import pandas as pd
import os

def extract_sales_csv(file_path):
    """Extracts sales data from CSV (Cali)."""
    try:
        df = pd.read_csv(file_path)
        # It's already in the common schema, but let's ensure columns
        df.rename(columns={
            'sale_line_id': 'sale_line_id',
            'sale_date': 'sale_date',
            'store_id': 'store_id',
            'product_id': 'product_id',
            'quantity': 'quantity',
            'unit_price': 'unit_price',
            'promotion_code': 'promotion_code',
            'payment_method': 'payment_method'
        }, inplace=True)
        df['sale_date'] = pd.to_datetime(df['sale_date'], format='%Y-%m-%d', errors='coerce')
        return df
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def extract_sales_json(file_path):
    """Extracts sales data from JSON (Bogota)."""
    try:
        df = pd.read_json(file_path)
        df.rename(columns={
            'id_linea': 'sale_line_id',
            'fecha': 'sale_date',
            'sucursal': 'store_id',
            'codigo_producto': 'product_id',
            'unidades': 'quantity',
            'precio': 'unit_price',
            'promocion': 'promotion_code',
            'medio_pago': 'payment_method'
        }, inplace=True)
        df['sale_date'] = pd.to_datetime(df['sale_date'], format='%d/%m/%Y', errors='coerce')
        return df
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def extract_sales_xml(file_path):
    """Extracts sales data from XML (Medellin)."""
    try:
        df = pd.read_xml(file_path, parser='etree')
        df.rename(columns={
            'line_id': 'sale_line_id',
            'date': 'sale_date',
            'branch_code': 'store_id',
            'sku': 'product_id',
            'units': 'quantity',
            'unit_value': 'unit_price',
            'promo_code': 'promotion_code',
            'payment': 'payment_method'
        }, inplace=True)
        df['sale_date'] = pd.to_datetime(df['sale_date'], format='%m-%d-%Y', errors='coerce')
        return df
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def extract_reference_data(raw_dir):
    """Extracts reference data tables."""
    try:
        products = pd.read_csv(os.path.join(raw_dir, 'products.csv'))
        stores = pd.read_csv(os.path.join(raw_dir, 'stores.csv'))
        promotions = pd.read_csv(os.path.join(raw_dir, 'promotions.csv'))
        targets = pd.read_csv(os.path.join(raw_dir, 'monthly_targets.csv'))
        return products, stores, promotions, targets
    except Exception as e:
        print(f"Error reading reference data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def extract_all_transactions(raw_dir):
    """Extracts and combines all transaction data."""
    cali_path = os.path.join(raw_dir, 'sales_cali.csv')
    bogota_path = os.path.join(raw_dir, 'sales_bogota.json')
    medellin_path = os.path.join(raw_dir, 'sales_medellin.xml')

    df_cali = extract_sales_csv(cali_path)
    df_bogota = extract_sales_json(bogota_path)
    df_medellin = extract_sales_xml(medellin_path)

    # Combine all into one DataFrame
    df_all = pd.concat([df_cali, df_bogota, df_medellin], ignore_index=True)
    return df_all
