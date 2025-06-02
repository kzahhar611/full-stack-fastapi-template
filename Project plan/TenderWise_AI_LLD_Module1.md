# Low-Level Design (LLD): TenderWise AI
## Module 1: RFP Analysis & Strategic Decision Support

**1. Introduction**

*   **1.1 Purpose:** This document details the low-level design for Module 1 (RFP Analysis & Strategic Decision Support) of the TenderWise AI system. It includes class diagrams, sequence diagrams for key operations, API endpoint specifications, and database schema details relevant to this module.
*   **1.2 Scope:** Design of the components and interactions involved in uploading an RFP, AI-driven analysis, risk identification, "Go/No-Go" recommendation, and dashboard display for Module 1.
*   **1.3 Date of Preparation:** 2025-05-31
*   **1.4 References:**
    *   TenderWise AI HLD (High-Level Design)
    *   TenderWise AI SRS (Software Requirements Specification) - particularly sections FR-M1-001 to FR-M1-008.

**2. Component Breakdown (Module 1 Focus)**

*   **Frontend Components (Module 1 UI):**
    *   `RFPFileUploadComponent`: Handles RFP file selection and upload.
    *   `RFPAnalysisRequestComponent`: Allows users to trigger analysis and input optional parameters.
    *   `RFPAnalysisDisplayComponent`: Displays the "Go/No-Go" recommendation, justifications, risks, and key extracted information.
    *   `RFPDashboardComponent`: Visualizes KPIs and factors from the RFP analysis.
*   **Backend Components (Web Application Server - Module 1 Logic):**
    *   `RFPController`: Handles HTTP requests related to RFPs.
    *   `RFPService`: Contains business logic for managing RFPs (upload, metadata storage, initiating analysis).
    *   `RFPAnalysisResultService`: Manages storage and retrieval of analysis results.
    *   `RFPTaskProducer`: Enqueues RFP analysis tasks to the Task Queue.
*   **AI Orchestration Layer Components (Module 1 Focus):**
    *   `RFPAnalysisTaskConsumer`: Worker process that consumes "Analyze RFP" tasks.
    *   `RFPParserService`: Extracts text and basic structure from RFP documents.
    *   `RFPCloudAIIntegrator`: Interacts with specific Cloud AI APIs for detailed analysis (e.g., entity extraction, sentiment analysis, risk identification, summarization).
    *   `RFPRecommendationEngine`: Applies logic (potentially configurable rules or a simple model) to generate the "Go/No-Go" decision based on AI analysis outputs.
*   **Database Schema (Module 1 Tables):** (Detailed in Section 6)

**3. Class Diagrams (Conceptual)**

*   **3.1 Backend - `RFPService` and related entities:**
    ```plantuml
    @startuml
    class User {
      userId: UUID
      username: String
      // ... other user fields
    }

    class RFP {
      rfpId: UUID
      fileName: String
      originalFileSize: Long
      storagePath: String // Path in File Storage
      uploadTimestamp: DateTime
      status: RFPStatus // (e.g., UPLOADED, PENDING_ANALYSIS, ANALYSIS_COMPLETE, ANALYSIS_FAILED)
      uploadedBy: User
      --
      + addRFP(file, user): RFP
      + updateStatus(newStatus: RFPStatus): void
      + getRFPById(rfpId: UUID): RFP
    }

    enum RFPStatus {
      UPLOADED
      PENDING_ANALYSIS
      ANALYSIS_IN_PROGRESS
      ANALYSIS_COMPLETE
      ANALYSIS_FAILED
    }

    class RFPAnalysisResult {
      resultId: UUID
      rfp: RFP
      goNoGoDecision: String // "Go", "No-Go"
      justification: Text
      identifiedRisks: JSON // [{description, category: 'Technical'/'Legal', severity: 'High'/'Medium'/'Low'}, ...]
      keyRequirementsSummary: Text
      extractedEntities: JSON // {budget: [], timeline: [], tech_stack: [], ...}
      kpiDashboardData: JSON // Data for RFPDashboardComponent
      analysisTimestamp: DateTime
      analyzedByAIModel: String // Identifier for AI model/version used
      --
      + saveResult(resultData): RFPAnalysisResult
      + getResultByRFP(rfpId: UUID): RFPAnalysisResult
    }

    RFP "1" -- "1" RFPAnalysisResult : (analyzed into)
    RFP "1" -- "1" User : (uploaded by)

    interface RFPService {
      + uploadRFP(file: File, userId: UUID): RFP
      + initiateAnalysis(rfpId: UUID, userParams: Map): void
      + getRFPDetails(rfpId: UUID): RFP
      + getAnalysisResult(rfpId: UUID): RFPAnalysisResult
    }
    @enduml
    ```
    *(Note: PlantUML source for diagram)*

