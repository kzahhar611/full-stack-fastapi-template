"""
AI Agent models for specialized tasks
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, Enum, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum
from datetime import datetime

from .base import Base


class AgentType(enum.Enum):
    """Types of AI agents"""
    RFP_ANALYZER = "rfp_analyzer"
    PROPOSAL_GENERATOR = "proposal_generator"
    COMPLIANCE_CHECKER = "compliance_checker"
    DOCUMENT_PROCESSOR = "document_processor"
    EVALUATOR = "evaluator"
    RISK_ASSESSOR = "risk_assessor"
    COST_OPTIMIZER = "cost_optimizer"
    CUSTOM = "custom"


class AgentStatus(enum.Enum):
    """Agent status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"


class LLMProvider(enum.Enum):
    """LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGING_FACE = "hugging_face"
    LOCAL = "local"


class ExecutionStatus(enum.Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class Agent(Base):
    """AI Agent model for specialized tasks"""
    
    __tablename__ = "agents"
    
    # Basic Information
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    agent_type = Column(Enum(AgentType), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)
    
    # Configuration
    llm_provider = Column(Enum(LLMProvider), nullable=False)
    model_name = Column(String(100), nullable=False)  # e.g., "gpt-4", "claude-3-opus"
    
    # Prompts and Instructions
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=True)
    few_shot_examples = Column(JSONB, default=[], nullable=False)
    
    # LLM Parameters
    temperature = Column(Numeric(3, 2), default=0.7, nullable=False)
    max_tokens = Column(Integer, default=2000, nullable=False)
    top_p = Column(Numeric(3, 2), default=1.0, nullable=False)
    frequency_penalty = Column(Numeric(3, 2), default=0.0, nullable=False)
    presence_penalty = Column(Numeric(3, 2), default=0.0, nullable=False)
    
    # Capabilities
    capabilities = Column(JSONB, default=[], nullable=False)  # List of capabilities
    input_types = Column(JSONB, default=[], nullable=False)  # Supported input types
    output_types = Column(JSONB, default=[], nullable=False)  # Supported output types
    
    # Validation and Quality
    input_validation_schema = Column(JSONB, default={}, nullable=False)
    output_validation_schema = Column(JSONB, default={}, nullable=False)
    quality_metrics = Column(JSONB, default={}, nullable=False)
    
    # Performance Settings
    timeout_seconds = Column(Integer, default=300, nullable=False)  # 5 minutes default
    retry_attempts = Column(Integer, default=3, nullable=False)
    batch_size = Column(Integer, default=1, nullable=False)
    
    # System Fields
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Performance Metrics
    total_executions = Column(Integer, default=0, nullable=False)
    successful_executions = Column(Integer, default=0, nullable=False)
    average_execution_time = Column(Integer, nullable=True)  # In seconds
    average_cost = Column(Numeric(10, 4), nullable=True)  # Average cost per execution
    
    # Cost Tracking
    total_input_tokens = Column(Integer, default=0, nullable=False)
    total_output_tokens = Column(Integer, default=0, nullable=False)
    total_cost = Column(Numeric(10, 4), default=0.0, nullable=False)
    
    # Relationships
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    executions = relationship("AgentExecution", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(name='{self.name}', type='{self.agent_type}')>"
    
    @property
    def success_rate(self) -> float:
        """Calculate agent success rate"""
        if self.total_executions == 0:
            return 0.0
        return (self.successful_executions / self.total_executions) * 100
    
    @property
    def average_cost_per_execution(self) -> float:
        """Calculate average cost per execution"""
        if self.total_executions == 0:
            return 0.0
        return float(self.total_cost / self.total_executions)


class AgentExecution(Base):
    """Agent execution records for tracking performance and costs"""
    
    __tablename__ = "agent_executions"
    
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
    
    # LLM Interaction
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost Tracking
    cost = Column(Numeric(10, 4), nullable=True)
    pricing_model = Column(String(50), nullable=True)  # per_token, per_request, etc.
    
    # Model Information
    model_used = Column(String(100), nullable=True)
    provider_used = Column(String(50), nullable=True)
    
    # Quality Metrics
    confidence_score = Column(Numeric(5, 2), nullable=True)  # 0.00 to 100.00
    quality_score = Column(Numeric(5, 2), nullable=True)  # 0.00 to 100.00
    
    # Context
    triggered_by = Column(String(200), nullable=True)  # What triggered this execution
    context = Column(JSONB, default={}, nullable=False)  # Additional context
    
    # Relationships
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    agent = relationship("Agent", back_populates="executions")
    
    executed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_by = relationship("User")
    
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=True)
    
    def __repr__(self):
        return f"<AgentExecution(status='{self.status}', agent_id={self.agent_id})>"
    
    @property
    def duration_minutes(self) -> float:
        """Get execution duration in minutes"""
        if self.execution_time:
            return self.execution_time / 60
        return 0.0
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens processed per second"""
        if self.execution_time and self.total_tokens:
            return self.total_tokens / self.execution_time
        return 0.0
    
    @property
    def cost_per_token(self) -> float:
        """Calculate cost per token"""
        if self.total_tokens and self.cost:
            return float(self.cost / self.total_tokens)
        return 0.0