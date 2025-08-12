
#!/usr/bin/env python3

from app import create_app
from database import db
from sqlalchemy import text

def migrate_threshold():
    """Add low_stock_threshold column to items table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(items)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'low_stock_threshold' not in columns:
                print("Adding low_stock_threshold column to items table...")
                db.session.execute(text("ALTER TABLE items ADD COLUMN low_stock_threshold NUMERIC(10,2) DEFAULT 5"))
                db.session.commit()
                print("✅ Column added successfully!")
                
                # Update existing items with default threshold
                db.session.execute(text("UPDATE items SET low_stock_threshold = 5 WHERE low_stock_threshold IS NULL"))
                db.session.commit()
                print("✅ Default thresholds set for existing items!")
            else:
                print("✅ low_stock_threshold column already exists!")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_threshold()