**4. Sequence Diagrams for Key Operations**

*   **4.1 User Uploads RFP and Initiates Analysis:**
    ```plantuml
    @startuml
    actor User
    participant RFPFileUploadComponent as FE_Upload
    participant WebAppServer_RFPController as BE_Ctrl
    participant WebAppServer_RFPService as BE_Svc
    participant FileStorage as FS
    participant Database as DB
    participant TaskQueueProducer as TQP
    participant TaskQueue as TQ

    User -> FE_Upload: Selects RFP file, clicks Upload
    FE_Upload -> BE_Ctrl: POST /api/v1/rfps (file, userId)
    BE_Ctrl -> BE_Svc: uploadRFP(file, userId)
    BE_Svc -> FS: Store file (e.g., S3.putObject(file))
    FS --> BE_Svc: Returns storagePath
    BE_Svc -> DB: Save RFP metadata (fileName, storagePath, userId, status: UPLOADED)
    DB --> BE_Svc: Confirms save (returns rfpId)
    BE_Svc --> BE_Ctrl: Returns rfpId, status
    BE_Ctrl --> FE_Upload: { rfpId, status: 'UPLOADED', message: 'File uploaded successfully' }
    FE_Upload --> User: Displays success message, enables "Analyze" button

    User -> FE_Upload: Clicks "Analyze RFP" (for rfpId)
    FE_Upload -> BE_Ctrl: POST /api/v1/rfps/{rfpId}/analyze (userParams)
    BE_Ctrl -> BE_Svc: initiateAnalysis(rfpId, userParams)
    BE_Svc -> DB: Update RFP status to PENDING_ANALYSIS
    BE_Svc -> TQP: enqueueRFPAnalysisTask(rfpId, userParams)
    TQP -> TQ: Add task to queue
    TQ --> TQP: Confirms task enqueued
    TQP --> BE_Svc: Confirms
    BE_Svc --> BE_Ctrl: { message: 'Analysis initiated' }
    BE_Ctrl --> FE_Upload: { message: 'Analysis initiated' }
    FE_Upload --> User: Displays "Analysis in progress..."
    @enduml
    ```

*   **4.2 AI Orchestration - RFP Analysis Task Processing:**
    ```plantuml
    @startuml
    participant TaskQueue as TQ
    participant RFPAnalysisTaskConsumer as Worker
    participant AI_RFPParserService as Parser
    participant AI_CloudAIIntegrator as AI_Client
    participant CloudAIService as Ext_AI
    participant AI_RFPRecommendationEngine as Rec_Eng
    participant Database as DB

    TQ -> Worker: Delivers "Analyze RFP" task (rfpId, userParams)
    Worker -> DB: Get RFP metadata (storagePath) for rfpId
    DB --> Worker: Returns RFP metadata
    Worker -> DB: Update RFP status to ANALYSIS_IN_PROGRESS
    Worker -> Parser: parseRFP(storagePath)
    Parser --> Worker: Returns extractedText, basicStructure
    Worker -> AI_Client: analyzeRFPContent(extractedText, userParams)
    AI_Client -> Ext_AI: Call relevant API endpoints (e.g., entity extraction, risk detection)
    Ext_AI --> AI_Client: Returns AI analysis (raw JSON/text)
    AI_Client --> Worker: Returns processedAIAnalysis
    Worker -> Rec_Eng: generateRecommendation(processedAIAnalysis, userParams, companyContext)
    Rec_Eng --> Worker: Returns {goNoGoDecision, justification, kpiData, ...}
    Worker -> DB: Save RFPAnalysisResult (linking to rfpId, decision, risks, summary, etc.)
    Worker -> DB: Update RFP status to ANALYSIS_COMPLETE (or FAILED)
    DB --> Worker: Confirms save
    Worker -> TQ: Acknowledge task completion
    ' (Notification to user happens via a separate mechanism, e.g., WebSockets or polling from frontend, triggered by status change)
    @enduml
    ```

