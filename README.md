# MedExplain 

### AI-Powered Medical Report Explanation Platform

MedExplain is an AI-powered web application that helps users understand complex medical reports in simpler and more accessible language.

Medical reports often contain clinical terminology, abbreviations, laboratory values, reference ranges, and other information that can be difficult for non-medical users to understand. MedExplain combines **Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), embeddings, vector search, PDF processing, OCR, and a web application backend** to generate understandable, evidence-grounded explanations.

> **Important:** MedExplain is an educational and informational tool. It does not provide medical diagnoses, prescriptions, or treatment decisions and should not replace consultation with a qualified healthcare professional.

---

##  Live Demo

**Live Application:** Coming soon


---

##  Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Project Goals](#-project-goals)
- [Key Features](#-key-features)
- [How MedExplain Works](#-how-medexplain-works)
- [System Architecture](#-system-architecture)
- [RAG Pipeline](#-rag-pipeline)
- [Medical Knowledge Base](#-medical-knowledge-base)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running the Backend](#-running-the-backend)
- [Running with Docker](#-running-with-docker)
- [Testing](#-testing)
- [API](#-api)
- [Medical Safety](#-medical-safety)
- [Security Considerations](#-security-considerations)
- [Screenshots](#-screenshots)
- [Articles](#-articles)
- [Future Improvements](#-future-improvements)
- [Learning Outcomes](#-learning-outcomes)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

#  Project Overview

MedExplain was built to explore how modern AI technologies can be applied to a real-world problem in the healthcare domain.

The application accepts a medical report, extracts its contents, processes the information, retrieves relevant medical knowledge, and uses an LLM to generate a simpler explanation.

The main focus of the project is not simply generating text with an LLM. It is about building a complete AI application around:

- Document processing
- Information retrieval
- Semantic search
- Retrieval-Augmented Generation
- LLM-based explanation
- Backend APIs
- Data storage
- Medical safety
- Testing
- Containerization
- Cloud deployment

---

#  Problem Statement

Medical reports are usually written for communication between healthcare professionals.

For a general user, a report can contain terms such as:

- Hemoglobin
- Platelet count
- Creatinine
- TSH
- LDL
- HDL
- Reference range
- RBC
- WBC
- Clinical abbreviations

Even when the information is technically correct, understanding what these values mean can be difficult without medical knowledge.

MedExplain attempts to solve the **understanding and explanation problem** by converting technical report information into simpler language while providing relevant medical context.

The application is intentionally designed as an **educational explanation system**, not as a diagnostic system.

---

#  Project Goals

The main goals of MedExplain are:

1. Make medical reports easier to understand.
2. Use RAG instead of relying only on the LLM's internal knowledge.
3. Retrieve relevant medical information from trusted sources.
4. Process both text-based and potentially scanned PDF reports.
5. Build a modular and scalable backend architecture.
6. Keep medical safety as a core application requirement.
7. Build the project using production-oriented engineering practices.
8. Deploy the application as a publicly accessible web application.

---

#  Key Features

###  Medical Report Upload

Users can upload medical report documents through the web interface.

###  PDF Text Extraction

The backend processes uploaded PDF documents and extracts available text.

###  OCR Support

OCR can be used when the report is scanned or does not contain directly extractable text.

###  Document Chunking

Large documents are divided into smaller meaningful chunks before embedding and retrieval.

###  Embeddings

Text chunks are converted into numerical vector representations that capture semantic meaning.

###  Semantic Search

The system searches the vector database for information that is semantically relevant to the report.

###  Retrieval-Augmented Generation

Relevant medical knowledge is retrieved and provided to the LLM as additional context.

###  LLM Explanation

The LLM generates a simpler explanation based on the report and retrieved context.

###  Medical Safety

The application is designed to avoid presenting generated explanations as diagnoses or prescriptions.

###  Docker Support

The backend can be containerized using Docker for consistent development and deployment.

###  Automated Testing

Core backend functionality is tested using automated tests.

---

#  How MedExplain Works

At a high level, the workflow looks like this:

```text
                User
                  │
                  ▼
          Upload Medical Report
                  │
                  ▼
             Frontend
                  │
                  ▼
              FastAPI
                  │
                  ▼
        PDF Processing / OCR
                  │
                  ▼
            Text Extraction
                  │
                  ▼
           Text Chunking
                  │
                  ▼
             Embeddings
                  │
                  ▼
          Semantic Retrieval
                  │
                  ▼
       Relevant Medical Context
                  │
                  ▼
          RAG Prompt Assembly
                  │
                  ▼
                 LLM
                  │
                  ▼
       Understandable Explanation
                  │
                  ▼
                User
```

---

#  System Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                         USER                            │
│                  Upload Medical Report                  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                       FRONTEND                          │
│                    HTML / CSS / JS                      │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                       FASTAPI                           │
│                     Backend API                         │
└───────────────────────────┬─────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌─────────────────────────┐   ┌───────────────────────────┐
│   Document Processing   │   │     Application Data      │
│                         │   │                           │
│ • PDF Parsing           │   │        MongoDB            │
│ • OCR                   │   │                           │
│ • Text Extraction       │   │                           │
└────────────┬────────────┘   └───────────────────────────┘
             │
             ▼
┌─────────────────────────┐
│      Text Chunking      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       Embeddings        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Vector Database     │
│                         │
│   Semantic Retrieval    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Relevant Context      │
│   from Medical KB       │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│          RAG            │
│                         │
│ Context + User Report   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│          LLM            │
│     Explanation         │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│    User-Friendly        │
│      Explanation        │
└─────────────────────────┘
```

---

#  RAG Pipeline

MedExplain uses **Retrieval-Augmented Generation (RAG)** to provide relevant supporting context to the LLM.

Instead of asking the LLM to explain a medical report using only its pretrained knowledge, the application retrieves relevant information from a medical knowledge base.

## Knowledge Ingestion

The knowledge-base pipeline is:

```text
Trusted Medical Sources
          │
          ▼
     Documents
          │
          ▼
    Text Extraction
          │
          ▼
       Chunking
          │
          ▼
     Embeddings
          │
          ▼
    Vector Database
```

## Query / Explanation Pipeline

When a user submits a report:

```text
Medical Report
      │
      ▼
Text Extraction
      │
      ▼
Query / Relevant Text
      │
      ▼
Embedding
      │
      ▼
Vector Search
      │
      ▼
Relevant Medical Chunks
      │
      ▼
Prompt Construction
      │
      ▼
LLM
      │
      ▼
Final Explanation
```

The retrieved information provides additional context that can help the LLM generate more grounded explanations.

---

#  Why RAG?

A general-purpose LLM may know a large amount of medical information, but relying only on its internal knowledge has limitations.

RAG allows the application to:

- Retrieve relevant information dynamically.
- Ground responses in a controlled knowledge base.
- Update knowledge without retraining the LLM.
- Provide source-aware explanations.
- Reduce reliance on unsupported model-generated information.

RAG does not eliminate hallucinations or guarantee medical correctness. It is one component of a broader safety and evaluation strategy.

---

#  Medical Knowledge Base

The medical knowledge base is intended to use reliable and authoritative sources.

Examples include:

- Government health organizations
- Academic medical institutions
- Peer-reviewed medical literature
- Established clinical reference sources
- Publicly available authoritative medical resources

The knowledge base should be reviewed and maintained carefully because medical information can change over time.

The project is designed to prefer **authoritative medical sources over random web content**.

---

#  Technology Stack

## Backend

- Python
- FastAPI
- Pydantic
- REST APIs

## AI / LLM

- Large Language Models
- Embeddings
- Retrieval-Augmented Generation
- Semantic Search
- Prompt Engineering

## Document Processing

- PDF parsing
- OCR
- Text extraction
- Document chunking

## Databases

- MongoDB
- Vector Database

## Frontend

- HTML
- CSS
- JavaScript

## Testing

- Pytest
- API testing

## DevOps

- Docker
- Git
- GitHub

## Deployment

- Vercel
- Render

---

#  Project Structure

The project is organized to keep the application modular and maintainable.

```text
MedExplain/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── rag/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
│
├── data/
│   └── knowledge_base/
│
├── .dockerignore
├── .gitignore
├── docker-compose.yml
└── README.md
```

> The exact structure may evolve as the application moves toward production deployment.

---

#  Getting Started

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Git
- Docker (optional but recommended)
- MongoDB or a MongoDB cloud instance
- Required LLM API access
- Vector database access

---

# 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MedExplain.git
cd MedExplain
```

Replace `YOUR_USERNAME` with your GitHub username.

---

# 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

If your requirements file is located elsewhere, use the corresponding path.

---

#  Environment Variables

Create a `.env` file for local development.

Example:

```env
LLM_API_KEY=your_llm_api_key
MONGODB_URI=your_mongodb_connection_string
VECTOR_DB_URL=your_vector_database_url
```

Depending on the final implementation, additional variables may include:

```env
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Never commit secrets

Do not commit:

- API keys
- Database passwords
- Authentication secrets
- Private credentials
- `.env` files

Make sure `.env` is included in `.gitignore`.

---

# ▶️ Running the Backend

From the backend directory:

```bash
cd backend
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI automatically provides interactive API documentation at:

```text
http://localhost:8000/docs
```

Alternative OpenAPI documentation:

```text
http://localhost:8000/redoc
```

---

# 🖥️ Running the Frontend

The frontend can be served using a local development server or the deployment configuration used by the project.

For a simple local static server:

```bash
cd frontend
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

The frontend communicates with the FastAPI backend through HTTP requests.

---

# 🐳 Docker

MedExplain includes Docker support to make the backend environment reproducible.

## Build the Image

```bash
docker build -t medexplain .
```

## Run the Container

```bash
docker run -p 8000:8000 medexplain
```

The API will then be available at:

```text
http://localhost:8000
```

---

#  Docker Compose

If the project uses Docker Compose:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

---

#  Testing

Run the automated test suite:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

The test suite is intended to validate important backend behavior and reduce regressions as the project evolves.

---

#  API

The backend is built with FastAPI.

Typical application endpoints can include:

```text
GET  /
GET  /health
POST /upload
POST /explain
```

The exact endpoints depend on the current implementation.

FastAPI's interactive API documentation can be accessed locally at:

```text
http://localhost:8000/docs
```

---

#  Medical Safety

Medical information is a high-risk domain, so safety is a core design consideration.

MedExplain is designed as an **explanation and education system**, not as a medical decision-making system.

The application should avoid:

- Diagnosing diseases
- Prescribing medication
- Recommending treatment plans
- Replacing professional medical advice
- Presenting uncertain information as certain
- Making unsupported claims from a medical report

Where appropriate, explanations should communicate uncertainty and encourage consultation with an appropriate healthcare professional.

---

#  Medical Disclaimer

**MedExplain is for educational and informational purposes only.**

The information generated by MedExplain should not be considered medical advice, diagnosis, treatment, or a prescription.

Users should consult a qualified healthcare professional for interpretation of their medical condition and for medical decisions.

Do not use MedExplain as a substitute for professional medical care.

---

#  Security Considerations

Medical reports may contain sensitive personal information.

The application therefore needs to consider security throughout the system.

Important considerations include:

- Secure file uploads
- File type validation
- File size limits
- API authentication where required
- Secure environment variables
- HTTPS in production
- Database access controls
- Avoiding sensitive information in logs
- Secure deletion/retention policies
- Rate limiting
- Input validation
- Dependency security
- Access control
- Secure cloud configuration

During development, synthetic/sample medical reports should be preferred whenever possible.

---

#  Screenshots

Screenshots of the application will be added as the production version is finalized.

### Home / Upload Page


### Medical Report Processing


---

# Articles & Development Journey

I am documenting the development of MedExplain and the technical decisions behind the project through LinkedIn articles.

## Article 1 — Introducing MedExplain

### Introducing MedExplain: Making Medical Reports Easier to Understand

I explain the problem behind MedExplain, why I started the project, and the idea behind using AI to make medical reports easier to understand.

🔗 **Read the article:**

https://www.linkedin.com/pulse/introducing-medexplain-making-medical-reports-easier-arpan-mondal-egfgc/

---

## Article 2 — From Medical Report to Clear Explanation

### From Medical Report to Clear Explanation: How I'm Building MedExplain

This article explains the development journey of MedExplain and how I am approaching the problem using modern AI application technologies.

 **Read the article:**

https://www.linkedin.com/pulse/from-medical-report-clear-explanation-how-im-building-arpan-mondal-7wgbe/





### Retrieval Evaluation

Possible metrics include:

- Precision@K
- Recall@K
- MRR
- Context relevance
- Retrieval accuracy

### Generation Evaluation

Possible dimensions include:

- Faithfulness
- Answer relevance
- Groundedness
- Completeness
- Medical safety
- Unsupported claim rate

The goal is to evaluate the system rather than assuming that a successful LLM response is automatically correct.

---

#  What I Learned From This Project

Building MedExplain has provided hands-on experience with several areas of modern AI engineering.

### Backend Development

- Python
- FastAPI
- REST API design
- Request validation
- Error handling
- Backend testing

### LLM Application Development

- LLM APIs
- Prompt engineering
- Context construction
- RAG architecture
- Embeddings
- Semantic search

### Document AI

- PDF processing
- OCR
- Text extraction
- Chunking
- Document pipelines

### Data & Databases

- MongoDB
- Vector databases
- Data modeling
- Retrieval systems

### DevOps

- Docker
- Git
- GitHub
- Environment configuration
- Cloud deployment

### AI Safety

- Limiting unsupported claims
- Medical disclaimers
- Grounded generation
- Source-aware responses
- Sensitive-data considerations

---

#  Why I Built MedExplain

The project started from a simple observation:

> Medical reports contain important information, but understanding that information can be difficult for people without a medical background.

Instead of building another general-purpose chatbot, I wanted to work on a focused real-world problem and explore how modern AI technologies could be combined into a useful application.

MedExplain gave me the opportunity to work across the complete AI application lifecycle:

```text
Problem
  ↓
Architecture
  ↓
Backend
  ↓
Document Processing
  ↓
RAG
  ↓
LLM
  ↓
Frontend
  ↓
Testing
  ↓
Docker
  ↓
Deployment
```

---

#  Deployment

The planned production architecture uses:

```text
                    Internet
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
          Vercel               Render
        Frontend              Backend
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
                 MongoDB     Vector DB       LLM
```

### Frontend

Planned deployment:

**Vercel**

### Backend

Planned deployment:

**Render**

### Database

**MongoDB**

### Vector Search

**Vector Database**

### LLM

**LLM API**

Production deployment details and live URLs will be added once deployment is complete.

---

#  Development Workflow

The project follows a development workflow based around incremental implementation and testing.

```text
Feature Planning
      ↓
Implementation
      ↓
Local Testing
      ↓
Automated Tests
      ↓
Git Commit
      ↓
GitHub
      ↓
Docker Build
      ↓
Deployment
      ↓
Production Testing
```

---

#  Contributing

This project is currently primarily a personal portfolio and learning project.

If contribution is enabled in the future, contribution guidelines will be added here.

For suggestions or technical discussions, feel free to open an issue in the repository.

---

#  Support the Project

If you find MedExplain interesting, consider giving the repository a ⭐ on GitHub.

It helps others discover the project and supports continued development.

---

#  License

This project is currently intended for educational, research, and portfolio purposes.

A formal open-source license will be added if the project is released for public contribution.

---

#  Author

## Arpan Mondal

Engineer focused on AI/ML and LLM application development.

MedExplain is a hands-on project exploring how modern AI engineering techniques can be used to build practical, production-oriented applications.

---

## 🔗 Connect & Follow the Project

LinkedIn articles documenting the development journey:

- **Introducing MedExplain: Making Medical Reports Easier to Understand**  
  https://www.linkedin.com/pulse/introducing-medexplain-making-medical-reports-easier-arpan-mondal-egfgc/

- **From Medical Report to Clear Explanation: How I'm Building MedExplain**  
  https://www.linkedin.com/pulse/from-medical-report-clear-explanation-how-im-building-arpan-mondal-7wgbe/

---

# ⭐ MedExplain

**Making complex medical reports easier to understand — with AI, RAG, and responsible engineering.**
