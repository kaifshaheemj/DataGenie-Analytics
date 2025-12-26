import psycopg2
from psycopg2 import sql, extras
import pandas as pd
import os
from datetime import datetime
import sys
from dotenv import load_dotenv
load_dotenv()

PSWD = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
DATASET_PATH = os.getenv("DATASET_PATH")

DB_CONFIG = {
    'host': host,
    'port': port,
    'database': db_name,
    'user': db_user,
    'password': PSWD
}


# CSV File mappings
CSV_FILES = {
    'dim_calendar': 'AdventureWorks Calendar Lookup.csv',
    'dim_customers': 'AdventureWorks Customer Lookup.csv',
    'dim_product_categories': 'AdventureWorks Product Categories Lookup.csv',
    'dim_product_subcategories': 'AdventureWorks Product Subcategories Lookup.csv',
    'dim_products': 'AdventureWorks Product Lookup.csv',
    'dim_territories': 'AdventureWorks Territory Lookup.csv',
    'fact_sales_2020': 'AdventureWorks Sales Data 2020.csv',
    'fact_sales_2021': 'AdventureWorks Sales Data 2021.csv',
    'fact_sales_2022': 'AdventureWorks Sales Data 2022.csv',    
    'fact_returns': 'AdventureWorks Returns Data.csv'
}


def get_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✓ Successfully connected to database: {DB_CONFIG['database']}")
        return conn
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        sys.exit(1)

# ============================================================================
# TABLE CREATION
# ============================================================================

