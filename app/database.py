import sqlite3
import csv
import os
from datetime import datetime

# Use absolute paths so it works during deployment and testing
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "sales.db")
CSV_PATH = os.path.join(BASE_DIR, "data", "sales.csv")

def get_db_connection():
    """Establish a read-only or standard connection to the database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    """Reads the CSV, validates data, and populates the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            Transaction_Id TEXT PRIMARY KEY,
            Order_date DATE,
            Product TEXT,
            Category TEXT,
            Region TEXT,
            Sales_channel TEXT,
            Quantity INTEGER,
            Unit_price REAL,
            Discount_amount REAL,
            Status TEXT,
            Revenue REAL
        )
    ''')
    
    # Clear existing data so we don't duplicate on restarts (useful for Render deployment)
    cursor.execute('DELETE FROM sales')

    stats = {
        "rows_processed": 0,
        "successfully_imported": 0,
        "rejected_rows": 0,
        "rejection_reasons": []
    }

    if not os.path.exists(CSV_PATH):
        print("Warning: CSV file not found at", CSV_PATH)
        return stats

    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stats["rows_processed"] += 1
            txn_id = row['Transaction_Id']
            
            # Validation 1: Check for missing unit price
            if not row['Unit_price'] or row['Unit_price'].strip() == "":
                stats["rejected_rows"] += 1
                stats["rejection_reasons"].append(f"{txn_id}: Missing Unit_price")
                continue

            # Validation 2: Check for invalid quantity
            try:
                qty = int(row['Quantity'])
                if qty <= 0:
                    stats["rejected_rows"] += 1
                    stats["rejection_reasons"].append(f"{txn_id}: Quantity is zero or negative")
                    continue
            except ValueError:
                stats["rejected_rows"] += 1
                stats["rejection_reasons"].append(f"{txn_id}: Invalid Quantity format")
                continue
                
            # Date formatting (DD-MM-YYYY to YYYY-MM-DD for proper SQL sorting)
            try:
                raw_date = row['Order_date']
                parsed_date = datetime.strptime(raw_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
                stats["rejected_rows"] += 1
                stats["rejection_reasons"].append(f"{txn_id}: Malformed date {raw_date}")
                continue

            unit_price = float(row['Unit_price'])
            discount = float(row['Discount_amount']) if row['Discount_amount'] else 0.0
            
            # Pre-calculate Revenue for convenience, but rely on SQL for aggregations
            revenue = (qty * unit_price) - discount

            # Insert valid row
            cursor.execute('''
                INSERT INTO sales (Transaction_Id, Order_date, Product, Category, Region, Sales_channel, Quantity, Unit_price, Discount_amount, Status, Revenue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                txn_id, parsed_date, row['Product'], row['Category'], 
                row['Region'], row['Sales_channel'], qty, unit_price, discount, row['Status'], revenue
            ))
            stats["successfully_imported"] += 1

    conn.commit()
    conn.close()
    return stats

# Initialize database when this module is run directly for testing
if __name__ == "__main__":
    results = init_db()
    print("Database Initialization Complete:")
    print(results)