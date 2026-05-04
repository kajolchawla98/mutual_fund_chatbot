import re

class QueryClassifier:
    def __init__(self):
        # Basic keyword/pattern matching for fast intent classification
        self.advisory_keywords = [
            "should i invest", "is it good", "which is better", 
            "recommend", "suggest", "where to invest", "best fund"
        ]
        
        self.performance_keywords = [
            "returns in 1 year", "past performance", "historical return", 
            "how much return", "cagr"
        ]

        # Valid scheme keywords (simplified for example)
        self.scheme_keywords = [
            "hdfc", "motilal oswal", "icici", "birla sun life", "mid-cap", "small cap", "liquid"
        ]

    def classify_intent(self, sanitized_query):
        """
        Classifies the query into FACTUAL, ADVISORY_REFUSE, OUT_OF_SCOPE_REFUSE, or PERFORMANCE_REDIRECT.
        """
        query_lower = sanitized_query.lower()
        
        # 1. Check for Advisory
        if any(keyword in query_lower for keyword in self.advisory_keywords):
            return "ADVISORY_REFUSE"
            
        # 2. Check for Performance analysis requests
        if any(keyword in query_lower for keyword in self.performance_keywords):
            return "PERFORMANCE_REDIRECT"
            
        # 3. Check Scope (Does it mention mutual funds or recognized AMCs?)
        # A simple check: if it lacks fund keywords and general mutual fund terms.
        mf_terms = ["fund", "sip", "lumpsum", "nav", "expense ratio", "exit load"] + self.scheme_keywords
        if not any(term in query_lower for term in mf_terms):
            return "OUT_OF_SCOPE_REFUSE"
            
        # Default to FACTUAL if it passes all refusal checks
        return "FACTUAL"

    def extract_entities(self, query):
        """
        Extracts basic entities like Fund Name or Data Metric using heuristics.
        """
        query_lower = query.lower()
        entities = {"scheme_name": None, "metric": None}
        
        # Simple extraction logic
        if "expense ratio" in query_lower:
            entities["metric"] = "expense ratio"
        elif "exit load" in query_lower:
            entities["metric"] = "exit load"
        elif "sip" in query_lower:
            entities["metric"] = "minimum sip"
            
        for fund in ["hdfc", "motilal oswal", "icici", "birla"]:
            if fund in query_lower:
                entities["scheme_name"] = fund.upper()
                break
                
        return entities
