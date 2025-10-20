"""
DevBhoomi SQLite Setup Script
"""

import os
import sys

def setup_database():
    """Setup SQLite Database And Create Tables"""
    try:
        # Add Current Directory To Path So We Can Import Our Modules
        sys.path.insert(0, os.path.dirname(__file__))

        from Config import Config
        from Models import db

        # Create Flask App Context For Database Operations
        from flask import Flask
        app = Flask(__name__)
        app.config.from_object(Config)

        # Initialize Database With App
        db.init_app(app)

        with app.app_context():
            # Create All Tables
            db.create_all()
            print("✓ Database Tables Created Successfully")

        return True

    except Exception as e:
        print(f"✗ Error Setting Up Database: {e}")
        return False

def create_directories():
    """Create Necessary Directories"""
    directories = ['Instance', 'Flask_Session', 'Repositories', 'Uploads']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ Created Directory: {directory}")
        else:
            print(f"✓ Directory Already Exists: {directory}")

def main():
    """Main Setup Function"""
    print("DevBhoomi SQLite Setup")
    print("=" * 40)

    print("\n1. Creating Directories...")
    create_directories()

    print("\n2. Setting Up Database...")
    if not setup_database():
        print("Failed To Setup Database.")
        return 1

    print("\n3. Setup Complete!")
    print("\nTo Run The Application:")
    print("  python App.py")
    print("\nAccess The Application At: http://localhost:5000")

    return 0

if __name__ == '__main__':
    sys.exit(main())