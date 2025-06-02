# AI Prompts and LLM Recommendations: TenderWise AI

**Date of Preparation:** 2025-05-31
**Prepared By:** kzahhar611 (Project Initiator) / Copilot (AI Assistant)

This document provides example AI prompts for each core module of TenderWise AI and recommendations for suitable LLMs. These prompts are starting points and would likely require iteration and refinement based on testing with specific LLMs and real-world documents.

---

## Module 1: RFP Analysis & Strategic Decision Support

**Core Task:** Analyze an RFP document to extract key information, identify risks, and provide a "Go/No-Go" recommendation.

**Example AI Prompts (Illustrative - these would be combined or chained):**

1.  **Initial RFP Processing & Key Information Extraction:**
    *   **Prompt:**
        ```
        You are an expert RFP (Request for Proposal) Analyst. Given the following RFP text, please extract and structure the following information in JSON format:
        1.  **Project Title/Name:** (If explicitly stated)
        2.  **Client/Issuing Organization:**
        3.  **Project Type:** (e.g., Software Development, Consultancy, Infrastructure)
        4.  **Key Objectives/Scope Summary:** (A brief summary of what the client wants to achieve)
        5.  **Stated Budget:** (Any explicit mentions of budget figures or ranges)
        6.  **Project Duration/Timeline:** (Any mentions of start dates, end dates, or duration)
        7.  **Submission Deadline:**
        8.  **Key Technologies Mentioned:** (List any specific technologies, platforms, or programming languages requested)
        9.  **Main Evaluation Criteria:** (List the criteria the client will use to evaluate proposals)
        10. **Key Deliverables Expected:** (List the main deliverables requested from the vendor)

        RFP Text:
        '''
        {RFP_DOCUMENT_TEXT_HERE}
        '''

        Output the result as a single JSON object.
        ```
    *   **Purpose:** General information extraction.

2.  **Risk Identification:**
    *   **Prompt:**
        ```
        Based on the RFP text provided below, identify potential risks for a vendor bidding on this project. For each risk, categorize it as 'Technical', 'Legal/Compliance', 'Financial', 'Resource', or 'Project Management'. Also, assign a preliminary severity level: 'Low', 'Medium', or 'High'. Provide a brief justification for each identified risk.

        Output the results as a JSON array, where each element is an object with fields: "description", "category", "severity", and "justification".

        RFP Text:
        '''
        {RFP_DOCUMENT_TEXT_HERE}
        '''
        Consider factors like unclear requirements, aggressive timelines, dependencies on third parties mentioned, specific contractual clauses, new or unproven technologies requested, penalties, etc.
        ```
    *   **Purpose:** Focus on risk factors.

3.  **"Go/No-Go" Recommendation Factors (to feed into internal logic or a final LLM call):**
    *   **Prompt (could be for specific sections or a summarization task):**
        ```
        Analyze the provided RFP text focusing on our company's ability to meet the core requirements. Our company strengths are: [{COMPANY_STRENGTHS_LIST}]. Our typical project size is [{TYPICAL_PROJECT_SIZE_RANGE}]. We have expertise in [{COMPANY_EXPERTISE_AREAS}].

        Based on this context and the RFP, provide a summary of:
        1.  **Alignment with Company Strengths:** (How well does the RFP align?)
        2.  **Technical Feasibility for Us:** (Can we realistically deliver the technical solution?)
        3.  **Resource Availability Match (High-Level):** (Does this seem like something we could staff?)
        4.  **Potential Showstoppers or Major Concerns from Our Perspective:**

        RFP Text:
        '''
        {RFP_DOCUMENT_TEXT_HERE}
        '''
        This output will be used to help make a Go/No-Go decision.
        ```
    *   **Purpose:** Gather specific points for the decision-making logic. The final Go/No-Go might be a combination of LLM outputs and programmatic rules.

**LLM Recommendations for Module 1:**

*   **Type:** Models with strong natural language understanding (NLU), excellent document comprehension, information extraction, and summarization capabilities. A large context window is crucial for processing lengthy RFPs.
*   **Examples (High-End):**
    *   OpenAI: GPT-4, GPT-4 Turbo (especially versions with large context windows)
    *   Anthropic: Claude 3 (Opus or Sonnet)
    *   Google: Gemini 1.5 Pro
