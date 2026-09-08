# 📄 Document Q&A — Gemini RAG Assistant

An AI-powered **Document Question Answering application** built with **Streamlit, LangChain, Google Gemini, FAISS, Hugging Face Embeddings, and Hybrid Search**.

The application allows users to upload documents and ask questions about their content. It combines **semantic vector search and keyword-based retrieval** to find relevant information before sending the retrieved context to Google Gemini for answer generation.

The project is designed as a practical **Retrieval-Augmented Generation (RAG)** application for working with documents and structured data.

---

## 🚀 Features

* 📄 Upload and process documents
* 📚 Support for multiple documents
* 💬 Interactive AI question-answering chatbot
* 🤖 Google Gemini-powered responses
* 🧠 Retrieval-Augmented Generation (RAG)
* 🔍 Semantic similarity search using FAISS
* 🔑 Keyword-based retrieval using BM25
* 🔀 Hybrid Search combining semantic and keyword retrieval
* 📑 PDF and DOCX document support
* 📊 Excel data extraction and generation
* 🗂️ Conversation-aware question answering
* 📌 Retrieves relevant document context before generating answers
* 🔐 API keys stored securely using Streamlit secrets
* 🌐 Streamlit-based user interface

---

## 🧠 Hybrid Search

This project uses **Hybrid Search** to improve document retrieval.

Instead of relying only on semantic similarity, the application combines two retrieval approaches:

### 1. Semantic Search

FAISS searches for document chunks based on their **meaning and semantic similarity**.

```text
User Question
      ↓
Hugging Face Embedding
      ↓
FAISS Similarity Search
      ↓
Relevant Documents
```

### 2. Keyword Search

BM25 searches for documents based on **important words and exact keyword matches**.

```text
User Question
      ↓
BM25 Keyword Search
      ↓
Relevant Documents
```

### 3. Combined Retrieval

The results from both approaches are combined to provide better context to Gemini.

```text
                 User Question
                       ↓
             ┌─────────┴─────────┐
             ↓                   ↓
       Semantic Search       BM25 Search
           (FAISS)            (Keywords)
             ↓                   ↓
             └─────────┬─────────┘
                       ↓
                Combined Results
                       ↓
                Relevant Context
                       ↓
                 Google Gemini
                       ↓
                  Final Answer
```

This approach helps the application handle both **concept-based questions and exact keyword-based questions**.

---

## 🏗️ Project Architecture

```text
                  User
                   ↓
             Upload Documents
                   ↓
             Document Loaders
                   ↓
              Text Splitting
                   ↓
          Hugging Face Embeddings
                   ↓
              FAISS Vector Store
                   │
                   │
                   ├───────────────┐
                   │               │
                   ↓               ↓
             Semantic Search    BM25 Search
                   │               │
                   └───────┬───────┘
                           ↓
                    Hybrid Retrieval
                           ↓
                   Relevant Context
                           ↓
                    Google Gemini
                           ↓
                     Final Answer
```

For Excel-related requests, the application can process structured spreadsheet information separately and provide the requested Excel output.

---

## 🛠️ Technologies Used

| Technology        | Purpose                                |
| ----------------- | -------------------------------------- |
| **Python**        | Core programming language              |
| **Streamlit**     | Web application interface              |
| **LangChain**     | LLM and RAG framework                  |
| **Google Gemini** | AI answer generation                   |
| **FAISS**         | Vector similarity search               |
| **Hugging Face**  | Text embeddings                        |
| **BM25**          | Keyword-based retrieval                |
| **PyPDF**         | PDF document processing                |
| **DOCX Loader**   | Microsoft Word document processing     |
| **Pandas**        | Structured data and Excel processing   |
| **OpenPyXL**      | Excel file generation and manipulation |

---

## 📁 Project Structure

```text
Document Gemini/
│
├── app.py
├── rag.py
├── ingest.py
├── excel_structure.py
│
├── documents/
│   └── Your documents
│
├── faiss_index/
│   ├── index.faiss
│   └── index.pkl
│
├── .streamlit/
│   └── config.toml
│
├── .gitignore
├── requirements.txt
├── styles.css
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Anas55233/Document-QA-Gemini-RAG.git
```

### 2. Enter the project directory

```bash
cd Document-QA-Gemini-RAG
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment on Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Setup

This project uses **Google Gemini** for AI-generated responses.

Create the following file locally:

```text
.streamlit/secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

### 🔐 Security

**Never upload your real API key to GitHub.**

The project uses `.gitignore` to prevent secret files from being committed.

Example:

```text
.streamlit/secrets.toml
```

Your API key should remain local and should never be hard-coded inside Python source files.

---

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📚 Supported Documents

The application is designed to work with documents such as:

* PDF
* DOCX
* Multiple uploaded documents

The retrieval pipeline processes the uploaded content and creates searchable document chunks.

---

## 📊 Excel Support

The application also includes functionality for working with structured Excel data.

Users can ask questions related to spreadsheet information and request Excel output when appropriate.

The Excel workflow is designed to separate **document retrieval** from **structured spreadsheet processing**, allowing the assistant to handle both unstructured documents and structured data.

---

## 🧠 How the RAG Pipeline Works

### Step 1 — Document Upload

The user uploads one or more supported documents.

### Step 2 — Document Processing

The application loads the documents and extracts their text.

### Step 3 — Text Splitting

Large documents are divided into smaller chunks so they can be efficiently searched.

### Step 4 — Embeddings

Hugging Face sentence-transformer embeddings convert document chunks into numerical vectors.

### Step 5 — FAISS Indexing

The vectors are stored in FAISS for fast semantic similarity search.

### Step 6 — BM25 Indexing

The document chunks are also indexed using BM25 for keyword-based retrieval.

### Step 7 — Hybrid Retrieval

When the user asks a question, both FAISS and BM25 retrieve relevant information.

### Step 8 — Context Creation

The retrieved document chunks are combined into context for the language model.

### Step 9 — Gemini Response

Google Gemini receives the relevant context and generates the final answer.

```text
Documents
    ↓
Load
    ↓
Split
    ↓
Embeddings ─────→ FAISS
    │
    └────────────→ BM25
                     ↓
                User Question
                     ↓
             Hybrid Retrieval
                     ↓
              Relevant Context
                     ↓
               Google Gemini
                     ↓
                Final Answer
```

---

## 🎯 Project Goal

The goal of this project is to demonstrate how **Retrieval-Augmented Generation can be used to build a practical AI document assistant**.

The project combines:

* Large Language Models
* Document processing
* Text embeddings
* Vector databases
* Keyword retrieval
* Hybrid search
* Conversation memory
* Structured data processing
* Excel generation
* Streamlit application development

into a single AI-powered application.

---

## 🔮 Future Improvements

Possible future improvements include:

* 🔎 Advanced reranking of retrieved documents
* 📌 Page-level source citations
* 📄 More document formats
* 🗂️ Better multi-document management
* 🧠 Improved conversation memory
* ⚡ Retrieval performance optimization
* 🌐 Online deployment
* 👥 User authentication
* 📊 Advanced Excel analysis
* 🤖 More specialized AI agents
* 📈 Retrieval evaluation and benchmarking

---

## 👨‍💻 Author

**Anas Sohail**

AI / Machine Learning Learner

GitHub:
https://github.com/Anas55233

---

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.
