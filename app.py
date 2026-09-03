# --------------------------------
# Import Libraries
# --------------------------------

import streamlit as st
from rag import answer_question, get_all_chunks, build_bm25_index
from PyPDF2 import PdfReader
import docx
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from io import BytesIO
from pathlib import Path
import re


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Document GPT",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # --------------------------------
# # Load CSS
# # --------------------------------

css_file = Path(__file__).parent / "styles.css"

if css_file.exists():
    
    with open(css_file, "r", encoding="utf-8") as f:
        css = f.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )

# --------------------------------
# Session State
# --------------------------------

# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store FAISS vector store of the current document
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# prevent re-processing the same document multiple times
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Track whether the current file is receiving its first question
if "first_question_for_file" not in st.session_state:
    st.session_state.first_question_for_file = True
    
# Store uploaded document data
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

# Store the summary of the current document
if "document_summary" not in st.session_state:
    st.session_state.document_summary = ""
   
# Store the BM25 index of the current document
if "bm25_index" not in st.session_state:
    st.session_state.bm25_index = None

# Store all chunks of the current document
if "all_chunks" not in st.session_state:
    st.session_state.all_chunks = None

# Store all uploaded documents
if "all_documents" not in st.session_state:
    st.session_state.all_documents = []
    

# --------------------------------
# App Header
# --------------------------------

st.title("📄 DocumentIQ")
st.markdown("### Your intelligent document assistant")
st.caption("Upload a document and ask questions about its contents.")
st.divider()



# --------------------------------
# Step 3: Main Welcome Section
# --------------------------------

if not st.session_state.messages:
    
    st.markdown("## 👋 Welcome!")

    st.caption(
        "I can help you understand your uploaded document. "
        "Ask questions, find specific information, "
        "or summarize content."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📖 Ask")
        st.caption(
            "Ask questions about your document."
        )

    with col2:
        st.markdown("### 🔎 Find")
        st.caption(
            "Find specific information quickly."
        )

    with col3:
        st.markdown("### 🧠 Understand")
        st.caption(
            "Get clear answers from your document."
        )

    st.info(
        "📤 Upload a document from the sidebar to get started."
    )

# --------------------------------
# Step 5: Document Upload
# --------------------------------

with st.sidebar:

    st.markdown("## 📤 Upload Document")

    st.caption(
        "Upload a PDF, DOCX, or CSV file to get started."
    )

    uploaded_files= st.file_uploader(
        "Choose one or more documents",
        type=["pdf", "docx", "csv"],
        label_visibility = "visible",
        accept_multiple_files=True
    )

  
    
    if uploaded_files:
        st.markdown("### 📄 Uploaded Documents")
        for f in uploaded_files:
            st.info(f"**{f.name}** ({f.size / 1024:.1f} KB)")

        new_files = [
            f for f in uploaded_files
            if f.name not in st.session_state.processed_files
        ]

        if new_files:
            st.write(f"Processing {len(new_files)} new file(s)...")
            # extraction/chunking/FAISS code will go HERE in the next step
            
            documents = []
            
            for uploaded_file in new_files:
                file_data = uploaded_file.getvalue()
                
                if uploaded_file.name.endswith(".pdf"):

                    reader = PdfReader(BytesIO(file_data))

                    for page_number, page in enumerate(reader.pages, start=1):

                        page_text = page.extract_text() or ""

                        documents.append(
                            Document(
                                page_content=page_text,
                                metadata={
                                    "source": uploaded_file.name,
                                    "page": page_number
                                }
                            )
                        )
                        
                elif uploaded_file.name.endswith(".docx"):
    
                    doc = docx.Document(BytesIO(file_data))

                    text = ""

                    for para in doc.paragraphs:
                        text += para.text + "\n"

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": uploaded_file.name
                            }
                        )
                    )
                
                elif uploaded_file.name.endswith(".csv"):
                    import pandas as pd

                    df = pd.read_csv(BytesIO(file_data))
                    text = df.to_string(index=False)

                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": uploaded_file.name
                            }
                        )
                    )
                    
            st.success("Text extracted successfully!")
            st.session_state.all_documents.extend(documents)
            
            
            # --------------------------------
            # Split all documents into chunks
            # --------------------------------

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=400
            )
            
            chunks = text_splitter.split_documents(
                st.session_state.all_documents
            )
            
            st.success(
                f"{len(st.session_state.all_documents)} document sections created "
                f"and {len(chunks)} chunks created."
            )

           # --------------------------------
           ## Create Embeddings
           # --------------------------------
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
            
            # --------------------------------
            # Create FAISS Vector Store
            # --------------------------------
            
            vector_store = FAISS.from_documents(
                chunks,
                embedding=embeddings
            )
            
            # --------------------------------
            # Store in Session State
            #-------------------------------
            st.session_state.vector_store = vector_store
            
            # --------------------------------
            # Build BM25 Index
            # --------------------------------
            st.session_state.all_chunks = get_all_chunks(vector_store)
            st.session_state.bm25_index = build_bm25_index(st.session_state.all_chunks)
            st.success("Document hybrid search initialized successfully!")
            
            # --------------------------------
            # Mark files as processed
            # --------------------------------
            for uploaded_file in new_files:
                st.session_state.processed_files.add(uploaded_file.name)
                st.success("🟢 Document ready")

                        
# --------------------------------
# Step 13: Display Chat History
# --------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])

        # Display sources for assistant messages
        if message["role"] == "assistant":

            sources = message.get("sources", [])

            if sources:
                with st.expander("📚 See sources"):

                    for source in sources:
                        st.write(source)                       
              
# --------------------------------
# Step 14: Chat Input
# --------------------------------

question = st.chat_input(
    "Ask a question about your document..."
)


# --------------------------------
# Step 15: Check Vector Store
# --------------------------------

if question:

    if st.session_state.vector_store is None:

        st.warning(
            "Please upload and process a document first."
        )

        st.stop()
        
        
    # --------------------------------
    # Step 16: Save User Message
    # --------------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )
    
    # Display user's question immediately
    with st.chat_message("user"):
        st.write(question)

    # --------------------------------
    # Step 17: Prepare Chat History
    # --------------------------------
    
    chat_history = ""

    # Use previous messages only
    for message in st.session_state.messages[:-1]:

        chat_history += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    # --------------------------------
    # Step 18: Ask RAG System
    # --------------------------------
    
    if st.session_state.first_question_for_file:
    
        # First question for the newly uploaded document
        with st.spinner(
            "📄 New document generating answer..."
        ):

            response = answer_question(
                question,
                chat_history,
                st.session_state.vector_store,
                st.session_state.bm25_index,
                st.session_state.all_chunks
            )

        # First question is now completed
        st.session_state.first_question_for_file = False

    else:

        # Questions for the already processed document
        
        with st.spinner("📂 Uploaded document generating answer..."):
        
            response = answer_question(
                question,
                chat_history,
                st.session_state.vector_store,
                st.session_state.bm25_index,
                st.session_state.all_chunks
            )

        # --------------------------------
        # Step 19: Save Assistant Answer
        # --------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response["answer"],
            "sources": response.get("sources", [])
        }
    )


        # --------------------------------
        # Step 20: Display Assistant Answer
        # --------------------------------

    with st.chat_message("assistant"):

            st.write(response["answer"])

            sources = response.get("sources", [])

            if sources:

                with st.expander("📚 See sources"):

                    for source in sources:
                        st.write(source)

        # --------------------------------
        # Step 21: Refresh UI
        # --------------------------------

    st.rerun()




