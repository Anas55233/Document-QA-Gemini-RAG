import os
# import libraries
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from openpyxl import Workbook
# =========================================================
# Add this near the top of rag.py, with your other imports
# =========================================================
from rank_bm25 import BM25Okapi
import pandas as pd
from io import BytesIO


# load environment variables
load_dotenv()

# define function to create embeddings
@st.cache_resource
def create_embeddings():
    embeddings = HuggingFaceEmbeddings( 
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return embeddings

# function to load the vector store
@st.cache_resource
def load_vector_store():
    embeddings = create_embeddings()
    vector_store = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store

# Define a function to rag search
def retrieve_documents(vector_store, question, k = 15):
    results = vector_store.similarity_search_with_score(        # Step 1: Retrieve candidate chunks from FAISS
        question, 
        k = k
    )
    return results


import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # remove punctuation
    return text.split()



# =========================================================
# Add these 3 functions anywhere in rag.py
# (below your existing retrieve_documents function is a good spot)
# =========================================================

def get_all_chunks(vector_store):
    """
    Pulls every chunk that's already stored inside your FAISS
    vector store, as a plain list. We reuse the same chunks —
    no new data is created here.
    """
    return list(vector_store.docstore._dict.values())


def build_bm25_index(all_docs):
    """
    Builds a keyword-search index (BM25) from your chunks.
    BM25 needs each chunk broken into individual words (tokens),
    so it can later score chunks based on exact word matches.
    """
    tokenized = [clean_text(doc.page_content) for doc in all_docs]
    bm25 = BM25Okapi(tokenized)
    return bm25


def bm25_search(bm25, all_docs, question, k=5):
    """
    Searches for chunks that share the most exact words with
    the question. Returns the top k chunks, best match first.
    """
    query_words = clean_text(question)
    scores = bm25.get_scores(query_words)
    # Pair each chunk with its score
    pairs = list(zip(all_docs, scores))
    # Best (highest score) first
    pairs.sort(key=lambda pair: pair[1], reverse=True)
    return pairs[:k]


def hybrid_search(vector_store, bm25, all_docs, question, k=10):
    # Search 1: by meaning (your existing FAISS search)
    vector_results = vector_store.similarity_search(question, k=k)
    # Search 2: by exact keywords (BM25)
    bm25_results = bm25_search(bm25, all_docs, question, k=k)
    bm25_docs = [doc for doc, score in bm25_results]
    # Combine both lists together
    combined = vector_results + bm25_docs
    # Remove exact duplicates, but keep chunks that appeared in both
    # (this naturally ranks doubly-found chunks higher when we count them)
    seen = {}
    for doc in combined:
        key = doc.page_content  # use the text itself to detect duplicates
        if key in seen:
            seen[key] = (doc, seen[key][1] + 1)  # count how many times found
        else:
            seen[key] = (doc, 1)

    # Sort by how many times each chunk was found (2 = found by both methods)
    ranked = sorted(seen.values(), key=lambda pair: pair[1], reverse=True)

    # Return just the documents, best first
    return [doc for doc, count in ranked]



def create_context(results):
    context = ""
    for result, score in results:
        source = result.metadata.get("source", "Unknown")
        page = result.metadata.get("page", "Unknown")
        context += (
            f"[SOURCE: {source} | PAGE: {page}]\n"
            f"{result.page_content}\n\n"
        )
    return context


# define funtion to ask gemini:
def ask_gemini(model, question, context, chat_history):
    prompt = f"""
    You are a helpful Document GPT assistant.
    Your job is to answer the user's question using the
    provided document context and conversation history.

    IMPORTANT RULES:
    1. Use the document context as the primary and most reliable
    source of information.
    2. Answer the question only from information supported by
    the provided document context.
    3. Do not assume that information exists in the document
    just because the user expects an answer.
    4. If the answer cannot be found or reasonably determined
    from the document context, say:
    "I don't know based on the provided document."
    5. Do not make up, invent, or hallucinate information.
    6. If the question requires combining or calculating
    information from multiple parts of the context, do so
    carefully using only the provided information.
    7. If the user asks about a specific date, name, number,
    amount, section, paragraph, or other exact information,
    pay close attention to exact matches in the context.
    8. Use conversation history only to understand follow-up
    questions and references such as "he", "she", "they",
    "it", "this", "that", or "the previous one".
    9. Do not use conversation history as a replacement for
    missing document information.
    10. If the document context conflicts with conversation
        history, prefer the document context.

    Chat History:
    {chat_history}
    
    Document Context:
    {context}

    User Question:
    {question}

    Helpful Answer:
    """

    
    try:
        response = model.invoke(prompt)
        return response.content[0]["text"]

    except Exception as e:
        error_message = str(e)
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return "⚠️ Gemini API quota exceeded. Please try again later or use another API key/model."
        elif "401" in error_message or "403" in error_message:
            return "❌ Gemini API authentication/permission error. Please check your API key."
        else:
            return f"❌ Gemini API error: {error_message}"

# define a function to create gemini model with api key
def create_gemini_model():
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable")
    model = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=gemini_api_key,
        timeout = 60
    )
    return model


    
# define funtion of answer_quetion():
def answer_question(question, chat_history="", vector_store = None, bm25=None, all_chunks=None):
    if vector_store is None:
        vector_store = load_vector_store()
    model = create_gemini_model()
    
    # results = retrieve_documents(vector_store, question) 

    hybrid_results = hybrid_search(vector_store, bm25, all_chunks, question, k=10)

    # create_context expects (doc, score) pairs, so we fake a score of 0 here
    results = [(doc, 0) for doc in hybrid_results]
    
    
    context = create_context(results)
    answer = ask_gemini(model, question, context, chat_history)
    
    sources = []
    for result, score in results:
        source = result.metadata.get("source")
        page = result.metadata.get("page")
        if source:
            if page:
                citation = f"{source} — Page {page}"
            else:
                citation = source
            if citation not in sources:
                sources.append(citation)
    # return answer, results
    return {
    "answer": answer,
    "sources": sources,
    "documents": results
}



