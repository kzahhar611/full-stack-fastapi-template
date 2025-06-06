# 🔧 TenderWise AI v2: Detailed Technical Specifications

**Date**: June 4, 2025  
**Version**: 2.0.0  
**Architecture**: Enterprise Microservices  

---

## 🏗️ **CORE ARCHITECTURE SPECIFICATIONS**

### **🎨 FRONTEND ARCHITECTURE**

#### **Technology Stack**
```typescript
// Framework & Core
Next.js 14.0+ (App Router, Server Components)
React 18+ (Concurrent Features, Suspense)
TypeScript 5.0+ (Strict Mode)

// Styling & UI
Tailwind CSS 3.3+ (RTL Support, Custom Themes)
Headless UI 1.7+ (Accessible Components)
Framer Motion 10+ (Animations & Transitions)
Lucide React (Icon System)

// State Management
Zustand 4.4+ (Global State)
React Query 3.39+ (Server State)
React Hook Form 7.48+ (Form Management)

// Workflow & AI
React Flow 11+ (Workflow Designer)
Monaco Editor (Code Editing)
PDF.js (Document Viewer)

// Internationalization
next-intl 3.0+ (i18n Framework)
date-fns 2.30+ (Date Utilities)
date-fns-jalali 2.30+ (Hijri Calendar)
```

#### **Component Architecture**
```typescript
// Component Library Structure
interface ComponentLibrary {
  // Base UI Components
  ui: {
    Button: React.FC<ButtonProps>;
    Input: React.FC<InputProps>;
    Select: React.FC<SelectProps>;
    Modal: React.FC<ModalProps>;
    Table: React.FC<TableProps>;
    Card: React.FC<CardProps>;
    Badge: React.FC<BadgeProps>;
    Tooltip: React.FC<TooltipProps>;
  };
  
  // Form Components
  forms: {
    FormField: React.FC<FormFieldProps>;
    FormSection: React.FC<FormSectionProps>;
    FormWizard: React.FC<FormWizardProps>;
    ValidationMessage: React.FC<ValidationProps>;
  };
  
  // Chart Components
  charts: {
    LineChart: React.FC<LineChartProps>;
    BarChart: React.FC<BarChartProps>;
    PieChart: React.FC<PieChartProps>;
    KPICard: React.FC<KPICardProps>;
    MetricsDashboard: React.FC<MetricsDashboardProps>;
  };
  
  // Workflow Components
  workflow: {
    WorkflowDesigner: React.FC<WorkflowDesignerProps>;
    NodeLibrary: React.FC<NodeLibraryProps>;
    NodeEditor: React.FC<NodeEditorProps>;
    WorkflowExecutor: React.FC<WorkflowExecutorProps>;
  };
  
  // AI Agent Components
  agents: {
    AgentBuilder: React.FC<AgentBuilderProps>;
    AgentLibrary: React.FC<AgentLibraryProps>;
    AgentMonitor: React.FC<AgentMonitorProps>;
    PromptEditor: React.FC<PromptEditorProps>;
  };
  
  // Template Components
  templates: {
    TemplateDesigner: React.FC<TemplateDesignerProps>;
    TemplatePreview: React.FC<TemplatePreviewProps>;
    TemplateLibrary: React.FC<TemplateLibraryProps>;
  };
}
```

#### **State Management Architecture**
```typescript
// Zustand Store Structure
interface AppState {
  // Authentication
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    permissions: Permission[];
  };
  
  // UI State
  ui: {
    theme: 'light' | 'dark' | 'auto';
    locale: 'en' | 'ar';
    direction: 'ltr' | 'rtl';
    sidebar: boolean;
    notifications: Notification[];
  };
  
  // Application State
  app: {
    currentEntity: Entity | null;
    currentProject: Project | null;
    workspaces: Workspace[];
    preferences: UserPreferences;
  };
  
  // Workflow State
  workflow: {
    currentWorkflow: Workflow | null;
    nodes: WorkflowNode[];
    connections: WorkflowConnection[];
    isExecuting: boolean;
    executionStatus: ExecutionStatus;
  };
  
  // AI Agents State
  agents: {
    agents: AIAgent[];
    currentAgent: AIAgent | null;
    agentExecutions: AgentExecution[];
    agentMetrics: AgentMetrics;
  };
}
```

### **🔧 BACKEND ARCHITECTURE**