*   **Considerations:**
    *   Ability to handle long documents (RFP length can vary significantly).
    *   Accuracy in extracting specific details and nuances.
    *   Ability to follow complex instructions for structured output (e.g., JSON).
    *   Cost per token, given RFPs can be long.

---

## Module 2: Proposal Compliance & Vendor Assessment

**Core Task:** Compare a vendor's proposal against an RFP, generate a compliance matrix, and assess the vendor based on predefined criteria.

**Example AI Prompts:**

1.  **Requirement Compliance Check (Iterative per RFP requirement):**
    *   **Prompt (This would likely be part of a larger loop or batch process):**
        ```
        You are a meticulous Proposal Compliance Analyst.
        RFP Requirement: "{RFP_REQUIREMENT_TEXT_HERE}" (ID: {RFP_REQUIREMENT_ID})
        Vendor Proposal Text:
        '''
        {VENDOR_PROPOSAL_TEXT_HERE}
        '''

        Analyze the Vendor Proposal Text to determine if and how it addresses the RFP Requirement.
        Output your findings in JSON format with the following fields:
        - "requirement_id": "{RFP_REQUIREMENT_ID}"
        - "compliance_status": ("Compliant", "Partially Compliant", "Non-Compliant", "Not Addressed")
        - "relevant_excerpts": ["List of direct quotes from the proposal that address the requirement. If none, empty array."]
        - "ai_comments": "Your brief explanation of the compliance status, highlighting gaps or direct evidence."
        ```
    *   **Purpose:** Check individual requirements.

2.  **Vendor Assessment Data Extraction (for specific criteria):**
    *   **Prompt (Example for "Experience" criterion):**
        ```
        Based on the provided Vendor Proposal Text and the original RFP Text (for context), extract information relevant to assessing the vendor's "Experience".
        Focus on:
        - Years in business or relevant service.
        - Number of similar projects completed.
        - Specific examples of past projects cited that match the RFP's scope.
        - Client testimonials or references related to experience.

        RFP Text (Context):
        '''
        {RFP_DOCUMENT_TEXT_HERE}
        '''
        Vendor Proposal Text:
        '''
        {VENDOR_PROPOSAL_TEXT_HERE}
        '''
        Output the extracted information in a structured summary or a JSON object with relevant fields.
        ```
    *   **Purpose:** Extract data points for each assessment category (experience, team, project plan, etc.). The final assessment score might be calculated programmatically based on these extractions.

**LLM Recommendations for Module 2:**

*   **Type:** Models with strong analytical and comparative abilities. High attention to detail is critical. Good at information retrieval from multiple documents or long texts.
*   **Examples (High-End):**
    *   OpenAI: GPT-4, GPT-4 Turbo
    *   Anthropic: Claude 3 (Opus or Sonnet)
    *   Google: Gemini 1.5 Pro
*   **Considerations:**
    *   Ability to perform "semantic search" or find relevant passages across documents.
    *   Precision in matching RFP requirements to proposal statements.
    *   Consistency in applying assessment criteria.
    *   May benefit from a Retrieval Augmented Generation (RAG) approach if comparing very large documents or needing to reference specific sections accurately.

---

## Module 3: AI-Powered Technical Proposal Generation

**Core Task:** Generate a draft technical proposal based on an RFP, user inputs, and a selected template.

**Example AI Prompts:**

