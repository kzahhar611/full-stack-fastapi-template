# 🎨 **TenderWise AI - Release 5 Phase 2 Development Plan**

**Phase Focus**: Frontend Rich Text Editor & Document Upload UI  
**Duration**: 3-4 hours  
**Status**: 🟡 **IN PROGRESS**  
**Reference Repos**: Open WebUI (modern UI patterns), Langflow (workflow interfaces), FastAPI Full-Stack (frontend integration)

---

## 📋 **Phase 2 Objectives**

### **Primary Goals** 🎯
- [ ] **Rich Text Editor Integration**: TipTap editor with toolbar for HTML content
- [ ] **Document Upload Interface**: Drag & drop with progress indicators and preview
- [ ] **Enhanced RFP Creation Wizard**: Multi-step form with template selection
- [ ] **Template Management UI**: Create, edit, and manage RFP templates
- [ ] **Advanced Search Interface**: Enhanced filtering and search with live results

### **Secondary Goals** 🎯
- [ ] **File Management Dashboard**: Document preview, metadata editing, bulk operations
- [ ] **RFP Status Workflow UI**: Visual status progression with action buttons
- [ ] **Template Gallery**: Visual template selection with preview
- [ ] **Enhanced RFP List**: Rich cards with document counts, deadlines, status
- [ ] **Mobile Responsiveness**: Ensure all new components work on mobile

---

## 🏗️ **Technical Implementation Plan**

### **Phase 2A: Rich Text Editor (1.5 hours)**

#### **1. TipTap Editor Integration**
Following **Open WebUI** patterns for rich content editing:

```bash
# Install TipTap dependencies
npm install @tiptap/core @tiptap/starter-kit @tiptap/extension-placeholder
npm install @tiptap/extension-link @tiptap/extension-image @tiptap/extension-table
npm install @tiptap/extension-bullet-list @tiptap/extension-ordered-list
npm install @tiptap/extension-text-style @tiptap/extension-color
```

#### **2. Rich Text Editor Component**
```svelte
<!-- RichTextEditor.svelte -->
<script lang="ts">
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { Editor } from '@tiptap/core';
  import StarterKit from '@tiptap/starter-kit';
  import Placeholder from '@tiptap/extension-placeholder';
  import Link from '@tiptap/extension-link';
  import Table from '@tiptap/extension-table';
  
  export let content: string = '';
  export let placeholder: string = 'Start writing...';
  export let editable: boolean = true;
  export let minHeight: string = '200px';
  
  const dispatch = createEventDispatcher();
  
  let element: HTMLElement;
  let editor: Editor;
  
  const editorConfig = {
    element,
    content,
    editable,
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder }),
      Link.configure({ openOnClick: false }),
      Table.configure({ resizable: true })
    ],
    onUpdate: ({ editor }) => {
      content = editor.getHTML();
      dispatch('update', { content });
    }
  };
</script>

<div class="rich-text-editor" style="min-height: {minHeight}">
  <!-- Toolbar -->
  <div class="editor-toolbar">
    <!-- Format buttons following Open WebUI style -->
    <div class="toolbar-group">
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().toggleBold().run()}>
        <i class="lucide-bold"></i>
      </button>
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().toggleItalic().run()}>
        <i class="lucide-italic"></i>
      </button>
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().toggleUnderline().run()}>
        <i class="lucide-underline"></i>
      </button>
    </div>
    
    <div class="toolbar-group">
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().toggleBulletList().run()}>
        <i class="lucide-list"></i>
      </button>
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().toggleOrderedList().run()}>
        <i class="lucide-list-ordered"></i>
      </button>
    </div>
    
    <div class="toolbar-group">
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().setHorizontalRule().run()}>
        <i class="lucide-minus"></i>
      </button>
      <button class="toolbar-btn" on:click={() => editor?.chain().focus().insertTable().run()}>
        <i class="lucide-table"></i>
      </button>
    </div>
  </div>
  
  <!-- Editor Content -->
  <div class="editor-content" bind:this={element}></div>
</div>
```

#### **3. Editor Styling (Open WebUI inspired)**
```css
.rich-text-editor {
  @apply border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden bg-white dark:bg-gray-800;
}

.editor-toolbar {
  @apply flex items-center gap-1 p-2 border-b border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700;
}

.toolbar-group {
  @apply flex items-center gap-1 px-2 border-r border-gray-200 dark:border-gray-600 last:border-r-0;
}

.toolbar-btn {
  @apply p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 transition-colors;
}

.editor-content {
  @apply p-4 min-h-[200px] prose prose-sm dark:prose-invert max-w-none;
}
```

### **Phase 2B: Document Upload Interface (1.5 hours)**

