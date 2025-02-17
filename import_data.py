"""
Google Play Store Data Import Script

This script imports data from a CSV file into a PostgreSQL database. It processes the data
in chunks to minimize memory usage and provides progress bars for all operations.

The script handles three main entities:
1. Categories - App categories (e.g., Games, Education)
2. Developers - App developers with their details
3. Apps - The main app data with references to categories and developers
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
import time
from tqdm import tqdm

# Configuration
CSV_PATH = 'data/Google-Playstore.csv'
CHUNK_SIZE = 10000  # Adjust based on available memory
BATCH_SIZE = 1000   # Size for database inserts
DB_PARAMS = {
    'dbname': 'playstore',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

class DataProcessor:
    """Handles data processing and database operations for the import process."""
    
    def __init__(self, conn):
        """Initialize with a database connection."""
        self.conn = conn
    
    def clean_numeric(self, value, max_value=2147483647):
        """
        Convert string numeric values to proper numeric types.
        Handles PostgreSQL integer limits (max 2^31-1 = 2147483647).
        """
        if pd.isna(value):
            return None
        try:
            num = int(float(str(value).replace(',', '').replace('+', '')))
            # Handle PostgreSQL integer limits
            return min(num, max_value)
        except (ValueError, TypeError):
            return None
    
    def clean_price(self, value):
        """Convert price strings to float values."""
        if pd.isna(value):
            return None
        return float(str(value).replace('$', '').replace(',', ''))
    
    def parse_boolean(self, value):
        """Convert string boolean values to Python booleans."""
        if pd.isna(value):
            return False
        return str(value).lower() == 'true'
    
    def parse_date(self, date_str):
        """Convert date strings to Python date objects."""
        if pd.isna(date_str):
            return None
        try:
            return datetime.strptime(date_str, '%b %d, %Y').date()
        except:
            return None
    
    def get_category_map(self):
        """Get mapping of category names to IDs."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name FROM categories")
            return {row[1]: row[0] for row in cur.fetchall()}
    
    def get_developer_map(self):
        """Get mapping of developer (name, email) to IDs."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, name, email FROM developers")
            return {(row[1], row[2]): row[0] for row in cur.fetchall()}
    
    def process_categories(self, total_rows):
        """Process categories in chunks and return category mapping."""
        print("\nProcessing categories...")
        categories_set = set()
        
        # Read unique categories
        with tqdm(total=total_rows, desc="Reading categories") as pbar:
            for chunk in pd.read_csv(CSV_PATH, usecols=['Category'], chunksize=CHUNK_SIZE):
                categories_set.update(chunk['Category'].unique())
                pbar.update(len(chunk))
        
        # Insert categories in batches
        categories_df = pd.DataFrame(list(categories_set), columns=['name'])
        print(f"\nFound {len(categories_df)} unique categories")
        
        # Insert in batches
        batches = range(0, len(categories_df), BATCH_SIZE)
        with tqdm(total=len(categories_df), desc="Inserting categories") as pbar:
            for i in batches:
                batch = categories_df.iloc[i:i + BATCH_SIZE]
                self._insert_categories_batch(batch)
                pbar.update(len(batch))
        
        # Get category mapping
        category_map = self.get_category_map()
        return category_map
    
    def process_developers(self, total_rows):
        """Process developers in chunks and return developer mapping."""
        print("\nProcessing developers...")
        developers_set = set()
        
        # Read unique developers
        with tqdm(total=total_rows, desc="Reading developers") as pbar:
            for chunk in pd.read_csv(CSV_PATH, 
                                   usecols=['Developer Id', 'Developer Website', 'Developer Email'],
                                   chunksize=CHUNK_SIZE):
                chunk_developers = list(zip(chunk['Developer Id'], 
                                         chunk['Developer Website'].fillna(''),
                                         chunk['Developer Email'].fillna('')))
                developers_set.update(chunk_developers)
                pbar.update(len(chunk))
        
        # Insert developers in batches
        developers_df = pd.DataFrame(list(developers_set), columns=['name', 'website', 'email'])
        print(f"\nFound {len(developers_df)} unique developers")
        
        # Insert in batches
        batches = range(0, len(developers_df), BATCH_SIZE)
        with tqdm(total=len(developers_df), desc="Inserting developers") as pbar:
            for i in batches:
                batch = developers_df.iloc[i:i + BATCH_SIZE]
                self._insert_developers_batch(batch)
                pbar.update(len(batch))
        
        # Get developer mapping
        developer_map = self.get_developer_map()
        return developer_map
    
    def process_apps(self, total_rows, category_map, developer_map):
        """Process apps in chunks."""
        print("\nProcessing apps...")
        processed_rows = 0
        
        with tqdm(total=total_rows, desc="Importing apps") as pbar:
            for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE):
                apps_data = self._process_app_chunk(chunk, category_map, developer_map)
                self._insert_apps_batch(apps_data)
                processed_rows += len(chunk)
                pbar.update(len(chunk))
        
        return processed_rows
    
    def _process_app_chunk(self, chunk, category_map, developer_map):
        """Process a chunk of app data."""
        apps_data = []
        for _, row in chunk.iterrows():
            dev_id = developer_map.get((row['Developer Id'], row['Developer Email']))
            category_id = category_map.get(row['Category'])
            
            if dev_id is None or category_id is None:
                continue

            try:
                app_data = (
                    row['App Name'],
                    row['App Id'],
                    category_id,
                    dev_id,
                    float(row['Rating']) if pd.notna(row['Rating']) else None,
                    self.clean_numeric(row['Rating Count']),
                    str(self.clean_numeric(row['Installs'], max_value=9223372036854775807)),  # bigint max
                    self.clean_numeric(row['Minimum Installs']),  # int4 max
                    self.clean_numeric(row['Maximum Installs']),  # int4 max
                    self.parse_boolean(row['Free']),
                    self.clean_price(row['Price']),
                    row['Currency'],
                    row['Size'],
                    row['Minimum Android'],
                    self.parse_date(row['Released']),
                    self.parse_date(row['Last Updated']),
                    row['Content Rating'],
                    row['Privacy Policy'],
                    self.parse_boolean(row['Ad Supported']),
                    self.parse_boolean(row['In App Purchases']),
                    self.parse_boolean(row['Editors Choice']),
                    datetime.strptime(row['Scraped Time'], '%Y-%m-%d %H:%M:%S')
                )
                apps_data.append(app_data)
            except Exception as e:
                print(f"Error processing row {row['App Id']}: {e}")
                continue
                
        return apps_data

    def _insert_categories_batch(self, categories_df):
        """Insert a batch of categories into database."""
        try:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO categories (name) VALUES %s ON CONFLICT (name) DO NOTHING",
                    categories_df.values
                )
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting category batch: {e}")

    def _insert_developers_batch(self, developers_df):
        """Insert a batch of developers into database."""
        try:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO developers (name, website, email) 
                    VALUES %s 
                    ON CONFLICT (name, email) DO NOTHING
                    """,
                    developers_df.values
                )
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting developer batch: {e}")

    def _insert_apps_batch(self, apps_data):
        """Insert a batch of apps into database."""
        if not apps_data:
            return 0
            
        try:
            with self.conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO apps (
                        name, app_id, category_id, developer_id, rating, rating_count,
                        installs, min_installs, max_installs, is_free, price, currency,
                        size, min_android, released_date, last_updated, content_rating,
                        privacy_policy_url, has_ads, has_in_app_purchases,
                        is_editors_choice, scraped_time
                    )
                    VALUES %s
                    ON CONFLICT (app_id) DO NOTHING
                    """,
                    apps_data
                )
                self.conn.commit()
                return len(apps_data)
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting batch: {e}")
            return 0

def main():
    """Main function to run the import process."""
    # Create a connection pool
    pool = SimpleConnectionPool(1, 10, **DB_PARAMS)
    conn = pool.getconn()
    
    try:
        # Get total rows for progress tracking
        total_rows = sum(1 for _ in open(CSV_PATH)) - 1
        
        print("Starting data import...")
        start_time = time.time()
        
        # Initialize processor
        processor = DataProcessor(conn)
        
        # Process each entity
        category_map = processor.process_categories(total_rows)
        developer_map = processor.process_developers(total_rows)
        processed_rows = processor.process_apps(total_rows, category_map, developer_map)
        
        # Print summary
        end_time = time.time()
        print(f"\nData import completed successfully!")
        print(f"Total time: {end_time - start_time:.2f} seconds")
        print(f"Processed {processed_rows:,} rows")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pool.putconn(conn)
        pool.closeall()

if __name__ == "__main__":
    main()