#### **Microservices Structure**
```python
# Service Architecture
services = {
    # Core Services
    "gateway": {
        "port": 8000,
        "purpose": "API Gateway, Load Balancing, Rate Limiting",
        "technology": "FastAPI + Nginx",
        "dependencies": ["auth", "users"]
    },
    
    "auth": {
        "port": 8001,
        "purpose": "Authentication, Authorization, JWT Management",
        "technology": "FastAPI + SQLAlchemy",
        "database": "postgresql://auth_db"
    },
    
    "users": {
        "port": 8002,
        "purpose": "User Management, Organizations, RBAC",
        "technology": "FastAPI + SQLAlchemy",
        "database": "postgresql://users_db"
    },
    
    # Business Services
    "rfp": {
        "port": 8003,
        "purpose": "RFP Management, CRUD, Business Logic",
        "technology": "FastAPI + SQLAlchemy",
        "database": "postgresql://rfp_db"
    },
    
    "documents": {
        "port": 8004,
        "purpose": "Document Storage, Processing, OCR",
        "technology": "FastAPI + MinIO + OCR",
        "storage": "minio://documents"
    },
    
    "ai-agents": {
        "port": 8005,
        "purpose": "AI Agent Management, Execution, Monitoring",
        "technology": "FastAPI + LangChain",
        "dependencies": ["llm-manager"]
    },
    
    "workflows": {
        "port": 8006,
        "purpose": "Workflow Engine, Execution, Scheduling",
        "technology": "FastAPI + Celery",
        "queue": "redis://workflow_queue"
    },
    
    "templates": {
        "port": 8007,
        "purpose": "Template Management, PDF/PPT Generation",
        "technology": "FastAPI + Jinja2 + WeasyPrint",
        "storage": "minio://templates"
    },
    
    "analytics": {
        "port": 8008,
        "purpose": "Analytics, Reporting, Metrics",
        "technology": "FastAPI + ClickHouse",
        "database": "clickhouse://analytics_db"
    },
    
    "llm-manager": {
        "port": 8009,
        "purpose": "LLM Provider Management, Cost Tracking",
        "technology": "FastAPI + Redis",
        "providers": ["openai", "anthropic", "google", "azure"]
    },
    
    "notifications": {
        "port": 8010,
        "purpose": "Email, SMS, Push Notifications",
        "technology": "FastAPI + Celery + SMTP",
        "queue": "redis://notification_queue"
    }
}
```

#### **Database Schema Design**
```sql
-- Core Database Schemas

-- Users & Organizations
CREATE SCHEMA users;
CREATE TABLE users.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type organization_type NOT NULL,
    settings JSONB DEFAULT '{}',
    branding JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    organization_id UUID REFERENCES users.organizations(id),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RFPs & Proposals
CREATE SCHEMA rfp;
CREATE TABLE rfp.rfps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfp_number VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    type rfp_type NOT NULL,
    status rfp_status DEFAULT 'draft',
    budget_min DECIMAL(15,2),
    budget_max DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'SAR',
    issue_date DATE,
    submission_deadline TIMESTAMPTZ,
    requirements JSONB DEFAULT '{}',
    evaluation_criteria JSONB DEFAULT '{}',
    ai_analysis JSONB DEFAULT '{}',
    organization_id UUID NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rfp.proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rfp_id UUID REFERENCES rfp.rfps(id),
    vendor_id UUID REFERENCES users.organizations(id),
    title VARCHAR(500) NOT NULL,
    content JSONB DEFAULT '{}',
    technical_score DECIMAL(5,2),
    financial_score DECIMAL(5,2),
    compliance_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    status proposal_status DEFAULT 'draft',
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Agents
CREATE SCHEMA ai;
CREATE TABLE ai.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type agent_type NOT NULL,
    llm_provider VARCHAR(50) NOT NULL,
    llm_model VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    user_prompt_template TEXT,
    parameters JSONB DEFAULT '{}',
    tools JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    organization_id UUID NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai.agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES ai.agents(id),
    input_data JSONB NOT NULL,
    output_data JSONB,
    token_count INTEGER,
    cost DECIMAL(10,6),
    execution_time_ms INTEGER,
    status execution_status DEFAULT 'pending',
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflows
CREATE SCHEMA workflow;
CREATE TABLE workflow.workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL, -- Workflow nodes and connections
    trigger_type trigger_type NOT NULL,
    trigger_config JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    version INTEGER DEFAULT 1,
    organization_id UUID NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE workflow.executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow.workflows(id),
    trigger_data JSONB,
    status execution_status DEFAULT 'pending',
    current_node VARCHAR(100),
    execution_log JSONB DEFAULT '[]',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

-- Documents
CREATE SCHEMA docs;
CREATE TABLE docs.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    content_hash VARCHAR(64) UNIQUE NOT NULL,
    extracted_text TEXT,
    metadata JSONB DEFAULT '{}',
    ai_analysis JSONB DEFAULT '{}',
    rfp_id UUID REFERENCES rfp.rfps(id),
    organization_id UUID NOT NULL,
    uploaded_by UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics
CREATE SCHEMA analytics;
CREATE TABLE analytics.usage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(50) NOT NULL, -- 'ai_agent', 'workflow', 'document'
    entity_id UUID NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metadata JSONB DEFAULT '{}',
    organization_id UUID NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_users_organization ON users.users(organization_id);
CREATE INDEX idx_users_email ON users.users(email);
CREATE INDEX idx_rfps_organization ON rfp.rfps(organization_id);
CREATE INDEX idx_rfps_status ON rfp.rfps(status);
CREATE INDEX idx_proposals_rfp ON rfp.proposals(rfp_id);
CREATE INDEX idx_agents_organization ON ai.agents(organization_id);
CREATE INDEX idx_agent_executions_agent ON ai.agent_executions(agent_id);
CREATE INDEX idx_workflows_organization ON workflow.workflows(organization_id);
CREATE INDEX idx_documents_rfp ON docs.documents(rfp_id);
CREATE INDEX idx_usage_metrics_entity ON analytics.usage_metrics(entity_type, entity_id);
```

