with open("core/tools/firestore_vector_store.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD", "")
content = content.replace("=======", "")
content = content.replace(">>>>>>> origin/jules-3466090822907057400-4af64808", "")
content = content.replace("self._connector = FirebaseConnector)", "self._connector = FirebaseConnector()")
content = content.replace("self._semantic_router = SemanticRouter)", "self._semantic_router = SemanticRouter()")

with open("core/tools/firestore_vector_store.py", "w") as f:
    f.write(content)
