import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.knowledge_base.vectorstore import get_or_create_vectorstore, VECTORSTORE_PATH
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader

def ingest_single_document(file_path, user_id):
    """
    Ingest a single document and associate it with a user.
    """
    # Initialize vectorstore
    # Initialize vectorstore for the specific user
    vectorstore = get_or_create_vectorstore(user_id)

    docs = []
    filename = os.path.basename(file_path)
    
    if filename.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
        docs.extend(loader.load())
    elif filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        docs.extend(loader.load())
    else:
        print(f"Unsupported file type: {filename}")
        return

    # Split large texts into smaller chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunked_docs = []
    
    for doc in docs:
        # Add user_id to metadata
        doc.metadata["user_id"] = user_id
        chunked_texts = text_splitter.split_text(doc.page_content)
        for chunk in chunked_texts:
            chunked_docs.append({"page_content": chunk, "metadata": doc.metadata})

    # Add to vectorstore
    if chunked_docs:
        vectorstore.add_texts(
            texts=[d["page_content"] for d in chunked_docs],
            metadatas=[d["metadata"] for d in chunked_docs]
        )
        vectorstore.save_local(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base", f"faiss_index_{user_id}"))
        print(f"Ingested {len(chunked_docs)} chunks for user {user_id} into vectorstore.")
    else:
        print("No content to ingest.")

if __name__ == "__main__":
    # Example usage for testing
    pass
