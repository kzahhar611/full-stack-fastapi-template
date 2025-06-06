#!/usr/bin/env python3
"""
Create Compliance Analysis Tables for TenderWise AI Platform
Module 2: Proposal Compliance & Vendor Assessment

This script creates the database tables for compliance analysis functionality.
Run this script to set up the database schema for Module 2.
"""

import sys
import os
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import models to ensure they are registered
from app.core.database import Base
from app.models.user import User
from app.models.organization import Organization
from app.models.rfp import RFP
from app.models.rfp_analysis import RFPAnalysis  # Module 1 tables
from app.models.compliance_analysis import (  # Module 2 tables
    ComplianceAnalysis, RFPRequirement, VendorProposal, 
    ComplianceMatrix, ComplianceScore
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///./tenderwise_ai.db"


def create_compliance_tables():
    """Create compliance analysis tables in the database"""
    try:
        logger.info("Starting compliance analysis table creation")
        
        # Create engine and session
        engine = create_engine(DATABASE_URL, echo=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create all tables (only new ones will be created)
        logger.info("Creating database tables...")
        
        # Import specific tables for compliance analysis only
        from app.models.compliance_analysis import (
            ComplianceAnalysis, RFPRequirement, VendorProposal, 
            ComplianceMatrix, ComplianceScore
        )
        
        # Create only the compliance analysis tables
        compliance_tables = [
            ComplianceAnalysis.__table__,
            RFPRequirement.__table__,
            VendorProposal.__table__,
            ComplianceMatrix.__table__,
            ComplianceScore.__table__
        ]
        
        for table in compliance_tables:
            try:
                table.create(bind=engine, checkfirst=True)
                logger.info(f"Created/verified table: {table.name}")
            except Exception as e:
                logger.warning(f"Table {table.name} already exists or error: {e}")
        
        # Verify tables were created
        db = SessionLocal()
        
        # Check if tables exist
        table_names = [
            'compliance_analyses',
            'rfp_requirements', 
            'vendor_proposals',
            'compliance_matrix',
            'compliance_scores'
        ]
        
        for table_name in table_names:
            result = db.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
            if result.fetchone():
                logger.info(f"✅ Table '{table_name}' created successfully")
            else:
                logger.error(f"❌ Table '{table_name}' was not created")
        
        # Display table structure
        logger.info("\n" + "="*60)
        logger.info("COMPLIANCE ANALYSIS DATABASE SCHEMA")
        logger.info("="*60)
        
        for table_name in table_names:
            logger.info(f"\n📊 Table: {table_name}")
            result = db.execute(text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            
            for column in columns:
                col_name = column[1]
                col_type = column[2]
                not_null = "NOT NULL" if column[3] else "NULL"
                primary_key = "PRIMARY KEY" if column[5] else ""
                logger.info(f"  - {col_name:<25} {col_type:<15} {not_null:<8} {primary_key}")
        
        # Show foreign key relationships
        logger.info(f"\n🔗 Foreign Key Relationships:")
        for table_name in table_names:
            result = db.execute(text(f"PRAGMA foreign_key_list({table_name})"))
            fks = result.fetchall()
            
            for fk in fks:
                from_col = fk[3]
                to_table = fk[2]
                to_col = fk[4]
                logger.info(f"  {table_name}.{from_col} -> {to_table}.{to_col}")
        
        # Test data insertion and retrieval
        logger.info(f"\n🧪 Testing database operations...")
        
        # Test compliance analysis creation
        test_analysis = ComplianceAnalysis(
            user_id="test-user-id",
            rfp_document_name="Test RFP.pdf",
            rfp_content="This is a test RFP content for compliance analysis.",
            total_requirements=0,
            total_proposals=0
        )
        
        db.add(test_analysis)
        db.commit()
        db.refresh(test_analysis)
        
        logger.info(f"✅ Test compliance analysis created: {test_analysis.id}")
        
        # Test requirement creation
        test_requirement = RFPRequirement(
            compliance_analysis_id=test_analysis.id,
            requirement_text="The system shall provide user authentication functionality.",
            requirement_summary="User authentication requirement",
            requirement_category="Security",
            weight=1.0
        )
        
        db.add(test_requirement)
        db.commit()
        db.refresh(test_requirement)
        
        logger.info(f"✅ Test requirement created: {test_requirement.id}")
        
        # Test vendor proposal creation
        test_proposal = VendorProposal(
            compliance_analysis_id=test_analysis.id,
            vendor_name="Test Vendor Inc.",
            document_name="Test Proposal.pdf",
            proposal_content="Our solution provides comprehensive user authentication with multi-factor support."
        )
        
        db.add(test_proposal)
        db.commit()
        db.refresh(test_proposal)
        
        logger.info(f"✅ Test proposal created: {test_proposal.id}")
        
        # Test compliance matrix creation
        test_matrix = ComplianceMatrix(
            compliance_analysis_id=test_analysis.id,
            requirement_id=test_requirement.id,
            proposal_id=test_proposal.id,
            compliance_score=85.0,
            evidence_text="The proposal mentions multi-factor authentication support.",
            gap_description="No gaps identified for this requirement."
        )
        
        db.add(test_matrix)
        db.commit()
        db.refresh(test_matrix)
        
        logger.info(f"✅ Test compliance matrix created: {test_matrix.id}")
        
        # Test compliance score creation
        test_score = ComplianceScore(
            compliance_analysis_id=test_analysis.id,
            proposal_id=test_proposal.id,
            overall_score=85.0,
            rank_position=1,
            total_requirements=1,
            total_compliant=1,
            total_partial=0,
            total_non_compliant=0,
            total_not_addressed=0
        )
        
        db.add(test_score)
        db.commit()
        db.refresh(test_score)
        
        logger.info(f"✅ Test compliance score created: {test_score.id}")
        
        # Query test data
        analyses = db.query(ComplianceAnalysis).all()
        requirements = db.query(RFPRequirement).all()
        proposals = db.query(VendorProposal).all()
        matrix_records = db.query(ComplianceMatrix).all()
        scores = db.query(ComplianceScore).all()
        
        logger.info(f"\n📊 Database Record Counts:")
        logger.info(f"  Compliance Analyses: {len(analyses)}")
        logger.info(f"  RFP Requirements: {len(requirements)}")
        logger.info(f"  Vendor Proposals: {len(proposals)}")
        logger.info(f"  Compliance Matrix: {len(matrix_records)}")
        logger.info(f"  Compliance Scores: {len(scores)}")
        
        # Clean up test data
        logger.info(f"\n🧹 Cleaning up test data...")
        
        db.delete(test_score)
        db.delete(test_matrix)
        db.delete(test_proposal)
        db.delete(test_requirement)
        db.delete(test_analysis)
        db.commit()
        
        logger.info(f"✅ Test data cleaned up successfully")
        
        db.close()
        
        logger.info(f"\n🎉 COMPLIANCE ANALYSIS TABLES SETUP COMPLETE!")
        logger.info(f"✅ All 5 tables created and tested successfully")
        logger.info(f"✅ Foreign key relationships established")
        logger.info(f"✅ Database operations verified")
        logger.info(f"\nDatabase location: {DATABASE_URL}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating compliance tables: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def main():
    """Main function"""
    logger.info("TenderWise AI - Module 2: Compliance Analysis Database Setup")
    logger.info("="*60)
    
    success = create_compliance_tables()
    
    if success:
        logger.info("\n✅ SUCCESS: Compliance analysis database setup completed!")
        logger.info("You can now use Module 2 functionality.")
        sys.exit(0)
    else:
        logger.error("\n❌ FAILED: Compliance analysis database setup failed!")
        logger.error("Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()