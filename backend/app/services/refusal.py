import logging
from datetime import datetime

# Setup simple audit log for refusals
logging.basicConfig(filename='refusal_audit.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class RefusalHandler:
    def __init__(self):
        self.educational_link = "AMFI Investor Corner"
        self.sebi_link = "SEBI Investor Education"

    def handle_refusal(self, intent, query=""):
        """
        Routes the refusal intent to the correct polite template, logs it, 
        and ensures output complies with max 3 sentences and 1 link.
        """
        response_text = ""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if intent == "ADVISORY_REFUSE":
            response_text = f"I am a facts-only assistant and cannot provide investment advice or recommendations. Please consult a registered financial advisor. For educational resources on mutual funds, visit {self.educational_link}."
            
        elif intent == "PERFORMANCE_REDIRECT":
            response_text = f"I cannot analyze or predict historical fund performance or calculate returns. You can view the official historical data on the AMC's official factsheet or learn more at {self.educational_link}."
            
        elif intent == "OUT_OF_SCOPE_REFUSE":
            response_text = f"My knowledge is limited to specific factual information regarding allowlisted mutual funds. I cannot answer queries outside this scope. For general queries, please check {self.sebi_link}."
            
        else:
            # Fallback for unexpected intents
            response_text = f"I cannot process this request based on my strict factual guidelines. Learn more about mutual funds at {self.educational_link}."

        # No footer for refusals
        final_response = response_text

        # Log policy audit for refusals
        self._audit_log(intent, query)
        
        return final_response

    def _audit_log(self, reason_code, query):
        """Captures refusal reason code for analytics."""
        logging.info(f"REFUSAL_TRIGGERED | Code: {reason_code} | Query Snippet: {query[:30]}...")
