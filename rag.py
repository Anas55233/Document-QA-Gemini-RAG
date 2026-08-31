import os
# import libraries
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


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
    
    # Step 1: Retrieve candidate chunks from FAISS
    results = vector_store.similarity_search_with_score(
        question, 
        k = k
    )
    return results



# Define a function to create context:

# def create_context(results):
#     context = ""
#     for result, score in results:
#         context += result.page_content + "\n\n"
#     return context


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
        model="gemini-3.5-flash",
        google_api_key=gemini_api_key
    )
    
    return model



# define funtion of answer_quetion():

def answer_question(question, chat_history="", vector_store = None):
    
    if vector_store is None:
        vector_store = load_vector_store()
        
    model = create_gemini_model()
    
    # exact_search(vector_store, "13 Dec 2025")
    results = retrieve_documents(vector_store, question)
        
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





