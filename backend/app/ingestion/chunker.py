import tiktoken
import re

class TextChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        # Using cl100k_base which is commonly used by modern models
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            pass
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def section_aware_split(self, text):
        """
        Splits text by headers or paragraphs. 
        A very naive implementation splitting by double newlines to simulate paragraphs/sections.
        """
        sections = re.split(r'\n\s*\n', text)
        return [sec.strip() for sec in sections if len(sec.strip()) > 0]

    def create_chunks(self, normalized_data, metadata_context=None):
        """
        Creates chunks from normalized text using token-based sizing
        and section-aware grouping.
        """
        text = normalized_data.get('content', '')
        sections = self.section_aware_split(text)
        
        chunks = []
        base_metadata = normalized_data.get('metadata', {})
        if metadata_context:
            base_metadata.update(metadata_context)
            
        for section in sections:
            tokens = self.tokenizer.encode(section)
            
            # If the section itself is larger than chunk_size, split it
            if len(tokens) > self.chunk_size:
                start = 0
                while start < len(tokens):
                    end = start + self.chunk_size
                    chunk_tokens = tokens[start:end]
                    chunks.append({
                        "text": self.tokenizer.decode(chunk_tokens),
                        "metadata": base_metadata.copy()
                    })
                    start += (self.chunk_size - self.chunk_overlap)
            else:
                # Basic grouping (simplified for now to avoid the previous bug)
                chunks.append({
                    "text": section,
                    "metadata": base_metadata.copy()
                })
            
        return chunks
