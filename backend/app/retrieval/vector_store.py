import chromadb
from chromadb.config import Settings
import uuid

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "mutual_fund_chunks"
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} # Use cosine similarity
        )

    def add_chunks(self, chunks):
        """
        Adds text chunks and their metadata to Chroma DB.
        """
        if not chunks:
            return

        documents = []
        metadatas = []
        ids = []

        for idx, chunk in enumerate(chunks):
            # Generate a unique ID for each chunk
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            documents.append(chunk["text"])
            
            # Ensure metadata values are strings, ints, or floats
            safe_metadata = {
                k: str(v) if v is not None else "" 
                for k, v in chunk.get("metadata", {}).items()
            }
            metadatas.append(safe_metadata)

        # Upsert documents into the collection
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return len(ids)

    def search(self, query, top_k=5, filter_metadata=None):
        """
        Searches the vector store for the closest chunks to the query.
        """
        where_clause = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        if results and results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results and results['distances'] else None
                })
                
        return formatted_results
