# 🚀 RFPWizard Quick Start Guide

**Updated Architecture:** Langflow + FastAPI Full Stack Template  
**Setup Time:** ~2-3 hours for complete development environment

## 📋 Prerequisites

- Python 3.10+ 
- Node.js 18+
- Docker & Docker Compose
- Git

## ⚡ Rapid Setup (Step-by-Step)

### **Step 1: Clone FastAPI Template (5 minutes)**
```bash
# Navigate to your project directory
cd /Users/khaledalzahhar/Memex/RFP.Wizard

# Clone the FastAPI Full Stack Template
git clone https://github.com/fastapi/full-stack-fastapi-template.git .

# Or use copier for customization
pipx install copier
copier copy https://github.com/fastapi/full-stack-fastapi-template . --trust
```

### **Step 2: Install Langflow (2 minutes)**
```bash
# Install Langflow
pip install langflow

# Or with uv (recommended)
uv pip install langflow

# Test installation
langflow --help
```

### **Step 3: Setup Development Environment (10 minutes)**
```bash
# Setup the FastAPI template
cd /Users/khaledalzahhar/Memex/RFP.Wizard

# Configure environment variables
cp .env.example .env

# Edit .env file with your settings:
# - SECRET_KEY=your_secret_key_here
# - FIRST_SUPERUSER_EMAIL=rfp@kzahhar.com  
# - FIRST_SUPERUSER_PASSWORD=password123
# - POSTGRES_PASSWORD=your_postgres_password

# Start with Docker Compose
docker-compose up -d
```

### **Step 4: Start Langflow (2 minutes)**
```bash
# In a new terminal, start Langflow
langflow run --host 0.0.0.0 --port 7860

# Access Langflow UI at: http://localhost:7860
```

### **Step 5: Verify Setup (5 minutes)**
```bash
# Check FastAPI backend: http://localhost:8000/docs
# Check React frontend: http://localhost:3000  
# Check Langflow: http://localhost:7860
# Check PostgreSQL: localhost:5432
```

## 🎨 Create Your First RFP Workflow

### **In Langflow UI (http://localhost:7860):**

1. **Create New Flow**
   - Click "New Flow"
   - Name: "RFP Analysis Workflow"

2. **Add Components** (Drag & Drop):
   - **File Input** → for RFP document upload
   - **PDF Parser** → extract text from PDF
   - **OpenAI** → for AI analysis  
   - **Text Output** → display results

3. **Connect Components:**
   ```
   File Input → PDF Parser → OpenAI → Text Output
   ```

4. **Configure OpenAI Component:**
   - Model: gpt-4
   - Prompt: "Analyze this RFP document and provide a Go/No-Go recommendation with risk assessment"
   - Add your OpenAI API key

5. **Test Workflow:**
   - Upload a sample RFP PDF
   - Run the workflow
   - View AI analysis results

6. **Export as API:**
   - Click "Export" → "API"
   - Copy the generated API endpoint
   - Note: This creates an API you can call from your FastAPI backend

## 🔗 Integration Setup

### **Connect Langflow to FastAPI (30 minutes):**

1. **Add Langflow Client to FastAPI:**
```python
# In your FastAPI backend, install langflow client
pip install langflow-client

# Create integration service
# backend/app/services/langflow_service.py
```

2. **Create API Endpoints:**
```python
# backend/app/api/routes/rfp.py
@router.post("/analyze-rfp")
async def analyze_rfp(file: UploadFile):
    # Call Langflow workflow
    # Store results in PostgreSQL
    # Return analysis to frontend
```

3. **Update React Frontend:**
```typescript
// frontend/src/components/RFPUpload.tsx
// Add RFP upload component
// Display analysis results
// Show workflow status
```

## 🎯 Quick Test Scenario

### **Test the Complete Flow:**

1. **Upload RFP Document** → React frontend
2. **Trigger Analysis** → FastAPI calls Langflow workflow  
3. **AI Processing** → Langflow executes workflow with OpenAI
4. **Store Results** → FastAPI saves to PostgreSQL
5. **Display Results** → React shows analysis + recommendation

## 📁 Project Structure

```
RFP.Wizard/
├── backend/          # FastAPI application
├── frontend/         # React application  
├── langflow_flows/   # Exported Langflow workflows
├── docker-compose.yml # Development environment
├── .env             # Environment variables
└── docs/            # Documentation
```

## 🔧 Development Workflow

### **Daily Development:**
1. **Design/Modify Workflows** → Langflow UI (visual)
2. **Test Workflows** → Langflow playground
3. **Export APIs** → From Langflow to FastAPI
4. **Build UI** → React components for interaction
5. **Test Integration** → End-to-end testing

## 🚨 Common Issues & Solutions

### **Port Conflicts:**
- FastAPI: 8000
- React: 3000  
- Langflow: 7860
- PostgreSQL: 5432

### **API Key Setup:**
- OpenAI API key in Langflow components
- Store sensitive keys in environment variables
- Use secrets management for production

### **Docker Issues:**
```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d --build
```

## 🎉 Next Steps After Setup

1. **Create Multi-Agent Workflows** → Different agents for different tasks
2. **Add Role-Based Access** → Admin/Manager/User workflows
3. **Implement Document Processing** → PDF, DOCX, Excel parsing
4. **Build Analytics Dashboard** → Track RFP processing metrics
5. **Add Notification System** → Workflow completion alerts

## 🆘 Need Help?

- **Langflow Documentation:** https://docs.langflow.org
- **FastAPI Template Docs:** https://github.com/fastapi/full-stack-fastapi-template
- **Issues & Solutions:** Check TASK_LOG.md for troubleshooting

## ✅ Success Criteria

After setup, you should have:
- ✅ FastAPI backend running with authentication
- ✅ React frontend with user management
- ✅ Langflow running with visual workflow builder
- ✅ PostgreSQL database connected
- ✅ First RFP analysis workflow created and tested
- ✅ Basic integration between all systems working

**Estimated Total Setup Time:** 2-3 hours  
**Ready to Build:** Advanced AI workflows with visual design!