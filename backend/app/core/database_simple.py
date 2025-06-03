"""
Simplified database configuration for testing
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from .config import settings
from ..models.base import Base

# Create database engine (using SQLite for development)
DATABASE_URL = "sqlite:///./tenderwise_ai.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and initial data"""
    from ..models.user_simple import User, UserRole, UserStatus
    from ..core.security import get_password_hash
    
    # Create tables
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if super admin already exists
        super_admin = db.query(User).filter(
            User.email == "rfp@kzahhar.com"
        ).first()
        
        if not super_admin:
            # Create super admin user
            super_admin = User(
                email="rfp@kzahhar.com",
                hashed_password=get_password_hash("password123"),
                first_name="System",
                last_name="Administrator",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True
            )
            db.add(super_admin)
            db.commit()
            
            print(f"✅ Created super admin user: {super_admin.email}")
        else:
            print(f"ℹ️  Super admin user already exists: {super_admin.email}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Allow running this file directly to initialize database
    init_db()