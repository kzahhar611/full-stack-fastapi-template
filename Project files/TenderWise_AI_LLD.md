# TenderWise AI - Low-Level Design (LLD)

## Database Schema Design

### User Management Tables
- `users`: User accounts and authentication details
- `roles`: System roles and permissions
- `user_roles`: Many-to-many relationship between users and roles
- `groups`: User groups for team organization
- `group_members`: Users belonging to each group
- `entities`: Company entities within the system
- `user_entity_access`: Access levels for users to entities
- `user_preferences`: User-specific settings (language, theme, etc.)

### AI & Agent Management Tables
- `llm_providers`: Available LLM providers and configurations
- `llm_models`: Models available from each provider
- `ai_agents`: Configured AI agents
- `agent_prompts`: System and user prompts for agents
- `agent_llm_config`: LLM configurations for each agent
- `llm_usage`: Usage tracking for billing and limitations
- `llm_cost_settings`: Cost rates and limitations

### Workflow Management Tables
- `workflows`: Workflow definitions and metadata
- `workflow_versions`: Version history for workflows
- `workflow_nodes`: Individual nodes within workflows
- `workflow_connections`: Connections between nodes
- `workflow_executions`: Execution history and results
- `workflow_templates`: Reusable workflow templates

### Document Management Tables
- `documents`: Document metadata and storage information
- `document_versions`: Version history for documents
- `document_tags`: Categorization tags for documents
- `document_permissions`: Access controls for documents
- `templates`: Document templates for generation
- `template_sections`: Sections within templates

### Module-Specific Tables
- `rfp_analysis`: RFP analysis results and metadata
- `proposal_compliance`: Compliance assessment results
- `vendor_assessments`: Vendor evaluation results
- `generated_proposals`: Metadata for generated proposals
- `generated_rfps`: Metadata for generated RFPs

### System Management Tables
- `email_templates`: Templates for system emails
- `notification_settings`: User notification preferences
- `system_logs`: System-wide transaction logs
- `user_logs`: User activity logs
- `tasks`: Task definitions and assignments
- `calendar_events`: Scheduled events
- `api_keys`: API keys for external integrations
- `scheduled_jobs`: Configuration for scheduled tasks

## Service Implementation Details

### API Gateway Implementation
- FastAPI application with middleware for authentication
- API versioning support (v1, v2, etc.)
- Request validation using Pydantic models
- Cross-Origin Resource Sharing (CORS) configuration
- Documentation via OpenAPI/Swagger

```python
# Example API Gateway route
@app.post("/api/v1/rfp/analyze", response_model=RFPAnalysisResponse)
async def analyze_rfp(
    request: RFPAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    # Validate access to entity
    validate_entity_access(current_user, request.entity_id)
    
    # Forward request to RFP Analysis Service
    response = await rfp_analysis_client.analyze(request, user_id=current_user.id)
    
    # Log the request
    await log_user_action(current_user.id, "RFP_ANALYSIS", request.rfp_id)
    
    return response
```

### Authentication Service Implementation
- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Role-based permission checking
- User registration with email verification
- Password reset functionality

```python
# Example authentication route
@auth_router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # Log successful login
    await log_user_login(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### AI Engine Service Implementation
- Agent configuration and management
- LLM provider integration
- Prompt template management
- Usage tracking and rate limiting
- Chain and workflow execution

```python
# Example AI agent execution
class AIAgentExecutor:
    def __init__(self, agent_id: str):
        self.agent = await get_agent_by_id(agent_id)
        self.llm_config = await get_llm_config(self.agent.llm_config_id)
        self.provider = await get_llm_provider(self.llm_config.provider_id)
        
    async def execute(self, input_data: dict, user_id: str):
        # Check usage limits
        await validate_usage_limits(user_id, self.provider.id)
        
        # Format prompts
        system_prompt = await format_prompt(self.agent.system_prompt, input_data)
        user_prompt = await format_prompt(self.agent.user_prompt, input_data)
        
        # Call LLM
        start_time = time.time()
        response = await self._call_llm(system_prompt, user_prompt)
        duration = time.time() - start_time
        
        # Log usage
        await log_llm_usage(
            user_id=user_id,
            agent_id=self.agent.id,
            provider_id=self.provider.id,
            model_id=self.llm_config.model_id,
            tokens_input=calculate_tokens(system_prompt + user_prompt),
            tokens_output=calculate_tokens(response),
            duration=duration
        )
        
        return response
```

### Document Processing Service Implementation
- Document parsing with appropriate libraries
- Content extraction and structure normalization
- Template rendering
- Format conversion for exports

```python
# Example proposal generation
class ProposalGenerator:
    def __init__(self, template_id: str):
        self.template = await get_template_by_id(template_id)
        
    async def generate_proposal(self, rfp_analysis: dict, user_inputs: dict):
        # Prepare content for each section
        sections = await self._prepare_sections(rfp_analysis, user_inputs)
        
        # Apply template formatting
        document = await self._apply_template(sections)
        
        # Generate outputs in requested formats
        outputs = {}
        if user_inputs.get("formats", {}).get("pdf"):
            outputs["pdf"] = await self._generate_pdf(document)
        if user_inputs.get("formats", {}).get("pptx"):
            outputs["pptx"] = await self._generate_pptx(document)
        if user_inputs.get("formats", {}).get("html"):
            outputs["html"] = await self._generate_html(document)
            
        return outputs
