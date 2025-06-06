#!/usr/bin/env python3
"""
Create proposal generation tables for TenderWise AI Platform
Module 3: AI-Powered Technical Proposal Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_proposal_generation_tables():
    """Create all tables for proposal generation module"""
    
    # Database connection
    DATABASE_URL = "sqlite:///tenderwise_ai.db"
    engine = create_engine(DATABASE_URL, echo=True)
    
    # SQL for creating proposal generation tables
    create_tables_sql = """
    -- Proposal Projects table
    CREATE TABLE IF NOT EXISTS proposal_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        client_name VARCHAR(255),
        opportunity_value VARCHAR(100),
        submission_deadline DATETIME,
        status VARCHAR(50) DEFAULT 'created',
        progress_percentage INTEGER DEFAULT 0,
        rfp_filename VARCHAR(255),
        rfp_file_path VARCHAR(500),
        rfp_file_size INTEGER,
        rfp_upload_date DATETIME,
        ai_analysis_completed BOOLEAN DEFAULT 0,
        requirements_extracted BOOLEAN DEFAULT 0,
        content_generation_started BOOLEAN DEFAULT 0,
        total_requirements INTEGER DEFAULT 0,
        completed_sections INTEGER DEFAULT 0,
        total_sections INTEGER DEFAULT 0,
        estimated_completion_date DATETIME,
        content_quality_score INTEGER,
        completeness_score INTEGER,
        consistency_score INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by_id INTEGER,
        assigned_to_id INTEGER,
        organization_id INTEGER,
        generation_settings JSON,
        export_settings JSON,
        collaboration_settings JSON,
        FOREIGN KEY (created_by_id) REFERENCES users (id),
        FOREIGN KEY (assigned_to_id) REFERENCES users (id),
        FOREIGN KEY (organization_id) REFERENCES organizations (id)
    );

    -- RFP Requirements Analysis table
    CREATE TABLE IF NOT EXISTS rfp_requirements_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        project_id INTEGER NOT NULL,
        requirement_text TEXT NOT NULL,
        requirement_type VARCHAR(50) NOT NULL,
        section_title VARCHAR(255),
        page_number INTEGER,
        paragraph_number VARCHAR(50),
        priority_level VARCHAR(20),
        complexity_score INTEGER,
        word_count_estimate INTEGER,
        assigned_content_type VARCHAR(50),
        response_status VARCHAR(50) DEFAULT 'not_started',
        estimated_effort_hours INTEGER,
        extraction_confidence INTEGER,
        keywords JSON,
        related_requirements JSON,
        clarity_score INTEGER,
        measurability_score INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        processing_notes TEXT,
        manual_review_required BOOLEAN DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES proposal_projects (id) ON DELETE CASCADE
    );

    -- Content Templates table
    CREATE TABLE IF NOT EXISTS content_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        content_type VARCHAR(50) NOT NULL,
        template_content TEXT NOT NULL,
        variables JSON,
        styling_info JSON,
        industry_tags JSON,
        service_tags JSON,
        complexity_level VARCHAR(20),
        usage_count INTEGER DEFAULT 0,
        success_rate INTEGER,
        average_rating INTEGER,
        word_count INTEGER,
        estimated_completion_time INTEGER,
        last_used_date DATETIME,
        is_public BOOLEAN DEFAULT 1,
        is_approved BOOLEAN DEFAULT 0,
        created_by_id INTEGER,
        organization_id INTEGER,
        version VARCHAR(20) DEFAULT '1.0',
        parent_template_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ai_optimized BOOLEAN DEFAULT 0,
        optimization_notes TEXT,
        FOREIGN KEY (created_by_id) REFERENCES users (id),
        FOREIGN KEY (organization_id) REFERENCES organizations (id),
        FOREIGN KEY (parent_template_id) REFERENCES content_templates (id)
    );

    -- Generated Sections table
    CREATE TABLE IF NOT EXISTS generated_sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        project_id INTEGER NOT NULL,
        requirement_id INTEGER,
        template_id INTEGER,
        section_title VARCHAR(255) NOT NULL,
        content_type VARCHAR(50) NOT NULL,
        section_order INTEGER DEFAULT 0,
        generated_content TEXT NOT NULL,
        original_prompt TEXT,
        ai_provider VARCHAR(50),
        word_count INTEGER,
        estimated_reading_time INTEGER,
        generation_status VARCHAR(50) DEFAULT 'pending',
        generation_started_at DATETIME,
        generation_completed_at DATETIME,
        generation_duration INTEGER,
        ai_confidence_score INTEGER,
        content_quality_score INTEGER,
        relevance_score INTEGER,
        completeness_score INTEGER,
        human_reviewed BOOLEAN DEFAULT 0,
        human_approved BOOLEAN DEFAULT 0,
        human_review_notes TEXT,
        reviewed_by_id INTEGER,
        reviewed_at DATETIME,
        edit_count INTEGER DEFAULT 0,
        version_number INTEGER DEFAULT 1,
        is_current_version BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        improvement_suggestions JSON,
        related_sections JSON,
        FOREIGN KEY (project_id) REFERENCES proposal_projects (id) ON DELETE CASCADE,
        FOREIGN KEY (requirement_id) REFERENCES rfp_requirements_analysis (id),
        FOREIGN KEY (template_id) REFERENCES content_templates (id),
        FOREIGN KEY (reviewed_by_id) REFERENCES users (id)
    );

    -- Proposal Documents table
    CREATE TABLE IF NOT EXISTS proposal_documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        project_id INTEGER NOT NULL,
        document_name VARCHAR(255) NOT NULL,
        document_type VARCHAR(50),
        format_type VARCHAR(20),
        section_count INTEGER DEFAULT 0,
        total_word_count INTEGER DEFAULT 0,
        total_page_count INTEGER DEFAULT 0,
        assembled_content TEXT,
        table_of_contents JSON,
        section_mapping JSON,
        file_path VARCHAR(500),
        file_size INTEGER,
        export_settings JSON,
        overall_quality_score INTEGER,
        consistency_score INTEGER,
        professional_score INTEGER,
        assembly_status VARCHAR(50) DEFAULT 'draft',
        is_final_version BOOLEAN DEFAULT 0,
        submission_ready BOOLEAN DEFAULT 0,
        approved_by_id INTEGER,
        approved_at DATETIME,
        approval_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        exported_at DATETIME,
        collaborators JSON,
        change_log JSON,
        FOREIGN KEY (project_id) REFERENCES proposal_projects (id) ON DELETE CASCADE,
        FOREIGN KEY (approved_by_id) REFERENCES users (id)
    );

    -- Generation History table
    CREATE TABLE IF NOT EXISTS generation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uuid VARCHAR(36) UNIQUE NOT NULL,
        project_id INTEGER NOT NULL,
        section_id INTEGER,
        document_id INTEGER,
        action_type VARCHAR(50) NOT NULL,
        action_description TEXT,
        content_before TEXT,
        content_after TEXT,
        changes_summary TEXT,
        performed_by_id INTEGER NOT NULL,
        performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        ai_provider_used VARCHAR(50),
        processing_time INTEGER,
        quality_metrics JSON,
        user_notes TEXT,
        system_notes TEXT,
        related_actions JSON,
        FOREIGN KEY (project_id) REFERENCES proposal_projects (id) ON DELETE CASCADE,
        FOREIGN KEY (section_id) REFERENCES generated_sections (id),
        FOREIGN KEY (document_id) REFERENCES proposal_documents (id),
        FOREIGN KEY (performed_by_id) REFERENCES users (id)
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_proposal_projects_status ON proposal_projects(status);
    CREATE INDEX IF NOT EXISTS idx_proposal_projects_created_at ON proposal_projects(created_at);
    CREATE INDEX IF NOT EXISTS idx_proposal_projects_organization ON proposal_projects(organization_id);
    CREATE INDEX IF NOT EXISTS idx_proposal_projects_uuid ON proposal_projects(uuid);

    CREATE INDEX IF NOT EXISTS idx_rfp_requirements_project ON rfp_requirements_analysis(project_id);
    CREATE INDEX IF NOT EXISTS idx_rfp_requirements_type ON rfp_requirements_analysis(requirement_type);
    CREATE INDEX IF NOT EXISTS idx_rfp_requirements_uuid ON rfp_requirements_analysis(uuid);

    CREATE INDEX IF NOT EXISTS idx_content_templates_type ON content_templates(content_type);
    CREATE INDEX IF NOT EXISTS idx_content_templates_public ON content_templates(is_public);
    CREATE INDEX IF NOT EXISTS idx_content_templates_approved ON content_templates(is_approved);
    CREATE INDEX IF NOT EXISTS idx_content_templates_uuid ON content_templates(uuid);

    CREATE INDEX IF NOT EXISTS idx_generated_sections_project ON generated_sections(project_id);
    CREATE INDEX IF NOT EXISTS idx_generated_sections_status ON generated_sections(generation_status);
    CREATE INDEX IF NOT EXISTS idx_generated_sections_type ON generated_sections(content_type);
    CREATE INDEX IF NOT EXISTS idx_generated_sections_uuid ON generated_sections(uuid);

    CREATE INDEX IF NOT EXISTS idx_proposal_documents_project ON proposal_documents(project_id);
    CREATE INDEX IF NOT EXISTS idx_proposal_documents_status ON proposal_documents(assembly_status);
    CREATE INDEX IF NOT EXISTS idx_proposal_documents_uuid ON proposal_documents(uuid);

    CREATE INDEX IF NOT EXISTS idx_generation_history_project ON generation_history(project_id);
    CREATE INDEX IF NOT EXISTS idx_generation_history_performed_at ON generation_history(performed_at);
    CREATE INDEX IF NOT EXISTS idx_generation_history_action ON generation_history(action_type);
    CREATE INDEX IF NOT EXISTS idx_generation_history_uuid ON generation_history(uuid);
    """
    
    try:
        # Execute table creation
        with engine.connect() as connection:
            # Split and execute each statement
            statements = [stmt.strip() for stmt in create_tables_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    logger.info(f"Executing: {statement[:100]}...")
                    connection.execute(text(statement))
            
            connection.commit()
            logger.info("✅ All proposal generation tables created successfully!")
            
        # Verify tables were created
        with engine.connect() as connection:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%proposal%';"))
            tables = result.fetchall()
            logger.info(f"📊 Created tables: {[table[0] for table in tables]}")
            
            # Check total table count
            result = connection.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table';"))
            total_tables = result.fetchone()[0]
            logger.info(f"📈 Total tables in database: {total_tables}")
            
    except Exception as e:
        logger.error(f"❌ Error creating proposal generation tables: {e}")
        raise
    
    return True

def insert_sample_templates():
    """Insert sample content templates for testing"""
    
    DATABASE_URL = "sqlite:///tenderwise_ai.db"
    engine = create_engine(DATABASE_URL)
    
    sample_templates_sql = """
    INSERT OR IGNORE INTO content_templates (
        uuid, name, description, content_type, template_content, 
        variables, industry_tags, service_tags, complexity_level,
        word_count, estimated_completion_time, is_public, is_approved
    ) VALUES 
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'Technical Approach - Software Development',
        'Comprehensive technical approach template for software development projects',
        'technical_approach',
        'Our technical approach for {project_name} leverages industry best practices and proven methodologies.\n\n## Development Methodology\nWe will employ an {methodology} approach to ensure {quality_attributes}.\n\n## Technology Stack\nOur recommended technology stack includes:\n- {primary_technology}\n- {database_technology}\n- {framework_technology}\n\n## Quality Assurance\nOur QA process includes {testing_approaches} to ensure {quality_outcomes}.',
        '["project_name", "methodology", "quality_attributes", "primary_technology", "database_technology", "framework_technology", "testing_approaches", "quality_outcomes"]',
        '["technology", "software", "it_services"]',
        '["development", "consulting", "implementation"]',
        'Intermediate',
        850,
        45,
        1,
        1
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'Executive Summary - Government Contract',
        'Executive summary template optimized for government contract proposals',
        'executive_summary',
        '{company_name} is pleased to submit our proposal for {project_title}.\n\n## Understanding of Requirements\nWe understand that {agency_name} requires {primary_requirement}.\n\n## Our Solution\nOur solution provides {key_benefits} through {approach_summary}.\n\n## Why Choose Us\n- {differentiator_1}\n- {differentiator_2}\n- {differentiator_3}\n\n## Investment\nOur total investment for this project is {total_cost}, delivering exceptional value through {value_proposition}.',
        '["company_name", "project_title", "agency_name", "primary_requirement", "key_benefits", "approach_summary", "differentiator_1", "differentiator_2", "differentiator_3", "total_cost", "value_proposition"]',
        '["government", "public_sector"]',
        '["consulting", "implementation", "support"]',
        'Basic',
        650,
        30,
        1,
        1
    ),
    (
        '550e8400-e29b-41d4-a716-446655440003',
        'Team Qualifications - Engineering Project',
        'Team qualifications and staff augmentation template for engineering projects',
        'team_qualifications',
        'Our team brings {total_experience} years of combined experience in {domain_expertise}.\n\n## Project Manager\n{pm_name} will serve as Project Manager, bringing {pm_experience} years of experience in {pm_expertise}.\n\n## Technical Lead\n{tech_lead_name} will lead the technical implementation with expertise in {tech_expertise}.\n\n## Development Team\nOur development team includes:\n{team_members}\n\n## Certifications and Credentials\n{certifications}\n\n## Past Performance\nRelevant past performance includes:\n{past_projects}',
        '["total_experience", "domain_expertise", "pm_name", "pm_experience", "pm_expertise", "tech_lead_name", "tech_expertise", "team_members", "certifications", "past_projects"]',
        '["engineering", "technology", "construction"]',
        '["staffing", "consulting", "project_management"]',
        'Advanced',
        1200,
        60,
        1,
        1
    ),
    (
        '550e8400-e29b-41d4-a716-446655440004',
        'Risk Management - IT Infrastructure',
        'Comprehensive risk management template for IT infrastructure projects',
        'risk_management',
        'We have identified and developed mitigation strategies for all potential project risks.\n\n## Technical Risks\n{technical_risks}\n\n## Schedule Risks\n{schedule_risks}\n\n## Resource Risks\n{resource_risks}\n\n## Mitigation Strategies\nOur risk mitigation approach includes:\n1. {mitigation_strategy_1}\n2. {mitigation_strategy_2}\n3. {mitigation_strategy_3}\n\n## Contingency Planning\n{contingency_plans}\n\n## Risk Monitoring\nWe will monitor risks through {monitoring_approach}.',
        '["technical_risks", "schedule_risks", "resource_risks", "mitigation_strategy_1", "mitigation_strategy_2", "mitigation_strategy_3", "contingency_plans", "monitoring_approach"]',
        '["it_infrastructure", "technology", "enterprise"]',
        '["implementation", "consulting", "support"]',
        'Advanced',
        950,
        50,
        1,
        1
    ),
    (
        '550e8400-e29b-41d4-a716-446655440005',
        'Project Timeline - Agile Development',
        'Project timeline and milestone template for agile development projects',
        'project_timeline',
        'Our project timeline is structured around {sprint_duration} sprints over {total_duration}.\n\n## Phase 1: Planning and Setup ({phase1_duration})\n{phase1_activities}\n\n## Phase 2: Development Sprints ({phase2_duration})\n{phase2_activities}\n\n## Phase 3: Testing and Deployment ({phase3_duration})\n{phase3_activities}\n\n## Key Milestones\n{key_milestones}\n\n## Deliverables Schedule\n{deliverables_schedule}\n\n## Critical Path\n{critical_path_items}',
        '["sprint_duration", "total_duration", "phase1_duration", "phase1_activities", "phase2_duration", "phase2_activities", "phase3_duration", "phase3_activities", "key_milestones", "deliverables_schedule", "critical_path_items"]',
        '["software", "agile", "technology"]',
        '["development", "project_management", "consulting"]',
        'Intermediate',
        750,
        40,
        1,
        1
    );
    """
    
    try:
        with engine.connect() as connection:
            connection.execute(text(sample_templates_sql))
            connection.commit()
            logger.info("✅ Sample content templates inserted successfully!")
            
            # Verify templates were inserted
            result = connection.execute(text("SELECT COUNT(*) FROM content_templates;"))
            count = result.fetchone()[0]
            logger.info(f"📊 Total content templates: {count}")
            
    except Exception as e:
        logger.error(f"❌ Error inserting sample templates: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Creating proposal generation tables for TenderWise AI Platform...")
    
    try:
        # Create tables
        create_proposal_generation_tables()
        
        # Insert sample data
        insert_sample_templates()
        
        print("\n🎉 Module 3 database setup completed successfully!")
        print("📊 Proposal generation infrastructure ready for development")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)