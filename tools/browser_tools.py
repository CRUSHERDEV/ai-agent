import logging
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from newspaper import Article, Config
from bs4 import BeautifulSoup

# 1. Setup proper logging for an autonomous agent
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Create a robust session with connection pooling and automated retries
def create_robust_session():
    session = requests.Session()
    # Automatically retry on common server errors and rate limits
    retries = Retry(total=3, backoff_factor=1.5, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Modern browser headers to avoid basic bot-blocking
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    })
    return session

# Global session instance to reuse connections across multiple calls
http_session = create_robust_session()

def clean_text_advanced(text, max_paragraphs=50):
    if not text:
        return ""
    
    # Standardize whitespace and remove excessive blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Advanced filter: Keep lines that have at least 5 words (removes UI buttons, dates, tags)
    cleaned = [line for line in lines if len(line.split()) >= 5]
    
    return "\n\n".join(cleaned[:max_paragraphs])

def fetch_page_text(url, timeout=10):
    logger.info(f"Extracting data from: {url}")
    
    try:
        # Pass our robust headers into newspaper3k
        config = Config()
        config.browser_user_agent = http_session.headers['User-Agent']
        config.request_timeout = timeout
        
        article = Article(url, config=config)
        article.download()
        article.parse()
        
        # Check if newspaper failed to grab meaningful text (often happens on heavily JS-rendered sites)
        if not article.text or len(article.text.strip()) < 100:
            raise ValueError("Newspaper extraction yielded insufficient text. Triggering fallback.")

        cleaned_text = clean_text_advanced(article.text)
        publish_date = article.publish_date if article.publish_date else "Unknown"
        title = article.title if article.title else "Unknown"

        return f"""TITLE:\n{title}\n\nPUBLISH DATE:\n{publish_date}\n\nCONTENT:\n{cleaned_text}"""

    except Exception as e:
        logger.warning(f"Primary extraction failed for {url}: {e}. Initiating BeautifulSoup fallback.")
        
        try:
            # Fallback scraper using our robust session
            response = http_session.get(url, timeout=timeout)
            response.raise_for_status() # Raise error for bad HTTP codes (404, 403, etc.)
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # CRITICAL: Strip out noise tags before extracting text
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
                
            raw_text = soup.get_text(separator='\n')
            cleaned_text = clean_text_advanced(raw_text)
            
            if not cleaned_text:
                return "ERROR: Extracted text was empty after cleaning."
                
            return f"""TITLE:\nFallback Extraction\n\nCONTENT:\n{cleaned_text}"""
            
        except requests.exceptions.RequestException as req_error:
            logger.error(f"Complete failure extracting {url}: {req_error}")
            return f"ERROR: Network or access issue preventing extraction. {req_error}"