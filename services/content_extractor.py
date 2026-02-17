import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_content(url):
    """Extract relevant content from competitor website"""
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        logger.info(f"Extracting content from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extract text from main content areas
        content_areas = soup.find_all(['main', 'article', 'section', 'div'], limit=10)
        
        text_content = []
        for area in content_areas:
            text = area.get_text(separator=' ', strip=True)
            if len(text) > 100:  # Only meaningful content
                text_content.append(text)
        
        # Combine and limit content
        full_content = ' '.join(text_content)[:5000]  # Limit to 5000 chars
        
        logger.info(f"Extracted {len(full_content)} characters from {url}")
        return full_content
        
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return f"Could not extract content from {url}"