#### **1. File Upload Component**
Inspired by **Langflow's** node-based file handling and **Open WebUI's** drag & drop patterns:

```svelte
<!-- FileUploadZone.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api/client';
  
  export let rfpId: number;
  export let multiple: boolean = true;
  export let acceptedTypes: string[] = ['.pdf', '.doc', '.docx', '.xls', '.xlsx'];
  export let maxFileSize: number = 100 * 1024 * 1024; // 100MB
  
  const dispatch = createEventDispatcher();
  
  let dragActive = false;
  let uploading = false;
  let uploadProgress: { [key: string]: number } = {};
  let uploadedFiles: any[] = [];
  
  async function handleFileUpload(files: FileList) {
    uploading = true;
    const uploadPromises = Array.from(files).map(uploadSingleFile);
    
    try {
      const results = await Promise.allSettled(uploadPromises);
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;
      
      dispatch('upload-complete', { successful, failed, files: uploadedFiles });
    } finally {
      uploading = false;
      uploadProgress = {};
    }
  }
  
  async function uploadSingleFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', 'ATTACHMENT');
    formData.append('is_public', 'true');
    
    try {
      const response = await apiClient.post(
        `/rfps-enhanced/${rfpId}/documents`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            uploadProgress[file.name] = progress;
            uploadProgress = { ...uploadProgress };
          }
        }
      );
      
      uploadedFiles.push(response.data);
      return response.data;
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  }
</script>

<div class="file-upload-zone" 
     class:drag-active={dragActive}
     class:uploading={uploading}
     on:dragover|preventDefault={() => dragActive = true}
     on:dragleave={() => dragActive = false}
     on:drop|preventDefault={(e) => {
       dragActive = false;
       handleFileUpload(e.dataTransfer.files);
     }}>
  
  {#if uploading}
    <div class="upload-progress">
      <div class="upload-icon">
        <i class="lucide-upload animate-pulse"></i>
      </div>
      <h3>Uploading Files...</h3>
      
      {#each Object.entries(uploadProgress) as [filename, progress]}
        <div class="progress-item">
          <div class="progress-info">
            <span class="filename">{filename}</span>
            <span class="percentage">{progress}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="upload-content">
      <div class="upload-icon">
        <i class="lucide-cloud-upload"></i>
      </div>
      <h3>Drop files here or click to browse</h3>
      <p>Supports: {acceptedTypes.join(', ')}</p>
      <p class="text-sm text-gray-500">Max file size: {Math.round(maxFileSize / 1024 / 1024)}MB</p>
      
      <input type="file" 
             {multiple} 
             accept={acceptedTypes.join(',')}
             on:change={(e) => handleFileUpload(e.target.files)}
             class="hidden-input" />
    </div>
  {/if}
</div>

<style>
  .file-upload-zone {
    @apply border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer transition-all duration-200 hover:border-blue-500 dark:hover:border-blue-400;
  }
  
  .drag-active {
    @apply border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20;
  }
  
  .uploading {
    @apply cursor-not-allowed border-gray-400;
  }
  
  .upload-icon {
    @apply text-4xl text-gray-400 dark:text-gray-500 mb-4;
  }
  
  .progress-item {
    @apply mt-4 text-left;
  }
  
  .progress-info {
    @apply flex justify-between items-center mb-2;
  }
  
  .progress-bar {
    @apply w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2;
  }
  
  .progress-fill {
    @apply bg-blue-500 h-2 rounded-full transition-all duration-300;
  }
  
  .hidden-input {
    @apply absolute inset-0 w-full h-full opacity-0 cursor-pointer;
  }
</style>
```

### **Phase 2C: RFP Creation Wizard (1 hour)**

#### **1. Multi-Step Wizard Component**
Following **Langflow's** workflow step patterns:

