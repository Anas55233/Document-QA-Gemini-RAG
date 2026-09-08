# --------------------------------
# Import Libraries
# --------------------------------
from rag import (
    answer_question, get_all_chunks, build_bm25_index, hybrid_search,create_context)

import streamlit as st
from PyPDF2 import PdfReader
import docx
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from io import BytesIO
from pathlib import Path
import re
import pandas as pd
from excel_structure import check_excel_possible, create_excel
 


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Document Gemini",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# # --------------------------------
# # Load CSS
# # --------------------------------

# make sure the CSS file is in the same directory as this script
css_file = Path(__file__).parent / "styles.css"

# load the CSS file if it exists
if css_file.exists():
    
# load the CSS file contents
    with open(css_file, "r", encoding="utf-8") as f:
        css = f.read()

# apply the CSS to the Streamlit app      
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
    
# Store uploaded document data
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
   
# Store the BM25 index of the current document
if "bm25_index" not in st.session_state:
    st.session_state.bm25_index = None

# Store all chunks of the current document
if "all_chunks" not in st.session_state:
    st.session_state.all_chunks = None

# Store all uploaded documents
if "all_documents" not in st.session_state:
    st.session_state.all_documents = []
  
 # Store the uploaded Excel file   
if "excel_file" not in st.session_state:
    st.session_state.excel_file = None
    

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

# Show welcome message if no messages have been exchanged yet
if not st.session_state.messages:
    
    st.markdown("## 👋 Welcome!")

    st.caption(
        "I can help you understand your uploaded document. "
        "Ask questions, find specific information, "
        "or summarize content."
    )
# create three columns for the main features
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

# Sidebar for document upload
with st.sidebar:

# header for the sidebar
    st.markdown("## 📤 Upload Document")
# caption for the sidebar
    st.caption(
        "Upload a PDF, DOCX, or CSV file to get started."
    )
# file uploader for PDF, DOCX, and CSV files
    uploaded_files= st.file_uploader(
        "Choose one or more documents",
        type=["pdf", "docx", "csv"],
        label_visibility = "visible",
        accept_multiple_files=True
    )
