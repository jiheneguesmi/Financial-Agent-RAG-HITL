# Financial Agent with RAG + HITL

An intelligent financial data extraction and analysis agent combining **RAG (Retrieval-Augmented Generation)**, **LLM (Large Language Models)**, and **HITL (Human-In-The-Loop)** for precise extraction with human validation.

## Overview

This agent automates the extraction of financial data from PDF and JSON documents while allowing for interactive validation and correction by human users. It learns from corrections to continuously improve its accuracy.

### Key Features

- **Automatic Extraction**: Extracts 11 key financial fields with confidence scores.
- **RAG (Retrieval-Augmented Generation)**: Semantic search through indexed documents.
- **LLM GPT-4o**: Generation and analysis using OpenAI's most advanced model.
- **HITL Validation**: Interactive interface for validating and correcting results.
- **Persistent Memory**: Learns from corrections to improve future extractions.
- **Intelligent Q&A**: Answering business-related questions based on documents.
- **Web Interface**: Modern and intuitive Streamlit interface.

<img width="1906" height="851" alt="image" src="https://github.com/user-attachments/assets/684bb773-0498-41b2-8993-dfa57ac01647" />
<img width="1884" height="857" alt="image" src="https://github.com/user-attachments/assets/6c61a302-ba89-4e8f-9241-acbfbc95c764" /><img width="1895" height="867" alt="image" src="https://github.com/user-attachments/assets/f9359e3f-cc58-4f47-ae96-e733dcf46742" />
<img width="1905" height="862" alt="image" src="https://github.com/user-attachments/assets/6ae7922c-fbfc-47f5-9b88-5238c2ac5554" />




## Installation

### Prerequisites

- Python 3.11+
- pip or conda
- OpenAI API Key (free or paid)

### Installation Steps