```svelte
<!-- RFPCreationWizard.svelte -->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import RichTextEditor from '$lib/components/RichTextEditor.svelte';
  import FileUploadZone from '$lib/components/FileUploadZone.svelte';
  import TemplateSelector from '$lib/components/TemplateSelector.svelte';
  
  export let templates: any[] = [];
  
  const dispatch = createEventDispatcher();
  
  let currentStep = 1;
  const totalSteps = 5;
  
  let rfpData = {
    title: '',
    rfp_number: '',
    rfp_type: 'services',
    category: '',
    estimated_budget: null,
    budget_range_min: null,
    budget_range_max: null,
    currency: 'USD',
    submission_deadline: '',
    description_html: '',
    requirements_html: '',
    evaluation_criteria: {},
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    is_public: false,
    template_id: null
  };
  
  let selectedTemplate = null;
  let documents = [];
  
  const steps = [
    { id: 1, title: 'Template & Basic Info', icon: 'file-text' },
    { id: 2, title: 'Description & Requirements', icon: 'edit-3' },
    { id: 3, title: 'Budget & Timeline', icon: 'calendar' },
    { id: 4, title: 'Evaluation Criteria', icon: 'star' },
    { id: 5, title: 'Documents & Review', icon: 'check-circle' }
  ];
  
  function applyTemplate(template) {
    selectedTemplate = template;
    rfpData.template_id = template.id;
    rfpData.rfp_type = template.rfp_type;
    rfpData.category = template.category;
    
    if (template.description_template) {
      rfpData.description_html = template.description_template;
    }
    
    if (template.requirements_template) {
      rfpData.requirements_html = template.requirements_template;
    }
    
    if (template.evaluation_criteria_template) {
      rfpData.evaluation_criteria = template.evaluation_criteria_template;
    }
  }
  
  function nextStep() {
    if (currentStep < totalSteps) {
      currentStep++;
    }
  }
  
  function previousStep() {
    if (currentStep > 1) {
      currentStep--;
    }
  }
  
  async function submitRFP() {
    try {
      dispatch('submit', { rfpData, documents });
    } catch (error) {
      console.error('Failed to create RFP:', error);
    }
  }
</script>

<div class="rfp-wizard">
  <!-- Progress Indicator -->
  <div class="wizard-progress">
    <div class="progress-bar">
      <div class="progress-fill" style="width: {(currentStep / totalSteps) * 100}%"></div>
    </div>
    
    <div class="steps">
      {#each steps as step}
        <div class="step" 
             class:active={step.id === currentStep} 
             class:completed={step.id < currentStep}>
          <div class="step-icon">
            <i class="lucide-{step.icon}"></i>
          </div>
          <span class="step-title">{step.title}</span>
        </div>
      {/each}
    </div>
  </div>
  
  <!-- Step Content -->
  <div class="wizard-content">
    {#if currentStep === 1}
      <!-- Template Selection & Basic Info -->
      <div class="step-content">
        <h2>Choose Template & Basic Information</h2>
        
        <TemplateSelector {templates} on:select={(e) => applyTemplate(e.detail)} />
        
        <div class="form-grid">
          <div class="form-group">
            <label for="title">RFP Title *</label>
            <input type="text" id="title" bind:value={rfpData.title} 
                   placeholder="Enter RFP title" required />
          </div>
          
          <div class="form-group">
            <label for="rfp_number">RFP Number</label>
            <input type="text" id="rfp_number" bind:value={rfpData.rfp_number} 
                   placeholder="Auto-generated if empty" />
          </div>
          
          <div class="form-group">
            <label for="rfp_type">RFP Type *</label>
            <select id="rfp_type" bind:value={rfpData.rfp_type} required>
              <option value="services">Services</option>
              <option value="goods">Goods</option>
              <option value="construction">Construction</option>
              <option value="consulting">Consulting</option>
              <option value="technology">Technology</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="category">Category</label>
            <input type="text" id="category" bind:value={rfpData.category} 
                   placeholder="e.g., Professional Services" />
          </div>
        </div>
      </div>
      
    {:else if currentStep === 2}
      <!-- Description & Requirements -->
      <div class="step-content">
        <h2>Description & Requirements</h2>
        
        <div class="form-group">
          <label>RFP Description</label>
          <RichTextEditor 
            bind:content={rfpData.description_html}
            placeholder="Describe the project background, objectives, and scope..."
            minHeight="300px" />
        </div>
        
        <div class="form-group">
          <label>Requirements & Specifications</label>
          <RichTextEditor 
            bind:content={rfpData.requirements_html}
            placeholder="Detail the specific requirements, deliverables, and specifications..."
            minHeight="300px" />
        </div>
      </div>
      
    {:else if currentStep === 3}
      <!-- Budget & Timeline -->
      <div class="step-content">
        <h2>Budget & Timeline</h2>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="estimated_budget">Estimated Budget</label>
            <input type="number" id="estimated_budget" bind:value={rfpData.estimated_budget} 
                   placeholder="0.00" step="0.01" />
          </div>
          
          <div class="form-group">
            <label for="budget_min">Budget Range Min</label>
            <input type="number" id="budget_min" bind:value={rfpData.budget_range_min} 
                   placeholder="0.00" step="0.01" />
          </div>
          
          <div class="form-group">
            <label for="budget_max">Budget Range Max</label>
            <input type="number" id="budget_max" bind:value={rfpData.budget_range_max} 
                   placeholder="0.00" step="0.01" />
          </div>
          
          <div class="form-group">
            <label for="currency">Currency</label>
            <select id="currency" bind:value={rfpData.currency}>
              <option value="USD">USD ($)</option>
              <option value="SAR">SAR (ر.س)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="submission_deadline">Submission Deadline *</label>
            <input type="datetime-local" id="submission_deadline" 
                   bind:value={rfpData.submission_deadline} required />
          </div>
        </div>
      </div>
      
    {:else if currentStep === 4}
      <!-- Evaluation Criteria -->
      <div class="step-content">
        <h2>Evaluation Criteria</h2>
        
        {#if selectedTemplate?.evaluation_criteria_template}
          <div class="template-criteria">
            <h3>Template Criteria (you can modify):</h3>
            <!-- Dynamic criteria editor based on template -->
          </div>
        {:else}
          <div class="custom-criteria">
            <p>Define how proposals will be evaluated...</p>
            <!-- Custom criteria builder -->
          </div>
        {/if}
      </div>
      
    {:else if currentStep === 5}
      <!-- Documents & Review -->
      <div class="step-content">
        <h2>Documents & Final Review</h2>
        
        <div class="form-group">
          <label>Upload Supporting Documents</label>
          <FileUploadZone rfpId={0} on:upload-complete={(e) => documents = e.detail.files} />
        </div>
        
        <div class="rfp-preview">
          <h3>RFP Preview</h3>
          <div class="preview-content">
            <h4>{rfpData.title}</h4>
            <div class="preview-html">{@html rfpData.description_html}</div>
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Navigation -->
  <div class="wizard-navigation">
    <button class="btn-secondary" on:click={previousStep} disabled={currentStep === 1}>
      <i class="lucide-chevron-left"></i>
      Previous
    </button>
    
    <div class="step-indicator">
      Step {currentStep} of {totalSteps}
    </div>
    
    {#if currentStep === totalSteps}
      <button class="btn-primary" on:click={submitRFP}>
        <i class="lucide-check"></i>
        Create RFP
      </button>
    {:else}
      <button class="btn-primary" on:click={nextStep}>
        Next
        <i class="lucide-chevron-right"></i>
      </button>
    {/if}
  </div>
</div>
```

