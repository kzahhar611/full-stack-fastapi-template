"""
Database-agnostic types for cross-platform compatibility
"""
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB


def get_json_type():
    """Get appropriate JSON type based on database"""
    # Return JSON (works with both SQLite and PostgreSQL)
    # In production with PostgreSQL, this can be changed to JSONB for better performance
    return JSON