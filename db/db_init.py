import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        """Initialize database manager"""
        self.db_path = db_path or os.getenv('DATABASE_PATH', 'db/bookkeeper.db')
        self.db_dir = os.path.dirname(self.db_path)
        self.table_name = os.getenv('TABLE_NAME', 'transactions')

    def init_database(self) -> None:
        """Initialize database and create necessary tables"""
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            transaction_type TEXT NOT NULL
        )
        """)
        
        # Create indices
        cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_date 
        ON {self.table_name}(date)
        """)
        
        cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_transaction_type 
        ON {self.table_name}(transaction_type)
        """)
        
        # Insert test data
        test_data = [
            ('Lunch', 150.0, '2024-03-01', 'Expense'),
            ('Salary', 50000.0, '2024-03-05', 'Income'),
            ('Transportation', 30.0, '2024-03-02', 'Expense'),
            ('Coffee', 80.0, '2024-03-03', 'Expense')
        ]
        
        cursor.executemany(f"""
        INSERT INTO {self.table_name} (item, amount, date, transaction_type)
        VALUES (?, ?, ?, ?)
        """, test_data)
        
        conn.commit()
        conn.close()
        print("Database initialization completed!")
        print(f"Database location: {os.path.abspath(self.db_path)}")

    def check_database(self) -> Dict[str, Any]:
        """Check database status and return status information"""
        status = {
            'exists': False,
            'table_exists': False,
            'record_count': 0,
            'error': None
        }
        
        try:
            status['exists'] = os.path.exists(self.db_path)
            if not status['exists']:
                return status
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'")
            status['table_exists'] = cursor.fetchone() is not None
            
            if status['table_exists']:
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                status['record_count'] = cursor.fetchone()[0]
            
            conn.close()
            
        except Exception as e:
            status['error'] = str(e)
            
        return status

    def clean_database(self) -> bool:
        """Clean all records in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"DELETE FROM {self.table_name}")
            
            conn.commit()
            conn.close()
            print("Database records have been cleaned")
            return True
            
        except Exception as e:
            print(f"Error occurred while cleaning database: {str(e)}")
            return False

def main():
    db_manager = DatabaseManager()
    
    # Check database status
    print("Checking database status...")
    status = db_manager.check_database()
    
    if status['error']:
        print(f"Error: {status['error']}")
        return
        
    print(f"Database file exists: {'Yes' if status['exists'] else 'No'}")
    print(f"Transactions table exists: {'Yes' if status['table_exists'] else 'No'}")
    print(f"Current record count: {status['record_count']}")
    
    # Ask whether to clean database
    if status['exists'] and status['record_count'] > 0:
        response = input("Do you want to clean the database? (y/n): ")
        if response.lower() == 'y':
            db_manager.clean_database()
    
    # Ask whether to reinitialize database
    response = input("Do you want to reinitialize the database? (y/n): ")
    if response.lower() == 'y':
        db_manager.init_database()
        
        # Check status again
        print("\nRechecking database status...")
        status = db_manager.check_database()
        print(f"Current record count: {status['record_count']}")

if __name__ == "__main__":
    main()