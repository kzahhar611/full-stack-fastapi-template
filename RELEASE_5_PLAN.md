# 🚀 **TenderWise AI - Release 5 Development Plan**

**Release Focus**: Advanced RFP Features & Document Management  
**Duration**: 4-5 hours  
**Status**: 🟡 **IN PROGRESS**  
**Reference Repos**: Langflow (workflow patterns), FastAPI Full-Stack (file handling), Open WebUI (rich editor patterns)

---

## 📋 **Release 5 Objectives**

### **Primary Goals** 🎯
- [ ] **Rich Text Editor**: WYSIWYG editor for RFP descriptions and requirements
- [ ] **Document Management**: Upload, storage, and organization of RFP documents
- [ ] **RFP Creation Form**: Complete multi-step RFP creation wizard
- [ ] **File Upload System**: Backend and frontend file handling
- [ ] **RFP Template System**: Pre-configured RFP templates for different industries

### **Secondary Goals** 🎯
- [ ] **RFP Status Workflow**: Automated status transitions with notifications
- [ ] **Advanced Search**: Full-text search across RFP content and documents
- [ ] **Export Features**: PDF generation for RFP documents
- [ ] **Deadline Management**: Calendar integration and deadline notifications
- [ ] **Collaboration Features**: Comments and internal notes on RFPs

---

## 🏗️ **Technical Architecture Plan**

### **Backend Enhancements**

#### **1. File Storage System**
```python
# New models to add
class RFPDocument(Base):
    __tablename__ = "rfp_documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    rfp_id: Mapped[int] = mapped_column(ForeignKey("rfps.id"))
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int]
    mime_type: Mapped[str] = mapped_column(String(100))
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    upload_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_public: Mapped[bool] = mapped_column(default=False)
    
class RFPTemplate(Base):
    __tablename__ = "rfp_templates"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(default=uuid4, unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100))  # Services, Goods, Construction, etc.
    template_data: Mapped[dict] = mapped_column(JSON)  # Form structure and defaults
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_system_template: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

#### **2. Enhanced RFP Model**
```python
# Extend existing RFP model
class RFP(Base):
    # ... existing fields ...
    
    # Rich content fields
    description_html: Mapped[str] = mapped_column(Text, nullable=True)  # Rich HTML content
    requirements_html: Mapped[str] = mapped_column(Text, nullable=True)  # Structured requirements
    evaluation_criteria: Mapped[dict] = mapped_column(JSON, nullable=True)  # Scoring criteria
    
    # Document relationships
    documents: Mapped[List["RFPDocument"]] = relationship("RFPDocument", back_populates="rfp")
    
    # Workflow fields
    submission_deadline: Mapped[datetime] = mapped_column(nullable=True)
    publication_date: Mapped[datetime] = mapped_column(nullable=True)
    clarification_deadline: Mapped[datetime] = mapped_column(nullable=True)
    
    # Advanced fields
    is_template_based: Mapped[bool] = mapped_column(default=False)
    template_id: Mapped[int] = mapped_column(ForeignKey("rfp_templates.id"), nullable=True)
    internal_notes: Mapped[str] = mapped_column(Text, nullable=True)
```

#### **3. New API Endpoints**
```python
# File management
POST   /api/v1/rfps/{rfp_id}/documents        # Upload document
GET    /api/v1/rfps/{rfp_id}/documents        # List documents
DELETE /api/v1/rfps/{rfp_id}/documents/{doc_id}  # Delete document
GET    /api/v1/documents/{doc_id}/download    # Download document

# Templates
GET    /api/v1/rfp-templates                  # List templates
POST   /api/v1/rfp-templates                  # Create template
PUT    /api/v1/rfp-templates/{template_id}    # Update template
DELETE /api/v1/rfp-templates/{template_id}    # Delete template
POST   /api/v1/rfps/from-template/{template_id}  # Create RFP from template

