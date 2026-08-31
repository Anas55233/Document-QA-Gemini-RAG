from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("documents/Visa Purpose.pdf")

pdf_documents = loader.load()

from langchain_community.document_loaders import Docx2txtLoader

docx_loader = Docx2txtLoader("documents/Visa Purpose.docx")
docx_documents = docx_loader.load()

print("PDF documents:", len(pdf_documents))
print("DOCX documents:", len(docx_documents))

documents = pdf_documents + docx_documents

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400
)

chunks = text_splitter.split_documents(documents)


# 2. Create the embedding model
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 3. Convert documents into embeddings and store them in FAISS
from langchain_community.vectorstores import FAISS

vector_store = FAISS.from_documents(
    chunks,
    embedding=embeddings
)


# # -----------------------------
# # 4. PDF content
# # -----------------------------

# print("\n========== PDF ==========")

# print("\nPDF text:")
# print(pdf_documents[0].page_content)

# print("\nPDF metadata:")
# print(pdf_documents[0].metadata)


# # -----------------------------
# # 5. DOCX content
# # -----------------------------

# print("\n========== DOCX ==========")

# print("\nDOCX text:")
# print(docx_documents[0].page_content)

# print("\nDOCX metadata:")
# print(docx_documents[0].metadata)

    
vector_store.save_local("faiss_index")

print("\nFAISS vector store created successfully!")

# -----------------------------
# 9. Search the vector store
# -----------------------------

question = "Which country does the person want to visit?"

results = vector_store.similarity_search(
    question,
    k=3
)


# -----------------------------
# 10. Display search results
# -----------------------------

print("\n========== SEARCH RESULTS ==========")

for i, document in enumerate(results, start=1):

    print(f"\n--- Result {i} ---")

    print("Text:")
    print(document.page_content)

    print("\nMetadata:")
    print(document.metadata)