Project Management (Doorlopend vanaf Fase 0):

[ ] Project Backlog Beheren (taken prioriteren, verfijnen).
[ ] Voortgang Monitoren & Rapporteren.
[ ] Risicoregister Bijhouden & Acties Monitoren.   
[ ] Stakeholder Communicatie Onderhouden.
[ ] Documentatie Bijwerken (technisch, gebruiker).
Fase 0: Fundering & Planning (± 1-2 weken)

[ ] Task 0.1: Definieer & Finaliseer MVP Scope en Succescriteria.
[ ] Task 0.2: Maak GitHub Repository aan (Private).
[ ] Task 0.3: Zet Supabase Project op (DB, Auth, Storage).
[ ] Task 0.4: Schakel pgvector extensie in & Configureer HNSW Indexering.   
[ ] Task 0.5: Kies & Zet Cloud Redis Instance op (Managed service aanbevolen).   
[ ] Task 0.6: Kies Definitief Frontend Framework (React/Vue/Angular).
[ ] Task 0.7: Kies Cloud Hosting Platform (bv. GCP Cloud Run, AWS ECS) & Zet basis IaC (Terraform/Pulumi) op.   
[ ] Task 0.8: Zet Ontwikkelomgeving op (Project IDX / Lokaal venv).
[ ] Task 0.9: Clone Repo & Initialiseer Backend (FastAPI) en Frontend projectstructuren.
[ ] Task 0.10: Installeer Core Dependencies (Backend & Frontend).
[ ] Task 0.11: Configureer Basis .env / Secrets Management.   
[ ] Task 0.12: Zet Basis Celery Configuratie op (met cloud Redis URL).   
[ ] Task 0.13: Stel Initiële Risicoregister op.   
[ ] Task 0.14: Start Formele DPIA: Data mapping, identificeren risico's.   
[ ] Task 0.15: Vraag DPA's op bij Supabase & Google Cloud.   
Fase 1: MVP Backend Kern (± 2-3 weken)

[ ] Task 1.1: Implementeer Supabase Auth integratie (JWT middleware, user dependency).
[ ] Task 1.2: Definieer DB Modellen (MVP Scope) met SQLModel/SQLAlchemy.   
[ ] Task 1.3: Zet DB Migraties (Alembic) op & voer uit.
[ ] Task 1.4: Sla structuur van één template op (JSON Schema in DB).
[ ] Task 1.5: Implementeer API Endpoints: Case CRUD (/cases), Document Lijst (/cases/{case_id}/documents).
[ ] Task 1.6: Implementeer API Endpoint: Document Upload (/cases/{case_id}/upload_mvp) (docx/txt, Supabase Storage, DB record, trigger Celery).
[ ] Task 1.7: Implementeer Celery Taak Stubs: trigger_document_processing_mvp, process_document_mvp, chunk_and_embed_document_mvp, generate_report_mvp. Update status in DB.
[ ] Task 1.8: Implementeer Basis Logging voor backend.
[ ] Task 1.9: Schrijf Unit & Integratie Tests voor API's en DB Models (Start).
Fase 2: MVP Basis RAG & Generatie (± 3-4 weken, Iteratief)

[ ] Task 2.1: Implementeer process_document_mvp taak: Download, basis parsing (docx, txt).
[ ] Task 2.2: Implementeer chunk_and_embed_document_mvp taak: Basis chunking, Roep Gemini Embedding API aan, Sla op in pgvector.
[ ] Task 2.3: Implementeer generate_report_mvp taak:
Haal data op (Report, Case, Chunks).
Voor essentiële MVP secties:
Formuleer basis vraag.
Voer vector similarity search uit (pgvector <=>).
Ontwikkel/Test/Verfijn Prompt: Strikte grounding, basis Markdown output.   
Roep Gemini 1.5 Pro API aan (lage temperature).
Log gebruikte chunks.
Assembleer & Sla output op in GeneratedReport.
Update status.
[ ] Task 2.4: Handmatige Evaluatie & Prompt Iteratie: Test met voorbeelddocumenten, beoordeel output, pas prompts aan.
[ ] Task 2.5: Breid Unit/Integratie Tests uit voor Celery taken en basis RAG flow.
Fase 3: MVP Frontend & Integratie (± 3-4 weken, Parallel met Fase 2)

