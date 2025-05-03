# Product Context

## Why this project exists
The AD-Rapport Generator AI project aims to automate and streamline the process of generating reports for Arbeidsdeskundigen (Occupational Experts) in the Netherlands. Manually creating these reports is time-consuming and repetitive. This tool will help experts work more efficiently by automatically generating draft reports based on case documents and user prompts.

## Problems it solves
- **Time-consuming report writing:** Automates the generation of draft reports, significantly reducing the manual effort required.
- **Inconsistent report quality:** Provides a consistent starting point for reports based on structured data and AI generation.
- **Difficulty in extracting relevant information:** The RAG pipeline helps retrieve the most relevant information from case documents to inform the report.

## How it should work
1. Users log in to the application.
2. Users can create and manage cases.
3. Users upload relevant documents (e.g., medical reports, employer statements) for a specific case.
4. The system processes the documents asynchronously (parses, chunks, embeds).
5. Users can provide a prompt or question related to the case documents.
6. The system performs a vector search to find relevant document chunks based on the prompt.
7. The system uses the retrieved chunks as context and an LLM (via OpenRouter) to generate a draft report or answer the user's prompt.
8. Users can view and potentially edit the generated report.

## User Experience Goals
- **Intuitive and easy to use:** The interface should be straightforward for Arbeidsdeskundigen to navigate.
- **Efficient workflow:** The process from document upload to report generation should be quick and seamless.
- **Reliable results:** The generated reports should be accurate and relevant based on the provided documents and prompts.
- **Secure:** User data and uploaded documents must be handled securely.
- **Accessible:** The application should be accessible to the target users.
