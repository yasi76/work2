import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from typing import Optional, Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CompanyNameExtractor:
    """Extract company names from URLs using multiple methods in priority order."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_company_name(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract company name using multiple methods in priority order.
        Returns a dictionary with all extracted names and the final result.
        """
        results = {
            'og_site_name': None,
            'application_name': None,
            'title': None,
            'cleaned_title': None,
            'h1': None,
            'logo_alt': None,
            'domain_based': None,
            'final_result': None
        }
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Check og:site_name (highest priority)
            og_site_name = soup.find('meta', property='og:site_name')
            if og_site_name and og_site_name.get('content'):
                results['og_site_name'] = og_site_name['content'].strip()
                results['final_result'] = results['og_site_name']
                logger.info(f"Found company name from og:site_name: {results['og_site_name']}")
                return results
            
            # 2. Check application-name
            app_name = soup.find('meta', attrs={'name': 'application-name'})
            if app_name and app_name.get('content'):
                results['application_name'] = app_name['content'].strip()
                results['final_result'] = results['application_name']
                logger.info(f"Found company name from application-name: {results['application_name']}")
                return results
            
            # 3. Extract from title tag
            if soup.title and soup.title.string:
                full_title = soup.title.string.strip()
                results['title'] = full_title
                
                # Clean the title
                cleaned = self._clean_title(full_title)
                if cleaned and cleaned.lower() not in ['home', 'welcome', 'index']:
                    results['cleaned_title'] = cleaned
                    results['final_result'] = cleaned
                    logger.info(f"Found company name from title: {cleaned}")
                    return results
            
            # 4. Check H1 tags
            h1_tags = soup.find_all('h1')
            for h1 in h1_tags:
                h1_text = h1.get_text(strip=True)
                if h1_text and len(h1_text) < 50:  # Reasonable length for company name
                    results['h1'] = h1_text
                    results['final_result'] = h1_text
                    logger.info(f"Found company name from H1: {h1_text}")
                    return results
            
            # 5. Check logo alt text
            logo_patterns = ['logo', 'brand', 'company']
            for pattern in logo_patterns:
                logo = soup.find('img', alt=re.compile(pattern, re.I))
                if logo and logo.get('alt'):
                    alt_text = self._clean_logo_alt(logo['alt'])
                    if alt_text:
                        results['logo_alt'] = alt_text
                        results['final_result'] = alt_text
                        logger.info(f"Found company name from logo alt: {alt_text}")
                        return results
            
            # 6. Fallback to domain-based extraction
            domain_name = self._extract_from_domain(url)
            if domain_name:
                results['domain_based'] = domain_name
                results['final_result'] = domain_name
                logger.info(f"Using domain-based extraction: {domain_name}")
                
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            # If we can't fetch the page, at least try domain extraction
            domain_name = self._extract_from_domain(url)
            if domain_name:
                results['domain_based'] = domain_name
                results['final_result'] = domain_name
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
        
        return results
    
    def _clean_title(self, title: str) -> Optional[str]:
        """Clean and extract company name from title tag."""
        if not title:
            return None
        
        # Common patterns to remove
        patterns = [
            r'\s*[\||\-|–|—|·|•|:]\s*Home\s*$',
            r'^Home\s*[\||\-|–|—|·|•|:]\s*',
            r'\s*[\||\-|–|—|·|•|:]\s*Welcome\s*$',
            r'^Welcome to\s*',
            r'\s*[\||\-|–|—|·|•|:]\s*Official (Website|Site)\s*$',
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.I)
        
        # If title contains separator, extract the most meaningful part
        separators = ['|', '-', '–', '—', '·', '•', ':']
        for sep in separators:
            if sep in cleaned:
                parts = [p.strip() for p in cleaned.split(sep)]
                # Filter out generic terms
                generic_terms = ['home', 'welcome', 'official', 'website', 'site', 'page']
                meaningful_parts = [p for p in parts if p.lower() not in generic_terms and len(p) > 2]
                if meaningful_parts:
                    return meaningful_parts[0]
        
        return cleaned.strip() if cleaned.strip() else None
    
    def _clean_logo_alt(self, alt_text: str) -> Optional[str]:
        """Clean logo alt text to extract company name."""
        if not alt_text:
            return None
        
        # Remove common suffixes/prefixes
        patterns = [
            r'\s*logo\s*$',
            r'^\s*logo\s+',
            r'\s*brand\s*$',
            r'\s*icon\s*$',
            r'\s*image\s*$',
        ]
        
        cleaned = alt_text
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.I)
        
        return cleaned.strip() if cleaned.strip() else None
    
    def _extract_from_domain(self, url: str) -> Optional[str]:
        """Extract company name from domain as last resort."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www
            domain = re.sub(r'^www\.', '', domain)
            
            # Extract main part before TLD
            parts = domain.split('.')
            if len(parts) >= 2:
                main_part = parts[0]
                
                # Handle special cases like 'get-company' or 'company-app'
                main_part = re.sub(r'^(get|app|my|the)[-_]', '', main_part)
                main_part = re.sub(r'[-_](app|online|web|site)$', '', main_part)
                
                # Convert to title case and handle hyphens/underscores
                company_name = main_part.replace('-', ' ').replace('_', ' ').title()
                
                return company_name if company_name else None
                
        except Exception as e:
            logger.error(f"Error extracting from domain: {e}")
            return None
    
    def process_urls(self, urls: List[str], delay: float = 1.0) -> Dict[str, Dict]:
        """Process multiple URLs with rate limiting."""
        results = {}
        
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")
            results[url] = self.extract_company_name(url)
            
            # Rate limiting
            if i < len(urls) - 1:
                time.sleep(delay)
        
        return results


def main():
    """Example usage with test URLs."""
    test_urls = [
        "https://floy.health",
        "https://www.actimi.com",
        "https://getnutrio.shop",
        "https://example.com",
        "floy.health",  # Test without protocol
    ]
    
    extractor = CompanyNameExtractor()
    
    print("\n" + "="*80)
    print("Company Name Extraction Results")
    print("="*80 + "\n")
    
    for url in test_urls:
        print(f"\nURL: {url}")
        print("-" * 40)
        
        result = extractor.extract_company_name(url)
        
        print(f"Final Result: {result['final_result'] or 'Not found'}")
        print("\nAll extracted values:")
        for method, value in result.items():
            if method != 'final_result' and value:
                print(f"  - {method}: {value}")
    
    print("\n" + "="*80)
    
    # Batch processing example
    print("\nBatch Processing Example:")
    print("-" * 40)
    
    batch_results = extractor.process_urls(test_urls[:3])
    
    for url, data in batch_results.items():
        print(f"\n{url}: {data['final_result'] or 'Not found'}")


if __name__ == "__main__":
    main()