**5. API Endpoint Specifications (Module 1)**

Base URL: `/api/v1/rfps`

*   **`POST /api/v1/rfps`**
    *   **Description:** Uploads a new RFP document.
    *   **Request Body:** `multipart/form-data` containing the RFP file and `userId`.
    *   **Response (Success 201 Created):**
        ```json
        {
          "rfpId": "uuid-string",
          "fileName": "example_rfp.pdf",
          "status": "UPLOADED",
          "uploadTimestamp": "2025-05-31T22:19:18Z",
          "message": "File uploaded successfully. Ready for analysis."
        }
        ```
    *   **Response (Error 4xx/5xx):** Standard error JSON.

*   **`POST /api/v1/rfps/{rfpId}/analyze`**
    *   **Description:** Initiates the AI analysis for a previously uploaded RFP.
    *   **Path Parameter:** `rfpId` (UUID string).
    *   **Request Body (Optional JSON):**
        ```json
        {
          "userParameters": { // Optional user inputs to refine analysis
            "focusAreas": ["risk", "budget"],
            "companyStrength": "innovation"
          }
        }
        ```
    *   **Response (Success 202 Accepted):**
        ```json
        {
          "rfpId": "uuid-string",
          "status": "PENDING_ANALYSIS", // Or ANALYSIS_IN_PROGRESS if quick
          "message": "RFP analysis has been initiated."
        }
        ```

*   **`GET /api/v1/rfps/{rfpId}`**
    *   **Description:** Retrieves details and status of a specific RFP.
    *   **Path Parameter:** `rfpId` (UUID string).
    *   **Response (Success 200 OK):**
        ```json
        {
          "rfpId": "uuid-string",
          "fileName": "example_rfp.pdf",
          "status": "ANALYSIS_COMPLETE", // Current status
          "uploadTimestamp": "2025-05-31T22:19:18Z",
          "uploadedBy": "user_uuid_string"
          // ... other RFP metadata
        }
        ```

*   **`GET /api/v1/rfps/{rfpId}/analysis-result`**
    *   **Description:** Retrieves the analysis result for an RFP. Only available if status is `ANALYSIS_COMPLETE`.
    *   **Path Parameter:** `rfpId` (UUID string).
    *   **Response (Success 200 OK):**
        ```json
        {
          "resultId": "uuid-string",
          "rfpId": "uuid-string",
          "goNoGoDecision": "Go",
          "justification": "The RFP aligns well with company strategy and resource availability. Key risks identified are manageable.",
          "identifiedRisks": [
            {"description": "Short project timeline", "category": "Project Management", "severity": "Medium"},
            {"description": "Dependency on new unproven technology X", "category": "Technical", "severity": "High"}
          ],
          "keyRequirementsSummary": "The system must achieve X, Y, and Z. Integration with A and B is required.",
          "extractedEntities": {
            "budget": ["approx $500k", "not to exceed $1M"],
            "timeline": ["6 months", "Q4 completion"],
            "technologyStack": ["Java", "Kubernetes", "AWS"]
          },
          "kpiDashboardData": {
            "riskScore": 75, // Example KPI
            "alignmentScore": 88,
            "factors": [
                {"name": "Strategic Fit", "value": "High"},
                {"name": "Resource Availability", "value": "Medium"}
            ]
          },
          "analysisTimestamp": "2025-05-31T22:30:00Z",
          "analyzedByAIModel": "gpt-4-turbo-2024-04-09_custom-prompt-v1.2"
        }
        ```
    *   **Response (Error 404 Not Found):** If analysis is not yet complete or RFP doesn't exist.