#### **API Design Patterns**
```python
# FastAPI Service Template
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

logger = structlog.get_logger()

# Service Base Class
class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logger
    
    async def create(self, data: dict) -> dict:
        """Create a new entity"""
        pass
    
    async def get_by_id(self, entity_id: str) -> Optional[dict]:
        """Get entity by ID"""
        pass
    
    async def list(self, filters: dict, pagination: dict) -> List[dict]:
        """List entities with filtering and pagination"""
        pass
    
    async def update(self, entity_id: str, data: dict) -> dict:
        """Update an entity"""
        pass
    
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass

# API Router Template
from fastapi import APIRouter, Depends
from .schemas import EntityCreate, EntityUpdate, EntityResponse
from .service import EntityService
from app.core.deps import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=EntityResponse)
async def create_entity(
    data: EntityCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = EntityService(db)
    result = await service.create(data.dict())
    return result

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = EntityService(db)
    result = await service.get_by_id(entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Entity not found")
    return result

# Error Handling
from app.core.exceptions import BusinessLogicError, ValidationError

@router.exception_handler(BusinessLogicError)
async def business_logic_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "business_logic", "message": str(exc)}
    )

@router.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "validation", "message": str(exc), "details": exc.details}
    )
```

---

## 🤖 **AI INTEGRATION SPECIFICATIONS**

### **LLM Provider Management**
```python
# LLM Provider Interface
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import asyncio

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict:
        pass
    
    @abstractmethod
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass

# OpenAI Provider Implementation
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
        }
    
    async def chat_completion(self, messages, model, **kwargs):
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.dict(),
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {str(e)}")
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        if model not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost

# LLM Manager Service
class LLMManager:
    def __init__(self):
        self.providers = {}
        self.usage_tracker = UsageTracker()
        self.rate_limiter = RateLimiter()
    
    def register_provider(self, name: str, provider: LLMProvider):
        self.providers[name] = provider
    
    async def execute_completion(
        self,
        provider_name: str,
        model: str,
        messages: List[Dict],
        user_id: str,
        organization_id: str,
        **kwargs
    ) -> Dict:
        # Check rate limits
        await self.rate_limiter.check_limits(user_id, organization_id)
        
        # Get provider
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not found")
        
        # Execute completion
        start_time = time.time()
        result = await provider.chat_completion(messages, model, **kwargs)
        execution_time = time.time() - start_time
        
        # Track usage
        usage_data = {
            "provider": provider_name,
            "model": model,
            "input_tokens": result["usage"]["prompt_tokens"],
            "output_tokens": result["usage"]["completion_tokens"],
            "total_tokens": result["usage"]["total_tokens"],
            "cost": provider.calculate_cost(
                result["usage"]["prompt_tokens"],
                result["usage"]["completion_tokens"],
                model
            ),
            "execution_time": execution_time,
            "user_id": user_id,
            "organization_id": organization_id
        }
        
        await self.usage_tracker.record_usage(usage_data)
        
        return result
```

### **AI Agent Framework**
```python
# AI Agent Base Class
class AIAgent:
    def __init__(
        self,
        agent_id: str,
        name: str,
        llm_provider: str,
        llm_model: str,
        system_prompt: str,
        user_prompt_template: str,
        parameters: Dict = None,
        tools: List = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.system_prompt = system_prompt
        self.user_prompt_template = user_prompt_template
        self.parameters = parameters or {}
        self.tools = tools or []
        self.memory = AgentMemory()
        self.performance_metrics = PerformanceMetrics()
    
    async def execute(self, input_data: Dict, context: Dict = None) -> Dict:
        """Execute the AI agent with given input"""
        try:
            # Prepare messages
            messages = self._prepare_messages(input_data, context)
            
            # Execute LLM call
            llm_manager = get_llm_manager()
            result = await llm_manager.execute_completion(
                provider_name=self.llm_provider,
                model=self.llm_model,
                messages=messages,
                user_id=context.get("user_id"),
                organization_id=context.get("organization_id"),
                **self.parameters
            )
            
            # Process tools if needed
            if self.tools and self._has_tool_calls(result):
                result = await self._process_tools(result, context)
            
            # Update memory
            await self.memory.add_interaction(input_data, result)
            
            # Record metrics
            await self.performance_metrics.record_execution(result)
            
            return {
                "output": result["content"],
                "metadata": {
                    "agent_id": self.agent_id,
                    "model": result["model"],
                    "usage": result["usage"],
                    "execution_time": result.get("execution_time"),
                    "cost": result.get("cost")
                }
            }
            
        except Exception as e:
            await self.performance_metrics.record_error(str(e))
            raise AgentExecutionError(f"Agent {self.name} execution failed: {str(e)}")
    
    def _prepare_messages(self, input_data: Dict, context: Dict) -> List[Dict]:
        """Prepare messages for LLM call"""
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add memory context if available
        memory_context = self.memory.get_relevant_context(input_data)
        if memory_context:
            messages.append({
                "role": "system", 
                "content": f"Previous context: {memory_context}"
            })
        
        # Prepare user message from template
        user_message = self.user_prompt_template.format(**input_data)
        messages.append({"role": "user", "content": user_message})
        
        return messages

# Specialized Agent Types
class RFPAnalysisAgent(AIAgent):
    """Specialized agent for RFP analysis"""
    
    def __init__(self, agent_id: str, **kwargs):
        system_prompt = """
        You are an expert RFP analyst with deep knowledge of procurement processes,
        risk assessment, and project evaluation. Your role is to analyze RFP documents
        and provide strategic recommendations.
        
        Analyze the following aspects:
        1. Technical requirements and complexity
        2. Financial considerations and budget alignment
        3. Timeline feasibility and resource requirements
        4. Risk factors (technical, legal, commercial)
        5. Strategic value and opportunity assessment
        
        Provide a clear Go/No-Go recommendation with detailed justification.
        """
        
        user_prompt_template = """
        Analyze the following RFP:
        
        Title: {title}
        Description: {description}
        Requirements: {requirements}
        Budget: {budget_min} - {budget_max} {currency}
        Deadline: {submission_deadline}
        
        Provide your analysis and recommendation.
        """
        
        super().__init__(
            agent_id=agent_id,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt_template,
            **kwargs
        )

class ProposalGeneratorAgent(AIAgent):
    """Specialized agent for proposal generation"""
    
    def __init__(self, agent_id: str, **kwargs):
        system_prompt = """
        You are an expert proposal writer with extensive experience in creating
        winning technical and commercial proposals. Your role is to generate
        comprehensive, compliant, and compelling proposal content.
        
        Focus on:
        1. Complete requirement compliance
        2. Clear technical approach and methodology
        3. Realistic project timeline and milestones
        4. Qualified team structure and expertise
        5. Competitive pricing strategy
        6. Risk mitigation and quality assurance
        
        Generate professional, well-structured proposal content.
        """
        
        super().__init__(
            agent_id=agent_id,
            system_prompt=system_prompt,
            **kwargs
        )
```

---

## 🔀 **WORKFLOW ENGINE SPECIFICATIONS**

