with open("core/tools/rag_tool.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD", "")
content = content.replace("=======", "")
content = content.replace(">>>>>>> origin/jules-3466090822907057400-4af64808", "")
content = content.replace("FirestoreVectorStoreapi_key=api_key)", "FirestoreVectorStore(api_key=api_key)")

with open("core/tools/rag_tool.py", "w") as f:
    f.write(content)
