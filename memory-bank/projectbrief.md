# Project Brief: AD-Rapport Generator AI

## Project Goal
To build an AI-powered application that assists Arbeidsdeskundigen (Occupational Experts) in generating reports by automating the process of extracting relevant information from case documents and generating draft report content.

## Core Requirements
- **User Authentication:** Secure registration and login for users.
- **Case Management:** Ability to create, view, and manage individual cases.
- **Document Handling:** Secure upload, storage, parsing, and processing of case documents (`.docx`, `.txt`).
- **RAG Pipeline:** Implement a system to retrieve relevant information from processed documents based on user prompts.
- **Report Generation:** Generate draft report content using an LLM based on user prompts and retrieved document context.
- **User Interface:** An intuitive web interface for all functionalities.

## Project Phases
1. **Backend Core & Infrastructure Setup:** Set up the basic backend framework (FastAPI), database (Supabase), task queue (Celery/Redis), and authentication. (Completed)
2. **Document Handling & RAG Pipeline Backend:** Implement document upload, processing (parsing, chunking, embedding), vector search, and initial report generation logic. (Completed, including OpenRouter integration)
3. **Frontend UI Development:** Build the complete user interface and integrate it with the backend API. (Current Phase)
4. **Advanced Features & Refinements:** Implement features like report templates, improved chunking, support for more document types, and UI/UX enhancements.
5. **Deployment:** Deploy the application to a production environment.

## Key Deliverables
- Functional web application with user authentication, case management, document handling, RAG, and report generation.
- Well-structured and maintainable codebase.
- Comprehensive documentation (Memory Bank).

## Stakeholders
- Arbeidsdeskundigen (End Users)
- Project Owner/Sponsor
- Development Team (Cline and User)

## Success Criteria
- The application successfully automates a significant portion of the report writing process.
- Users find the application easy to use and the generated reports helpful.
- The system is stable, secure, and scalable.
