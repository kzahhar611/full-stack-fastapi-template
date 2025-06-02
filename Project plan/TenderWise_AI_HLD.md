# High-Level Design (HLD): TenderWise AI

**1. Introduction**

*   **1.1 Purpose:** This document provides a high-level overview of the TenderWise AI system architecture, its major components, their interactions, and the technologies involved. It serves as a blueprint for the detailed design and development phases.
*   **1.2 Scope:** This HLD covers the architectural design for all modules and system features defined in the SRS (Software Requirements Specification) for TenderWise AI.
*   **1.3 Date of Preparation:** 2025-05-31
*   **1.4 References:**
    *   TenderWise AI Project Summary
    *   TenderWise AI Project Charter
    *   TenderWise AI Business Requirements Document (BRD)
    *   TenderWise AI Software Requirements Specification (SRS)

**2. System Architecture**

*   **2.1 Architectural Style:** A **Modular Monolith** with a **Service-Oriented approach for AI functionalities** is proposed for the initial version. This provides a good balance between development simplicity and future scalability. Core business logic and system features will reside within a central application, while AI processing tasks will be handled by dedicated services or an orchestration layer that interacts with external Cloud AI APIs. A **job queue system** will be used for handling long-running AI tasks asynchronously.

*   **2.2 Architectural Diagram:**

    ```
    +---------------------------------------------------------------------------------+
    |                                  End Users                                      |
    | (Admins, Managers, Standard Users via Web Browser)                              |
    +---------------------------------------------------------------------------------+
                       ^                                       | HTTPS
                       |                                       v
    +--------------------------------------+    +-------------------------------------+
    |      Web Application Server (API)    |    |        Frontend (Web UI)            |
    | (e.g., Python/Django, Node.js/Express)|    | (e.g., React, Angular, Vue.js)      |
    | - Authentication & Authorization     |<--->| - User Interface & Interaction      |
    | - Business Logic (Non-AI)            |    | - API Client Logic                  |
    | - Request Handling & Routing         |    +-------------------------------------+
    | - Serves Frontend Assets             |
    +--------------------------------------+
          ^   |                 |   ^
          |   |                 |   |
          |   v                 v   |
    +-------------------+  +--------------------------+  +-----------------------------+
    |   AI Orchestration|  |    Task Queue System     |  |     Relational Database     |
    |      Layer        |  | (e.g., Celery, RabbitMQ) |  | (e.g., PostgreSQL, MySQL)   |
    | - Manages AI tasks|<-| - Asynchronous Task Proc.|->| - User Data                 |
    | - Interfaces with |  +--------------------------+  | - Tender/Project Data       |
    |   Cloud AI APIs   |                                | - Analysis Results          |
    | - Prompt Mgmt     |                                | - Task Data, Notifications  |
    +-------------------+                                | - File Metadata             |
          ^   |                                          +-----------------------------+
          |   | (Secure API Calls)                                     ^
          |   v                                                        |
    +-------------------+  +-------------------+  +-------------------------------------+
    | Cloud AI Service 1|  | Cloud AI Service 2|  |      File Storage (Cloud/Local)     |
    | (e.g., OpenAI,    |  | (e.g., Google AI, |  | (e.g., AWS S3, Google Cloud Storage)|
    |  Vertex AI, Azure |  |  AWS Bedrock)     |  | - Stores large documents (RFPs, etc.)|
    |  OpenAI Service)  |  |                   |  +-------------------------------------+
    +-------------------+  +-------------------+                     ^
                                                                     |
                                                                     v
                                                          +---------------------+
                                                          | SMTP Service (Email)|
                                                          +---------------------+
    ```

*   **2.3 Rationale for Architectural Choices:**
    *   **Modular Monolith:** Easier to develop, deploy, and test for a system of this complexity initially, compared to a full microservices architecture. Modularity within the monolith will allow for clearer separation of concerns (e.g., user management, RFP module, proposal module).
    *   **Service-Oriented AI Layer:** Decouples AI processing from the main application, allowing for independent scaling or swapping of AI models/providers.
    *   **Task Queue:** Essential for handling potentially long-running AI analysis and generation tasks without blocking the main application threads, improving user experience.
    *   **Relational Database:** Suitable for structured data like user information, project details, and relationships between entities.
    *   **Separate File Storage:** Efficient for storing large binary files (documents) rather than bloating the database.

