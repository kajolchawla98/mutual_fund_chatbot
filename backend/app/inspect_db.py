import os
import chromadb
from pprint import pprint

# Connect to the Chroma DB
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
client = chromadb.PersistentClient(path=db_path)

# Get our collection
collection = client.get_collection(name="mutual_fund_chunks")

# Peek at the data
print(f"Total chunks in database: {collection.count()}")

print("\n--- Let's look at 1 random chunk ---")
# 'peek' returns the first few items in the collection
results = collection.peek(limit=1)

print("\n[METADATA]:")
pprint(results['metadatas'][0])

print("\n[TEXT CHUNK]:")
print(results['documents'][0])

print("\n[VECTOR LENGTH]:")
print(len(results['embeddings'][0]) if results['embeddings'] else "No embeddings fetched by peek")