1. **Clone the project**:
```bash
git clone https://github.com/jiheneguesmi/Financial-Agent-RAG-HITL.git
cd "agent IA Harington"
Create a virtual environment (optional but recommended):

python -m venv agent_harington
source agent_harington/bin/activate  # Linux/Mac
# or
agent_harington\Scripts\Activate.ps1  # Windows PowerShell


Install dependencies:

pip install -r requirements.txt


Set up OpenAI API key:

Create a .env file at the root of the project:

OPENAI_API_KEY=sk-proj-your-api-key-here


Or set the environment variable:

# Linux/Mac
export OPENAI_API_KEY="sk-proj-..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-proj-..."

Quick Usage
Option 1: Streamlit Interface (Recommended)
streamlit run app.py


The app will open at http://localhost:8501

Option 2: Launch Script
python run_streamlit.py

Option 3: Command-line Pipeline
python main.py

Architecture
agent IA Harington/
├── app.py                      # Streamlit app
├── main.py                     # Main entry point
├── run_streamlit.py            # Launch script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (to be created)
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── src/
│   ├── __init__.py
│   ├── config.py              # Centralized configuration
│   ├── document_processor.py   # PDF/JSON processing
│   ├── rag_engine.py          # RAG engine (indexing + retrieval)
│   ├── extractor.py           # Financial data extraction
│   ├── qa_engine.py           # Question/Answer engine
│   ├── hitl_manager.py        # Human validation manager
│   └── memory_manager.py      # Persistent memory management
├── data/                      # Source documents (PDF/JSON)
├── outputs/                   # Extraction results
├── memory/                    # Corrections and history
├── rag_index/                 # FAISS vector index
├── PLAN_PROJET.md            # Detailed project plan
├── STREAMLIT_README.md       # Streamlit documentation
├── QUICKSTART.md             # Quickstart guide
├── MODIFICATIONS.md          # Modification history
└── README.md                 # This file

Main Components
1. DocumentProcessor (src/document_processor.py)

Processes incoming documents (PDF and JSON) and splits them into chunks.

Features:

PDF text extraction using PyPDF2

Support for JSON files

Intelligent chunking with overlap

Automatic metadata generation

2. RAGEngine (src/rag_engine.py)

Vector search and retrieval-augmented generation engine.

Features:

FAISS indexing of documents

OpenAI embeddings text-embedding-3-small

Semantic search

Contextual generation

Index persistence

3. FinancialExtractor (src/extractor.py)

Structured extraction of financial data with confidence scores.

Extracted Fields:

finYear: Fiscal year

finSales: Sales revenue

finProfit: Net profit

finEquity: Equity

finCapital: Share capital

finBalanceSheet: Balance sheet total

finAvailableFunds: Available cash

finOperationInc: Operating income

finFinancialInc: Financial income

finNonRecurring: Non-recurring income

finSecurities: Securities

4. QAEngine (src/qa_engine.py)

Intelligent question answering for business-related queries.

Features:

Natural language questions

Contextual search

Confidence scores

Interactive validation

5. HITLManager (src/hitl_manager.py)

Manages human validation and corrections.

Features:

Interactive extraction validation

Manual correction of values

Adding missing fields

Validation of Q&A responses

6. MemoryManager (src/memory_manager.py)

Manages persistent memory for learning.

Features:

Storing corrections

Q&A history

Searching memory

Usage statistics

7. Config (src/config.py)

Central configuration for the system.

Key Parameters:

LLM model: gpt-4o

Embedding model: text-embedding-3-small

Chunk size: 1000 tokens

Top-K retrieval: 5 documents

Streamlit Interface

The web interface offers 5 main pages:

1. Home

System overview

Component status

Quick documentation

2. Data Extraction

Upload PDF/JSON files

Automatic processing

Extraction of 11 financial fields

HITL interactive validation

Export results to JSON

3. Q&A

Chat interface

RAG semantic search

Confidence score responses

Validation and correction of answers

Learning from corrections

4. Memory Management

View recorded corrections

View recorded Q&A history

Reset memory

Usage statistics

5. Settings

View configuration

LLM model used

RAG and validation settings

System information

Processing Flow
Financial Extraction
Documents (data/)
    ↓
DocumentProcessor (Extraction + chunking)
    ↓
RAGEngine (Vector indexing)
    ↓
FinancialExtractor (Extract 11 fields)
    ↓
Confidence score calculated
    ↓
HITLManager (Validation decision)
    ├─ Score ≥ 0.9: Auto-validation
    ├─ 0.6 ≤ Score < 0.9: Interactive validation
    └─ Score < 0.6: Mandatory validation
    ↓
MemoryManager (Storing corrections)
    ↓
JSON results (outputs/)

Q&A
User question
    ↓
MemoryManager (Search history)
    ↓
QAEngine (Generate answer)
    ├─ RAG search
    ├─ Augmented context
    └─ GPT-4o generation
    ↓
Confidence score
    ↓
HITLManager (Validation if necessary)
    ├─ High confidence: Accept
    └─ Low confidence: Interactive correction
    ↓
Validated answer + sources

Output Format

The extraction results are in a structured JSON format:

{
  "sheet": {
    "finYear": 2024,
    "finSales": 56734000.0,
    "finProfit": 2500000.0,
    "finEquity": 15000000.0,
    ...
  },
  "confidence_score": 0.92,
  "missing_fields": [],
  "additional_information": [
    "Sector: Financial services",
    "Managers: Jean Dupont, Marie Martin"
  ]
}

Configuration
Main Parameters (src/config.py)
# LLM
llm_model = "gpt-4o"
llm_temperature = 0  # Deterministic
llm_max_tokens = 4000

# RAG
chunk_size = 1000
chunk_overlap = 200
top_k_retrieval = 5
embedding_model = "text-embedding-3-small"

# Extraction
confidence_threshold = 0.7
missing_field_threshold = 3

# HITL
auto_validate_above = 0.9
require_validation_below = 0.6
