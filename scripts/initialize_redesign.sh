#!/bin/bash

# TenderWise AI - Complete Redesign Initialization Script
# This script sets up the new project structure for the complete redesign

set -e

echo "🚀 TenderWise AI - Complete Redesign Initialization"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="tenderwise-ai"
NEW_PROJECT_DIR="../tenderwise-ai-v2"

echo -e "${BLUE}📋 Project Configuration:${NC}"
echo "  Project Name: $PROJECT_NAME"
echo "  Directory: $NEW_PROJECT_DIR"
echo "  Architecture: Microservices with Next.js + FastAPI"
echo ""

# Create main project directory
echo -e "${YELLOW}📁 Creating project structure...${NC}"
mkdir -p "$NEW_PROJECT_DIR"
cd "$NEW_PROJECT_DIR"

# Initialize git repository
echo -e "${YELLOW}🔧 Initializing Git repository...${NC}"
git init
echo "# TenderWise AI - Enterprise RFP & Tendering Platform" > README.md

# Create main directory structure
echo -e "${YELLOW}📂 Creating directory structure...${NC}"

# Frontend structure (Next.js 14)
mkdir -p frontend/{src/{app,components,lib,hooks,providers,types},public,docs}
mkdir -p frontend/src/components/{ui,forms,charts,workflow,agents,templates}
mkdir -p frontend/src/lib/{auth,api,stores,i18n,utils}
mkdir -p frontend/src/app/{api,\[locale\],\(auth\),\(dashboard\)}

# Backend structure (Microservices)
mkdir -p backend/{gateway,services,shared,docs,tests}
mkdir -p backend/services/{auth,users,rfp,documents,ai-agents,workflows,modules,templates,notifications,analytics,llm-manager,scheduler,audit}

# Infrastructure
mkdir -p infrastructure/{docker,kubernetes,terraform,monitoring}

# Documentation
mkdir -p docs/{architecture,api,user-guide,deployment}

# Configuration
mkdir -p config/{development,staging,production}

# Scripts
mkdir -p scripts/{deployment,development,data}

echo -e "${GREEN}✅ Directory structure created${NC}"

# Create initial configuration files
echo -e "${YELLOW}⚙️ Creating configuration files...${NC}"