def create_tables(conn):
    """Create all dimension and fact tables."""
    
    print("\n" + "="*70)
    print("CREATING TABLES")
    print("="*70)
    
    cursor = conn.cursor()
    
    # Drop existing tables (in correct order due to foreign keys)
    drop_commands = [
        "DROP TABLE IF EXISTS fact_returns CASCADE;",
        "DROP TABLE IF EXISTS fact_sales CASCADE;",
        "DROP TABLE IF EXISTS dim_products CASCADE;",
        "DROP TABLE IF EXISTS dim_product_subcategories CASCADE;",
        "DROP TABLE IF EXISTS dim_product_categories CASCADE;",
        "DROP TABLE IF EXISTS dim_territories CASCADE;",
        "DROP TABLE IF EXISTS dim_customers CASCADE;",
        "DROP TABLE IF EXISTS dim_calendar CASCADE;"
    ]
    
    print("\n1. Dropping existing tables (if any)...")
    for cmd in drop_commands:
        cursor.execute(cmd)
    conn.commit()
    print("   ✓ Existing tables dropped")
    
    # Create dimension tables
    create_commands = [
        # Calendar
        """
        CREATE TABLE dim_calendar (
            date DATE PRIMARY KEY,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            month_name VARCHAR(20),
            day_of_week INTEGER,
            day_name VARCHAR(20),
            week_of_year INTEGER
        );
        """,
        
        # Customers
        """
        CREATE TABLE dim_customers (
            customer_key INTEGER PRIMARY KEY,
            prefix VARCHAR(10),
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            birth_date DATE,
            marital_status VARCHAR(10),
            gender VARCHAR(10),
            email_address VARCHAR(100),
            annual_income INTEGER,
            total_children INTEGER,
            education_level VARCHAR(50),
            occupation VARCHAR(50),
            home_owner VARCHAR(10)
        );
        """,
        
        # Product Categories
        """
        CREATE TABLE dim_product_categories (
            product_category_key INTEGER PRIMARY KEY,
            category_name VARCHAR(50) NOT NULL
        );
        """,
        
        # Product Subcategories
        """
        CREATE TABLE dim_product_subcategories (
            product_subcategory_key INTEGER PRIMARY KEY,
            subcategory_name VARCHAR(100) NOT NULL,
            product_category_key INTEGER,
            FOREIGN KEY (product_category_key) 
                REFERENCES dim_product_categories(product_category_key)
        );
        """,
        
        # Products
        """
        CREATE TABLE dim_products (
            product_key INTEGER PRIMARY KEY,
            product_subcategory_key INTEGER,
            product_sku VARCHAR(50),
            product_name VARCHAR(100),
            model_name VARCHAR(50),
            product_description TEXT,
            product_color VARCHAR(20),
            product_size VARCHAR(10),
            product_style VARCHAR(10),
            product_cost DECIMAL(10,4),
            product_price DECIMAL(10,4),
            FOREIGN KEY (product_subcategory_key) 
                REFERENCES dim_product_subcategories(product_subcategory_key)
        );
        """,
        
        # Territories
        """
        CREATE TABLE dim_territories (
            sales_territory_key INTEGER PRIMARY KEY,
            region VARCHAR(50),
            country VARCHAR(50),
            continent VARCHAR(50)
        );
        """,
        
        # Sales Fact
        """
        CREATE TABLE fact_sales (
            sales_id SERIAL,
            order_date DATE NOT NULL,
            stock_date DATE,
            order_number VARCHAR(20) NOT NULL,
            product_key INTEGER NOT NULL,
            customer_key INTEGER NOT NULL,
            territory_key INTEGER NOT NULL,
            order_line_item INTEGER NOT NULL,
            order_quantity INTEGER NOT NULL,
            PRIMARY KEY (order_number, order_line_item),
            FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
            FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key),
            FOREIGN KEY (territory_key) REFERENCES dim_territories(sales_territory_key)
        );
        """,
        
        # Returns Fact
        """
        CREATE TABLE fact_returns (
            return_id SERIAL PRIMARY KEY,
            return_date DATE NOT NULL,
            territory_key INTEGER NOT NULL,
            product_key INTEGER NOT NULL,
            return_quantity INTEGER NOT NULL,
            FOREIGN KEY (territory_key) REFERENCES dim_territories(sales_territory_key),
            FOREIGN KEY (product_key) REFERENCES dim_products(product_key)
        );
        """
    ]
    
    print("\n2. Creating tables...")
    table_names = [
        'dim_calendar', 'dim_customers', 'dim_product_categories',
        'dim_product_subcategories', 'dim_products', 'dim_territories',
        'fact_sales', 'fact_returns'
    ]
    
    for idx, cmd in enumerate(create_commands):
        cursor.execute(cmd)
        print(f"   ✓ Created {table_names[idx]}")
    
    conn.commit()
    print("\n✓ All tables created successfully!")
    cursor.close()

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_calendar_data(conn):
    """Load calendar dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_calendar...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_calendar'])
    df = pd.read_csv(csv_path)
    
    # Convert to datetime and extract components
    df['Date'] = pd.to_datetime(df['Date'])
    df['year'] = df['Date'].dt.year
    df['quarter'] = df['Date'].dt.quarter
    df['month'] = df['Date'].dt.month
    df['month_name'] = df['Date'].dt.strftime('%B')
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['day_name'] = df['Date'].dt.strftime('%A')
    df['week_of_year'] = df['Date'].dt.isocalendar().week
    
    # Rename for database
    df.columns = df.columns.str.lower()
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO dim_calendar (date, year, quarter, month, month_name, 
                                     day_of_week, day_name, week_of_year)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['date'], row['year'], row['quarter'], row['month'], 
              row['month_name'], row['day_of_week'], row['day_name'], row['week_of_year']))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_calendar")

def load_customers_data(conn):
    """Load customer dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_customers...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_customers'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            print(f"   Trying encoding: {encoding}...")
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"   ✓ Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    # Rename columns to match database schema
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Clean data: strip whitespace from all string columns
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Replace 'nan' string with None for proper NULL handling
    df = df.replace('nan', None)
    df = df.replace('NaN', None)
    df = df.replace('', None)
    
    cursor = conn.cursor()
    
    print(f"   Inserting {len(df)} records...")
    for idx, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO dim_customers (
                    customer_key, prefix, first_name, last_name, birth_date,
                    marital_status, gender, email_address, annual_income,
                    total_children, education_level, occupation, home_owner
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        except Exception as e:
            print(f"   ✗ Error at row {idx}: {e}")
            print(f"   Row data: {row.to_dict()}")
            raise
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_customers")

def load_product_categories_data(conn):
    """Load product categories dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_product_categories...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_product_categories'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Clean data
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO dim_product_categories (product_category_key, category_name)
            VALUES (%s, %s)
        """, tuple(row))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_product_categories")

def load_product_subcategories_data(conn):
    """Load product subcategories dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_product_subcategories...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_product_subcategories'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Clean data
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO dim_product_subcategories (
                product_subcategory_key, subcategory_name, product_category_key
            ) VALUES (%s, %s, %s)
        """, tuple(row))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_product_subcategories")

