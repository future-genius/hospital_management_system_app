#!/usr/bin/env python
"""
Database migration script to recreate the database with the new schema.
"""
import os
import shutil

def migrate_database():
    """Delete and recreate the database with new schema."""
    db_path = 'instance/app.db'
    
    print("Step 1: Removing old database...")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"  ✓ Removed {db_path}")
        except Exception as e:
            print(f"  ! Could not remove file: {e}")
    
    print("\nStep 2: Importing app and models...")
    from app import app
    from models import db
    
    print("\nStep 3: Creating new database with updated schema...")
    with app.app_context():
        db.create_all()
        print("  ✓ All tables created")
    
    print("\nStep 4: Populating initial data...")
    from init_db import setup_database
    setup_database()
    
    print("\n" + "="*50)
    print("✓ Database migration completed successfully!")
    print("="*50)

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
