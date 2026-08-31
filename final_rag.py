# from rag import answer_question

# question = "Which country does the person want to visit?"


# answer, results = answer_question(question)


# print("\nQuestion:")
# print(question)

# print("\nAnswer:")
# print(answer)

# print("\nSources:")

# for i, result in enumerate(results, start=1):

#     print(f"\n--- Source {i} ---")

#     print(result.metadata["source"])
    
    
    
    
from rag import answer_question


question = "Which country does the person want to visit?"


response = answer_question(question)


answer = response["answer"]
sources = response["sources"]
results = response["documents"]


print("\nQuestion:")
print(question)


print("\nAnswer:")
print(answer)


print("\nSources:")

for i, source in enumerate(sources, start=1):

    print(f"\n--- Source {i} ---")

    print(source)