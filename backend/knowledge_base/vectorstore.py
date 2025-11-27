

import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Path to store the FAISS index locally
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "faiss_index")


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def get_vectorstore(user_id):
    """Load existing FAISS index for a specific user. Raises error if not found."""
    user_index_path = os.path.join(os.path.dirname(__file__), f"faiss_index_{user_id}")
    embeddings = get_embeddings()
    
    if os.path.exists(user_index_path):
        vectorstore = FAISS.load_local(user_index_path, embeddings)
        print(f"Loaded existing FAISS index for user {user_id}.")
        return vectorstore
    else:
        return None
        # raise FileNotFoundError(f"Vector index not found for user {user_id}. Please upload documents first.")

def get_or_create_vectorstore(user_id):
    """Load existing FAISS index or create a new one for a specific user (used during upload)."""
    user_index_path = os.path.join(os.path.dirname(__file__), f"faiss_index_{user_id}")
    embeddings = get_embeddings()
    
    if os.path.exists(user_index_path):
        vectorstore = FAISS.load_local(user_index_path, embeddings)
        print(f"Loaded existing FAISS index for user {user_id}.")
    else:
        # Create a new empty vectorstore
        vectorstore = FAISS.from_texts([""], embeddings)
        print(f"Created new FAISS index for user {user_id}.")
    return vectorstore