def load_products_data(conn):
    """Load products dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_products...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_products'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Clean data
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Replace 'nan' with None
    df = df.replace('nan', None)
    df = df.replace('NaN', None)
    
    cursor = conn.cursor()
    
    print(f"   Inserting {len(df)} records...")
    for idx, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO dim_products (
                    product_key, product_subcategory_key, product_sku, product_name,
                    model_name, product_description, product_color, product_size,
                    product_style, product_cost, product_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        except Exception as e:
            print(f"   ✗ Error at row {idx}: {e}")
            print(f"   Row data: {row.to_dict()}")
            raise
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_products")

def load_territories_data(conn):
    """Load territories dimension data."""
    print("\n" + "-"*70)
    print("Loading dim_territories...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['dim_territories'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    # Clean data
    string_columns = df.select_dtypes(include=['object']).columns
    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO dim_territories (
                sales_territory_key, region, country, continent
            ) VALUES (%s, %s, %s, %s)
        """, tuple(row))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into dim_territories")

def load_sales_data(conn):
    """Load all sales fact data (2020, 2021, 2022)."""
    print("\n" + "-"*70)
    print("Loading fact_sales...")
    
    cursor = conn.cursor()
    total_records = 0
    
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for year in ['2020', '2021', '2022']:
        csv_key = f'fact_sales_{year}'
        csv_path = os.path.join(DATASET_PATH, CSV_FILES[csv_key])
        
        # Try different encodings
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            raise Exception(f"Could not read {year} sales CSV file with any common encoding")
        
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        print(f"   Loading sales data for {year}...")
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO fact_sales (
                    order_date, stock_date, order_number, product_key,
                    customer_key, territory_key, order_line_item, order_quantity
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))
        
        conn.commit()
        print(f"   ✓ Loaded {len(df)} records for {year}")
        total_records += len(df)
    
    cursor.close()
    print(f"✓ Total sales records loaded: {total_records}")

