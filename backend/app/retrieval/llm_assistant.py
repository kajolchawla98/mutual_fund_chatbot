import os
from groq import Groq

class LLMAssistant:
    def __init__(self):
        # Assumes GROQ_API_KEY is set in the environment
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY", "dummy_key_for_testing"),
        )
        self.model = os.environ.get("GROQ_MODEL", "llama3-8b-8192")

    def rewrite_query(self, user_query):
        """
        Rewrites the user query to optimize it for vector search retrieval.
        Extracts entity (scheme name) and metric type.
        """
        prompt = f"""
        You are a helpful assistant optimizing search queries for a mutual fund database.
        Given the user query, output a concise search query focusing on the key entity and metric.
        Do not answer the query. Just provide the optimized search string.
        
        User Query: {user_query}
        Optimized Query:
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return user_query # Fallback to original query

    def rerank_chunks(self, user_query, chunks):
        """
        Optional: Reranks the retrieved chunks using the LLM for better relevance.
        (Implementation depends on specific reranking prompt strategy)
        """
        # For a fast model, we might just score them or sort them based on explicit mentions.
        # This is a placeholder for the actual reranking logic.
        return chunks # Return as-is for now
