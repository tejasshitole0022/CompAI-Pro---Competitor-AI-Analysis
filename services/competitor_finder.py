import logging
import os
import re
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_company_info(company_url, api_key):
    """Get detailed information about what the company does"""
    try:
        parsed = urlparse(company_url)
        domain = parsed.netloc or company_url
        company_name = domain.replace('www.', '').split('.')[0]
        
        url = "https://serpapi.com/search"
        params = {
            'q': f'"{company_name}" company industry business',
            'api_key': api_key,
            'engine': 'google',
            'num': 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        description = ""
        industry = ""
        
        # Extract from knowledge graph first (most accurate)
        if 'knowledge_graph' in data:
            kg = data['knowledge_graph']
            description = kg.get('description', '')
            if 'type' in kg:
                industry = kg.get('type', '')
        
        # Extract from answer box
        if 'answer_box' in data:
            description += " " + data['answer_box'].get('snippet', '')
        
        # Extract from organic results
        if 'organic_results' in data:
            for result in data['organic_results'][:3]:
                snippet = result.get('snippet', '')
                if company_name.lower() in snippet.lower():
                    description += " " + snippet
        
        full_info = f"{industry} {description}".strip()
        logger.info(f"Company info for {company_name}: {full_info[:150]}...")
        return full_info
    except Exception as e:
        logger.warning(f"Failed to get company info: {e}")
        return ""

def find_competitors(company_url):
    """Find top 3 competitors using API"""
    try:
        # Add protocol if missing
        if not company_url.startswith(('http://', 'https://')):
            company_url = 'https://' + company_url
        
        parsed = urlparse(company_url)
        domain = parsed.netloc or company_url
        company_name = domain.replace('www.', '').split('.')[0]
        
        logger.info(f"Searching competitors for: {company_name} ({company_url})")
        
        # Try API first if key is available
        api_key = os.getenv('SERPAPI_KEY')
        if not api_key:
            logger.error("No SERPAPI_KEY found in environment")
            return []
        
        logger.info("Using SerpAPI for competitor search")
        
        # Get detailed company information
        company_info = get_company_info(company_url, api_key)
        
        # Search for competitors with context
        competitors = search_competitors_api(company_name, company_info, api_key)
        
        if competitors and len(competitors) > 0:
            logger.info(f"Found {len(competitors)} unique competitors")
            return competitors[:3]
        else:
            logger.warning("No competitors found")
            return []
            
    except Exception as e:
        logger.error(f"Error finding competitors: {e}")
        raise

def search_competitors_api(company_name, company_info, api_key):
    """Search for competitors using SerpAPI with context-aware queries"""
    try:
        # Extract industry keywords from company info
        industry_keywords = extract_industry_keywords(company_info)
        
        # Build targeted search queries with fallbacks
        search_queries = []
        
        if industry_keywords:
            search_queries.append(f'{company_name} competitors {industry_keywords}')
            search_queries.append(f'top {industry_keywords} companies')
        
        # Simpler, more reliable searches
        search_queries.append(f'{company_name} competitors')
        search_queries.append(f'{company_name} vs')
        search_queries.append(f'companies like {company_name}')
        
        all_competitors = []
        seen = set([company_name.lower()])
        
        # Minimal blacklist - only obvious non-competitors
        blacklist = {
            'google', 'wikipedia', 'facebook', 'twitter', 'linkedin', 'youtube', 
            'instagram', 'reddit', 'medium', 'wordpress', 'github'
        }
        
        for query in search_queries:
            if len(all_competitors) >= 5:
                break
                
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'api_key': api_key,
                'engine': 'google',
                'num': 20
            }
            
            logger.info(f"Searching: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                logger.error(f"SERP API error: {data['error']}")
                continue
            
            # Extract from organic results
            for result in data.get('organic_results', []):
                if len(all_competitors) >= 5:
                    break
                
                link = result.get('link', '')
                
                # Only skip obvious review aggregators
                skip_domains = ['g2.com', 'capterra.com', 'trustpilot.com', 'play.google.com', 'apps.apple.com']
                
                if any(sd in link.lower() for sd in skip_domains):
                    continue
                
                # Extract domain
                try:
                    parsed = urlparse(link)
                    domain = parsed.netloc.replace('www.', '')
                    company = domain.split('.')[0]
                    
                    if (company and 
                        company.lower() not in blacklist and 
                        company.lower() not in seen and
                        len(company) >= 2 and
                        '.' in domain):
                        
                        seen.add(company.lower())
                        all_competitors.append({
                            'name': company.capitalize(),
                            'url': f"https://{domain}"
                        })
                        logger.info(f"Found competitor: {company.capitalize()}")
                except:
                    continue
        
        logger.info(f"Total competitors found: {len(all_competitors)}")
        return all_competitors[:3]
        
    except Exception as e:
        logger.warning(f"API search failed: {e}")
        return []

def extract_industry_keywords(company_info):
    """Extract relevant industry keywords from company description"""
    if not company_info:
        return ""
    
    # Common industry patterns
    patterns = [
        r'(e-commerce|ecommerce)',
        r'(streaming|video|music)',
        r'(social media|social network)',
        r'(cloud|software|saas)',
        r'(payment|fintech|financial)',
        r'(gaming|game)',
        r'(retail|shopping)',
        r'(travel|booking|hotel)',
        r'(food delivery|restaurant)',
        r'(ride sharing|transportation)',
        r'(healthcare|medical)',
        r'(education|learning)',
        r'(creator|content platform)',
        r'(marketplace)',
        r'(electronics|technology)',
        r'(fashion|apparel)',
        r'(automotive|car)',
        r'(real estate|property)'
    ]
    
    info_lower = company_info.lower()
    for pattern in patterns:
        match = re.search(pattern, info_lower)
        if match:
            return match.group(1)
    
    return ""

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
