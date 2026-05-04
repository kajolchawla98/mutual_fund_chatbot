import os
from datetime import datetime
from groq import Groq


class AnswerComposer:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY", ""),
        )
        self.model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.available_funds = self._load_available_funds()

    def _load_available_funds(self):
        import json
        try:
            registry_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "registry", "source_registry.json")
            with open(registry_path, 'r') as f:
                registry = json.load(f)
                # Map to simplified names for cleaner display
                mapping = {
                    "HDFC Mid-Cap Opportunities Fund Direct Growth": "HDFC Mid-Cap",
                    "ICICI Prudential Bluechip Fund Direct Growth": "ICICI Bluechip",
                    "Motilal Oswal Small Cap Fund Direct Growth": "Motilal Oswal Small Cap"
                }
                names = []
                for s in registry:
                    names.append(mapping.get(s['scheme_name'], s['scheme_name']))
                return names[:3] # Return exact 3 names
        except Exception:
            return ["HDFC Mid-Cap", "ICICI Bluechip", "Motilal Oswal Small Cap"]

    def generate_prompt(self, query, retrieved_chunks):
        """Build system prompt and context string from retrieved chunks."""
        context_text = ""
        for i, chunk in enumerate(retrieved_chunks):
            source_url = chunk.get("metadata", {}).get("url", "https://www.amfiindia.com/")
            context_text += f"[Source {i+1}] URL: {source_url}\n{chunk.get('text', '')}\n\n"

        system_prompt = (
            "You are a strict, facts-only mutual fund information assistant. "
            "Your ONLY job is to answer the user's question using the provided context.\n\n"
            "STRICT RULES:\n"
            "1. Answer in 2-4 sentences maximum.\n"
            "2. Use ONLY facts from the context. Do NOT invent any data.\n"
            "3. FOR FACTUAL ANSWERS: You MUST end your answer with exactly one markdown citation link in this format: [Official Source](URL)\n"
            f"4. IF INFORMATION IS MISSING: Say exactly: 'The specific information is not available in our current data. However, I can help you with information on these funds: {', '.join(self.available_funds)}' "
            "In this case, do NOT include ANY citation link or [Official Source].\n"
            "5. Do NOT include any explanations, disclaimers, or additional links."
        )

        return system_prompt, context_text

    def compose_answer(self, query, retrieved_chunks):
        """Generates a factual answer using Groq LLM based on retrieved chunks."""
        system_prompt, context = self.generate_prompt(query, retrieved_chunks)

        user_message = (
            f"Context:\n{context}\n"
            f"User Question: {query}\n\n"
            "Answer (end with [Official Source](URL)):"
        )

        current_date = datetime.now().strftime("%Y-%m-%d")
        fallback_url = (
            retrieved_chunks[0].get("metadata", {}).get("url", "https://www.amfiindia.com/")
            if retrieved_chunks else "https://www.amfiindia.com/"
        )

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model=self.model,
                temperature=0.0,
                max_tokens=300,
            )
            raw_answer = response.choices[0].message.content.strip()
            print(f"[COMPOSER] LLM raw answer: {raw_answer}")

            # Append freshness footer only if information is available
            if "The specific information is not available" in raw_answer:
                return raw_answer
            
            footer = f"\n\nLast updated from sources: {current_date}"
            return raw_answer + footer

        except Exception as e:
            print(f"[COMPOSER] Error calling Groq API: {e}")
            # Return raw retrieved text so user sees something useful
            if retrieved_chunks and retrieved_chunks[0].get("text"):
                snippet = retrieved_chunks[0]["text"][:400]
                return f"{snippet} [Official Source]({fallback_url})"
            
            return f"I was unable to retrieve a response at this time. [Official Source]({fallback_url})"
