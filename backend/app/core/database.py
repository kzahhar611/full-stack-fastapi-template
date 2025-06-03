"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from .config import settings
from ..models.base import Base

# Create database engine
database_url_str = str(settings.DATABASE_URL)
engine = create_engine(
    database_url_str,
    pool_pre_ping=True,
    # Use StaticPool for SQLite to avoid threading issues
    poolclass=StaticPool if database_url_str.startswith("sqlite") else None,
    connect_args={"check_same_thread": False} if database_url_str.startswith("sqlite") else {},
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


# For testing and development
def get_db_session() -> Session:
    """Get a database session (for scripts and testing)"""
    return SessionLocal()


def init_db():
    """Initialize database with tables and initial data"""
    from ..models import User, Organization, UserRole, UserStatus, OrganizationStatus, SubscriptionTier, OrganizationType
    from .security import get_password_hash
    
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
            # Create default organization
            default_org = Organization(
                name="TenderWise AI",
                slug="tenderwise-ai",
                description="Default organization for TenderWise AI platform",
                organization_type=OrganizationType.TECHNOLOGY,
                status=OrganizationStatus.ACTIVE,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                settings={
                    "default_language": "en",
                    "default_timezone": "UTC",
                    "features": {
                        "ai_workflows": True,
                        "document_processing": True,
                        "multi_language": True,
                        "advanced_analytics": True
                    }
                }
            )
            db.add(default_org)
            db.flush()  # Get the ID
            
            # Create super admin user
            super_admin = User(
                email="rfp@kzahhar.com",
                hashed_password=get_password_hash("password123"),
                first_name="System",
                last_name="Administrator",
                display_name="Super Admin",
                role=UserRole.SUPER_ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True,
                organization_id=default_org.id,
                preferences={
                    "language": "en",
                    "timezone": "UTC",
                    "theme": "dark",
                    "notifications": {
                        "email": True,
                        "in_app": True
                    }
                }
            )
            db.add(super_admin)
            db.commit()
            
            print(f"✅ Created super admin user: {super_admin.email}")
            print(f"✅ Created default organization: {default_org.name}")
        else:
            print(f"ℹ️  Super admin user already exists: {super_admin.email}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def reset_db():
    """Reset database (drop and recreate all tables) - USE WITH CAUTION!"""
    print("⚠️  WARNING: This will delete all data!")
    confirmation = input("Type 'RESET' to confirm: ")
    
    if confirmation == "RESET":
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Dropped all tables")
        init_db()
        print("✅ Database reset completed")
    else:
        print("❌ Database reset cancelled")


if __name__ == "__main__":
    # Allow running this file directly to initialize database
    init_db()