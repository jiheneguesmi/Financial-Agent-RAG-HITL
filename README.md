# Financial Agent RAG + HITL

An intelligent financial data extraction and analysis agent combining **RAG (Retrieval-Augmented Generation)**, **LLM (Large Language Models)**, and **HITL (Human-In-The-Loop)** for precise extraction with human validation.

## Overview

This agent automates the extraction of financial data from PDF and JSON documents while enabling interactive validation and correction by human users. It learns from corrections to continuously improve its accuracy.

### Key Features

- **Automatic Extraction**: Extraction of 11 key financial fields with confidence scores
- **RAG (Retrieval-Augmented Generation)**: Semantic search across indexed documents
- **LLM GPT-4o**: Generation and analysis using OpenAI's most advanced model
- **HITL Validation**: Interactive interface to correct and validate results
- **Persistent Memory**: Learning from corrections to improve future extractions
- **Intelligent Q&A**: Answer questions about the company based on documents
- **Web Interface**: Modern and intuitive Streamlit interface

  
<img width="1906" height="851" alt="image" src="https://github.com/user-attachments/assets/684bb773-0498-41b2-8993-dfa57ac01647" />
<img width="1884" height="857" alt="image" src="https://github.com/user-attachments/assets/6c61a302-ba89-4e8f-9241-acbfbc95c764" /><img width="1895" height="867" alt="image" src="https://github.com/user-attachments/assets/f9359e3f-cc58-4f47-ae96-e733dcf46742" />
<img width="1905" height="862" alt="image" src="https://github.com/user-attachments/assets/6ae7922c-fbfc-47f5-9b88-5238c2ac5554" />

## Installation

### Prerequisites

- Python 3.11+
- pip or conda
- OpenAI API key (free or paid)

### Installation Steps

1. **Clone the project**:
```bash
git clone https://github.com/jiheneguesmi/Financial-Agent-RAG-HITL.git
cd "agent IA Harington"
```

2. **Create a virtual environment** (optional but recommended):
```bash
python -m venv agent_harington
source agent_harington/bin/activate  # Linux/Mac
# or
agent_harington\Scripts\Activate.ps1  # Windows PowerShell
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure OpenAI API key**:

Create a `.env` file at the project root:
```
OPENAI_API_KEY=sk-proj-your-api-key-here
```

## Main Components

### 1. DocumentProcessor (`src/document_processor.py`)
Processes incoming documents (PDF and JSON) and divides them into chunks.

**Features**:
- Text extraction from PDF with PyPDF2
- JSON file support
- Smart chunking with overlap
- Automatic metadata

### 2. RAGEngine (`src/rag_engine.py`)
Vector search engine and retrieval-augmented generation.

**Features**:
- FAISS document indexing
- OpenAI embeddings `text-embedding-3-small`
- Semantic search
- Context-aware generation
- Index persistence

### 3. FinancialExtractor (`src/extractor.py`)
Structured financial data extraction with confidence scores.

**Extracted Fields**:
- `finYear`: Fiscal year
- `finSales`: Revenue/Sales
- `finProfit`: Net profit
- `finEquity`: Shareholders' equity
- `finCapital`: Share capital
- `finBalanceSheet`: Total assets
- `finAvailableFunds`: Available funds/Cash
- `finOperationInc`: Operating income
- `finFinancialInc`: Financial income
- `finNonRecurring`: Non-recurring income
- `finSecurities`: Securities

### 4. QAEngine (`src/qa_engine.py`)
Intelligent question answering about the company.

**Features**:
- Natural language questions
- Contextual search
- Confidence scores
- Interactive validation

### 5. HITLManager (`src/hitl_manager.py`)
Management of human validation and correction.

**Features**:
- Interactive extraction validation
- Manual value correction
- Missing field addition
- Q&A response validation

### 6. MemoryManager (`src/memory_manager.py`)
Persistent memory management for learning.

**Features**:
- Correction storage
- Q&A history
- Memory search
- Usage statistics

### 7. Config (`src/config.py`)
Centralized system configuration.

**Key Parameters**:
- LLM model: `gpt-4o`
- Embedding model: `text-embedding-3-small`
- Chunk size: 1000 tokens
- Top-K retrieval: 5 documents

## Streamlit Interface

The web interface offers 5 main pages:

### 1. Home
- System overview
- Component status
- Quick documentation

### 2. Data Extraction
- PDF/JSON file upload
- Automatic processing
- 11 financial field extraction
- Interactive HITL validation
- JSON result export

### 3. Question/Answers
- Chat interface
- Semantic search (RAG)
- Confidence-scored responses
- Response validation and correction
- Learning from corrections

### 4. Memory Management
- View stored corrections
- View stored Q&A
- Memory reset
- Usage statistics

### 5. Settings
- Configuration display
- LLM model used
- RAG and validation parameters
- System information

## Processing Flow

### Financial Extraction

```
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
MemoryManager (Store corrections)
    ↓
JSON Results (outputs/)
```

### Question/Answers

```
User question
    ↓
MemoryManager (Search history)
    ↓
QAEngine (Generate response)
    ├─ RAG search
    ├─ Context augmentation
    └─ GPT-4o generation
    ↓
Confidence score
    ↓
HITLManager (Validate if needed)
    ├─ High confidence: Accept
    └─ Low confidence: Interactive correction
    ↓
Validated response + sources
```

## Output Format

Extraction results are in structured JSON format

## Configuration

### Main Parameters (`src/config.py`)

```python
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
```

### .env File

```env
# OpenAI API key (required)
OPENAI_API_KEY=sk-proj-...

# Optional configuration
LOG_LEVEL=INFO
DEBUG=false
```

## Main Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| langchain | 0.1.0+ | LLM Framework |
| langchain-openai | 0.1.1+ | OpenAI Integration |
| openai | 1.12.0+ | OpenAI API |
| streamlit | 1.30.0+ | Web interface |
| faiss-cpu | 1.7.4+ | Vector indexing |
| pypdf | 4.0.1+ | PDF reading |
| pydantic | 2.5.3+ | Validation |
| python-dotenv | 1.0.0 | Environment variables |

See `requirements.txt` for complete list.


## Continuous Improvement

### Agent Learning

The agent learns from human corrections:

1. Each correction is recorded
2. During future extractions, corrections are used
3. Agent progressively improves accuracy

### Memory Files

- `memory/extraction_corrections.json` - Extraction corrections
- `memory/qa_corrections.json` - Q&A corrections
- `memory/manual_context.json` - Manually added context

## Roadmap

### Short Term
- [ ] Excel/CSV support
- [ ] Data visualization
- [ ] PDF export
- [ ] Dashboards

### Medium Term
- [ ] REST API (FastAPI)
- [ ] Multi-language support
- [ ] Model fine-tuning
- [ ] Complex table extraction

### Long Term
- [ ] Support other LLMs (Anthropic, Llama)
- [ ] ERP integration
- [ ] Anomaly detection
- [ ] Financial predictions

## Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Acknowledgments

- OpenAI for GPT-4o and embeddings
- LangChain for RAG architecture
- Streamlit for web interface
- Facebook Research for FAISS

## Changelog

### Version 1.0 
-  Complete extraction of 11 financial fields
-  RAG system with FAISS
-  Interactive HITL validation
-  Streamlit interface
-  Persistent memory
-  Intelligent Q&A
-  Complete documentation
-  Removal of all emojis

## Project Status

**Status**: Production Ready 

-  Extraction functional
-  RAG operational
-  HITL integrated
- Complete web interface
-  Exhaustive documentation
   Tests validated
-  Ready for deployment

---

