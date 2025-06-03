"""
Workflow and AI Agent models (Langflow-inspired)
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from .base import Base


class WorkflowStatus(enum.Enum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class WorkflowCategory(enum.Enum):
    """Workflow categories"""
    RFP_ANALYSIS = "rfp_analysis"
    PROPOSAL_GENERATION = "proposal_generation"
    COMPLIANCE_CHECK = "compliance_check"
    DOCUMENT_PROCESSING = "document_processing"
    EVALUATION = "evaluation"
    CUSTOM = "custom"


class NodeType(enum.Enum):
    """Node types in workflow"""
    INPUT = "input"
    OUTPUT = "output"
    LLM = "llm"
    PROMPT_TEMPLATE = "prompt_template"
    DOCUMENT_LOADER = "document_loader"
    TEXT_SPLITTER = "text_splitter"
    VECTOR_STORE = "vector_store"
    RETRIEVER = "retriever"
    CHAIN = "chain"
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    TRANSFORMER = "transformer"
    CUSTOM = "custom"


class ExecutionStatus(enum.Enum):
    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow(Base):
    """Workflow model for AI agent orchestration"""
    
    __tablename__ = "workflows"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(20), default="1.0", nullable=False)
    
    # Classification
    category = Column(Enum(WorkflowCategory), nullable=False)
    tags = Column(JSONB, default=[], nullable=False)  # Array of tag strings
    
    # Workflow Definition
    flow_data = Column(JSONB, default={}, nullable=False)  # Complete flow definition
    input_schema = Column(JSONB, default={}, nullable=False)  # Expected input schema
    output_schema = Column(JSONB, default={}, nullable=False)  # Expected output schema
    
    # Configuration
    settings = Column(JSONB, default={}, nullable=False)
    environment_variables = Column(JSONB, default={}, nullable=False)
    
    # System Fields
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Performance Metrics
    total_executions = Column(Integer, default=0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    average_execution_time = Column(Integer, nullable=True)  # In seconds
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="workflows")
    
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="workflows")
    
    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow")
    
    def __repr__(self):
        return f"<Workflow(name='{self.name}', category='{self.category}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate workflow success rate"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    @property
    def node_count(self) -> int:
        """Get number of nodes in the workflow"""
        return len(self.nodes)


class WorkflowNode(Base):
    """Individual nodes in a workflow"""
    
    __tablename__ = "workflow_nodes"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    node_type = Column(Enum(NodeType), nullable=False)
    
    # Position in UI
    position_x = Column(Integer, nullable=False, default=0)
    position_y = Column(Integer, nullable=False, default=0)
    
    # Node Configuration
    config = Column(JSONB, default={}, nullable=False)  # Node-specific configuration
    inputs = Column(JSONB, default={}, nullable=False)  # Input connections
    outputs = Column(JSONB, default={}, nullable=False)  # Output connections
    
    # Relationships
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    workflow = relationship("Workflow", back_populates="nodes")
    
    def __repr__(self):
        return f"<WorkflowNode(name='{self.name}', type='{self.node_type}')>"


class WorkflowExecution(Base):
    """Workflow execution records"""
    
    __tablename__ = "workflow_executions"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    
    # Execution Details
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time = Column(Integer, nullable=True)  # In seconds
    
    # Input/Output
    input_data = Column(JSONB, default={}, nullable=False)
    output_data = Column(JSONB, default={}, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Execution Log
    execution_log = Column(JSONB, default=[], nullable=False)  # Step-by-step execution log
    
    # Context
    triggered_by = Column(String(200), nullable=True)  # What triggered this execution
    context = Column(JSONB, default={}, nullable=False)  # Additional context
    
    # Relationships
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    workflow = relationship("Workflow", back_populates="executions")
    
    executed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_by = relationship("User")
    
    def __repr__(self):
        return f"<WorkflowExecution(status='{self.status}', workflow_id={self.workflow_id})>"
    
    @property
    def duration_minutes(self) -> float:
        """Get execution duration in minutes"""
        if self.execution_time:
            return self.execution_time / 60
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if execution is completed (success or failure)"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED]