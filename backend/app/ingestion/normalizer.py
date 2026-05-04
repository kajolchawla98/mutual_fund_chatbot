import re

class DataNormalizer:
    def __init__(self):
        # Regular expressions to find specific patterns in text
        self.expense_ratio_pattern = re.compile(r'Expense Ratio.*?([\d\.]+)\s*%', re.IGNORECASE)
        self.exit_load_pattern = re.compile(r'Exit Load.*?(1%\s*if.*?|Nil)', re.IGNORECASE)
        self.min_sip_pattern = re.compile(r'Minimum SIP.*?₹\s*([\d,]+)', re.IGNORECASE)

    def normalize(self, raw_data):
        """
        Takes raw text data from the fetcher and attempts to extract
        structured metadata fields.
        """
        content = raw_data.get('content', '')
        
        extracted_metadata = {
            'expense_ratio': self._extract_match(self.expense_ratio_pattern, content),
            'exit_load': self._extract_match(self.exit_load_pattern, content),
            'minimum_sip': self._extract_match(self.min_sip_pattern, content),
            'scheme_name': raw_data.get('scheme_name', 'Unknown')
        }
        
        return {
            'content': content,
            'metadata': extracted_metadata
        }

    def _extract_match(self, pattern, text):
        match = pattern.search(text)
        return match.group(1) if match else None
