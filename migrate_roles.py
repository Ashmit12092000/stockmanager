#!/usr/bin/env python3

from app import app
from database import db
from models import User, UserRole

def migrate_user_roles():
    """Migrate existing user roles to new enum system"""
    with app.app_context():
        # Find all users with network_admin role
        network_admin_users = User.query.filter_by(role=UserRole.NETWORK_ADMIN).all()

        print(f"Found {len(network_admin_users)} network_admin users to migrate")

        for user in network_admin_users:
            print(f"Migrating user: {user.username} ({user.full_name})")
            user.role = UserRole.MANAGER

        try:
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")

if __name__ == '__main__':
    migrate_user_roles()