### **Workflow Designer Architecture**
```typescript
// Workflow Node Types
interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: NodeData;
  inputs: NodeInput[];
  outputs: NodeOutput[];
}

enum NodeType {
  // AI Nodes
  AI_AGENT = 'ai_agent',
  LLM_CALL = 'llm_call',
  
  // Logic Nodes
  DECISION = 'decision',
  CONDITION = 'condition',
  LOOP = 'loop',
  
  // Data Nodes
  DATA_INPUT = 'data_input',
  DATA_OUTPUT = 'data_output',
  DATA_TRANSFORM = 'data_transform',
  
  // Integration Nodes
  API_CALL = 'api_call',
  DATABASE = 'database',
  FILE_OPERATION = 'file_operation',
  
  // Notification Nodes
  EMAIL = 'email',
  SMS = 'sms',
  WEBHOOK = 'webhook'
}

// Workflow Execution Engine
class WorkflowEngine {
  private executionContext: ExecutionContext;
  private nodeExecutors: Map<NodeType, NodeExecutor>;
  
  constructor() {
    this.nodeExecutors = new Map();
    this.registerExecutors();
  }
  
  async executeWorkflow(
    workflow: Workflow,
    triggerData: any,
    context: ExecutionContext
  ): Promise<WorkflowResult> {
    const execution = new WorkflowExecution(workflow, triggerData, context);
    
    try {
      // Start execution from trigger nodes
      const startNodes = workflow.nodes.filter(node => node.type === 'trigger');
      
      for (const startNode of startNodes) {
        await this.executeNode(startNode, execution);
      }
      
      // Wait for all parallel executions to complete
      await execution.waitForCompletion();
      
      return {
        success: true,
        result: execution.getResult(),
        executionTime: execution.getExecutionTime(),
        metrics: execution.getMetrics()
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message,
        executionTime: execution.getExecutionTime(),
        partialResult: execution.getPartialResult()
      };
    }
  }
  
  private async executeNode(
    node: WorkflowNode,
    execution: WorkflowExecution
  ): Promise<any> {
    const executor = this.nodeExecutors.get(node.type);
    if (!executor) {
      throw new Error(`No executor found for node type: ${node.type}`);
    }
    
    // Get input data from previous nodes
    const inputData = await this.getNodeInputData(node, execution);
    
    // Execute the node
    const result = await executor.execute(node, inputData, execution.context);
    
    // Store result in execution context
    execution.setNodeResult(node.id, result);
    
    // Execute downstream nodes
    const downstreamNodes = this.getDownstreamNodes(node, execution.workflow);
    for (const downstreamNode of downstreamNodes) {
      await this.executeNode(downstreamNode, execution);
    }
    
    return result;
  }
}

// AI Agent Node Executor
class AIAgentExecutor implements NodeExecutor {
  async execute(
    node: WorkflowNode,
    inputData: any,
    context: ExecutionContext
  ): Promise<any> {
    const { agentId, parameters } = node.data;
    
    // Get agent from registry
    const agentService = new AIAgentService(context.db);
    const agent = await agentService.getAgent(agentId);
    
    // Execute agent
    const result = await agent.execute(inputData, {
      user_id: context.userId,
      organization_id: context.organizationId,
      workflow_id: context.workflowId,
      execution_id: context.executionId,
      ...parameters
    });
    
    return result;
  }
}
```

