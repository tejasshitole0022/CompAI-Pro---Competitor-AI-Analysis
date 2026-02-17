import logging
import os
import re
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def find_competitors(company_url):
    """Find top 3 competitors using API or fallback"""
    try:
        # Add protocol if missing
        if not company_url.startswith(('http://', 'https://')):
            company_url = 'https://' + company_url
        
        parsed = urlparse(company_url)
        domain = parsed.netloc or company_url
        company_name = domain.replace('www.', '').split('.')[0]
        
        logger.info(f"Searching competitors for: {company_name}")
        
        # Try API first if key is available
        api_key = os.getenv('SERPAPI_KEY')
        if api_key:
            logger.info("Using SerpAPI for competitor search")
            competitors = search_competitors_api(company_name, api_key)
            if competitors and len(competitors) > 0:
                logger.info(f"Found {len(competitors)} competitors via API")
                return competitors[:3]
            else:
                logger.warning("API returned no results, using fallback")
        else:
            logger.info("No API key found, using fallback database")
        
        # Fallback to database
        competitors = get_fallback_competitors(company_name.lower())
        if competitors and len(competitors) >= 3:
            logger.info(f"Using {len(competitors)} competitors from database")
            return competitors[:3]
        
        # Last resort: use generic industry competitors
        logger.warning(f"No specific competitors found for {company_name}")
        return [
            {'name': 'Competitor A', 'url': 'https://www.example.com'},
            {'name': 'Competitor B', 'url': 'https://www.example.com'},
            {'name': 'Competitor C', 'url': 'https://www.example.com'}
        ]
            
    except Exception as e:
        logger.error(f"Error finding competitors: {e}")
        raise

def search_competitors_api(company_name, api_key):
    """Search for competitors using SerpAPI and extract from comparison pages"""
    try:
        url = "https://serpapi.com/search"
        params = {
            'q': f'{company_name} top competitors alternatives',
            'api_key': api_key,
            'engine': 'google',
            'num': 10
        }
        
        logger.info(f"Searching SERP API for: {company_name} competitors")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if 'error' in data:
            logger.error(f"SERP API error: {data['error']}")
            return []
        
        competitors = []
        seen = set()
        
        # Blacklist - sites that are NOT competitors
        blacklist = {'google', 'wikipedia', 'facebook', 'twitter', 'linkedin', 'youtube', 
                    'instagram', 'reddit', 'quora', 'forbes', 'bloomberg', 'techcrunch',
                    'crunchbase', 'comparably', 'owler', 'zoominfo', 'craft', 'cbinsights',
                    'g2', 'capterra', 'trustpilot', 'yelp', 'glassdoor', 'indeed', 'shopify',
                    'image', 'source', 'below', 'list', company_name.lower()}
        
        # First check related_questions for featured snippet
        for question in data.get('related_questions', []):
            if question.get('type') == 'featured_snippet':
                items = question.get('list', [])
                for item in items:
                    # Extract brand name from items like "eBay. Image Source: eBay. ..."
                    match = re.match(r'^([A-Za-z]+(?:\s+[A-Z][a-z]+)?)', item.strip())
                    if match:
                        name = match.group(1).strip()
                        name_lower = name.lower()
                        
                        if (name_lower not in blacklist and 
                            name_lower not in seen and 
                            name_lower != company_name.lower() and
                            len(name) >= 3):
                            
                            seen.add(name_lower)
                            competitors.append({
                                'name': name,
                                'url': f"https://www.{name_lower.replace(' ', '')}.com"
                            })
                            logger.info(f"Found competitor from featured snippet: {name}")
                            
                            if len(competitors) >= 3:
                                return competitors
        
        # Extract from snippets
        for result in data.get('organic_results', []):
            if len(competitors) >= 3:
                break
                
            snippet = result.get('snippet', '')
            
            # Look for patterns like "include Walmart, eBay, Target"
            # or "Alibaba, AliExpress, eBay, Walmart"
            matches = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)?)\b', snippet)
            
            for name in matches:
                name_lower = name.lower()
                
                if (name_lower not in blacklist and 
                    name_lower not in seen and 
                    name_lower != company_name.lower() and
                    len(name) >= 4):
                    
                    seen.add(name_lower)
                    competitors.append({
                        'name': name,
                        'url': f"https://www.{name_lower}.com"
                    })
                    logger.info(f"Found competitor: {name}")
                    
                    if len(competitors) >= 3:
                        break
        
        logger.info(f"API found {len(competitors)} competitors")
        return competitors
        
    except Exception as e:
        logger.warning(f"API search failed: {e}")
        return []