**6. Database Schema (Module 1 Relevant Tables)**

*   **`Users`** (Covered by system-wide LLD - includes `user_id`, `username`, `password_hash`, `email`, `role`, `created_at`, `updated_at`)

*   **`RFPs`**
    *   `rfp_id` (UUID, Primary Key)
    *   `file_name` (VARCHAR(255), NOT NULL)
    *   `original_file_size_bytes` (BIGINT)
    *   `storage_path` (VARCHAR(1024), NOT NULL)  -- Path/key in object storage
    *   `content_hash_sha256` (VARCHAR(64), NULL) -- To detect duplicate file uploads
    *   `status` (VARCHAR(50), NOT NULL, DEFAULT 'UPLOADED') -- UPLOADED, PENDING_ANALYSIS, ANALYSIS_IN_PROGRESS, ANALYSIS_COMPLETE, ANALYSIS_FAILED
    *   `uploaded_by_user_id` (UUID, Foreign Key to `Users.user_id`)
    *   `upload_timestamp` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   `last_status_update_timestamp` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   `user_parameters_for_analysis` (JSONB, NULL) -- Stores optional user inputs for analysis

*   **`RFPAnalysisResults`**
    *   `result_id` (UUID, Primary Key)
    *   `rfp_id` (UUID, Foreign Key to `RFPs.rfp_id`, UNIQUE) -- One result per RFP
    *   `go_no_go_decision` (VARCHAR(10)) -- 'Go', 'No-Go', 'Undetermined'
    *   `justification_text` (TEXT)
    *   `identified_risks_json` (JSONB) -- Array of risk objects
    *   `key_requirements_summary_text` (TEXT)
    *   `extracted_entities_json` (JSONB) -- Key-value pairs of extracted info
    *   `kpi_dashboard_data_json` (JSONB) -- Data for visualization
    *   `ai_model_identifier` (VARCHAR(255)) -- Which AI model/version/prompt was used
    *   `analysis_duration_ms` (INTEGER) -- How long the AI processing took
    *   `analysis_timestamp` (TIMESTAMP WITH TIME ZONE, DEFAULT CURRENT_TIMESTAMP)
    *   `error_message` (TEXT, NULL) -- If analysis failed

**7. Error Handling (Module 1)**

*   **File Upload Errors:** Invalid file type, file size exceeds limit, network errors. Frontend should validate, backend re-validates and returns appropriate 4xx errors.
*   **AI Service Errors:** API timeouts, rate limits, authentication failures with Cloud AI, unexpected AI output format.
    *   The `AIOrchestrationLayer` will implement retry logic for transient errors.
    *   Persistent errors will mark the RFP status as `ANALYSIS_FAILED` and log the error in `RFPAnalysisResults.error_message`.
    *   Users will be notified of failure.
*   **Database Errors:** Connection issues, constraint violations. Standard transaction management and error logging.

**8. Security Considerations (Module 1)**

*   Uploaded RFPs can contain sensitive business information. Access to RFP data and analysis results must be strictly controlled by user roles and permissions (defined system-wide).
*   File storage (e.g., S3 buckets) must be configured securely (e.g., private by default, access via pre-signed URLs or application-level credentials).
*   API keys for Cloud AI services must be stored securely (e.g., using a secrets manager) and not exposed in client-side code or version control.
*   All data in transit (Frontend <-> Backend, Backend <-> Cloud AI) must use HTTPS.

This LLD for Module 1 should give you a good idea of the depth required. The other modules and system features would have similarly detailed LLDs covering their specific classes, sequences, APIs, and database interactions.

What are your thoughts on this level of detail for an LLD? Shall we consider this the template for how the other LLDs would be structured, or would you like to dive into another module specifically?

Next on your list is the **Project Plan**.