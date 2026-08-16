import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Tuple

class CodeVectorStore:
    def __init__(self, collection_name="codebase"):
        """Initialize vector database for code search."""
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # Lightweight, good for code
        )
        
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Delete existing collection if it exists (clean start)
        try:
            self.client.delete_collection(collection_name)
        except:
            pass
        
        # Create new collection
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        
        self.documents = []
        self.metadatas = []
        self.ids = []
    
    def add_document(self, content: str, file_path: str, doc_id: str):
        """Add a document to the vector store."""
        self.documents.append(content)
        self.metadatas.append({"file_path": file_path})
        self.ids.append(doc_id)
    
    def index_codebase(self, repo_path: str):
        """Index all Python files in a repository."""
        print("📚 Indexing codebase...")
        count = 0
        
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.add_document(content, file_path, f"file_{count}")
                        count += 1
                    except Exception as e:
                        print(f"⚠️ Could not read {file_path}: {e}")
        
        # Add all documents to the collection
        if self.documents:
            self.collection.add(
                documents=self.documents,
                metadatas=self.metadatas,
                ids=self.ids
            )
        
        print(f"✅ Indexed {count} Python files")
        return count
    
    def search(self, query: str, n_results: int = 3) -> List[Tuple[str, str]]:
        """Search for relevant code snippets."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        retrieved = []
        if results['documents'] and results['metadatas']:
            for i, doc in enumerate(results['documents'][0]):
                file_path = results['metadatas'][0][i]['file_path']
                retrieved.append((doc, file_path))
        
        return retrieved