"""
Enhanced database setup for Release 5 with document management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from .config import settings
from ..models.base import Base
from ..models.rfp_enhanced import RFPEnhanced, RFPDocument, RFPTemplate, RFPStatus, RFPType, DocumentType

# Import existing models
from ..models import User, Organization, UserRole, UserStatus, OrganizationStatus, SubscriptionTier, OrganizationType

# Create database engine
database_url_str = str(settings.DATABASE_URL)
engine = create_engine(
    database_url_str,
    pool_pre_ping=True,
    poolclass=StaticPool if database_url_str.startswith("sqlite") else None,
    connect_args={"check_same_thread": False} if database_url_str.startswith("sqlite") else {},
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_enhanced_tables():
    """Create enhanced database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_enhanced_db():
    """Initialize enhanced database with enhanced models and sample data"""
    from ..core.security import get_password_hash
    
    # Create tables
    create_enhanced_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if we need to create initial data
        existing_org = db.query(Organization).first()
        
        if not existing_org:
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
                        "advanced_analytics": True,
                        "enhanced_rfp_features": True,
                        "document_management": True
                    }
                }
            )
            db.add(default_org)
            db.flush()
            
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
            db.flush()
            
            print(f"✅ Created super admin user: {super_admin.email}")
            print(f"✅ Created default organization: {default_org.name}")
        else:
            # Get existing organization and admin user
            default_org = existing_org
            super_admin = db.query(User).filter(User.email == "rfp@kzahhar.com").first()
            
            if not super_admin:
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
                db.flush()
                print(f"✅ Created super admin user: {super_admin.email}")
        
        # Create default RFP templates
        existing_templates = db.query(RFPTemplate).filter(RFPTemplate.is_system_template == True).count()
        
        if existing_templates == 0:
            print("📝 Creating default RFP templates...")
            
            # Services Template
            services_template = RFPTemplate(
                name="Professional Services RFP",
                description="Standard template for professional services procurement",
                category="Professional Services",
                rfp_type=RFPType.SERVICES,
                is_system_template=True,
                created_by_id=super_admin.id,
                template_data={
                    "sections": [
                        {
                            "title": "Project Overview",
                            "required": True,
                            "description": "High-level description of the project and objectives"
                        },
                        {
                            "title": "Scope of Work",
                            "required": True,
                            "description": "Detailed description of services required"
                        },
                        {
                            "title": "Deliverables",
                            "required": True,
                            "description": "Expected deliverables and milestones"
                        },
                        {
                            "title": "Timeline",
                            "required": True,
                            "description": "Project timeline and key dates"
                        },
                        {
                            "title": "Qualifications",
                            "required": True,
                            "description": "Required qualifications and experience"
                        }
                    ]
                },
                default_requirements={
                    "minimum_experience_years": 3,
                    "certifications_required": [],
                    "insurance_required": True,
                    "security_clearance": False,
                    "local_presence_required": False
                },
                evaluation_criteria_template={
                    "technical_capability": {"weight": 40, "max_score": 100},
                    "experience": {"weight": 25, "max_score": 100},
                    "cost": {"weight": 25, "max_score": 100},
                    "timeline": {"weight": 10, "max_score": 100}
                },
                description_template="""
                <h2>Project Overview</h2>
                <p>This RFP seeks qualified service providers to deliver [PROJECT DESCRIPTION].</p>
                
                <h2>Background</h2>
                <p>[ORGANIZATION BACKGROUND AND CONTEXT]</p>
                
                <h2>Objectives</h2>
                <ul>
                    <li>[OBJECTIVE 1]</li>
                    <li>[OBJECTIVE 2]</li>
                    <li>[OBJECTIVE 3]</li>
                </ul>
                """,
                requirements_template="""
                <h2>Scope of Work</h2>
                <p>The selected vendor will be responsible for:</p>
                <ul>
                    <li>[REQUIREMENT 1]</li>
                    <li>[REQUIREMENT 2]</li>
                    <li>[REQUIREMENT 3]</li>
                </ul>
                
                <h2>Deliverables</h2>
                <ol>
                    <li>[DELIVERABLE 1] - [DATE]</li>
                    <li>[DELIVERABLE 2] - [DATE]</li>
                    <li>[DELIVERABLE 3] - [DATE]</li>
                </ol>
                
                <h2>Qualifications</h2>
                <ul>
                    <li>Minimum [X] years of experience in [FIELD]</li>
                    <li>[CERTIFICATION] certification preferred</li>
                    <li>Proven track record of [SPECIFIC EXPERIENCE]</li>
                </ul>
                """
            )
            db.add(services_template)
            
            # Technology Template
            tech_template = RFPTemplate(
                name="Technology Solutions RFP",
                description="Template for technology and software procurement",
                category="Technology",
                rfp_type=RFPType.TECHNOLOGY,
                is_system_template=True,
                created_by_id=super_admin.id,
                template_data={
                    "sections": [
                        {
                            "title": "Technical Requirements",
                            "required": True,
                            "description": "Detailed technical specifications"
                        },
                        {
                            "title": "System Architecture",
                            "required": True,
                            "description": "Proposed system architecture and integration"
                        },
                        {
                            "title": "Security Requirements",
                            "required": True,
                            "description": "Security, compliance, and data protection requirements"
                        },
                        {
                            "title": "Support & Maintenance",
                            "required": True,
                            "description": "Ongoing support and maintenance requirements"
                        }
                    ]
                },
                default_requirements={
                    "scalability": True,
                    "security_compliance": ["ISO 27001", "SOC 2"],
                    "uptime_requirement": "99.9%",
                    "support_hours": "24/7",
                    "data_backup_required": True,
                    "cloud_compatible": True
                },
                evaluation_criteria_template={
                    "technical_solution": {"weight": 35, "max_score": 100},
                    "security": {"weight": 25, "max_score": 100},
                    "cost": {"weight": 20, "max_score": 100},
                    "vendor_experience": {"weight": 15, "max_score": 100},
                    "support": {"weight": 5, "max_score": 100}
                }
            )
            db.add(tech_template)
            
            # Construction Template
            construction_template = RFPTemplate(
                name="Construction & Engineering RFP",
                description="Template for construction and engineering projects",
                category="Construction",
                rfp_type=RFPType.CONSTRUCTION,
                is_system_template=True,
                created_by_id=super_admin.id,
                template_data={
                    "sections": [
                        {
                            "title": "Project Specifications",
                            "required": True,
                            "description": "Detailed construction specifications"
                        },
                        {
                            "title": "Site Conditions",
                            "required": True,
                            "description": "Site access, conditions, and constraints"
                        },
                        {
                            "title": "Safety Requirements",
                            "required": True,
                            "description": "Health, safety, and environmental requirements"
                        },
                        {
                            "title": "Quality Standards",
                            "required": True,
                            "description": "Quality control and assurance requirements"
                        }
                    ]
                },
                default_requirements={
                    "licensing_required": True,
                    "insurance_minimum": 5000000,
                    "safety_certification": True,
                    "local_permits_required": True,
                    "environmental_compliance": True,
                    "warranty_period_months": 12
                },
                evaluation_criteria_template={
                    "technical_approach": {"weight": 30, "max_score": 100},
                    "experience": {"weight": 25, "max_score": 100},
                    "cost": {"weight": 25, "max_score": 100},
                    "safety_record": {"weight": 15, "max_score": 100},
                    "timeline": {"weight": 5, "max_score": 100}
                }
            )
            db.add(construction_template)
            
            db.commit()
            print("✅ Created 3 system RFP templates")
        
        # Create sample enhanced RFPs
        existing_enhanced_rfps = db.query(RFPEnhanced).count()
        
        if existing_enhanced_rfps == 0:
            print("📄 Creating sample enhanced RFPs...")
            
            from datetime import datetime, timedelta
            
            # Sample RFP 1: Professional Services
            sample_rfp1 = RFPEnhanced(
                title="Digital Transformation Consulting Services",
                description="Seeking experienced consultants to support our digital transformation initiative",
                description_html="""
                <h2>Project Overview</h2>
                <p>Our organization is embarking on a comprehensive digital transformation journey to modernize our operations, enhance customer experience, and improve operational efficiency. We are seeking qualified consulting partners to guide us through this strategic initiative.</p>
                
                <h2>Background</h2>
                <p>We are a mid-sized organization with legacy systems that need modernization. Our goal is to implement cloud-based solutions, automate manual processes, and create a data-driven decision-making culture.</p>
                
                <h2>Objectives</h2>
                <ul>
                    <li>Assess current technology landscape and identify improvement opportunities</li>
                    <li>Develop a comprehensive digital transformation roadmap</li>
                    <li>Implement cloud migration strategy</li>
                    <li>Establish data governance and analytics capabilities</li>
                    <li>Train staff on new technologies and processes</li>
                </ul>
                """,
                rfp_number="RFP-2025-001",
                rfp_type=RFPType.CONSULTING,
                category="Digital Transformation",
                issue_date=datetime.utcnow().date(),
                submission_deadline=datetime.utcnow() + timedelta(days=30),
                publication_date=datetime.utcnow(),
                clarification_deadline=datetime.utcnow() + timedelta(days=20),
                estimated_budget=500000.0,
                budget_range_min=400000.0,
                budget_range_max=600000.0,
                currency="USD",
                requirements={
                    "minimum_experience_years": 5,
                    "team_size_minimum": 3,
                    "certifications_required": ["PMP", "Cloud Certifications"],
                    "industry_experience": ["Technology", "Consulting"],
                    "project_duration_months": 12
                },
                requirements_html="""
                <h2>Scope of Work</h2>
                <p>The selected consulting partner will be responsible for:</p>
                <ul>
                    <li>Conducting comprehensive technology assessment</li>
                    <li>Developing digital transformation strategy and roadmap</li>
                    <li>Leading cloud migration initiatives</li>
                    <li>Implementing data analytics solutions</li>
                    <li>Providing change management support</li>
                    <li>Training and knowledge transfer</li>
                </ul>
                
                <h2>Deliverables</h2>
                <ol>
                    <li>Current State Assessment Report - Month 2</li>
                    <li>Digital Transformation Strategy - Month 3</li>
                    <li>Implementation Roadmap - Month 4</li>
                    <li>Cloud Migration Plan - Month 6</li>
                    <li>Data Strategy Document - Month 8</li>
                    <li>Training Materials and Programs - Month 10</li>
                    <li>Final Implementation Report - Month 12</li>
                </ol>
                """,
                evaluation_criteria={
                    "technical_capability": {"weight": 35, "max_score": 100, "description": "Technical expertise and methodology"},
                    "experience": {"weight": 30, "max_score": 100, "description": "Relevant experience and case studies"},
                    "team_qualifications": {"weight": 20, "max_score": 100, "description": "Team composition and qualifications"},
                    "cost": {"weight": 15, "max_score": 100, "description": "Cost competitiveness and value"}
                },
                contact_person="Sarah Johnson",
                contact_email="procurement@tenderwise.ai",
                contact_phone="+1-555-0123",
                is_public=True,
                status=RFPStatus.PUBLISHED,
                organization_id=default_org.id,
                created_by_id=super_admin.id,
                is_template_based=True,
                template_id=1  # Services template
            )
            db.add(sample_rfp1)
            
            # Sample RFP 2: Technology
            sample_rfp2 = RFPEnhanced(
                title="Enterprise Resource Planning (ERP) System Implementation",
                description="Implementation of comprehensive ERP system for manufacturing operations",
                description_html="""
                <h2>Project Overview</h2>
                <p>We are seeking a qualified vendor to implement a comprehensive ERP system to replace our legacy systems and streamline our manufacturing operations across multiple locations.</p>
                
                <h2>Current Challenges</h2>
                <ul>
                    <li>Fragmented systems across departments</li>
                    <li>Manual data entry and reporting processes</li>
                    <li>Limited real-time visibility into operations</li>
                    <li>Inefficient inventory management</li>
                    <li>Lack of integrated financial reporting</li>
                </ul>
                """,
                rfp_number="RFP-2025-002",
                rfp_type=RFPType.TECHNOLOGY,
                category="Enterprise Software",
                issue_date=datetime.utcnow().date(),
                submission_deadline=datetime.utcnow() + timedelta(days=45),
                publication_date=datetime.utcnow(),
                clarification_deadline=datetime.utcnow() + timedelta(days=30),
                estimated_budget=2000000.0,
                budget_range_min=1500000.0,
                budget_range_max=2500000.0,
                currency="USD",
                requirements={
                    "manufacturing_modules": True,
                    "financial_management": True,
                    "inventory_management": True,
                    "reporting_analytics": True,
                    "mobile_access": True,
                    "cloud_deployment": True,
                    "integration_apis": True,
                    "user_capacity": 500
                },
                evaluation_criteria={
                    "functional_fit": {"weight": 30, "max_score": 100},
                    "technical_architecture": {"weight": 25, "max_score": 100},
                    "vendor_experience": {"weight": 20, "max_score": 100},
                    "total_cost": {"weight": 15, "max_score": 100},
                    "implementation_approach": {"weight": 10, "max_score": 100}
                },
                contact_person="Michael Chen",
                contact_email="it.procurement@tenderwise.ai",
                contact_phone="+1-555-0124",
                is_public=True,
                status=RFPStatus.OPEN,
                organization_id=default_org.id,
                created_by_id=super_admin.id,
                is_template_based=True,
                template_id=2  # Technology template
            )
            db.add(sample_rfp2)
            
            # Sample RFP 3: Construction
            sample_rfp3 = RFPEnhanced(
                title="Corporate Headquarters Renovation",
                description="Comprehensive renovation of corporate headquarters building",
                rfp_number="RFP-2025-003",
                rfp_type=RFPType.CONSTRUCTION,
                category="Building Renovation",
                issue_date=datetime.utcnow().date(),
                submission_deadline=datetime.utcnow() + timedelta(days=60),
                publication_date=datetime.utcnow(),
                clarification_deadline=datetime.utcnow() + timedelta(days=40),
                estimated_budget=5000000.0,
                budget_range_min=4000000.0,
                budget_range_max=6000000.0,
                currency="USD",
                requirements={
                    "leed_certification_required": True,
                    "building_area_sqft": 50000,
                    "parking_spaces": 200,
                    "construction_duration_months": 18,
                    "minimal_business_disruption": True,
                    "sustainability_features": True
                },
                evaluation_criteria={
                    "technical_approach": {"weight": 25, "max_score": 100},
                    "experience": {"weight": 25, "max_score": 100},
                    "cost": {"weight": 25, "max_score": 100},
                    "timeline": {"weight": 15, "max_score": 100},
                    "sustainability": {"weight": 10, "max_score": 100}
                },
                contact_person="David Williams",
                contact_email="facilities@tenderwise.ai",
                contact_phone="+1-555-0125",
                is_public=False,
                status=RFPStatus.DRAFT,
                organization_id=default_org.id,
                created_by_id=super_admin.id,
                is_template_based=True,
                template_id=3  # Construction template
            )
            db.add(sample_rfp3)
            
            db.commit()
            print("✅ Created 3 sample enhanced RFPs")
        
        print("🎉 Enhanced database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing enhanced database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def reset_enhanced_db():
    """Reset enhanced database - USE WITH CAUTION!"""
    print("⚠️  WARNING: This will delete all data including enhanced models!")
    confirmation = input("Type 'RESET_ENHANCED' to confirm: ")
    
    if confirmation == "RESET_ENHANCED":
        Base.metadata.drop_all(bind=engine)
        print("🗑️  Dropped all tables")
        init_enhanced_db()
        print("✅ Enhanced database reset completed")
    else:
        print("❌ Enhanced database reset cancelled")


if __name__ == "__main__":
    # Allow running this file directly to initialize enhanced database
    init_enhanced_db()