### **Module System Architecture**
```python
# Module Definition Interface
class ModuleDefinition:
    def __init__(
        self,
        module_id: str,
        name: str,
        description: str,
        version: str,
        dependencies: List[str] = None,
        workflows: List[Dict] = None,
        agents: List[Dict] = None,
        templates: List[Dict] = None,
        configurations: Dict = None
    ):
        self.module_id = module_id
        self.name = name
        self.description = description
        self.version = version
        self.dependencies = dependencies or []
        self.workflows = workflows or []
        self.agents = agents or []
        self.templates = templates or []
        self.configurations = configurations or {}
    
    def validate(self) -> bool:
        """Validate module definition"""
        # Check required fields
        if not all([self.module_id, self.name, self.version]):
            return False
        
        # Validate workflows
        for workflow in self.workflows:
            if not self._validate_workflow(workflow):
                return False
        
        # Validate agents
        for agent in self.agents:
            if not self._validate_agent(agent):
                return False
        
        return True
    
    def _validate_workflow(self, workflow: Dict) -> bool:
        required_fields = ['name', 'definition', 'trigger_type']
        return all(field in workflow for field in required_fields)
    
    def _validate_agent(self, agent: Dict) -> bool:
        required_fields = ['name', 'llm_provider', 'system_prompt']
        return all(field in agent for field in required_fields)

# Module Manager
class ModuleManager:
    def __init__(self):
        self.installed_modules = {}
        self.module_registry = ModuleRegistry()
    
    async def install_module(
        self,
        module_definition: ModuleDefinition,
        organization_id: str
    ) -> bool:
        """Install a module for an organization"""
        try:
            # Validate module
            if not module_definition.validate():
                raise ValueError("Invalid module definition")
            
            # Check dependencies
            await self._check_dependencies(module_definition.dependencies)
            
            # Install workflows
            workflow_service = WorkflowService()
            for workflow_def in module_definition.workflows:
                await workflow_service.create_workflow(
                    workflow_def, organization_id
                )
            
            # Install agents
            agent_service = AIAgentService()
            for agent_def in module_definition.agents:
                await agent_service.create_agent(
                    agent_def, organization_id
                )
            
            # Install templates
            template_service = TemplateService()
            for template_def in module_definition.templates:
                await template_service.create_template(
                    template_def, organization_id
                )
            
            # Record installation
            self.installed_modules[module_definition.module_id] = {
                "definition": module_definition,
                "organization_id": organization_id,
                "installed_at": datetime.utcnow(),
                "status": "active"
            }
            
            return True
            
        except Exception as e:
            await self._rollback_installation(module_definition, organization_id)
            raise ModuleInstallationError(f"Failed to install module: {str(e)}")
    
    async def uninstall_module(
        self,
        module_id: str,
        organization_id: str
    ) -> bool:
        """Uninstall a module"""
        if module_id not in self.installed_modules:
            raise ValueError(f"Module {module_id} not installed")
        
        module_info = self.installed_modules[module_id]
        module_def = module_info["definition"]
        
        # Remove workflows, agents, templates
        # This should be done in reverse order of installation
        
        # Remove from installed modules
        del self.installed_modules[module_id]
        
        return True

# Pre-built Modules
class RFPAnalysisModule(ModuleDefinition):
    def __init__(self):
        super().__init__(
            module_id="rfp_analysis_v1",
            name="RFP Analysis & Decision Support",
            description="Complete RFP analysis with AI-powered recommendations",
            version="1.0.0",
            workflows=[
                {
                    "name": "RFP Analysis Workflow",
                    "description": "Automated RFP analysis and recommendation",
                    "definition": {
                        "nodes": [
                            {
                                "id": "rfp_input",
                                "type": "data_input",
                                "data": {"schema": "rfp_document"}
                            },
                            {
                                "id": "analysis_agent",
                                "type": "ai_agent",
                                "data": {"agent_type": "rfp_analyzer"}
                            },
                            {
                                "id": "risk_assessment",
                                "type": "ai_agent",
                                "data": {"agent_type": "risk_assessor"}
                            },
                            {
                                "id": "decision_matrix",
                                "type": "decision",
                                "data": {"criteria": "go_no_go_logic"}
                            },
                            {
                                "id": "report_output",
                                "type": "data_output",
                                "data": {"format": "analysis_report"}
                            }
                        ],
                        "connections": [
                            {"from": "rfp_input", "to": "analysis_agent"},
                            {"from": "analysis_agent", "to": "risk_assessment"},
                            {"from": "risk_assessment", "to": "decision_matrix"},
                            {"from": "decision_matrix", "to": "report_output"}
                        ]
                    },
                    "trigger_type": "document_upload"
                }
            ],
            agents=[
                {
                    "name": "RFP Analyzer",
                    "type": "rfp_analyzer",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4",
                    "system_prompt": "You are an expert RFP analyst...",
                    "user_prompt_template": "Analyze this RFP: {rfp_content}"
                },
                {
                    "name": "Risk Assessor",
                    "type": "risk_assessor",
                    "llm_provider": "anthropic",
                    "llm_model": "claude-3-sonnet",
                    "system_prompt": "You are a risk assessment expert...",
                    "user_prompt_template": "Assess risks for: {analysis_result}"
                }
            ]
        )
```

---

## 📄 **DOCUMENT MANAGEMENT SPECIFICATIONS**

