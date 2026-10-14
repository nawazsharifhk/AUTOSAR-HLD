from backend.rag.embeddings import embedding_service

# Expose embedding operations cleanly
def get_embedding_service():
    return embedding_service
