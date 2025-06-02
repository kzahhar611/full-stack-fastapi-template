# User Stories & Test Cases: TenderWise AI
## Module 1: RFP Analysis & Strategic Decision Support

**User Roles Involved:**
*   **Standard User:** (e.g., Sales Team Member, Analyst) - Primary interactor with Module 1.
*   **Manager:** (e.g., Sales Manager) - May also use Module 1, review results, and oversee.
*   **Administrator:** Configures Module 1 settings (AI models, etc.) - not directly covered in these user-facing stories.

---

**Epic 1: RFP Upload and Initial Processing**

**User Story 1.1:**
*   **ID:** US-M1-001
*   **As a:** Standard User
*   **I want to:** Upload an RFP document (PDF or DOCX) into the system
*   **So that:** It can be stored and prepared for AI analysis.
*   **Acceptance Criteria:**
    1.  The system must provide an interface to select or drag-and-drop a file.
    2.  The system must accept files with `.pdf` and `.docx` extensions.
    3.  The system must reject files with other extensions and show an appropriate error message.
    4.  The system should display a progress indicator during upload.
    5.  Upon successful upload, the system must confirm success and list the RFP in the "RFP Listing" screen with an "Uploaded" or "Ready for Analysis" status.
    6.  If the upload fails (e.g., network error, server error), the system must show an appropriate error message.
    7.  The uploaded file must be securely stored in the designated file storage.
    8.  Metadata about the RFP (filename, upload date, uploader, initial status) must be saved in the database.

*   **Test Cases for US-M1-001:**
    *   **TC-M1-001.1 (Happy Path - PDF):**
        *   **Given:** User is logged in and on the RFP Upload screen.
        *   **When:** User selects a valid PDF file (e.g., `test_rfp.pdf`) and initiates upload.
        *   **Then:** Upload progress is shown, a success message is displayed, the RFP appears in the listing with "Uploaded" status, and the file is verified in backend storage.
    *   **TC-M1-001.2 (Happy Path - DOCX):**
        *   **Given:** User is logged in and on the RFP Upload screen.
        *   **When:** User selects a valid DOCX file (e.g., `test_rfp.docx`) and initiates upload.
        *   **Then:** Upload progress is shown, a success message is displayed, the RFP appears in the listing with "Uploaded" status, and the file is verified in backend storage.
    *   **TC-M1-001.3 (Invalid File Type):**
        *   **Given:** User is logged in and on the RFP Upload screen.
        *   **When:** User selects an invalid file type (e.g., `image.jpg`).
        *   **Then:** An error message "Invalid file type. Please upload PDF or DOCX." is displayed, and the file is not uploaded.
    *   **TC-M1-001.4 (File Too Large - if limit exists):**
        *   **Given:** User is logged in, and a file size limit (e.g., 50MB) is configured.
        *   **When:** User selects a valid PDF file exceeding the size limit.
        *   **Then:** An error message "File size exceeds the limit of 50MB." is displayed.
    *   **TC-M1-001.5 (Network Error during Upload):**
        *   **Given:** User is logged in and initiates an upload.
        *   **When:** Network connectivity is lost during the upload.
        *   **Then:** An appropriate error message "Upload failed due to a network error. Please try again." is displayed.

---

**Epic 2: RFP Analysis Initiation and Processing**

**User Story 1.2:**
*   **ID:** US-M1-002
*   **As a:** Standard User
*   **I want to:** Initiate an AI analysis for an uploaded RFP
*   **So that:** I can get strategic insights, risk assessment, and a Go/No-Go recommendation.
*   **Acceptance Criteria:**
    1.  The system must allow me to select an uploaded RFP (status "Uploaded" or "Ready for Analysis").
    2.  The system must provide a button/action to "Start Analysis."
    3.  (Optional) The system may allow me to input specific parameters to guide the analysis (e.g., focus areas).
    4.  Upon initiating analysis, the RFP status must change to "Pending Analysis" or "Analysis in Progress."
    5.  The system must confirm that the analysis has started.
    6.  The AI analysis task must be added to an asynchronous processing queue.
    7.  The system should provide an indication that analysis is ongoing (e.g., in the RFP listing).