# Advanced RFP operations
PUT    /api/v1/rfps/{rfp_id}/status           # Update RFP status
POST   /api/v1/rfps/{rfp_id}/publish          # Publish RFP
POST   /api/v1/rfps/{rfp_id}/export           # Export to PDF
GET    /api/v1/rfps/search                    # Full-text search
```

### **Frontend Enhancements**

#### **1. Rich Text Editor Integration**
```typescript
// Using TipTap or similar editor
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Document from '@tiptap/extension-document'
import Paragraph from '@tiptap/extension-paragraph'
import Text from '@tiptap/extension-text'
import Bold from '@tiptap/extension-bold'
import Italic from '@tiptap/extension-italic'
import BulletList from '@tiptap/extension-bullet-list'
import OrderedList from '@tiptap/extension-ordered-list'
import ListItem from '@tiptap/extension-list-item'
```

#### **2. File Upload Component**
```svelte
<!-- FileUpload.svelte -->
<script lang="ts">
  export let rfpId: string;
  export let onUpload: (file: File) => void;
  
  let dragActive = false;
  let uploading = false;
  let uploadProgress = 0;
</script>

<div class="file-upload-zone" 
     class:drag-active={dragActive}
     on:dragover|preventDefault={() => dragActive = true}
     on:dragleave={() => dragActive = false}
     on:drop|preventDefault={handleDrop}>
  
  {#if uploading}
    <div class="upload-progress">
      <div class="progress-bar" style="width: {uploadProgress}%"></div>
    </div>
  {:else}
    <div class="upload-content">
      <svg class="upload-icon"><!-- Upload icon --></svg>
      <p>Drag & drop files here, or click to browse</p>
      <input type="file" multiple accept=".pdf,.doc,.docx,.xls,.xlsx" />
    </div>
  {/if}
</div>
```

#### **3. RFP Creation Wizard**
```svelte
<!-- RFPWizard.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import RichTextEditor from '$lib/components/RichTextEditor.svelte';
  import FileUpload from '$lib/components/FileUpload.svelte';
  import TemplateSelector from '$lib/components/TemplateSelector.svelte';
  
  export let template: RFPTemplate | null = null;
  
  let currentStep = 1;
  const totalSteps = 5;
  
  let rfpData = {
    title: '',
    rfp_number: '',
    type: 'services',
    estimated_budget: 0,
    description_html: '',
    requirements_html: '',
    submission_deadline: '',
    publication_date: '',
    evaluation_criteria: {},
    documents: []
  };
</script>

<div class="wizard-container">
  <!-- Progress indicator -->
  <div class="wizard-progress">
    {#each Array(totalSteps) as _, i}
      <div class="step" class:active={i + 1 === currentStep} class:completed={i + 1 < currentStep}>
        {i + 1}
      </div>
    {/each}
  </div>
  
  <!-- Step content -->
  {#if currentStep === 1}
    <!-- Basic Information -->
  {:else if currentStep === 2}
    <!-- Description & Requirements -->
  {:else if currentStep === 3}
    <!-- Evaluation Criteria -->
  {:else if currentStep === 4}
    <!-- Documents & Attachments -->
  {:else if currentStep === 5}
    <!-- Review & Publish -->
  {/if}
  
  <!-- Navigation -->
  <div class="wizard-navigation">
    <button on:click={previousStep} disabled={currentStep === 1}>Previous</button>
    <button on:click={nextStep} disabled={currentStep === totalSteps}>Next</button>
    {#if currentStep === totalSteps}
      <button on:click={submitRFP} class="btn-primary">Create RFP</button>
    {/if}
  </div>
</div>
```

---

## 📋 **Implementation Timeline**

### **Phase 1: Backend Document System** (1.5 hours)
1. **Database Schema Updates**
   - Add RFPDocument and RFPTemplate models
   - Update RFP model with rich content fields
   - Create migrations and update relationships

2. **File Storage Service**
   - Implement file upload handling
   - Create secure file storage directory structure
   - Add file validation and security checks

3. **API Endpoints**
   - Document upload/download endpoints
   - Template management endpoints
   - Enhanced RFP operations

### **Phase 2: Frontend Rich Editor** (1.5 hours)
1. **Rich Text Editor Component**
   - Install and configure TipTap editor
   - Create reusable editor component
   - Implement toolbar with formatting options

2. **File Upload Interface**
   - Drag & drop file upload component
   - Progress indicators and error handling
   - File preview and management

### **Phase 3: RFP Creation Wizard** (1.5 hours)
1. **Multi-Step Form**
   - Create wizard component with navigation
   - Implement form validation and state management
   - Add template selection functionality

2. **Integration & Testing**
   - Connect wizard to backend APIs
   - Test file upload and rich content
   - End-to-end RFP creation flow

### **Phase 4: Advanced Features** (1 hour)
1. **Template System**
   - Create default RFP templates
   - Template-based RFP creation
   - Custom template management

2. **Search & Export**
   - Enhanced search functionality
   - PDF export capability
   - Status workflow improvements

---

## 🔧 **Dependencies & Tools**

### **Backend Dependencies**
```python
# Add to requirements.txt
python-multipart==0.0.6    # File upload handling
aiofiles==23.2.1           # Async file operations
python-magic==0.4.27       # File type detection
reportlab==4.0.4           # PDF generation
pypdf2==3.0.1             # PDF manipulation
```

### **Frontend Dependencies**
```json
// Add to package.json
{
  "@tiptap/core": "^2.1.0",
  "@tiptap/starter-kit": "^2.1.0",
  "@tiptap/extension-document": "^2.1.0",
  "@tiptap/extension-paragraph": "^2.1.0",
  "@tiptap/extension-text": "^2.1.0",
  "@tiptap/extension-bold": "^2.1.0",
  "@tiptap/extension-italic": "^2.1.0",
  "@tiptap/extension-bullet-list": "^2.1.0",
  "@tiptap/extension-ordered-list": "^2.1.0",
  "@tiptap/extension-list-item": "^2.1.0",
  "file-saver": "^2.0.5",
  "jszip": "^3.10.1"
}
```

---

## 🎯 **Success Criteria**

### **Technical Requirements** ✅
- [ ] Rich text editor with full formatting capabilities
- [ ] File upload system with drag & drop support
- [ ] Multi-step RFP creation wizard
- [ ] Template-based RFP creation
- [ ] Document management and preview
- [ ] Enhanced search across content and files
- [ ] PDF export functionality

### **User Experience** 👤
- [ ] Intuitive RFP creation process
- [ ] Professional rich text editing experience
- [ ] Seamless file upload with progress feedback
- [ ] Template selection and customization
- [ ] Quick access to frequently used features
- [ ] Mobile-responsive design maintained

### **Business Value** 💼
- [ ] Reduced time to create RFPs
- [ ] Standardized RFP templates
- [ ] Better document organization
- [ ] Enhanced RFP content quality
- [ ] Improved collaboration capabilities

---

## 🔄 **Risk Mitigation**

### **Technical Risks**
1. **File Upload Security**: Implement strict file type validation and virus scanning
2. **Storage Scalability**: Design file storage for future cloud migration
3. **Rich Editor Performance**: Optimize for large documents and mobile devices
4. **Browser Compatibility**: Test rich editor across all supported browsers

### **User Experience Risks**
1. **Complexity**: Keep wizard simple with clear progress indicators
2. **Performance**: Implement lazy loading for large files and documents
3. **Mobile Experience**: Ensure rich editor works well on mobile devices
4. **Data Loss**: Implement auto-save functionality

---

## 📊 **Expected Outcomes**

### **Immediate Benefits**
- Professional RFP creation experience
- Standardized RFP templates and formatting
- Centralized document management
- Enhanced search and discovery

### **Long-term Benefits**
- Foundation for AI-powered RFP analysis
- Workflow automation capabilities
- Advanced collaboration features
- Integration with external systems

---

**🎯 Release 5 Goal**: Transform TenderWise from a basic RFP management system into a professional procurement platform with advanced document handling and rich content creation capabilities.

---

**Generated on**: 2025-06-03 17:15 UTC  
**Admin Access**: rfp@kzahhar.com / password123  
**Current Services**: Backend (http://localhost:8000) | Frontend (http://localhost:5173)