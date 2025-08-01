
#!/usr/bin/env python3
"""
Database migration script to add missing columns to existing database
"""

import sqlite3
import os

def migrate_database():
    db_path = 'instance/stockflow.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database...")
        from app import app, db
        with app.app_context():
            db.create_all()
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if approval_flow column exists
        cursor.execute("PRAGMA table_info(stock_issue_request)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'approval_flow' not in columns:
            print("Adding approval_flow column...")
            cursor.execute("ALTER TABLE stock_issue_request ADD COLUMN approval_flow VARCHAR(20) DEFAULT 'regular'")
        
        if 'approver_id' not in columns:
            print("Adding approver_id column...")
            cursor.execute("ALTER TABLE stock_issue_request ADD COLUMN approver_id INTEGER")
        
        # Update status column to include new statuses if needed
        print("Migration completed successfully!")
        
        conn.commit()
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
