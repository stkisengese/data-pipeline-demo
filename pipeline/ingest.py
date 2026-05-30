import pandas as pd
import sqlite3
import os
from datetime import datetime

def ingest_csv_to_bronze(csv_path, table_name, db_path='data/humanitarian.db'):
    """
    Reads a CSV file and loads it into a SQLite table (Bronze layer).
    Adds an 'ingestion_timestamp' column.
    """
    print(f"Ingesting {csv_path} into {table_name}...")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source file not found: {csv_path}")
    
    # Read raw data
    df = pd.read_csv(csv_path)
    
    # Add ingestion metadata
    df['ingestion_timestamp'] = datetime.now().isoformat()
    
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    
    try:
        # Load into bronze table (overwrite if exists to keep it simple for this demo)
        df.to_sql(f"bronze_{table_name}", conn, if_exists='replace', index=False)
        print(f"Successfully loaded {len(df)} rows into bronze_{table_name}.")
    finally:
        conn.close()

def main():
    db_path = 'data/humanitarian.db'
    os.makedirs('data', exist_ok=True)
    
    # Define sources and their target bronze tables
    sources = [
        ('data/raw/beneficiaries.csv', 'beneficiaries'),
        ('data/raw/activities.csv', 'activities'),
        ('data/raw/disbursements.csv', 'disbursements')
    ]
    
    for csv_path, table_name in sources:
        ingest_csv_to_bronze(csv_path, table_name, db_path)

if __name__ == "__main__":
    main()
