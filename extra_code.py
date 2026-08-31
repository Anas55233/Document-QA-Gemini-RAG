# print(f"\nBEFORE DUPLICATE REMOVAL: {len(results)}")

    # for i, (doc, score) in enumerate(results):
    #     print(f"\n--- RESULT {i+1} ---")
    #     print("SCORE:", score)
    #     print("SOURCE:", doc.metadata.get("source"))
    #     print("PAGE:", doc.metadata.get("page"))
    #     print("CONTENT:")
    #     print(repr(doc.page_content))

    # # Remove exact duplicate chunks
    # unique_results = []
    # seen = set()

    # for doc, score in results:

    #     content = doc.page_content.strip()

    #     if content not in seen:
    #         seen.add(content)
    #         unique_results.append((doc, score))

    # print(f"\nAFTER DUPLICATE REMOVAL: {len(unique_results)}")

    # return unique_results 
    
    
    
    
    
# def retrieve_documents(vector_store, question, k=15, final_k=5):

#     # Step 1: Retrieve candidate chunks from FAISS
#     results = vector_store.similarity_search_with_score(
#         question,
#         k=k
#     )

#     print(f"\nBEFORE DUPLICATE REMOVAL: {len(results)}")

#     # Step 2: Remove exact duplicate chunks
#     unique_results = []
#     seen = set()

#     for doc, score in results:

#         content = doc.page_content.strip()

#         if content not in seen:
#             seen.add(content)
#             unique_results.append((doc, score))

#     print(f"AFTER DUPLICATE REMOVAL: {len(unique_results)}")

#     # Step 3: Keep only the best results
#     final_results = unique_results[:final_k]

#     print(f"FINAL RESULTS SENT TO GEMINI: {len(final_results)}")

#     # Step 4: Display final results for testing
#     for i, (doc, score) in enumerate(final_results):

#         print(f"\n--- FINAL RESULT {i+1} ---")
#         print("SCORE:", score)
#         print("SOURCE:", doc.metadata.get("source"))
#         print("PAGE:", doc.metadata.get("page"))
#         print("CONTENT:")
#         print(repr(doc.page_content))

#     return final_results


# def exact_search(vector_store, search_text):

#     print("\n========== EXACT SEARCH ==========")
#     print("SEARCH:", search_text)

#     found = []

#     all_documents = vector_store.docstore._dict.values()

#     for doc in all_documents:

#         if search_text.lower() in doc.page_content.lower():

#             found.append(doc)

#     print("FOUND:", len(found))

#     for i, doc in enumerate(found):

#         print(f"\n--- MATCH {i+1} ---")
#         print(doc.page_content)

#     return found

    
    

# define a function to remove duplicates:
# def remove_duplicate_documents(results):
#     unique_results = []
#     seen = set()

#     for result, score in results:

#         content = result.page_content.strip()

#         if content not in seen:
#             seen.add(content)
#             unique_results.append((result, score))

#     return unique_results





# def retrieve_documents(vector_store, question, k=4, fetch_k=20):
#     results = vector_store.max_marginal_relevance_search(
#         question,
#         k=k,
#         fetch_k=fetch_k
#     )
#     return results




   # # --------------------------------
            # # Step 7: Extract Text
            # # --------------------------------

            # text = ""

            # if uploaded_file.name.endswith(".pdf"):

            #     # reader = PdfReader(uploaded_file)
            #     reader = PdfReader(
            #         BytesIO(st.session_state.uploaded_file_data)
            #     )

            #     for page in reader.pages:
            #         text += page.extract_text() or ""


            # elif uploaded_file.name.endswith(".docx"):

            #     # doc = docx.Document(uploaded_file)
            #     doc = docx.Document(
            #         BytesIO(st.session_state.uploaded_file_data)
            #     )

            #     for para in doc.paragraphs:
            #         text += para.text + "\n"
                    
            # st.success("Text extracted successfully!")
                    
                    
            # # --------------------------------
            # # Step 8: Create LangChain Document
            # # --------------------------------

            # document = Document(
            #     page_content=text,
            #     metadata={
            #         "source": uploaded_file.name
            #     }
            # )
            
            # # st.success("LangChain document created successfully!")
            
            
            
            
            
            
            # --------------------------------
            # # Generate Document Summary
            # # --------------------------------

            # with st.spinner("🧠 Analyzing document..."):

            #     model = create_gemini_model()

            #     st.session_state.document_summary = create_document_summary(
            #         model,
            #         documents
            #     )

            # st.success("🧠 Document analysis completed!")
            # st.write(st.session_state.document_summary)
            
            
            
            
            
            
            
            