**3. Component Design**

*   **3.1 Frontend (Web UI):**
    *   **Description:** Single Page Application (SPA) providing the user interface.
    *   **Responsibilities:** Rendering UI components, handling user interactions, client-side validation, making API calls to the Web Application Server, displaying data and notifications.
    *   **Technologies:** React, Angular, or Vue.js (To be decided based on team expertise). HTML, CSS, JavaScript.

*   **3.2 Web Application Server (API Backend):**
    *   **Description:** The core backend application serving API requests from the frontend.
    *   **Responsibilities:**
        *   User authentication and authorization.
        *   Handling HTTP requests and routing them to appropriate controllers/services.
        *   Implementing business logic for non-AI system features (user management, task management, file metadata management, notifications, calendar).
        *   Interacting with the database for CRUD operations.
        *   Enqueuing AI-related tasks to the Task Queue System.
        *   Serving frontend static assets.
    *   **Technologies:** Python (Django/Flask) or Node.js (Express.js) (To be decided). RESTful APIs or GraphQL.

*   **3.3 AI Orchestration Layer:**
    *   **Description:** A dedicated module or service responsible for managing all interactions with external Cloud AI APIs. This could be part of the Web Application Server or a separate microservice if complexity grows.
    *   **Responsibilities:**
        *   Receiving AI processing requests (e.g., analyze RFP, generate proposal) from the Web Application Server (often via the Task Queue).
        *   Formatting data and constructing appropriate prompts for specific Cloud AI APIs.
        *   Making secure API calls to external AI services.
        *   Handling responses, errors, and retries from AI services.
        *   Parsing AI service outputs and transforming them into a structured format for storage and display.
        *   Managing API keys and configurations for different AI providers.
    *   **Technologies:** Python (due to its strong AI/ML library ecosystem).

*   **3.4 Task Queue System:**
    *   **Description:** Manages background jobs, particularly for AI processing.
    *   **Responsibilities:**
        *   Accepting tasks from the Web Application Server.
        *   Distributing tasks to worker processes that execute them (e.g., calling the AI Orchestration Layer).
        *   Managing task state (pending, in-progress, completed, failed).
        *   Handling retries for failed tasks.
    *   **Technologies:** Celery with RabbitMQ or Redis as a message broker.

*   **3.5 Relational Database:**
    *   **Description:** Primary data store for structured application data.
    *   **Responsibilities:** Storing and managing data for users, roles, permissions, tender projects, RFP details, analysis results, proposal details, compliance matrices, tasks, notifications, file metadata, system configurations.
    *   **Technologies:** PostgreSQL (preferred for its robustness and feature set) or MySQL.

*   **3.6 File Storage:**
    *   **Description:** Storage for large binary files.
    *   **Responsibilities:** Storing uploaded RFP documents, vendor proposals, AI-generated proposals (PDFs, HTMLs), and any other large attachments.
    *   **Technologies:** Cloud-based object storage (e.g., AWS S3, Google Cloud Storage, Azure Blob Storage) is recommended for scalability, durability, and manageability. Local file system storage for development/smaller deployments.

*   **3.7 SMTP Service Integration:**
    *   **Description:** Handles outgoing email notifications.
    *   **Responsibilities:** The Web Application Server will connect to a configured SMTP service to send emails for user registration, password resets, task alerts, and other notifications.
    *   **Technologies:** Standard SMTP protocol. Integration with services like SendGrid, Amazon SES, or a corporate SMTP server.

**4. Data Flow Diagrams (Conceptual)**

*   **4.1 RFP Analysis (Module 1):**
    1.  User uploads RFP via Frontend.
    2.  Frontend sends RFP file and metadata to Web App Server (API).
    3.  Web App Server saves file to File Storage, stores metadata in Database, and enqueues an "Analyze RFP" task in Task Queue.
    4.  A worker picks up the task and passes RFP data (or reference) to AI Orchestration Layer.
    5.  AI Orchestration Layer retrieves the file, calls relevant Cloud AI API(s) for parsing, analysis, risk assessment.
    6.  Cloud AI API responds to AI Orchestration Layer.
    7.  AI Orchestration Layer processes results and updates Database via Web App Server (or directly if a separate service).
    8.  Web App Server sends notification (UI and/or email via SMTP) to user.
    9.  User views analysis results and dashboard on Frontend, which fetches data from Web App Server.

