#!/usr/bin/env python3
"""
Create RFP Analysis tables for Module 1
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.models.base import Base
from app.models.rfp_analysis import RFPAnalysis, DecisionHistory, AnalysisTemplate

def create_tables():
    """Create the analysis tables"""
    # Use SQLite database
    DATABASE_URL = "sqlite:///./tenderwise_ai.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        # Import all models to ensure they're registered
        from app.models import rfp_simple, user_simple, organization
        
        # Create only the new analysis tables
        RFPAnalysis.__table__.create(engine, checkfirst=True)
        DecisionHistory.__table__.create(engine, checkfirst=True)
        AnalysisTemplate.__table__.create(engine, checkfirst=True)
        
        print("✅ Successfully created RFP Analysis tables")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['rfp_analyses', 'decision_history', 'analysis_templates']
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' created successfully")
            else:
                print(f"❌ Table '{table}' not found")
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)