---

## 📋 **Implementation Timeline**

### **Phase 2A: Rich Text Editor** (1.5 hours)
1. **TipTap Installation & Setup** (30 min)
   - Install TipTap dependencies
   - Create base RichTextEditor component
   - Implement toolbar with basic formatting

2. **Editor Styling & Features** (45 min)
   - Apply Open WebUI-inspired dark theme styling
   - Add advanced formatting options (tables, links, lists)
   - Implement placeholder and validation

3. **Integration & Testing** (15 min)
   - Test HTML content generation
   - Validate content persistence
   - Ensure mobile responsiveness

### **Phase 2B: File Upload Interface** (1.5 hours)
1. **Drag & Drop Component** (45 min)
   - Create FileUploadZone component
   - Implement drag & drop functionality
   - Add file validation and progress tracking

2. **Upload Integration** (30 min)
   - Connect to backend document API
   - Handle upload progress and errors
   - Implement bulk upload operations

3. **File Management UI** (15 min)
   - Create file list with metadata
   - Add delete and preview options
   - Style according to Open WebUI patterns

### **Phase 2C: RFP Creation Wizard** (1 hour)
1. **Wizard Structure** (30 min)
   - Create multi-step wizard component
   - Implement step navigation and validation
   - Add progress indicator (Langflow-inspired)

2. **Template Integration** (20 min)
   - Create template selector component
   - Implement template application logic
   - Add template preview functionality

3. **Final Integration** (10 min)
   - Connect all components together
   - Add form validation and submission
   - Test complete RFP creation flow

---

## 🎯 **Success Criteria**

### **Technical Requirements** ✅
- [ ] Rich text editor with full HTML output
- [ ] Drag & drop file upload with progress indicators
- [ ] Multi-step RFP creation with template support
- [ ] Template management interface
- [ ] Mobile-responsive design throughout

### **User Experience** 👤
- [ ] Intuitive RFP creation process
- [ ] Professional rich text editing experience
- [ ] Seamless file upload with visual feedback
- [ ] Quick template selection and application
- [ ] Consistent dark theme styling

### **Integration** 🔌
- [ ] Full backend API integration
- [ ] Real-time file upload progress
- [ ] Template data pre-population
- [ ] Form validation and error handling
- [ ] Responsive design on all devices

---

**🎯 Phase 2 Goal**: Transform TenderWise into a professional RFP creation platform with modern UI patterns inspired by Open WebUI and Langflow workflow interfaces.

---

**Generated on**: 2025-06-03 18:10 UTC  
**Reference Patterns**: Open WebUI (dark theme, rich editing), Langflow (workflow steps), FastAPI Full-Stack (integration patterns)  
**Current Services**: Backend (http://localhost:8000) | Frontend (http://localhost:5173)