*   **4.2 Proposal Generation (Module 3):**
    1.  User uploads RFP and inputs instructions/template choice via Frontend.
    2.  Frontend sends data to Web App Server.
    3.  Web App Server saves RFP, stores inputs in Database, and enqueues "Generate Proposal" task.
    4.  Worker passes task data to AI Orchestration Layer.
    5.  AI Orchestration Layer calls generative Cloud AI API with RFP content, user instructions, and template structure.
    6.  Cloud AI API returns draft proposal content.
    7.  AI Orchestration Layer formats the draft (HTML) and stores it (via Web App Server) in File Storage/Database.
    8.  Notification sent to user.
    9.  User views/edits HTML proposal on Frontend. Final PDF export is handled by Web App Server converting HTML to PDF.

**5. Technology Stack Summary (Proposed)**

*   **Frontend:** React, Angular, or Vue.js
*   **Backend (Web Application Server):** Python (Django or Flask) or Node.js (Express.js)
*   **AI Orchestration Layer:** Python
*   **Database:** PostgreSQL
*   **Task Queue:** Celery with RabbitMQ or Redis
*   **File Storage:** AWS S3, Google Cloud Storage, or Azure Blob Storage
*   **Cloud AI APIs:** To be selected from major providers (OpenAI, Google Vertex AI, AWS Bedrock, Azure OpenAI Service) based on capabilities and cost.
*   **Deployment:** Docker containers, managed by Kubernetes or a PaaS (e.g., AWS Elastic Beanstalk, Google App Engine, Azure App Service).
*   **CI/CD:** GitHub Actions, Jenkins, GitLab CI.

**6. Deployment Diagram (Conceptual)**

A cloud-based deployment is recommended:

```
+-------------------------------------------------------------------------------------+
|                                    Internet                                         |
+-------------------------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------------+
|                             Cloud Provider (e.g., AWS, GCP, Azure)                  |
| +---------------------------------------------------------------------------------+ |
| | Load Balancer                                                                   | |
| +---------------------------------------------------------------------------------+ |
|     |                      |                        |                             |
|     v                      v                        v                             |
| +-----------------+  +-----------------+  +---------------------------------------+ |
| | Web Server      |  | Web Server      |  | Task Queue Workers (Scalable Group)     | |
| | (Container 1)   |  | (Container N)   |  | +-----------------------------------+ | |
| | - Frontend      |  | - Frontend      |  | | AI Orchestration (in Worker)      | | |
| | - API Backend   |  | - API Backend   |  | +-----------------------------------+ | |
| +-----------------+  +-----------------+  +---------------------------------------+ |
|     |       |            |        |               |               |                 |
|     +-------+------------+--------+---------------+---------------+-----------------+
|             |            |                        |
|             v            v                        v
| +-----------------+  +-----------------+  +-----------------+  +-----------------+ |
| | Database        |  | Message Broker  |  | File Storage    |  | External AI/SMTP| |
| | (Managed Service)|  | (Managed Service)|  | (Object Storage)|  | Services (APIs) | |
| +-----------------+  +-----------------+  +-----------------+  +-----------------+ |
+-------------------------------------------------------------------------------------+
```
*   User traffic hits a Load Balancer.
*   Load Balancer distributes requests to multiple instances of the Web Application Server (running in containers).
*   Web Application Servers interact with a managed Database service and a managed Message Broker for the Task Queue.
*   Task Queue Workers (also in containers, potentially auto-scaling) consume tasks and interact with the AI Orchestration logic.
*   AI Orchestration logic calls external Cloud AI APIs.
*   File Storage is a managed object storage service.
*   SMTP service is external.

**7. Integration Points**

*   **Cloud AI APIs:** Secure (HTTPS, API Keys) connections for NLP, document understanding, and text generation.
*   **SMTP Service:** Standard SMTP/SMTPS connection for sending emails.
*   **User Authentication (Potentially):** Could integrate with OAuth/OpenID Connect providers in the future, but initial scope is internal user management.

This HLD provides the architectural foundation. The next step would be to create Low-Level Designs (LLD) for each component or module, detailing class diagrams, specific API endpoints, database schemas, etc.

What are your thoughts on this High-Level Design? Are there any areas you'd like to explore further or adjust?

When you're ready, we can proceed to the **Low-Level Design (LLD)**.