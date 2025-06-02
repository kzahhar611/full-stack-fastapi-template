# System Screens: TenderWise AI

This document describes the key screens and their primary elements for the TenderWise AI platform.

**I. Core System Screens**

1.  **Login Screen**
    *   **Purpose:** Authenticate users.
    *   **Elements:**
        *   Logo (TenderWise AI)
        *   Username/Email input field
        *   Password input field
        *   "Login" button
        *   "Forgot Password?" link
        *   (Optional: "Register" link if self-registration is allowed for certain roles, or "Contact Admin" for account requests)

2.  **Main Dashboard (Homepage after Login)**
    *   **Purpose:** Provide a personalized overview of relevant information and quick access to modules.
    *   **Elements:**
        *   **Header:** Logo, User Profile (name, avatar, logout), Notification Bell icon, Search Bar (global search TBD).
        *   **Navigation Menu (Sidebar or Top Bar):**
            *   Dashboard
            *   RFP Analysis (Module 1)
            *   Proposal Comparison (Module 2)
            *   Proposal Generation (Module 3)
            *   Task Management
            *   File Management
            *   Calendar
            *   Settings (Admin only)
            *   Help/Chatbot
        *   **Main Content Area (Widgets, customizable by user/role):**
            *   "My Active Tenders/Projects" summary list (links to details).
            *   "My Tasks" summary (due soon, overdue).
            *   "Recent Notifications" feed.
            *   Quick "Upload RFP" button (for Module 1 or 3).
            *   Key Performance Indicators (KPIs) relevant to the user's role (e.g., overall bid win rate, average analysis time - for Managers/Admins).

3.  **User Profile Screen**
    *   **Purpose:** Allow users to view and edit their profile information.
    *   **Elements:**
        *   User details (Name, Email, Role - Role usually non-editable by user).
        *   Change Password section.
        *   Notification preferences (e.g., email vs. in-app).
        *   (Optional: Avatar upload, language preferences).

4.  **Task Management Screen**
    *   **Purpose:** View, create, and manage tasks.
    *   **Elements:**
        *   "Create New Task" button.
        *   Task list/board view (filterable by status, assignee, project, due date).
            *   Each task item: Title, Assignee, Due Date, Priority, Status, Link to related RFP/Project.
        *   Task detail view (when a task is clicked): Full description, comments, attachments, history.

5.  **File Management Screen**
    *   **Purpose:** Browse, search, and manage uploaded files.
    *   **Elements:**
        *   Folder/Project-based navigation.
        *   File list (Name, Type, Size, Upload Date, Uploaded By, associated Project/RFP).
        *   Search bar for files.
        *   "Upload File" button.
        *   Actions per file (Download, View Details, Delete - permission-based).

6.  **Calendar Screen**
    *   **Purpose:** View project deadlines, task due dates, and personal reminders.
    *   **Elements:**
        *   Monthly/Weekly/Daily calendar view.
        *   Events displayed (color-coded by type: RFP deadline, task due, meeting).
        *   "Add Event/Reminder" button.

7.  **Notification Center Screen**
    *   **Purpose:** View all system notifications.
    *   **Elements:**
        *   List of notifications (chronological, filterable by read/unread, type).
        *   Each notification: Message, Timestamp, Link to relevant item.
        *   "Mark all as read" button.

8.  **Settings Screen (Admin Only)**
    *   **Purpose:** Configure system-wide settings.
    *   **Sub-sections:**
        *   **User Management:** List users, Add/Edit/Deactivate users, Assign roles.
        *   **AI Configuration:**
            *   Manage API keys for Cloud AI services.
            *   Select default LLMs/models for different tasks (M1, M2, M3).
            *   (Advanced) Configure parameters/prompts for AI agents/workflows.
        *   **Template Management (for Module 3):** Upload, view, edit, delete proposal templates.
        *   **SMTP Server Configuration.**
        *   **System Logs/Audit Trails (View access).**
        *   **(Optional) Workflow Editor (if dynamic workflows are implemented).**

**II. Module-Specific Screens**

**Module 1: RFP Analysis & Strategic Decision Support**

9.  **RFP Listing & Upload Screen (Module 1 Entry)**
    *   **Purpose:** View previously analyzed RFPs and upload new ones for analysis.
    *   **Elements:**
        *   "Upload New RFP for Analysis" button.
        *   List/Table of RFPs: RFP Name/ID, Upload Date, Status (Pending, In Progress, Complete, Failed), Go/No-Go Decision (if complete), Link to Analysis.
        *   Filters for list (by status, date range).
        *   Search bar for RFPs.

10. **RFP Upload & Analysis Initiation Form**
    *   **Purpose:** Upload an RFP file and provide optional parameters for analysis.
    *   **Elements:**
        *   File drop zone / "Browse File" button (for PDF, DOCX).
        *   (Optional) Input fields for user parameters to guide AI (e.g., specific areas of concern, company context).
        *   "Start Analysis" button.
        *   Progress indicator during upload.

