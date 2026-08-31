# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv()

# gemini_api_key = os.getenv("GEMINI_API_KEY")

# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY was not found")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.6-flash",
#     google_api_key=gemini_api_key
# )
# response = llm.invoke("Say hello in one sentence.")

# print(response.content)





import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


# --------------------------------
# 1. Load environment variables
# --------------------------------

load_dotenv()


# --------------------------------
# 2. Get Gemini API key
# --------------------------------

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY was not found.")


# --------------------------------
# 3. Create Gemini model
# --------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=gemini_api_key
)


# --------------------------------
# 4. Send a test question
# --------------------------------

question = "What is the capital of Pakistan?"

response = model.invoke(question)


# --------------------------------
# 5. Display Gemini's response
# --------------------------------

print("\nQuestion:")
print(question)

print("\nGemini Answer:")
print(response.content[0]["text"])