1.  **Full Proposal Section Generation (Iterative per section of a template):**
    *   **Prompt (Example for "Proposed Solution" section):**
        ```
        You are an expert Technical Proposal Writer.
        You are tasked with writing the "Proposed Solution" section of a technical proposal.

        Reference RFP Text:
        '''
        {RFP_DOCUMENT_TEXT_HERE}
        '''

        Key Win Themes for this Proposal:
        '''
        {USER_INPUT_WIN_THEMES}
        '''

        Our Company's Strengths/Value Propositions to Highlight:
        '''
        {USER_INPUT_COMPANY_STRENGTHS}
        '''

        Specific User Instructions/Inputs for this Section:
        '''
        {USER_INPUT_SECTION_SPECIFIC_INSTRUCTIONS}
        '''

        Proposal Template Structure for this section (if applicable, otherwise describe the expected content):
        '''
        {PROPOSAL_TEMPLATE_SECTION_OUTLINE_OR_DESCRIPTION_HERE}
        '''

        Based on all the above information, draft a compelling and detailed "Proposed Solution" section. Ensure it directly addresses the requirements and needs outlined in the RFP. Incorporate our company strengths and the specified win themes. Maintain a professional and persuasive tone.
        The output should be well-structured, ready for inclusion in a formal proposal document. Use Markdown for formatting if possible.
        ```
    *   **Purpose:** Generate content for a specific part of the proposal.

2.  **Answering Specific RFP Questions within the Proposal:**
    *   **Prompt:**
        ```
        The RFP asks the following question: "{RFP_QUESTION_TEXT_HERE}"
        Our company's standard answer approach or relevant information is: "{COMPANY_KNOWLEDGE_BASE_INFO_OR_USER_INPUT}"

        Draft a clear, concise, and positive response to this RFP question, suitable for inclusion in our technical proposal.
        ```
    *   **Purpose:** Generate targeted answers.

**LLM Recommendations for Module 3:**

*   **Type:** Models with strong creative text generation capabilities, excellent coherence over long outputs, and the ability to adhere to complex instructions, including tone, style, and structural requirements (templates).
*   **Examples (High-End):**
    *   OpenAI: GPT-4, GPT-4 Turbo (known for strong instruction following and writing quality).
    *   Anthropic: Claude 3 Opus (strong writing capabilities and large context).
    *   Google: Gemini 1.5 Pro (if its generative capabilities match for formal writing).
*   **Considerations:**
    *   **Instruction Following:** Critical for incorporating user inputs, win themes, and adhering to template structures.
    *   **Coherence and Fluency:** The generated text must be professional and read well.
    *   **Creativity vs. Factual Accuracy:** Needs to be creative in presentation but factually grounded in the RFP and company information.
    *   **Controllability:** Ability to guide the output in terms of length, detail, and focus for different sections.
    *   **Context Window:** Must be able to hold the RFP, user inputs, and potentially parts of the proposal already generated.

---

**General LLM Selection & Prompt Engineering Advice:**

*   **Start with Leading Models:** For complex tasks like these, starting with state-of-the-art models (like GPT-4, Claude 3 Opus, Gemini 1.5 Pro) is often best for initial prototyping to establish what's possible.
*   **Cost vs. Performance:** Evaluate the trade-offs. More powerful models are typically more expensive. For some sub-tasks (e.g., simple extraction), a less powerful/cheaper model might suffice.
*   **Prompt Chaining/Decomposition:** Break down complex tasks into smaller, manageable sub-tasks, each with its own focused prompt. The output of one prompt can feed into the next.
*   **Iterative Refinement:** Prompt engineering is an iterative process. Expect to test, analyze outputs, and refine prompts multiple times.
*   **Few-Shot Learning:** Provide examples in your prompts (few-shot learning) to guide the AI towards the desired output format and style, especially for structured data extraction or specific writing styles.
*   **Temperature & Other Parameters:** Experiment with LLM parameters like `temperature` (randomness/creativity), `top_p`, etc., to fine-tune the output. Lower temperatures are generally better for analytical tasks, while higher might be useful (with caution) for initial creative drafts.
*   **Retrieval Augmented Generation (RAG):** For tasks requiring grounding in specific, extensive documents (like proposal generation based on many internal knowledge base articles), consider a RAG architecture. This involves retrieving relevant document chunks first and then providing them as context to the LLM for generation.
*   **Evaluate, Evaluate, Evaluate:** Continuously evaluate the quality, accuracy, and relevance of LLM outputs against your requirements and real-world test cases.

This document should serve as a good foundation for developing the AI-driven components of TenderWise AI.
```

This file provides a solid starting point for your AI prompt engineering and LLM selection process. Remember that the field of AI and LLMs is rapidly evolving, so continuous research and testing will be important.

Is this what you had in mind?