*   **Test Cases for US-M1-002:**
    *   **TC-M1-002.1 (Happy Path - Initiate Analysis):**
        *   **Given:** An RFP `test_rfp.pdf` is successfully uploaded with status "Uploaded."
        *   **When:** User selects `test_rfp.pdf` and clicks "Start Analysis."
        *   **Then:** A confirmation message "Analysis initiated for test_rfp.pdf" is shown, the RFP status updates to "Pending Analysis," and an analysis task is verified in the task queue.
    *   **TC-M1-002.2 (Attempt to Analyze Non-Uploaded RFP):**
        *   **Given:** No RFP is selected, or an RFP that failed to upload is shown.
        *   **When:** User attempts to click a (disabled or non-existent) "Start Analysis" button.
        *   **Then:** No action is performed, or an appropriate message "Please select a valid uploaded RFP" is shown.
    *   **TC-M1-002.3 (Initiate Analysis with Optional Parameters):**
        *   **Given:** An RFP `test_rfp.pdf` is uploaded.
        *   **When:** User selects the RFP, enters "budget constraints" as a focus area, and clicks "Start Analysis."
        *   **Then:** Analysis is initiated, status updates, and the "budget constraints" parameter is verified as part of the enqueued task data.

---

**Epic 3: Viewing RFP Analysis Results**

**User Story 1.3:**
*   **ID:** US-M1-003
*   **As a:** Standard User or Manager
*   **I want to:** View the detailed AI analysis results for an RFP once processing is complete
*   **So that:** I can understand the Go/No-Go recommendation, risks, key requirements, and other insights.
*   **Acceptance Criteria:**
    1.  When analysis is complete, the RFP status must update to "Analysis Complete."
    2.  The system must provide a way to navigate to the analysis results page for a completed RFP.
    3.  The results page must clearly display:
        *   The overall "Go" or "No-Go" decision.
        *   A detailed justification for the decision.
        *   A list of identified risks (e.g., technical, legal) with severity.
        *   A summary of key RFP requirements.
        *   Extracted entities (e.g., budget mentions, timeline, tech stack).
        *   A KPI dashboard with relevant metrics (e.g., risk score, alignment score).
    4.  If analysis failed, the status should be "Analysis Failed," and a reason for failure should be viewable (if appropriate for the user).
    5.  The information displayed must be accurate based on the AI's output.

*   **Test Cases for US-M1-003:**
    *   **TC-M1-003.1 (Happy Path - View "Go" Decision):**
        *   **Given:** RFP `rfp_go.pdf` has status "Analysis Complete" and the AI determined a "Go" decision.
        *   **When:** User navigates to the analysis results for `rfp_go.pdf`.
        *   **Then:** The page displays "Go," along with the correct justification, risks, requirements, entities, and KPI dashboard data provided by the AI.
    *   **TC-M1-003.2 (Happy Path - View "No-Go" Decision):**
        *   **Given:** RFP `rfp_nogo.pdf` has status "Analysis Complete" and the AI determined a "No-Go" decision.
        *   **When:** User navigates to the analysis results for `rfp_nogo.pdf`.
        *   **Then:** The page displays "No-Go," along with its corresponding justification, risks, requirements, etc.
    *   **TC-M1-003.3 (View Results - Analysis Failed):**
        *   **Given:** RFP `rfp_failed.pdf` has status "Analysis Failed."
        *   **When:** User navigates to view information about `rfp_failed.pdf`.
        *   **Then:** The system displays "Analysis Failed" and a user-friendly error message or reason (e.g., "Could not parse document content," "AI service unavailable").
    *   **TC-M1-003.4 (Data Accuracy - Risks):**
        *   **Given:** RFP `rfp_risky.pdf` was analyzed, and the AI identified 3 specific risks (R1, R2, R3).
        *   **When:** User views the analysis results.
        *   **Then:** The "Identified Risks" section accurately lists R1, R2, and R3 with their AI-assigned categories and severities.
    *   **TC-M1-003.5 (KPI Dashboard Display):**
        *   **Given:** RFP `rfp_kpi.pdf` was analyzed, and the AI generated specific data for the KPI dashboard (e.g., riskScore: 60, alignmentScore: 75).
        *   **When:** User views the analysis results.
        *   **Then:** The KPI dashboard correctly visualizes these scores.

---
This provides a sample of how user stories and test cases would be structured for Module 1. A comprehensive test plan would include many more scenarios, including edge cases, security tests, performance tests, and usability tests for each feature.

Next on your list is the **Deployment Plan**. Shall we proceed with that?