# --------------------------------
# Exact Search
# --------------------------------

# def exact_search(vector_store, question):

#     exact_results = []

#     documents = vector_store.docstore._dict.values()

#     question_lower = question.lower()

#     # Detect dates like:
#     # 13 Dec 2025
#     # 13 December 2025

#     date_pattern = (
#         r"\b\d{1,2}\s+"
#         r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
#         r"[a-z]*\s+\d{4}\b"
#     )

#     dates = re.findall(
#         date_pattern,
#         question_lower
#     )

#     search_terms = dates

#     for document in documents:

#         content_lower = document.page_content.lower()

#         for term in search_terms:

#             if term in content_lower:

#                 exact_results.append(
#                     (document, 0.0)
#                 )

#                 break
#             st.success("Exact match found!")

#     return exact_results


# # --------------------------------
# # Semantic Search
# # --------------------------------

# def semantic_search(vector_store, question, k=15):

#     results = vector_store.similarity_search_with_score(
#         question,
#         k=k
#     )
    
#     st.success("Semantic search found " + str(len(results)) + " results!")

#     return results


# # --------------------------------
# # Hybrid Retrieval
# # --------------------------------

# def retrieve_documents(vector_store, question, k=15):

#     # Exact search
#     exact_results = exact_search(
#         vector_store,
#         question
#     )

#     # Semantic search
#     semantic_results = semantic_search(
#         vector_store,
#         question,
#         k=k
#     )

#     # Combine
#     combined_results = []

#     seen = set()

#     for result, score in exact_results + semantic_results:

#         document_id = (
#             result.metadata.get("source", ""),
#             result.metadata.get("page", ""),
#             result.page_content
#         )

#         if document_id not in seen:

#             seen.add(document_id)

#             combined_results.append(
#                 (result, score)
#             )
#     return combined_results










# 11. Give a clear, concise, and direct answer.
#     12. Do not include source names, page numbers, citations,
#     or citation markers in your answer.

#     13. Return only the answer to the user's question.
    
#     14. When answering an exact factual question, prioritize
#     context containing an exact match for the requested
#     date, name, number, amount, title, or phrase.

#     15. If multiple context sections contain relevant information,
#         combine them carefully when necessary.

#     16. Do not treat the number or order of retrieved sources
#         as evidence that all sources are relevant.

#     17. Use only the context that actually supports the answer.

#     18. Return only the answer. Do not return source names,
#         page numbers, or citation markers.






# # define function to create document summary

# def create_document_summary(model, documents):
    
#     document_text = ""

#     for document in documents:
#         document_text += document.page_content + "\n\n"

#     prompt = f"""
# You are analyzing a document for a Document GPT system.

# Read the document carefully and create a concise factual summary
# of the important information contained in it.

# The summary should help answer document-level questions later.

# Rules:
# 1. Use only information explicitly present in the document.
# 2. Do not invent or assume information.
# 3. Include important names, dates, numbers, titles, amounts,
#    organizations, locations, document type, and other key facts
#    when they are clearly available.
# 4. Preserve exact dates and numbers.
# 5. If something is not present, do not mention it.
# 6. Keep the summary concise but useful.
# 7. Do not answer any particular user question.

# DOCUMENT:
# {document_text}

# DOCUMENT SUMMARY:
# """

#     response = model.invoke(prompt)

#     return response.content[0]["text"]
