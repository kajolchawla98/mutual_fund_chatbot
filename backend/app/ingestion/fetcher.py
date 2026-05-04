import requests
from bs4 import BeautifulSoup
import PyPDF2
from io import BytesIO

class ContentFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_html(self, url):
        """Fetches HTML content from a given URL and extracts raw text."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text and remove excessive whitespace
            text = ' '.join(soup.stripped_strings)
            return {"status": "success", "content": text, "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}

    def fetch_pdf(self, url):
        """Fetches a PDF from a given URL and extracts text."""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            pdf_file = BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                    
            return {"status": "success", "content": text, "url": url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": url}
