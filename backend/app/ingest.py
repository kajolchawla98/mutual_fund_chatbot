import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import modules correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingestion.fetcher import ContentFetcher
from app.ingestion.normalizer import DataNormalizer
from app.ingestion.chunker import TextChunker
from app.retrieval.vector_store import VectorStore

def run_ingestion():
    print("Starting ingestion process...")
    
    # 1. Load Source Registry
    registry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "registry", "source_registry.json")
    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
    fetcher = ContentFetcher()
    normalizer = DataNormalizer()
    chunker = TextChunker()
    
    # Chroma DB directory (in the backend folder)
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    print(f"Vector DB will be stored at: {db_path}")
    vector_store = VectorStore(persist_directory=db_path)
    
    total_chunks_added = 0
    
    for source in registry:
        url = source['url']
        print(f"\nProcessing: {source['scheme_name']}")
        print(f"URL: {url}")
        
        # Phase 2.1 Fetch
        if source['doc_type'] == 'html':
            raw_data = fetcher.fetch_html(url)
        else:
            raw_data = fetcher.fetch_pdf(url)
            
        if raw_data['status'] == 'error':
            print(f"  -> Error fetching: {raw_data['error']}")
            continue
            
        raw_data['scheme_name'] = source['scheme_name']
        
        # Phase 2.2 Normalize
        normalized_data = normalizer.normalize(raw_data)
        
        # Base metadata mapping from source registry
        base_metadata = {
            "source_id": source['source_id'],
            "url": source['url'],
            "scheme_name": source['scheme_name'],
            "amc_name": source['amc_name'],
            "doc_type": source['doc_type'],
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Phase 2.3 Chunk
        chunks = chunker.create_chunks(normalized_data, metadata_context=base_metadata)
        print(f"  -> Created {len(chunks)} chunks.")
        
        # Phase 3 Vector Store Upsert
        if chunks:
            added = vector_store.add_chunks(chunks)
            total_chunks_added += added
            print(f"  -> Added {added} chunks to Chroma DB.")
            
    print(f"\nIngestion Complete! Total chunks stored in Chroma DB: {total_chunks_added}")
    print(f"Database saved to: {db_path}")

if __name__ == "__main__":
    run_ingestion()