[x] Task 3.1: Zet Frontend project op (gekozen framework).
[x] Task 3.2: Implementeer Login/Registratie UI (Supabase Auth JS).
[x] Task 3.3: Implementeer Case Management UI (Lijst, Aanmaken).
[ ] Task 3.4: Implementeer Document Upload UI (docx/txt).
[ ] Task 3.5: Implementeer Status Weergave (Documenten, Rapporten - polling/refresh).
[ ] Task 3.6: Implementeer Rapport Generatie Knop (roept MVP API aan).
[ ] Task 3.7: Implementeer Simpele Rapport Viewer (toont gegenereerde Markdown, basis textarea voor copy/edit).
[ ] Task 3.8: Implementeer Frontend Routing & Auth Guarding.
[ ] Task 3.9: Koppel UI aan alle MVP Backend API Endpoints.
Fase 4: MVP Testen, Feedback & Afronding (± 2 weken)

[ ] Task 4.1: Voer End-to-End tests uit op de MVP workflow.
[ ] Task 4.2: Implementeer Basis Supabase RLS (op Cases, Docs, Reports, Chunks).   
[ ] Task 4.3: Voer Handmatige RLS Tests uit (verifieer data scheiding).
[ ] Task 4.4: User Acceptance Testing (UAT) met 1-2 experts: Verzamel feedback op workflow & output kwaliteit.   
[ ] Task 4.5: Verwerk Kritieke MVP feedback / bugs.
[ ] Task 4.6: Schrijf Beknopte MVP Documentatie.
[ ] Task 4.7: Deploy MVP naar Staging/Test omgeving (via basis IaC/scripts).   
(Beslismoment: Evalueer MVP resultaten & feedback. Doorgaan met Post-MVP?)

Fase 5: Geavanceerde Parsing & RAG (Iteratief, Post-MVP)

[ ] Task 5.1: Onderzoek & Implementeer Structure-Aware Parsing library (bv. unstructured.io, llmsherpa). Pas process_document taak aan.   
[ ] Task 5.2: Onderzoek & Implementeer Geavanceerde Chunking Strategieën (semantisch, structureel). Evalueer impact.   
[ ] Task 5.3: Implementeer Opslag van Rijke Metadata bij Chunks.   
[ ] Task 5.4: Implementeer Hybrid Search (combineer pgvector & PostgreSQL FTS).   
[ ] Task 5.5: Onderzoek & Implementeer Reranking (bv. met cross-encoder).   
[ ] Task 5.6: Onderzoek & Implementeer evt. Query Transformation technieken.   
[ ] Task 5.7: Ontwikkel RAG Evaluation Suite: Dataset, Metrieken (Faithfulness, Relevance), Automatisering (evt. LLM-as-judge).   
[ ] Task 5.8: Gebruik Eval Suite om RAG pipeline iteratief te verbeteren.
Fase 6: Uitgebreide AI & Features (Iteratief, Post-MVP)

[ ] Task 6.1: Implementeer Multi-Template Support:
DB Model voor ReportTemplate uitbreiden (JSON Schema opslag).
API voor template CRUD.
Frontend UI voor template selectie.
Pas generate_report taak aan voor dynamische templates.
[ ] Task 6.2: Benchmark Gemini native OCR/ASR vs. Gespecialiseerde Tools.   
[ ] Task 6.3: Implementeer Gekozen OCR oplossing (indien nodig) voor gescande PDFs/images. Pas process_document aan.
[ ] Task 6.4: Implementeer Gekozen ASR oplossing (indien nodig) voor audiobestanden. Pas process_document aan.
[ ] Task 6.5: Verfijn Structured Output Prompting (bv. JSON mode). Pas backend validatie (Pydantic) aan.   
[ ] Task 6.6: Ontwikkel Prompt Library / Prompt Management Systeem.   
[ ] Task 6.7: Verfijn Few-Shot Examples voor prompts.   
Fase 7: Volledige Frontend & UX (Post-MVP)

