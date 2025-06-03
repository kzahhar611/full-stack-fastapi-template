"""
Initialize Database with Admin User
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from core.config import settings
from core.database import engine
from models.user import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_admin_user():
    """Create the admin user if it doesn't exist"""
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = session.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        
        if admin_user:
            print(f"Admin user {settings.FIRST_SUPERUSER} already exists")
            return
        
        # Create admin user
        admin_user = User(
            email=settings.FIRST_SUPERUSER,
            hashed_password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            is_verified=True,
            organization="TenderWise AI",
            position="System Administrator",
            language="en",
            timezone="UTC",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        session.add(admin_user)
        session.commit()
        
        print(f"Admin user {settings.FIRST_SUPERUSER} created successfully")
        print(f"Password: {settings.FIRST_SUPERUSER_PASSWORD}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Initializing database...")
    create_admin_user()
    print("Database initialization complete!")