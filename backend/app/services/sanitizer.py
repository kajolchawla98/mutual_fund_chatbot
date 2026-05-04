import re

class QuerySanitizer:
    def __init__(self):
        # Patterns to detect sensitive information
        self.pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', re.IGNORECASE)
        self.aadhaar_pattern = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
        self.phone_pattern = re.compile(r'\b(?:\+91|91)?[-\s]?\d{10}\b')
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.otp_pattern = re.compile(r'\b\d{4,6}\b') # Simple 4-6 digit OTP guess

    def sanitize(self, query):
        """
        Redacts sensitive personal identifiers from the user query.
        """
        sanitized = self.pan_pattern.sub('[REDACTED_PAN]', query)
        sanitized = self.aadhaar_pattern.sub('[REDACTED_AADHAAR]', sanitized)
        sanitized = self.phone_pattern.sub('[REDACTED_PHONE]', sanitized)
        sanitized = self.email_pattern.sub('[REDACTED_EMAIL]', sanitized)
        # Note: OTP pattern might accidentally catch numbers like "2000" (e.g. year), 
        # so in a real app we might only redact if preceded by "OTP".
        # For strictness, we leave simple digits unless it's clearly an OTP context.
        return sanitized