11. **RFP Analysis Result Screen**
    *   **Purpose:** Display the detailed results of an RFP analysis.
    *   **Elements:**
        *   RFP Title/Identifier.
        *   **Overall Recommendation:** "GO" or "NO-GO" prominently displayed.
        *   **Justification:** Detailed text explaining the recommendation.
        *   **Key Information Summary:**
            *   Project Type, Duration, Location, Budget Indicators, Client History Cues.
        *   **Identified Risks:** List of technical and legal risks (description, category, severity).
        *   **Key Requirements Summary:** Bulleted or numbered list of critical requirements.
        *   **Technology Stack Mentions.**
        *   **Evaluation Methodology Summary.**
        *   **KPI Dashboard (Embedded or Section):** Visual charts and graphs for risk score, alignment score, critical success factors.
        *   "Export Analysis" button (e.g., to PDF).
        *   Link to related tasks or to initiate a proposal (Module 3).

**Module 2: Proposal Compliance & Vendor Assessment**

12. **Proposal Comparison Listing Screen (Module 2 Entry)**
    *   **Purpose:** View past proposal comparisons and initiate new ones.
    *   **Elements:**
        *   "Start New Proposal Comparison" button.
        *   List/Table of Comparisons: Project Name, RFP, Vendor Proposal, Comparison Date, Overall Compliance Score, Go/No-Go Decision, Link to Details.
        *   Filters and search.

13. **New Proposal Comparison Form**
    *   **Purpose:** Upload RFP, vendor technical proposal, and vendor financial proposal.
    *   **Elements:**
        *   File upload fields for:
            *   RFP Document.
            *   Vendor Technical Proposal.
            *   Vendor Financial Proposal.
        *   "Start Comparison & Assessment" button.

14. **Proposal Comparison Result Screen**
    *   **Purpose:** Display the results of the comparison and vendor assessment.
    *   **Elements:**
        *   Project/RFP Identifier, Vendor Name.
        *   **Overall Recommendation:** "GO" or "NO-GO" for the vendor proposal.
        *   **Compliance Matrix:** Detailed table:
            *   Column 1: RFP Requirement ID/Description.
            *   Column 2: Compliance Status (Compliant, Partially Compliant, Non-Compliant, Not Addressed).
            *   Column 3: Excerpt/Reference from Vendor Proposal.
            *   Column 4: Notes/AI Comments.
        *   **Vendor Assessment Summary:**
            *   Scores/Ratings for: Experience, Similar Projects, Team Quality, Project Plan, Standards, Timeline, Financial Plan, Project/Risk/Communication Management.
            *   Overall Vendor Score.
        *   "Export Report" button.

**Module 3: AI-Powered Technical Proposal Generation**

15. **Proposal Generation Listing Screen (Module 3 Entry)**
    *   **Purpose:** View previously generated proposals and start new ones.
    *   **Elements:**
        *   "Generate New Technical Proposal" button.
        *   List/Table of Generated Proposals: Proposal Name, Associated RFP, Creation Date, Status (Draft, Finalized), Link to Edit/View.
        *   Filters and search.

16. **New Proposal Generation Setup Screen**
    *   **Purpose:** Upload RFP, provide instructions, and select a template.
    *   **Elements:**
        *   File upload for RFP.
        *   Input fields/Text areas for:
            *   Key win themes.
            *   Company-specific information/strengths.
            *   Specific instructions for AI.
        *   Dropdown to select a pre-loaded proposal template.
        *   "Generate Draft Proposal" button.

17. **Proposal Editor Screen**
    *   **Purpose:** View, edit, and finalize the AI-generated technical proposal.
    *   **Elements:**
        *   Rich Text Editor (WYSIWYG) displaying the proposal content (HTML).
        *   Proposal sections (based on template) likely navigable.
        *   Tools for formatting text, inserting images (if supported).
        *   "Save Draft" button.
        *   "Re-generate Section" (AI assistance for specific parts - advanced).
        *   "Export to PDF" button.
        *   "Mark as Final" button.

**III. Shared Components**

*   **Internal Chatbot Interface:**
    *   Typically a pop-up or docked window accessible from most screens.
    *   Text input for user queries.
    *   Display area for chatbot responses (text, links to help docs or system pages).

---
This list covers the primary screens. Each screen would have various states (e.g., empty state, loading state, error state) and responsive design considerations for different screen sizes.

Next, we'll move to **User Stories and Test Cases**. Similar to the LLD, creating exhaustive user stories and test cases for the entire system is a massive undertaking. I can provide examples for a few key features within Module 1 to illustrate the format and level of detail.

Shall I proceed with example User Stories and Test Cases for Module 1?