```

### Workflow Management Service Implementation
- Workflow definition and validation
- Node configuration
- Execution engine
- State management

```python
# Example workflow execution
class WorkflowExecutor:
    def __init__(self, workflow_id: str, version_id: str = None):
        self.workflow = await get_workflow(workflow_id, version_id)
        self.nodes = await get_workflow_nodes(self.workflow.id)
        self.connections = await get_workflow_connections(self.workflow.id)
        
    async def execute(self, input_data: dict, user_id: str):
        # Initialize execution context
        execution_id = generate_uuid()
        context = {
            "execution_id": execution_id,
            "user_id": user_id,
            "start_time": datetime.now(),
            "input_data": input_data,
            "node_results": {},
            "status": "running"
        }
        
        # Find start nodes (nodes with no incoming connections)
        start_nodes = self._find_start_nodes()
        
        # Execute workflow starting from start nodes
        try:
            for node_id in start_nodes:
                await self._execute_node(node_id, context)
            
            context["status"] = "completed"
        except Exception as e:
            context["status"] = "failed"
            context["error"] = str(e)
            
        # Save execution results
        await save_workflow_execution(context)
        
        return context
```

## Frontend Component Design

### Layout and Theme System
- Responsive layout using CSS Grid and Flexbox
- Theme provider with support for light/dark modes
- RTL/LTR switching based on language
- Customizable color schemes per entity

```typescript
// Theme configuration example
const themeConfig = {
  themes: {
    light: {
      primary: '#003366',      // PRIMARY_BLUE
      secondary: '#708090',    // SLATE_CUSTOM
      accent: '#D4AF37',       // GOLD_ACCENT
      background: '#FFFFFF',
      text: '#333333',
      // ... other colors
    },
    dark: {
      primary: '#1A4B77',
      secondary: '#4F5D6A',
      accent: '#D4AF37',
      background: '#1E1E1E',
      text: '#F5F5F5',
      // ... other colors
    }
  },
  fonts: {
    main: "'Inter', sans-serif",
    heading: "'Poppins', sans-serif",
    arabic: "'Cairo', sans-serif",
  }
};
```

### Workflow Editor Component
- Canvas-based editor using React Flow
- Custom node types for different agent capabilities
- Connection validation
- Property editors for nodes
- Mini-map and zoom controls

```typescript
// Example workflow editor component
const WorkflowEditor: React.FC<WorkflowEditorProps> = ({ workflowId }) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    // Load workflow data
    if (workflowId) {
      loadWorkflow(workflowId);
    }
  }, [workflowId]);

  const loadWorkflow = async (id: string) => {
    const { nodes, connections } = await workflowService.getWorkflow(id);
    setNodes(mapNodesToReactFlow(nodes));
    setEdges(mapConnectionsToReactFlow(connections));
  };

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // ... other handlers and rendering logic
};
```

### Document Template Editor
- WYSIWYG editor for template creation
- Dynamic content placeholders
- Preview mode
- Export options

### Dashboard Designer
- Drag-and-drop widget placement
- Widget library (charts, tables, metrics, etc.)
- Data source configuration
- Layout persistence

## API Endpoints

### Authentication API
- `POST /api/auth/register`: Create new user account
- `POST /api/auth/login`: Authenticate user
- `POST /api/auth/refresh`: Refresh access token
- `GET /api/auth/me`: Get current user profile
- `PUT /api/auth/me`: Update user profile
- `POST /api/auth/password/reset-request`: Request password reset
- `POST /api/auth/password/reset`: Reset password

### User Management API
- `GET /api/users`: List users (admin only)
- `GET /api/users/{id}`: Get user details
- `PUT /api/users/{id}`: Update user
- `DELETE /api/users/{id}`: Delete user
- `GET /api/users/{id}/permissions`: Get user permissions
- `PUT /api/users/{id}/permissions`: Update user permissions

### Entity Management API
- `GET /api/entities`: List accessible entities
- `POST /api/entities`: Create new entity (admin only)
- `GET /api/entities/{id}`: Get entity details
- `PUT /api/entities/{id}`: Update entity
- `GET /api/entities/{id}/users`: List users with access to entity
- `PUT /api/entities/{id}/users/{user_id}`: Update user's entity access

### AI Agent API
- `GET /api/agents`: List available agents
- `POST /api/agents`: Create new agent
- `GET /api/agents/{id}`: Get agent details
- `PUT /api/agents/{id}`: Update agent
- `DELETE /api/agents/{id}`: Delete agent
- `POST /api/agents/{id}/execute`: Execute agent
- `GET /api/agents/{id}/usage`: Get agent usage statistics

### Workflow API
- `GET /api/workflows`: List workflows
- `POST /api/workflows`: Create new workflow
- `GET /api/workflows/{id}`: Get workflow details
- `PUT /api/workflows/{id}`: Update workflow
- `DELETE /api/workflows/{id}`: Delete workflow
- `POST /api/workflows/{id}/execute`: Execute workflow
- `GET /api/workflows/{id}/executions`: List workflow executions
- `GET /api/workflows/{id}/versions`: List workflow versions
- `POST /api/workflows/{id}/versions`: Create new workflow version

### Document API
- `GET /api/documents`: List documents
- `POST /api/documents`: Upload new document
- `GET /api/documents/{id}`: Get document details
- `PUT /api/documents/{id}`: Update document metadata
- `DELETE /api/documents/{id}`: Delete document
- `GET /api/documents/{id}/content`: Download document
- `GET /api/documents/{id}/versions`: List document versions
- `POST /api/documents/{id}/versions`: Create new document version

### RFP Module API
- `POST /api/rfp/analyze`: Analyze RFP document
- `GET /api/rfp/analysis/{id}`: Get analysis results
- `POST /api/rfp/generate`: Generate new RFP
- `GET /api/rfp/templates`: List RFP templates

### Proposal Module API
- `POST /api/proposals/generate`: Generate proposal
- `POST /api/proposals/assess`: Assess proposal compliance
- `GET /api/proposals/templates`: List proposal templates

### Task Management API
- `GET /api/tasks`: List tasks
- `POST /api/tasks`: Create new task
- `GET /api/tasks/{id}`: Get task details
- `PUT /api/tasks/{id}`: Update task
- `DELETE /api/tasks/{id}`: Delete task
- `PUT /api/tasks/{id}/status`: Update task status

### Calendar API
- `GET /api/calendar/events`: List calendar events
- `POST /api/calendar/events`: Create new event
- `GET /api/calendar/events/{id}`: Get event details
- `PUT /api/calendar/events/{id}`: Update event
- `DELETE /api/calendar/events/{id}`: Delete event

### Notification API
- `GET /api/notifications`: List notifications
- `PUT /api/notifications/{id}/read`: Mark notification as read
- `GET /api/notifications/settings`: Get notification settings
- `PUT /api/notifications/settings`: Update notification settings

## Error Handling Strategy

### Error Classification
- `ValidationError`: Input validation failures
- `AuthenticationError`: Authentication issues
- `AuthorizationError`: Permission-related errors
- `ResourceNotFoundError`: Requested resource does not exist
- `ServiceError`: Internal service failures
- `DependencyError`: External service failures
- `RateLimitError`: Usage limitations exceeded
- `BusinessLogicError`: Application-specific rules violations

### Error Response Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested document was not found",
    "details": {
      "resourceType": "document",
      "resourceId": "123456"
    },
    "requestId": "abcd1234-efgh-5678-ijkl-9012mnopqrst"
  }
}
```