[ ] Task 7.1: Selecteer & Integreer Rich Text Editor (bv. Tiptap, CKEditor).   
[ ] Task 7.2: Selecteer & Integreer Diff Viewer component.   
[ ] Task 7.3: Implementeer Source Attribution UI (highlighting, bron-snippets tonen). Koppel aan backend logging van gebruikte chunks.   
[ ] Task 7.4: Onderzoek & Implementeer evt. Real-time Collaboration features.   
[ ] Task 7.5: Implementeer Realtime Status Updates (via Supabase Realtime).
[ ] Task 7.6: Verbeter Algemene UI/UX flow o.b.v. HCAI principes & UAT feedback.   
[ ] Task 7.7: Implementeer Feedback mechanisme in UI (per sectie).   
Fase 8: Compliance, Security & Schaalbaarheid (Post-MVP)

[ ] Task 8.1: Finaliseer & Documenteer DPIA; implementeer mitigaties.   
[ ] Task 8.2: Finaliseer & Teken DPA's (Supabase, Google Cloud).   
[ ] Task 8.3: Implementeer & Test Volledige RLS policies grondig.   
[ ] Task 8.4: Voer Uitgebreide Security Tests uit (SAST, DAST, evt. Pentest). Adresseer bevindingen.   
[ ] Task 8.5: Onderzoek & Implementeer evt. Pseudonimisering strategie (valideer effectiviteit & compliance).   
[ ] Task 8.6: Zet Bias Monitoring op (analyseer output, verzamel feedback).   
[ ] Task 8.7: Voer Performance & Load Tests uit. Optimaliseer knelpunten (DB queries, Celery workers, API's).   
[ ] Task 8.8: Configureer Auto-scaling voor backend/workers op hosting platform.
[ ] Task 8.9: Verfijn Logging & Monitoring voor productie.
Fase 9: Productie Deployment & Lancering (Post-MVP)

[ ] Task 9.1: Zet Volledige CI/CD Pipeline op (incl. tests, RAG eval, security scans, IaC deployment).   
[ ] Task 9.2: Configureer Productie Hosting Omgeving (via IaC).   
[ ] Task 9.3: Ontwikkel Gebruikerstraining Materiaal & Documentatie.   
[ ] Task 9.4: Ontwikkel & Voer Gebruikersadoptie & Communicatieplan uit.   
[ ] Task 9.5: Voer Finale UAT uit op staging omgeving.
[ ] Task 9.6: Deploy naar Productie (via CI/CD, evt. Blue/Green).   
[ ] Task 9.7: Voer Initiële User Onboarding & Training uit.
Fase 10: Continue Verbetering & Onderhoud (Doorlopend)

[ ] Task 10.1: Monitor Applicatie Performance, Errors & Kosten.
[ ] Task 10.2: Verzamel & Analyseer Gebruikersfeedback.
[ ] Task 10.3: Beheer Product Backlog voor nieuwe features & verbeteringen.
[ ] Task 10.4: Plan & Voer Regelmatige Sprints/Iteraties uit voor updates.
[ ] Task 10.5: Onderhoud & Update Dependencies (Python, JS).
[ ] Task 10.6: Update AI Model / Prompts / RAG pipeline o.b.v. performance & feedback.
[ ] Task 10.7: Bied Gebruikersondersteuning & Bug Fixing.
[ ] Task 10.8: Periodieke Security & Compliance Reviews.
