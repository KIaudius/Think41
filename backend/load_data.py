import pandas as pd
import sqlite3
import os
from datetime import datetime

def load_csv_to_sqlite():
    """Load CSV files from dataset directory into SQLite database"""
    
    # Connect to SQLite database
    conn = sqlite3.connect('ecommerce.db')
    
    # Path to dataset directory
    dataset_path = '../dataset'
    
    # List of CSV files to load
    csv_files = [
        'users.csv',
        'distribution_centers.csv', 
        'products.csv',
        'inventory_items.csv',
        'orders.csv',
        'order_items.csv'
    ]
    
    for csv_file in csv_files:
        file_path = os.path.join(dataset_path, csv_file)
        
        if os.path.exists(file_path):
            print(f"Loading {csv_file}...")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Convert datetime columns
            datetime_columns = ['created_at', 'sold_at', 'shipped_at', 'delivered_at', 'returned_at']
            for col in datetime_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Determine table name based on CSV filename
            table_name = csv_file.replace('.csv', '')
            
            # Load data into SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Loaded {len(df)} rows into {table_name} table")
        else:
            print(f"Warning: {file_path} not found")
    
    conn.close()
    print("Data loading completed!")

if __name__ == "__main__":
    load_csv_to_sqlite() 