### Frontend Error Handling
- Global error boundary components
- Error interceptors for API calls
- Toast notifications for errors
- Guided error recovery where possible

## Data Migration Strategy

- Database schema versioning
- Migration scripts for schema updates
- Data transformation utilities
- Backup and rollback procedures
- Validation and testing processes

## Internationalization Implementation

### Backend
- Message templates with placeholders
- Language-specific date and number formatting
- Database storage of translated content

### Frontend
- i18next integration
- Language detection and switching
- RTL/LTR layout handling
- Currency and date format localization

```typescript
// i18n configuration example
const i18nConfig = {
  resources: {
    en: {
      translation: {
        // English translations
        "dashboard.title": "Dashboard",
        "rfp.analysis.title": "RFP Analysis",
        // ... more translations
      }
    },
    ar: {
      translation: {
        // Arabic translations
        "dashboard.title": "لوحة المعلومات",
        "rfp.analysis.title": "تحليل طلب تقديم العروض",
        // ... more translations
      }
    }
  },
  lng: "en",
  fallbackLng: "en",
  interpolation: {
    escapeValue: false
  },
  react: {
    useSuspense: false
  }
};
```

## Security Implementation Details

### Authentication Flow
- Username/password validation
- JWT token generation and verification
- Refresh token rotation
- Session invalidation on logout
- Account lockout after failed attempts

### Data Access Control
- Entity-level access control
- Row-level security in database
- API permission validation
- Frontend component conditional rendering

### Secure Communication
- HTTPS enforcement
- API key validation for external integrations
- Request origin validation
- Content Security Policy implementation

## Monitoring and Logging

### Log Structure
```json
{
  "timestamp": "2025-06-03T12:34:56.789Z",
  "level": "INFO",
  "service": "rfp-analysis-service",
  "traceId": "abcd1234-efgh-5678-ijkl-9012mnopqrst",
  "userId": "user123",
  "entityId": "entity456",
  "action": "RFP_ANALYSIS_REQUESTED",
  "resource": {
    "type": "document",
    "id": "doc789"
  },
  "message": "RFP analysis requested",
  "additionalData": {
    // Context-specific information
  }
}
```

### Performance Metrics
- API response times
- Database query performance
- AI model execution times
- Resource utilization
- Error rates

### Alerts
- Service availability issues
- Error rate thresholds
- Performance degradation
- Security incidents
- Usage quota warnings