def extract_clean_domain(url):
    """Extract clean domain name and full URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        domain = domain.replace('www.', '').split('/')[0]
        domain_name = domain.split('.')[0]
        full_url = f"https://{domain}" if not url.startswith('http') else url
        return (domain_name, full_url)
    except:
        return None

def get_fallback_competitors(company_name):
    """Expanded fallback competitor mapping for common companies"""
    competitor_map = {
        # Tech & Electronics
        'samsung': [
            {'name': 'Apple', 'url': 'https://www.apple.com'},
            {'name': 'OnePlus', 'url': 'https://www.oneplus.in'},
            {'name': 'Xiaomi', 'url': 'https://www.mi.com'}
        ],
        'apple': [
            {'name': 'Samsung', 'url': 'https://www.samsung.com'},
            {'name': 'OnePlus', 'url': 'https://www.oneplus.in'},
            {'name': 'Google', 'url': 'https://store.google.com'}
        ],
        'oneplus': [
            {'name': 'Samsung', 'url': 'https://www.samsung.com'},
            {'name': 'Apple', 'url': 'https://www.apple.com'},
            {'name': 'Xiaomi', 'url': 'https://www.mi.com'}
        ],
        
        # Footwear & Fashion
        'redtape': [
            {'name': 'Woodland', 'url': 'https://www.woodlandworldwide.com'},
            {'name': 'Clarks', 'url': 'https://www.clarks.in'},
            {'name': 'Hushpuppies', 'url': 'https://www.hushpuppies.in'}
        ],
        'woodland': [
            {'name': 'Redtape', 'url': 'https://www.redtape.in'},
            {'name': 'Clarks', 'url': 'https://www.clarks.in'},
            {'name': 'Timberland', 'url': 'https://www.timberland.com'}
        ],
        'nike': [
            {'name': 'Adidas', 'url': 'https://www.adidas.com'},
            {'name': 'Puma', 'url': 'https://www.puma.com'},
            {'name': 'Reebok', 'url': 'https://www.reebok.com'}
        ],
        'adidas': [
            {'name': 'Nike', 'url': 'https://www.nike.com'},
            {'name': 'Puma', 'url': 'https://www.puma.com'},
            {'name': 'Reebok', 'url': 'https://www.reebok.com'}
        ],
        'puma': [
            {'name': 'Nike', 'url': 'https://www.nike.com'},
            {'name': 'Adidas', 'url': 'https://www.adidas.com'},
            {'name': 'Reebok', 'url': 'https://www.reebok.com'}
        ],
        
        # Automotive
        'tesla': [
            {'name': 'BMW', 'url': 'https://www.bmw.com'},
            {'name': 'Mercedes', 'url': 'https://www.mercedes-benz.com'},
            {'name': 'Audi', 'url': 'https://www.audi.com'}
        ],
        'bmw': [
            {'name': 'Mercedes', 'url': 'https://www.mercedes-benz.com'},
            {'name': 'Audi', 'url': 'https://www.audi.com'},
            {'name': 'Lexus', 'url': 'https://www.lexus.com'}
        ],
        
        # Streaming
        'netflix': [
            {'name': 'Disney', 'url': 'https://www.disneyplus.com'},
            {'name': 'Hulu', 'url': 'https://www.hulu.com'},
            {'name': 'Prime', 'url': 'https://www.primevideo.com'}
        ],
        'spotify': [
            {'name': 'Apple', 'url': 'https://music.apple.com'},
            {'name': 'YouTube', 'url': 'https://music.youtube.com'},
            {'name': 'Amazon', 'url': 'https://music.amazon.com'}
        ],
        
        # Food & Beverage
        'starbucks': [
            {'name': 'Dunkin', 'url': 'https://www.dunkindonuts.com'},
            {'name': 'Costa', 'url': 'https://www.costa.co.uk'},
            {'name': 'Peets', 'url': 'https://www.peets.com'}
        ],
        'mcdonalds': [
            {'name': 'Burgerking', 'url': 'https://www.bk.com'},
            {'name': 'KFC', 'url': 'https://www.kfc.com'},
            {'name': 'Wendys', 'url': 'https://www.wendys.com'}
        ]
    }
    
    # If company not in map, return empty to force API usage
    return competitor_map.get(company_name.lower(), [])