# Frontend package.json template
cat > frontend/package.json << 'EOF'
{
  "name": "tenderwise-ai-frontend",
  "version": "2.0.0",
  "description": "TenderWise AI - Enterprise RFP & Tendering Platform Frontend",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "@tailwindcss/forms": "^0.5.7",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    "framer-motion": "^10.16.16",
    "react-query": "^3.39.3",
    "zustand": "^4.4.7",
    "react-hook-form": "^7.48.2",
    "react-flow-renderer": "^10.3.17",
    "next-intl": "^3.0.0",
    "date-fns": "^2.30.0",
    "date-fns-jalali": "^2.30.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
EOF

# Backend requirements template
cat > backend/requirements.txt << 'EOF'
# TenderWise AI Backend Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
asyncpg==0.29.0
redis==5.0.1
celery==5.3.4
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
httpx==0.25.2
openai==1.3.8
anthropic==0.7.7
langchain==0.0.340
langchain-openai==0.0.2
langchain-anthropic==0.0.1
elasticsearch==8.11.0
minio==7.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
python-dotenv==1.0.0
loguru==0.7.2
prometheus-client==0.19.0
structlog==23.2.0
EOF

# Docker Compose for development
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: tenderwise_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis for caching and background tasks
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Elasticsearch for search
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  # MinIO for file storage
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  minio_data:
EOF

# Environment template
cat > .env.example << 'EOF'
# TenderWise AI Environment Configuration

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/tenderwise_ai

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# File Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Email
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# Monitoring
ENABLE_MONITORING=true
PROMETHEUS_PORT=8090

# Features
ENABLE_AI_AGENTS=true
ENABLE_WORKFLOWS=true
ENABLE_ANALYTICS=true
EOF

# Main README
cat > README.md << 'EOF'
# TenderWise AI - Enterprise RFP & Tendering Platform

A comprehensive, AI-powered platform designed to revolutionize the Request for Proposal (RFP) and tendering process through intelligent analysis, automation, and generation capabilities.

## 🚀 Features

### Core Modules
- **RFP Analysis & Strategic Decision Support**: AI-powered analysis with Go/No-Go recommendations
- **Proposal Compliance & Vendor Assessment**: Automated compliance checking and vendor evaluation
- **AI-Powered Technical Proposal Generation**: Intelligent proposal creation and optimization
- **RFP Creator**: Smart RFP generation with templates and AI assistance

### Platform Features
- **AI Agent Management**: Create and manage custom AI agents with LLM configurations
- **Visual Workflow Designer**: Drag-and-drop workflow creation with AI agent integration
- **Module System**: Custom module development and marketplace
- **Document Management**: Advanced document processing with AI analysis
- **Template Designer**: PDF and PowerPoint template creation and management
- **Multi-Language Support**: English and Arabic (RTL) support
- **Multi-Entity Support**: Enterprise-grade multi-tenant architecture

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with RTL support
- **State Management**: Zustand + React Query
- **UI Components**: Headless UI + Custom components
- **Internationalization**: next-intl for EN/AR support

### Backend
- **Framework**: FastAPI with microservices architecture
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Caching**: Redis for sessions and caching
- **Search**: Elasticsearch for advanced search
- **File Storage**: MinIO for document storage
- **Background Tasks**: Celery with Redis broker

### AI Integration
- **LLM Providers**: OpenAI, Anthropic, Google, Azure, Local LLMs
- **Frameworks**: LangChain for AI orchestration
- **Agent Management**: Custom agent framework
- **Cost Tracking**: Usage analytics and budget management

## 🚦 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tenderwise-ai-v2
   ```

2. **Start infrastructure services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Setup backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   
   # Setup environment
   cp ../.env.example .env
   # Edit .env with your configuration
   
   # Run migrations
   alembic upgrade head
   
   # Start backend services
   uvicorn app.main:app --reload --port 8000
   ```

4. **Setup frontend**
   ```bash
   cd frontend
   npm install
   
   # Start development server
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
tenderwise-ai-v2/
├── frontend/                 # Next.js frontend application
├── backend/                  # FastAPI microservices
├── infrastructure/           # Docker, K8s, Terraform configs
├── docs/                     # Documentation
├── scripts/                  # Deployment and utility scripts
└── config/                   # Environment configurations
```

## 🛠️ Development Workflow

### Backend Development
- Follow FastAPI best practices
- Use async/await for all database operations
- Implement comprehensive error handling
- Write tests for all endpoints
- Use Alembic for database migrations

### Frontend Development
- Use TypeScript for all components
- Follow Next.js App Router patterns
- Implement responsive design with Tailwind
- Use React Query for server state management
- Ensure accessibility compliance

### AI Integration
- Create reusable agent templates
- Implement cost tracking for all LLM calls
- Use proper error handling for AI operations
- Test AI responses thoroughly

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available configuration options.

### AI Providers
Configure your AI provider API keys in the environment file:
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Add additional providers as needed

## 📚 Documentation

- [Architecture Overview](docs/architecture/README.md)
- [API Documentation](docs/api/README.md)
- [User Guide](docs/user-guide/README.md)
- [Deployment Guide](docs/deployment/README.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Development
```bash
./scripts/deploy-dev.sh
```

### Production
```bash
./scripts/deploy-prod.sh
```

## 📄 License

Private - All Rights Reserved

## 🤝 Contributing

This is a private project. Contributing guidelines will be provided to team members.

---

**Built with ❤️ for the future of RFP and tendering processes**
EOF

# Create initial GitHub Actions workflow
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/

  test-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test
    
    - name: Build
      run: |
        cd frontend
        npm run build
EOF

# Create development scripts
mkdir -p scripts
cat > scripts/dev-setup.sh << 'EOF'
#!/bin/bash

echo "🚀 TenderWise AI Development Setup"
echo "================================="

# Start infrastructure services
echo "📦 Starting infrastructure services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Setup backend
echo "🔧 Setting up backend..."
cd backend
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    cp ../.env.example .env
    echo "📝 Please edit backend/.env with your configuration"
fi

# Run database migrations
echo "🗃️ Running database migrations..."
alembic upgrade head

cd ..

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install

echo "✅ Development setup complete!"
echo ""
echo "🚀 To start development:"
echo "1. Backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Access points:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
EOF

chmod +x scripts/dev-setup.sh

echo -e "${GREEN}✅ Configuration files created${NC}"

# Create initial commit
echo -e "${YELLOW}📝 Creating initial commit...${NC}"
git add .
git commit -m "feat: initial project structure for TenderWise AI v2

- Complete redesign architecture
- Next.js 14 frontend setup
- FastAPI microservices backend
- Docker development environment
- CI/CD pipeline configuration
- Documentation structure

🤖 Generated with Memex"

echo -e "${GREEN}🎉 TenderWise AI v2 project initialized successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Review the project structure in: $NEW_PROJECT_DIR"
echo "2. Read the complete redesign plan: TENDERWISE_AI_COMPLETE_REDESIGN_PLAN.md"
echo "3. Run the development setup: cd $NEW_PROJECT_DIR && ./scripts/dev-setup.sh"
echo "4. Start development according to Phase 1 timeline"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- Configure your .env file with API keys"
echo "- Review and customize the architecture as needed"
echo "- Set up your development team and tools"
echo ""
echo -e "${GREEN}🚀 Ready to build the future of RFP management!${NC}"
EOF