#  Show uploaded files
    if uploaded_files:
        st.markdown("### 📄 Uploaded Documents")
        for f in uploaded_files: st.info(f"**{f.name}** ({f.size / 1024:.1f} KB)")

        new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_files]


        if new_files: 
            st.write(f"Processing {len(new_files)} new file(s)...")
            # extraction/chunking/FAISS code will go HERE in the next step
            
            documents = []
            for uploaded_file in new_files:
                file_data = uploaded_file.getvalue()
                
                if uploaded_file.name.endswith(".pdf"):
                    reader = PdfReader(BytesIO(file_data))
                    for page_number, page in enumerate(reader.pages, start=1):
                        documents.append(Document(page_content=page.extract_text() or "",
                                metadata={"source": uploaded_file.name,"page": page_number}))
                        
                elif uploaded_file.name.endswith(".docx"):
                    doc = docx.Document(BytesIO(file_data))
                    text = "\n".join(para.text for para in doc.paragraphs)
                    documents.append( Document(page_content=text,
                                 metadata={"source": uploaded_file.name } ) )
                
                elif uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(BytesIO(file_data))
                    documents.append( Document(page_content=df.to_string(index=False),
                            metadata={ "source": uploaded_file.name } ) )
                    
            st.success("Text extracted successfully!")
            all_documents = st.session_state.all_documents
            all_documents.extend(documents)
             
            # --------------------------------
            # Split all documents into chunks
            # --------------------------------
            text_splitter = RecursiveCharacterTextSplitter( chunk_size=2000, chunk_overlap=400)
            chunks = text_splitter.split_documents(all_documents)
            st.success(f"{len(all_documents)} document sections created "
                       f"and {len(chunks)} chunks created.")

           # --------------------------------
           ## Create Embeddings and FAISS Vector Store
           # --------------------------------
            vector_store = FAISS.from_documents(chunks,
            embedding= HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
            
            # --------------------------------
            # Store in Session State
            #-------------------------------
            st.session_state.vector_store = vector_store
            
            # --------------------------------
            # Build BM25 Index
            # --------------------------------
            all_chunks = get_all_chunks(vector_store)
            bm25_index = build_bm25_index(all_chunks)
            st.session_state.all_chunks, st.session_state.bm25_index = all_chunks, bm25_index
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
    
            excel_file = message.get("excel_file")
            if excel_file:
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_file,
                    file_name="document_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

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
    
    excel_keywords = [
        "excel",
        "spreadsheet",
        "export to excel",
        "download as excel",
        "excel sheet",
        "create an excel",
        "make an excel",
        "give me an excel"
    ]

    is_excel_request = any(
        word in question.lower()
        for word in excel_keywords
    )

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
        role = message.get("role")
        content = message.get("content", "")
        
        if not content:
            continue  # Skip messages with empty content
        if message.get("excel_file"):
            continue  # Skip messages with Excel files
        
        chat_history += f"{role}: {content}\n"
        
        
        

# ================================= 
# EXCEL
# =================================

    if is_excel_request:

        with st.spinner("🔎 Checking document for Excel data..."):

            # Search document
            hybrid_results = hybrid_search(
                st.session_state.vector_store,
                st.session_state.bm25_index,
                st.session_state.all_chunks,
                question,
                k=10
            )
            # Create context
            results = [(doc, 0) for doc in hybrid_results]
            context = create_context(results)

# Check if Excel is actually possible
            excel_possible = check_excel_possible(question, context)
        # --------------------------------
        # Excel IS possible
        # --------------------------------

        if excel_possible:
            with st.spinner("📊 Creating Excel sheet..."):
                excel_file = create_excel(question, context, chat_history)
        # Show ONLY Excel
            with st.chat_message("assistant"):
                if excel_file:
                    st.success("📊 Your Excel sheet is ready!")
                    st.download_button(
                        "📥 Download Excel",
                        excel_file,
                        "document_data.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    # Save assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "📊 Your Excel sheet is ready!",
                        "excel_file": excel_file
                    })

                else:
                    st.warning( "I couldn't find suitable data in the document " "to create an Excel sheet." )
                    # Normal answer as fallback
                    response = answer_question(
                        question,
                        chat_history,
                        st.session_state.vector_store,
                        st.session_state.bm25_index,
                        st.session_state.all_chunks
                    )
                    st.write(response["answer"])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", [])
                    })
    # =================================
    # NORMAL QUESTION
    # =================================
    else:
        
        with st.spinner("📂 Generating answer..."):
            response = answer_question(
                 question,
                 chat_history,
                 st.session_state.vector_store,
                 st.session_state.bm25_index,
                 st.session_state.all_chunks
             )
        with st.chat_message("assistant"):
            st.write(response["answer"])
             
            if response.get("sources"):
                with st.expander("📚 See sources"):
                    for source in response["sources"]:
                        st.write(source)
         # Save answer
        st.session_state.messages.append({
             "role": "assistant",
             "content": response["answer"],
             "sources": response.get("sources", [])
         })

    # Refresh
    st.rerun()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

    # # --------------------------------
    # # Step 18: Ask RAG System
    # # --------------------------------
    
    # if st.session_state.first_question_for_file:
    
    #     # First question for the newly uploaded document
    #     with st.spinner(
    #         "📄 New document generating answer..."
    #     ):

    #         response = answer_question(
    #             question,
    #             chat_history,
    #             st.session_state.vector_store,
    #             st.session_state.bm25_index,
    #             st.session_state.all_chunks
    #         )
            
    #         # excel_file = markdown_table_to_excel(response["answer"])
    #         excel_keywords = ["excel", "spreadsheet", "sheet", "table"]

    #         if any(word in question.lower() for word in excel_keywords):

    #             excel_file = markdown_table_to_excel(response["answer"])

    #         else:

    #             excel_file = None
            
            

    #     # First question is now completed
    #     st.session_state.first_question_for_file = False

    # else:

    #     # Questions for the already processed document
        
    #     with st.spinner("📂 Uploaded document generating answer..."):
        
    #         response = answer_question(
    #             question,
    #             chat_history,
    #             st.session_state.vector_store,
    #             st.session_state.bm25_index,
    #             st.session_state.all_chunks
    #         )
            
    #         # excel_file = markdown_table_to_excel(response["answer"])
    #         excel_keywords = ["excel", "spreadsheet", "sheet", "table"]

    #         if any(word in question.lower() for word in excel_keywords):

    #             excel_file = markdown_table_to_excel(response["answer"])

    #         else:

    #             excel_file = None
            

    #     # --------------------------------
    #     # Step 19: Save Assistant Answer
    #     # --------------------------------

    # st.session_state.messages.append(
    #     {
    #         "role": "assistant",
    #         "content": response["answer"],
    #         "sources": response.get("sources", []),
    #         "excel_file": excel_file
    #     }
    # )


    #     # --------------------------------
    #     # Step 20: Display Assistant Answer
    #     # --------------------------------

    # with st.chat_message("assistant"):

    #     if is_excel_request:
    
    #         st.success("📊 Your Excel sheet is ready!")

    #         if excel_file:
    #             st.download_button(
    #                 label="📥 Download Excel",
    #                 data=excel_file,
    #                 file_name="document_data.xlsx",
    #                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #             )

    #     else:

    #         st.write(response["answer"])

    #         sources = response.get("sources", [])

    #         if sources:

    #             with st.expander("📚 See sources"):

    #                 for source in sources:
    #                     st.write(source)

    #     # --------------------------------
    #     # Step 21: Refresh UI
    #     # --------------------------------

    # st.rerun()




