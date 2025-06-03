"""
Simple database test
"""
import sys
sys.path.append('.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.user_simple import User, UserRole, UserStatus
from app.core.security import get_password_hash

# Create database engine (using SQLite for testing)
engine = create_engine("sqlite:///./test.db", echo=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Check if super admin already exists
    super_admin = db.query(User).filter(User.email == "rfp@kzahhar.com").first()
    
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
        
    # Test login
    user = db.query(User).filter(User.email == "rfp@kzahhar.com").first()
    print(f"✅ User found: {user.full_name} ({user.role.value})")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    raise
finally:
    db.close()

print("✅ Database test completed successfully!")