### **Advanced Document Processing**
```python
# Document Processing Pipeline
class DocumentProcessor:
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.parser_registry = ParserRegistry()
        self.ai_analyzer = AIDocumentAnalyzer()
        self.storage_manager = StorageManager()
    
    async def process_document(
        self,
        file: UploadFile,
        organization_id: str,
        user_id: str,
        metadata: Dict = None
    ) -> ProcessedDocument:
        """Complete document processing pipeline"""
        
        # 1. File validation and storage
        file_info = await self._validate_and_store(file, organization_id)
        
        # 2. Content extraction
        content = await self._extract_content(file_info)
        
        # 3. AI analysis
        analysis = await self._analyze_content(content, file_info)
        
        # 4. Metadata enrichment
        enriched_metadata = await self._enrich_metadata(
            content, analysis, metadata
        )
        
        # 5. Database storage
        document = await self._store_document_record({
            **file_info,
            "content": content,
            "analysis": analysis,
            "metadata": enriched_metadata,
            "organization_id": organization_id,
            "uploaded_by": user_id
        })
        
        return document
    
    async def _extract_content(self, file_info: Dict) -> Dict:
        """Extract content based on file type"""
        file_type = file_info["file_type"]
        file_path = file_info["storage_path"]
        
        parser = self.parser_registry.get_parser(file_type)
        if not parser:
            raise UnsupportedFileTypeError(f"No parser for {file_type}")
        
        content = await parser.extract(file_path)
        
        # OCR for image-based documents
        if file_type in ["pdf", "image"] and not content.get("text"):
            ocr_result = await self.ocr_engine.extract_text(file_path)
            content["text"] = ocr_result["text"]
            content["ocr_confidence"] = ocr_result["confidence"]
        
        return content
    
    async def _analyze_content(self, content: Dict, file_info: Dict) -> Dict:
        """AI-powered content analysis"""
        analysis_tasks = [
            self.ai_analyzer.classify_document(content),
            self.ai_analyzer.extract_entities(content),
            self.ai_analyzer.summarize_content(content),
            self.ai_analyzer.assess_quality(content),
            self.ai_analyzer.extract_requirements(content)
        ]
        
        results = await asyncio.gather(*analysis_tasks)
        
        return {
            "classification": results[0],
            "entities": results[1],
            "summary": results[2],
            "quality_score": results[3],
            "requirements": results[4],
            "processed_at": datetime.utcnow().isoformat()
        }

# Document Parser Registry
class ParserRegistry:
    def __init__(self):
        self.parsers = {
            "pdf": PDFParser(),
            "docx": DocxParser(),
            "txt": TextParser(),
            "xlsx": ExcelParser(),
            "pptx": PowerPointParser()
        }
    
    def get_parser(self, file_type: str) -> Optional[DocumentParser]:
        return self.parsers.get(file_type.lower())

# AI Document Analyzer
class AIDocumentAnalyzer:
    def __init__(self):
        self.llm_manager = get_llm_manager()
        self.classification_agent = DocumentClassificationAgent()
        self.entity_extraction_agent = EntityExtractionAgent()
    
    async def classify_document(self, content: Dict) -> Dict:
        """Classify document type and category"""
        text = content.get("text", "")[:5000]  # Limit for efficiency
        
        result = await self.classification_agent.execute({
            "text": text,
            "filename": content.get("filename", "")
        })
        
        return {
            "document_type": result["document_type"],
            "category": result["category"],
            "confidence": result["confidence"],
            "tags": result.get("tags", [])
        }
    
    async def extract_entities(self, content: Dict) -> List[Dict]:
        """Extract named entities and key information"""
        text = content.get("text", "")
        
        result = await self.entity_extraction_agent.execute({
            "text": text
        })
        
        return result["entities"]
    
    async def assess_quality(self, content: Dict) -> Dict:
        """Assess document quality and completeness"""
        metrics = {
            "readability": self._calculate_readability(content["text"]),
            "completeness": self._assess_completeness(content),
            "structure": self._assess_structure(content),
            "clarity": await self._assess_clarity(content["text"])
        }
        
        overall_score = sum(metrics.values()) / len(metrics)
        
        return {
            "overall_score": overall_score,
            "metrics": metrics,
            "recommendations": self._generate_quality_recommendations(metrics)
        }
```

---

## 🎨 **TEMPLATE DESIGNER SPECIFICATIONS**

