# TenderWise AI - Enterprise AI Platform for RFP & Tendering

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Svelte](https://img.shields.io/badge/Svelte-4.0+-orange.svg)](https://svelte.dev)

## 🎯 Overview

**TenderWise AI** is a comprehensive enterprise-grade AI platform designed to revolutionize the Request for Proposal (RFP) and tendering process through advanced AI agent orchestration, visual workflow design, and multi-tenant architecture.

### Key Features

- 🎨 **Visual AI Workflow Designer** - Drag-drop interface for creating custom AI workflows
- 🤖 **AI Agent Orchestration** - Multi-LLM support with cost tracking and management
- 📄 **Advanced Template Designer** - PDF/PowerPoint generation with AI content injection
- 🏢 **Multi-tenant Architecture** - Complete entity isolation with RBAC
- 🌍 **Internationalization** - Arabic/English support with RTL/LTR layouts
- 📅 **Dual Calendar System** - Hijri and Gregorian calendar support
- 📊 **Dashboard Builder** - Visual analytics and KPI tracking
- 🔧 **API Management** - Complete API gateway and integration platform

## 🏗️ Architecture

Built on proven enterprise foundations:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: Svelte + TypeScript + Vite
- **AI Engine**: Multi-LLM support (OpenAI, Anthropic, Azure, Local)
- **Workflow Engine**: Langflow-inspired visual designer
- **Authentication**: OAuth2 + JWT with RBAC
- **Deployment**: Docker + Kubernetes ready

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/tenderwise-ai.git
cd tenderwise-ai
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start Development Services**
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Or start individually:
# Backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Frontend: npm run dev
```

6. **Access the Application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Development Guide](docs/development.md)
- [API Documentation](docs/api.md)
- [Workflow Designer Guide](docs/workflows.md)
- [Deployment Guide](docs/deployment.md)
- [Contributing Guidelines](docs/contributing.md)

## 🏢 Core Modules

### Module 1: RFP Analysis & Strategic Decision Support
AI-powered analysis of RFP documents with risk assessment, resource identification, and "Go/No-Go" recommendations.

### Module 2: Proposal Compliance & Vendor Assessment  
Technical and financial proposal analysis against RFP requirements with comprehensive compliance matrix generation.

### Module 3: AI-Powered Technical Proposal Generation
RFP-driven technical proposal creation with template-based document generation and AI-assisted content.

### Module 4: RFP Creator
Template-based RFP generation with AI-assisted content creation and customizable formatting.

## 🛠️ Development

### Project Structure
```
tenderwise-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── workflows/      # AI workflow engine
├── frontend/               # Svelte frontend
│   ├── src/
│   │   ├── lib/           # Components & utilities
│   │   ├── routes/        # Page routes
│   │   └── stores/        # State management
├── docs/                  # Documentation
├── scripts/               # Deployment scripts
└── docker/               # Docker configurations
```

### Available Scripts

**Backend:**
```bash
make backend-dev          # Start backend in development mode
make backend-test         # Run backend tests
make backend-lint         # Lint backend code
make backend-format       # Format backend code
```

**Frontend:**
```bash
make frontend-dev         # Start frontend in development mode
make frontend-test        # Run frontend tests  
make frontend-build       # Build frontend for production
make frontend-lint        # Lint frontend code
```

**Full Stack:**
```bash
make dev                  # Start full development environment
make test                 # Run all tests
make build               # Build for production
make deploy              # Deploy to staging/production
```

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests  
cd frontend && npm test

# Integration tests
make test-integration

# E2E tests
make test-e2e
```

## 🚢 Deployment

### Docker Deployment
```bash
# Build and deploy
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3 --scale frontend=2
```

### Kubernetes Deployment
```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n tenderwise-ai
```

## 🔧 Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/tenderwise_ai
REDIS_URL=redis://localhost:6379

# Authentication
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_CORS=true
```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](docs/contributing.md) for details on:

- Code style and standards
- Development workflow
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-org/tenderwise-ai/issues)
- 💬 [Discussions](https://github.com/your-org/tenderwise-ai/discussions)
- 📧 [Email Support](mailto:support@tenderwise.ai)

## 🙏 Acknowledgments

Built on excellent open-source foundations:
- [Langflow](https://github.com/langflow-ai/langflow) - AI workflow inspiration
- [FastAPI Full-Stack Template](https://github.com/fastapi/full-stack-fastapi-template) - Backend architecture
- [Open WebUI](https://github.com/open-webui/open-webui) - UI/UX patterns
- [Awesome LLM Apps](https://github.com/Shubhamsaboo/awesome-llm-apps) - Implementation patterns

---

**Made with ❤️ for the future of intelligent tendering**

🤖 **Generated with [Memex](https://memex.tech)**