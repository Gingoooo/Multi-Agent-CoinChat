import os
import sqlite3
from langchain_core.tools import tool

# 連接到 SQLite 資料庫（或根據需要更改為其他資料庫）
def get_db_connection():
    conn = sqlite3.connect('db/transactions.db')
    conn.row_factory = sqlite3.Row
    return conn

@tool
def exec_sqlite3_sql(sql: str) -> str:
    """Execute SQL statement.
    
    Args:
        sql (str): SQL statement to execute, for example:
            INSERT INTO transactions (item, amount, date, transaction_type) 
            VALUES ('coffee', 100, '2024-02-05', 'Expense')
    
    Returns:
        str: Execution result
    """
    db_path = 'db/transactions.db'
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Executing SQL: {sql}")  # 除錯用
        cursor.execute(sql)
        conn.commit()
        conn.close()
        
        return "SQL execution successful"
    except Exception as e:
        error_msg = f"SQL execution error: {str(e)}"
        print(error_msg)  # 除錯用
        return error_msg

@tool
def execute_sql(sql: str) -> dict:
    """
    Execute the given SQL statement and return the results.

    Args:
        sql (str): The SQL statement to execute.

    Returns:
        dict: A dictionary containing execution results.
              - "status": Operation status ("success" or "failure").
              - "message": Detailed message (in case of failure).
              - "results": Query results (for successful SELECT statements).
    """
    print(f"Executing SQL: {sql}")  # Log the SQL statement being executed
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Check if the SQL statement is a SELECT query
        if sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            # Convert each row to dictionary format
            results = [dict(row) for row in rows]
            conn.close()
            print(f"SQL Execution Success: Retrieved {len(results)} records.")  # Log success
            return {
                "status": "success",
                "results": results
            }
        else:
            conn.commit()
            conn.close()
            print("SQL Execution Success: Non-SELECT statement executed.")  # Log success
            return {
                "status": "success",
                "message": "SQL statement executed successfully."
            }
    except Exception as e:
        print(f"SQL Execution Failure: {e}")  # Log failure
        return {
            "status": "failure",
            "message": f"Error executing SQL: {e}"
        }