def load_returns_data(conn):
    """Load returns fact data."""
    print("\n" + "-"*70)
    print("Loading fact_returns...")
    
    csv_path = os.path.join(DATASET_PATH, CSV_FILES['fact_returns'])
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise Exception("Could not read CSV file with any common encoding")
    
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO fact_returns (
                return_date, territory_key, product_key, return_quantity
            ) VALUES (%s, %s, %s, %s)
        """, tuple(row))
    
    conn.commit()
    cursor.close()
    print(f"✓ Loaded {len(df)} records into fact_returns")

# ============================================================================
# INDEXES AND OPTIMIZATIONS
# ============================================================================

def create_indexes(conn):
    """Create indexes for query performance."""
    print("\n" + "="*70)
    print("CREATING INDEXES")
    print("="*70)
    
    cursor = conn.cursor()
    
    index_commands = [
        # Sales fact indexes
        "CREATE INDEX idx_sales_order_date ON fact_sales(order_date);",
        "CREATE INDEX idx_sales_customer ON fact_sales(customer_key);",
        "CREATE INDEX idx_sales_product ON fact_sales(product_key);",
        "CREATE INDEX idx_sales_territory ON fact_sales(territory_key);",
        "CREATE INDEX idx_sales_order_number ON fact_sales(order_number);",
        
        # Returns fact indexes
        "CREATE INDEX idx_returns_date ON fact_returns(return_date);",
        "CREATE INDEX idx_returns_product ON fact_returns(product_key);",
        "CREATE INDEX idx_returns_territory ON fact_returns(territory_key);",
        
        # Customer indexes
        "CREATE INDEX idx_customer_income ON dim_customers(annual_income);",
        "CREATE INDEX idx_customer_occupation ON dim_customers(occupation);",
        
        # Product indexes
        "CREATE INDEX idx_product_subcategory ON dim_products(product_subcategory_key);",
        "CREATE INDEX idx_product_price ON dim_products(product_price);",
        
        # Calendar indexes
        "CREATE INDEX idx_calendar_year ON dim_calendar(year);",
        "CREATE INDEX idx_calendar_month ON dim_calendar(month);"
    ]
    
    for idx_cmd in index_commands:
        cursor.execute(idx_cmd)
        index_name = idx_cmd.split("INDEX ")[1].split(" ON")[0]
        print(f"   ✓ Created {index_name}")
    
    conn.commit()
    cursor.close()
    print("\n✓ All indexes created successfully!")

# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_data(conn):
    """Validate loaded data."""
    print("\n" + "="*70)
    print("DATA VALIDATION")
    print("="*70)
    
    cursor = conn.cursor()
    
    validation_queries = [
        ("dim_calendar", "SELECT COUNT(*) FROM dim_calendar"),
        ("dim_customers", "SELECT COUNT(*) FROM dim_customers"),
        ("dim_product_categories", "SELECT COUNT(*) FROM dim_product_categories"),
        ("dim_product_subcategories", "SELECT COUNT(*) FROM dim_product_subcategories"),
        ("dim_products", "SELECT COUNT(*) FROM dim_products"),
        ("dim_territories", "SELECT COUNT(*) FROM dim_territories"),
        ("fact_sales", "SELECT COUNT(*) FROM fact_sales"),
        ("fact_returns", "SELECT COUNT(*) FROM fact_returns"),
    ]
    
    print("\nRecord Counts:")
    print("-" * 50)
    
    for table_name, query in validation_queries:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"   {table_name:<30} {count:>10,} records")
    
    # Additional validation
    print("\n\nData Quality Checks:")
    print("-" * 50)
    
    # Check for orphaned sales records
    cursor.execute("""
        SELECT COUNT(*) FROM fact_sales s
        LEFT JOIN dim_products p ON s.product_key = p.product_key
        WHERE p.product_key IS NULL
    """)
    orphaned_products = cursor.fetchone()[0]
    print(f"   Orphaned sales (missing products): {orphaned_products}")
    
    cursor.execute("""
        SELECT COUNT(*) FROM fact_sales s
        LEFT JOIN dim_customers c ON s.customer_key = c.customer_key
        WHERE c.customer_key IS NULL
    """)
    orphaned_customers = cursor.fetchone()[0]
    print(f"   Orphaned sales (missing customers): {orphaned_customers}")
    
    # Calculate revenue
    cursor.execute("""
        SELECT 
            SUM(s.order_quantity * p.product_price) as total_revenue,
            COUNT(DISTINCT s.order_number) as total_orders,
            COUNT(DISTINCT s.customer_key) as unique_customers
        FROM fact_sales s
        JOIN dim_products p ON s.product_key = p.product_key
    """)
    revenue_data = cursor.fetchone()
    print(f"\n   Total Revenue: ${revenue_data[0]:,.2f}" if revenue_data[0] else "   Total Revenue: $0.00")
    print(f"   Total Orders: {revenue_data[1]:,}")
    print(f"   Unique Customers: {revenue_data[2]:,}")
    
    cursor.close()
    print("\n✓ Validation complete!")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("ADVENTUREWORKS DATA LOADER")
    print("="*70)
    print(f"Database: {DB_CONFIG['database']}")
    print(f"Dataset Path: {DATASET_PATH}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Check if dataset path exists
    if not os.path.exists(DATASET_PATH):
        print(f"\n✗ ERROR: Dataset path not found: {DATASET_PATH}")
        print("Please update DATASET_PATH in the script.")
        sys.exit(1)
    
    # Check if all CSV files exist
    print("\nChecking CSV files...")
    missing_files = []
    for key, filename in CSV_FILES.items():
        filepath = os.path.join(DATASET_PATH, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)
        else:
            print(f"   ✓ Found: {filename}")
    
    if missing_files:
        print(f"\n✗ ERROR: Missing CSV files:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)
    
    print("\n✓ All CSV files found!")
    
    try:
        # Connect to database
        conn = get_connection()
        
        # Create tables
        create_tables(conn)
        
        # Load data in correct order (dimensions first, then facts)
        print("\n" + "="*70)
        print("LOADING DATA")
        print("="*70)
        
        load_calendar_data(conn)
        load_customers_data(conn)
        load_product_categories_data(conn)
        load_product_subcategories_data(conn)
        load_products_data(conn)
        load_territories_data(conn)
        load_sales_data(conn)
        load_returns_data(conn)
        
        # Create indexes
        create_indexes(conn)
        
        # Validate data
        validate_data(conn)
        
        # Close connection
        conn.close()
        
        print("\n" + "="*70)
        print("✓ DATA LOADING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nYou can now query the data in pgAdmin!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
