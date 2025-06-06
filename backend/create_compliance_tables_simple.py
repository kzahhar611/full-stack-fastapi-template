#!/usr/bin/env python3
"""
Simple script to create compliance analysis tables
"""

import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_PATH = "tenderwise_ai.db"

def create_compliance_tables():
    """Create compliance analysis tables directly with SQL"""
    
    sql_statements = [
        # Compliance Analyses table
        """
        CREATE TABLE IF NOT EXISTS compliance_analyses (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            organization_id TEXT,
            rfp_document_name TEXT NOT NULL,
            rfp_content TEXT NOT NULL,
            rfp_metadata TEXT,
            analysis_status TEXT DEFAULT 'PENDING' NOT NULL,
            processing_progress REAL DEFAULT 0.0,
            total_requirements INTEGER DEFAULT 0,
            total_proposals INTEGER DEFAULT 0,
            analysis_results TEXT,
            processing_time_seconds REAL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (organization_id) REFERENCES organizations (id)
        )
        """,
        
        # RFP Requirements table
        """
        CREATE TABLE IF NOT EXISTS rfp_requirements (
            id TEXT PRIMARY KEY,
            compliance_analysis_id TEXT NOT NULL,
            requirement_text TEXT NOT NULL,
            requirement_summary TEXT,
            requirement_category TEXT,
            requirement_type TEXT DEFAULT 'FUNCTIONAL' NOT NULL,
            priority_level TEXT DEFAULT 'MEDIUM' NOT NULL,
            section_reference TEXT,
            page_number INTEGER,
            weight REAL DEFAULT 1.0,
            extraction_confidence REAL,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (compliance_analysis_id) REFERENCES compliance_analyses (id) ON DELETE CASCADE
        )
        """,
        
        # Vendor Proposals table
        """
        CREATE TABLE IF NOT EXISTS vendor_proposals (
            id TEXT PRIMARY KEY,
            compliance_analysis_id TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            vendor_company TEXT,
            vendor_email TEXT,
            document_name TEXT NOT NULL,
            document_size_bytes INTEGER,
            document_type TEXT,
            proposal_content TEXT NOT NULL,
            content_sections TEXT,
            submission_date TIMESTAMP,
            proposal_metadata TEXT,
            extraction_confidence REAL,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (compliance_analysis_id) REFERENCES compliance_analyses (id) ON DELETE CASCADE
        )
        """,
        
        # Compliance Matrix table
        """
        CREATE TABLE IF NOT EXISTS compliance_matrix (
            id TEXT PRIMARY KEY,
            compliance_analysis_id TEXT NOT NULL,
            requirement_id TEXT NOT NULL,
            proposal_id TEXT NOT NULL,
            compliance_status TEXT NOT NULL,
            compliance_score REAL NOT NULL,
            confidence_level REAL,
            evidence_text TEXT,
            gap_description TEXT,
            recommendations TEXT,
            technical_relevance REAL,
            completeness_score REAL,
            clarity_score REAL,
            analysis_method TEXT,
            keywords_matched TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (compliance_analysis_id) REFERENCES compliance_analyses (id) ON DELETE CASCADE,
            FOREIGN KEY (requirement_id) REFERENCES rfp_requirements (id) ON DELETE CASCADE,
            FOREIGN KEY (proposal_id) REFERENCES vendor_proposals (id) ON DELETE CASCADE
        )
        """,
        
        # Compliance Scores table
        """
        CREATE TABLE IF NOT EXISTS compliance_scores (
            id TEXT PRIMARY KEY,
            compliance_analysis_id TEXT NOT NULL,
            proposal_id TEXT NOT NULL,
            overall_score REAL NOT NULL,
            weighted_score REAL,
            rank_position INTEGER,
            technical_score REAL,
            functional_score REAL,
            commercial_score REAL,
            legal_score REAL,
            operational_score REAL,
            total_requirements INTEGER DEFAULT 0,
            total_compliant INTEGER DEFAULT 0,
            total_partial INTEGER DEFAULT 0,
            total_non_compliant INTEGER DEFAULT 0,
            total_not_addressed INTEGER DEFAULT 0,
            strength_areas TEXT,
            weakness_areas TEXT,
            risk_factors TEXT,
            recommendations TEXT,
            calculation_method TEXT,
            last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (compliance_analysis_id) REFERENCES compliance_analyses (id) ON DELETE CASCADE,
            FOREIGN KEY (proposal_id) REFERENCES vendor_proposals (id) ON DELETE CASCADE
        )
        """
    ]
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        logger.info("Creating compliance analysis tables...")
        
        for i, sql in enumerate(sql_statements):
            table_name = [
                "compliance_analyses", 
                "rfp_requirements", 
                "vendor_proposals", 
                "compliance_matrix", 
                "compliance_scores"
            ][i]
            
            cursor.execute(sql)
            logger.info(f"✅ Created table: {table_name}")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_compliance_analyses_user_id ON compliance_analyses(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_analyses_status ON compliance_analyses(analysis_status)",
            "CREATE INDEX IF NOT EXISTS idx_rfp_requirements_analysis_id ON rfp_requirements(compliance_analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_vendor_proposals_analysis_id ON vendor_proposals(compliance_analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_matrix_analysis_id ON compliance_matrix(compliance_analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_matrix_requirement_id ON compliance_matrix(requirement_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_matrix_proposal_id ON compliance_matrix(proposal_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_scores_analysis_id ON compliance_scores(compliance_analysis_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_scores_rank ON compliance_scores(rank_position)"
        ]
        
        logger.info("Creating indexes...")
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'compliance_%' OR name LIKE 'rfp_requirements' OR name LIKE 'vendor_proposals'")
        tables = cursor.fetchall()
        
        logger.info(f"\n📊 Created {len(tables)} compliance analysis tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        conn.close()
        
        logger.info(f"\n🎉 SUCCESS: Compliance analysis tables created!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_compliance_tables()