### **Template Engine Architecture**
```python
# Template Designer Engine
class TemplateEngine:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.pdf_generator = PDFGenerator()
        self.pptx_generator = PowerPointGenerator()
        self.html_generator = HTMLGenerator()
    
    async def create_template(
        self,
        template_data: Dict,
        organization_id: str,
        user_id: str
    ) -> Template:
        """Create a new template"""
        
        # Validate template structure
        validator = TemplateValidator()
        validation_result = validator.validate(template_data)
        if not validation_result.is_valid:
            raise TemplateValidationError(validation_result.errors)
        
        # Process template components
        processed_template = await self._process_template_components(template_data)
        
        # Store template
        template = Template(
            name=template_data["name"],
            type=template_data["type"],
            structure=processed_template,
            organization_id=organization_id,
            created_by=user_id
        )
        
        await self._store_template(template)
        return template
    
    async def generate_document(
        self,
        template_id: str,
        data: Dict,
        output_format: str = "pdf"
    ) -> GeneratedDocument:
        """Generate document from template and data"""
        
        # Get template
        template = await self._get_template(template_id)
        
        # Render template with data
        rendered_content = await self._render_template(template, data)
        
        # Generate final document
        generator = self._get_generator(output_format)
        document = await generator.generate(rendered_content, template.style)
        
        return GeneratedDocument(
            content=document,
            format=output_format,
            template_id=template_id,
            generated_at=datetime.utcnow()
        )
    
    async def _render_template(self, template: Template, data: Dict) -> str:
        """Render template with provided data"""
        jinja_template = self.jinja_env.from_string(template.structure["content"])
        
        # Add helper functions
        data.update({
            "format_date": self._format_date,
            "format_currency": self._format_currency,
            "format_number": self._format_number
        })
        
        return jinja_template.render(**data)

# PDF Generator
class PDFGenerator:
    def __init__(self):
        self.css_processor = CSSProcessor()
        self.weasyprint_config = self._setup_weasyprint()
    
    async def generate(self, html_content: str, styles: Dict) -> bytes:
        """Generate PDF from HTML content"""
        
        # Process CSS styles
        css_content = await self.css_processor.process_styles(styles)
        
        # Generate PDF
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=css_content)
        
        pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
        
        return pdf_bytes

# PowerPoint Generator
class PowerPointGenerator:
    def __init__(self):
        self.pptx_processor = PowerPointProcessor()
    
    async def generate(self, content: Dict, template_config: Dict) -> bytes:
        """Generate PowerPoint presentation"""
        
        # Create presentation
        prs = Presentation()
        
        # Process slides
        for slide_data in content["slides"]:
            slide = self._create_slide(prs, slide_data, template_config)
        
        # Save to bytes
        output = BytesIO()
        prs.save(output)
        output.seek(0)
        
        return output.getvalue()
    
    def _create_slide(self, prs, slide_data: Dict, config: Dict):
        """Create individual slide"""
        slide_layout = prs.slide_layouts[slide_data.get("layout", 0)]
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        if "title" in slide_data:
            title = slide.shapes.title
            title.text = slide_data["title"]
        
        # Add content
        if "content" in slide_data:
            content_placeholder = slide.placeholders[1]
            content_placeholder.text = slide_data["content"]
        
        # Add images, charts, etc.
        if "images" in slide_data:
            for image_data in slide_data["images"]:
                self._add_image(slide, image_data)
        
        return slide

# Template Library
class TemplateLibrary:
    """Pre-built template library"""
    
    @staticmethod
    def get_rfp_template() -> Dict:
        return {
            "name": "Standard RFP Template",
            "type": "rfp",
            "structure": {
                "sections": [
                    {
                        "id": "cover_page",
                        "title": "Cover Page",
                        "content": """
                        <div class="cover-page">
                            <h1>{{ rfp.title }}</h1>
                            <p>RFP Number: {{ rfp.rfp_number }}</p>
                            <p>Issue Date: {{ format_date(rfp.issue_date) }}</p>
                            <p>Submission Deadline: {{ format_date(rfp.submission_deadline) }}</p>
                            <div class="organization">
                                <h2>{{ organization.name }}</h2>
                                <p>{{ organization.address }}</p>
                            </div>
                        </div>
                        """
                    },
                    {
                        "id": "executive_summary",
                        "title": "Executive Summary",
                        "content": """
                        <section class="executive-summary">
                            <h2>Executive Summary</h2>
                            <p>{{ rfp.description }}</p>
                            <h3>Key Requirements</h3>
                            <ul>
                            {% for requirement in rfp.requirements %}
                                <li>{{ requirement }}</li>
                            {% endfor %}
                            </ul>
                        </section>
                        """
                    }
                ]
            },
            "styles": {
                "cover-page": {
                    "text-align": "center",
                    "margin": "50px",
                    "font-family": "Arial, sans-serif"
                },
                "h1": {
                    "color": "#2c3e50",
                    "font-size": "2.5em",
                    "margin-bottom": "20px"
                }
            }
        }
    
    @staticmethod
    def get_proposal_template() -> Dict:
        return {
            "name": "Technical Proposal Template",
            "type": "proposal",
            "structure": {
                "sections": [
                    {
                        "id": "technical_approach",
                        "title": "Technical Approach",
                        "content": """
                        <section class="technical-approach">
                            <h2>Technical Approach</h2>
                            <h3>Methodology</h3>
                            <p>{{ proposal.methodology }}</p>
                            
                            <h3>Technical Solution</h3>
                            <p>{{ proposal.technical_solution }}</p>
                            
                            <h3>Implementation Plan</h3>
                            <ol>
                            {% for phase in proposal.implementation_phases %}
                                <li>
                                    <strong>{{ phase.name }}</strong> ({{ phase.duration }})
                                    <br>{{ phase.description }}
                                </li>
                            {% endfor %}
                            </ol>
                        </section>
                        """
                    }
                ]
            }
        }
```

---

This technical specification provides a comprehensive blueprint for the TenderWise AI v2 redesign. The architecture is designed to be:

- **🏢 Enterprise-Grade**: Scalable, secure, and maintainable
- **🤖 AI-Native**: Built from the ground up for AI integration
- **🌍 Global-Ready**: Multi-language, multi-currency, multi-entity support
- **🔧 Extensible**: Modular architecture for future enhancements
- **👥 Developer-Friendly**: Clear patterns and comprehensive documentation

The next step is to begin Phase 1 implementation according to the roadmap in the Complete Redesign Plan.

---

**🤖 Generated with [Memex](https://memex.tech)**  
**Co-Authored-By: Memex <noreply@memex.tech>**