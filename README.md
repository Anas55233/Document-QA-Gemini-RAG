# 📄 Document Q&A — Gemini RAG Chatbot

An AI-powered **Document Question Answering application** built with **Streamlit, LangChain, FAISS, Hugging Face embeddings, and Google Gemini**.

The application allows users to work with documents and ask questions about their content. It uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant document information and provide context-aware answers using Gemini.

## 🚀 Features

* 📄 Document upload and processing
* 💬 Interactive question-answer chatbot
* 🤖 Google Gemini for AI-generated responses
* 🔍 Semantic similarity search
* 🧠 Retrieval-Augmented Generation (RAG)
* 📚 Hugging Face sentence-transformer embeddings
* ⚡ FAISS vector database
* 📑 Supports PDF and DOCX documents
* 🗂️ Conversation-aware question answering
* 📌 Retrieves relevant document context before generating answers

## 🏗️ Project Architecture

```text
Document
   ↓
Document Loader
   ↓
Text Splitting
   ↓
Hugging Face Embeddings
   ↓
FAISS Vector Database
   ↓
User Question
   ↓
Similarity Search
   ↓
Relevant Document Chunks
   ↓
Google Gemini
   ↓
Final Answer
```

## 🛠️ Technologies Used

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| Python        | Programming language      |
| Streamlit     | Web application interface |
| LangChain     | RAG and LLM framework     |
| Google Gemini | Answer generation         |
| FAISS         | Vector similarity search  |
| Hugging Face  | Text embeddings           |
| PyPDF         | PDF processing            |
| DOCX Loader   | Word document processing  |

## 📁 Project Structure

```text
Document GPT/
│
├── app.py
├── rag.py
├── ingest.py
├── final_rag.py
├── extra_code.py
├── test_gemini.py
│
├── documents/
│   ├── Visa Purpose.pdf
│   └── Visa Purpose.docx
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

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Anas55233/Document-QA-Gemini-RAG.git
```

Go to the project directory:

```bash
cd Document-QA-Gemini-RAG
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## 🔑 API Key Setup

This project uses Google Gemini.

Create a Streamlit secrets file locally:

```text
.streamlit/secrets.toml
```

Add your API key:

```toml
GEMINI_API_KEY = "your-api-key-here"
```

**Never upload your real API key to GitHub.**

The `.gitignore` file excludes the secrets file from Git.

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

## 🧠 How RAG Works in This Project

The application follows these main steps:

1. **Load documents** — PDF and DOCX files are loaded.
2. **Split text** — Large documents are divided into smaller chunks.
3. **Create embeddings** — Hugging Face converts text chunks into numerical vectors.
4. **Store vectors** — FAISS stores the embeddings for fast similarity search.
5. **Receive question** — The user asks a question about the document.
6. **Retrieve context** — FAISS finds the most relevant document chunks.
7. **Generate answer** — Gemini uses the retrieved context to generate the final response.

## 🎯 Project Goal

The goal of this project is to demonstrate how **Retrieval-Augmented Generation (RAG)** can be used to build an AI assistant capable of answering questions from user-provided documents.

It also demonstrates practical integration of **LLMs, embeddings, vector databases, document processing, and Streamlit** into a complete AI application.

## 🔮 Future Improvements

* Support more document formats
* Improve retrieval accuracy
* Add source citations and page references
* Add document-level filtering
* Improve conversation memory
* Add multiple document collections
* Deploy the application online
* Add advanced retrieval and reranking

## 👨‍💻 Author

**Anas Sohail**

AI / Machine Learning Learner

GitHub: [Anas55233](https://github.com/Anas55233)
