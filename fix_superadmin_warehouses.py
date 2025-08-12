
#!/usr/bin/env python3
"""
Script to assign all warehouses to existing superadmin users
"""

from app import app
from models import User, UserRole, Location
from database import db

def fix_superadmin_warehouses():
    """Assign all warehouses to superadmin users who don't have any assigned"""
    with app.app_context():
        # Get all superadmin users
        superadmin_users = User.query.filter_by(role=UserRole.SUPERADMIN).all()
        all_warehouses = Location.query.all()
        
        for user in superadmin_users:
            # Clear existing assignments and assign all warehouses
            user.assigned_warehouses.clear()
            for warehouse in all_warehouses:
                user.assigned_warehouses.append(warehouse)
            
            print(f"Assigned {len(all_warehouses)} warehouses to superadmin user: {user.username}")
        
        try:
            db.session.commit()
            print(f"Successfully updated {len(superadmin_users)} superadmin users")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating superadmin users: {e}")

if __name__ == '__main__':
    fix_superadmin_warehouses()
