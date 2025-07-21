import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import time
from typing import Optional, Dict, List, Tuple
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedCompanyNameExtractor:
    """Advanced company name extractor with GPT cleaning support and batch processing."""
    
    def __init__(self, timeout: int = 10, use_gpt_cleaning: bool = False, openai_api_key: Optional[str] = None):
        self.timeout = timeout
        self.use_gpt_cleaning = use_gpt_cleaning
        self.openai_api_key = openai_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Enhanced patterns for better extraction
        self.title_separators = ['|', '-', '–', '—', '·', '•', ':', '»', '«', '/', '\\']
        self.generic_terms = [
            'home', 'welcome', 'official', 'website', 'site', 'page', 'index',
            'main', 'landing', 'homepage', 'online', 'portal', 'platform'
        ]
        
        # Company indicators
        self.company_indicators = [
            'inc', 'llc', 'ltd', 'limited', 'corp', 'corporation', 'company',
            'co', 'plc', 'gmbh', 'sa', 'spa', 'ag', 'bv', 'nv'
        ]
    
    def extract_all_methods(self, url: str) -> Dict[str, Optional[str]]:
        """Extract company name using all available methods."""
        results = {
            'url': url,
            'og_site_name': None,
            'og_title': None,
            'twitter_site': None,
            'twitter_title': None,
            'application_name': None,
            'title': None,
            'cleaned_title': None,
            'h1': None,
            'logo_alt': None,
            'json_ld': None,
            'domain_based': None,
            'schema_org': None,
            'final_result': None,
            'confidence_score': 0,
            'extraction_method': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Open Graph metadata (highest priority)
            og_site_name = soup.find('meta', property='og:site_name')
            if og_site_name and og_site_name.get('content'):
                results['og_site_name'] = og_site_name['content'].strip()
                results['final_result'] = results['og_site_name']
                results['confidence_score'] = 0.95
                results['extraction_method'] = 'og:site_name'
                return results
            
            # 2. Schema.org/JSON-LD data
            json_ld_data = self._extract_json_ld(soup)
            if json_ld_data:
                results['json_ld'] = json_ld_data
                results['final_result'] = json_ld_data
                results['confidence_score'] = 0.9
                results['extraction_method'] = 'json-ld'
                return results
            
            # 3. Twitter metadata
            twitter_site = soup.find('meta', attrs={'name': 'twitter:site'})
            if twitter_site and twitter_site.get('content'):
                twitter_name = twitter_site['content'].strip().lstrip('@')
                results['twitter_site'] = twitter_name
                results['final_result'] = twitter_name
                results['confidence_score'] = 0.85
                results['extraction_method'] = 'twitter:site'
                return results
            
            # 4. Application name
            app_name = soup.find('meta', attrs={'name': 'application-name'})
            if app_name and app_name.get('content'):
                results['application_name'] = app_name['content'].strip()
                results['final_result'] = results['application_name']
                results['confidence_score'] = 0.85
                results['extraction_method'] = 'application-name'
                return results
            
            # 5. Enhanced title extraction
            if soup.title and soup.title.string:
                full_title = soup.title.string.strip()
                results['title'] = full_title
                
                cleaned = self._advanced_clean_title(full_title)
                if cleaned and cleaned.lower() not in self.generic_terms:
                    results['cleaned_title'] = cleaned
                    results['final_result'] = cleaned
                    results['confidence_score'] = 0.75
                    results['extraction_method'] = 'title'
                    return results
            
            # 6. Multiple H1 analysis
            h1_text = self._analyze_h1_tags(soup)
            if h1_text:
                results['h1'] = h1_text
                results['final_result'] = h1_text
                results['confidence_score'] = 0.7
                results['extraction_method'] = 'h1'
                return results
            
            # 7. Enhanced logo analysis
            logo_text = self._analyze_logos(soup)
            if logo_text:
                results['logo_alt'] = logo_text
                results['final_result'] = logo_text
                results['confidence_score'] = 0.65
                results['extraction_method'] = 'logo'
                return results
            
            # 8. Schema.org microdata
            schema_name = self._extract_schema_org(soup)
            if schema_name:
                results['schema_org'] = schema_name
                results['final_result'] = schema_name
                results['confidence_score'] = 0.8
                results['extraction_method'] = 'schema.org'
                return results
            
            # 9. Fallback to domain
            domain_name = self._advanced_domain_extraction(url)
            if domain_name:
                results['domain_based'] = domain_name
                results['final_result'] = domain_name
                results['confidence_score'] = 0.5
                results['extraction_method'] = 'domain'
                
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            # Domain extraction as last resort
            domain_name = self._advanced_domain_extraction(url)
            if domain_name:
                results['domain_based'] = domain_name
                results['final_result'] = domain_name
                results['confidence_score'] = 0.3
                results['extraction_method'] = 'domain-fallback'
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
        
        # Optional GPT cleaning
        if self.use_gpt_cleaning and results['final_result'] and self.openai_api_key:
            cleaned_name = self._gpt_clean_name(results['final_result'])
            if cleaned_name:
                results['final_result'] = cleaned_name
                results['confidence_score'] = min(results['confidence_score'] + 0.1, 1.0)
        
        return results
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company name from JSON-LD structured data."""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for Organization or WebSite types
                if data.get('@type') in ['Organization', 'Corporation', 'LocalBusiness', 'WebSite']:
                    return data.get('name', '').strip()
                    
            except json.JSONDecodeError:
                continue
        return None
    
    def _extract_schema_org(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract from schema.org microdata."""
        # Look for itemtype="http://schema.org/Organization"
        org_elem = soup.find(attrs={'itemtype': re.compile(r'schema\.org/(Organization|Corporation|LocalBusiness)', re.I)})
        if org_elem:
            name_elem = org_elem.find(attrs={'itemprop': 'name'})
            if name_elem:
                return name_elem.get_text(strip=True)
        return None
    
    def _analyze_h1_tags(self, soup: BeautifulSoup) -> Optional[str]:
        """Analyze multiple H1 tags and pick the best one."""
        h1_candidates = []
        
        for h1 in soup.find_all('h1'):
            text = h1.get_text(strip=True)
            if not text or len(text) > 100:
                continue
                
            # Score based on various factors
            score = 1.0
            
            # Bonus for being in header/nav
            if h1.find_parent(['header', 'nav']):
                score += 0.5
                
            # Penalty for generic terms
            if any(term in text.lower() for term in self.generic_terms):
                score -= 0.5
                
            # Bonus for company indicators
            if any(indicator in text.lower() for indicator in self.company_indicators):
                score += 0.3
                
            h1_candidates.append((text, score))
        
        # Return highest scoring H1
        if h1_candidates:
            h1_candidates.sort(key=lambda x: x[1], reverse=True)
            return h1_candidates[0][0]
        
        return None
    
    def _analyze_logos(self, soup: BeautifulSoup) -> Optional[str]:
        """Enhanced logo analysis."""
        logo_candidates = []
        
        # Multiple patterns to find logos
        logo_selectors = [
            {'tag': 'img', 'attrs': {'class': re.compile(r'logo', re.I)}},
            {'tag': 'img', 'attrs': {'id': re.compile(r'logo', re.I)}},
            {'tag': 'img', 'attrs': {'alt': re.compile(r'logo|brand', re.I)}},
            {'tag': 'img', 'attrs': {'src': re.compile(r'logo', re.I)}},
        ]
        
        for selector in logo_selectors:
            logos = soup.find_all(**selector)
            for logo in logos:
                alt_text = logo.get('alt', '').strip()
                if alt_text and not alt_text.lower() in ['logo', 'brand', 'image']:
                    cleaned = self._clean_logo_alt(alt_text)
                    if cleaned:
                        logo_candidates.append(cleaned)
        
        # Return most common if multiple found
        if logo_candidates:
            from collections import Counter
            most_common = Counter(logo_candidates).most_common(1)
            return most_common[0][0]
        
        return None
    
    def _advanced_clean_title(self, title: str) -> Optional[str]:
        """Advanced title cleaning with multiple strategies."""
        if not title:
            return None
        
        # Strategy 1: Remove common patterns
        patterns = [
            r'\s*[\||\-|–|—|·|•|:|»|«|/|\\]\s*Home\s*$',
            r'^Home\s*[\||\-|–|—|·|•|:|»|«|/|\\]\s*',
            r'\s*[\||\-|–|—|·|•|:|»|«|/|\\]\s*Welcome.*$',
            r'^Welcome to\s*',
            r'\s*[\||\-|–|—|·|•|:|»|«|/|\\]\s*Official.*$',
            r'\s*[\(\[](.*?)[\)\]]$',  # Remove trailing parentheses
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.I)
        
        # Strategy 2: Smart separator handling
        for sep in self.title_separators:
            if sep in cleaned:
                parts = [p.strip() for p in cleaned.split(sep)]
                
                # Score each part
                scored_parts = []
                for part in parts:
                    if not part or len(part) < 2:
                        continue
                        
                    score = 1.0
                    
                    # Penalty for generic terms
                    if part.lower() in self.generic_terms:
                        score -= 0.8
                    
                    # Bonus for company indicators
                    if any(ind in part.lower() for ind in self.company_indicators):
                        score += 0.5
                    
                    # Bonus for capitalized words (likely proper nouns)
                    capital_ratio = sum(1 for c in part if c.isupper()) / len(part)
                    score += capital_ratio * 0.3
                    
                    scored_parts.append((part, score))
                
                # Return highest scoring part
                if scored_parts:
                    scored_parts.sort(key=lambda x: x[1], reverse=True)
                    return scored_parts[0][0]
        
        return cleaned.strip() if cleaned.strip() else None
    
    def _advanced_domain_extraction(self, url: str) -> Optional[str]:
        """Advanced domain-based extraction."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove subdomain prefixes
            domain = re.sub(r'^(www|app|api|blog|shop|store|my|the)\.', '', domain)
            
            # Extract main part
            parts = domain.split('.')
            if len(parts) >= 2:
                main_part = parts[0]
                
                # Advanced cleaning
                # Remove common prefixes
                prefixes = ['get', 'try', 'use', 'buy', 'shop', 'visit', 'go']
                for prefix in prefixes:
                    main_part = re.sub(f'^{prefix}[-_]?', '', main_part, flags=re.I)
                
                # Remove common suffixes
                suffixes = ['app', 'online', 'web', 'site', 'store', 'shop', 'now', 'hq']
                for suffix in suffixes:
                    main_part = re.sub(f'[-_]?{suffix}$', '', main_part, flags=re.I)
                
                # Handle camelCase and PascalCase
                # Insert spaces before capital letters
                spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', main_part)
                
                # Convert to title case
                company_name = spaced.replace('-', ' ').replace('_', ' ').strip().title()
                
                return company_name if company_name else None
                
        except Exception as e:
            logger.error(f"Error in advanced domain extraction: {e}")
            return None
    
    def _clean_logo_alt(self, alt_text: str) -> Optional[str]:
        """Clean logo alt text."""
        if not alt_text:
            return None
        
        patterns = [
            r'\s*logo\s*$',
            r'^\s*logo\s+',
            r'\s*brand\s*$',
            r'\s*icon\s*$',
            r'\s*image\s*$',
            r'\s*\.(png|jpg|jpeg|gif|svg)\s*$',
        ]
        
        cleaned = alt_text
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.I)
        
        return cleaned.strip() if cleaned.strip() else None
    
    def _gpt_clean_name(self, name: str) -> Optional[str]:
        """Use GPT to clean and improve company name extraction."""
        # This is a placeholder for GPT integration
        # In production, you would call OpenAI API here
        logger.info(f"GPT cleaning would be applied to: {name}")
        return name
    
    def process_urls_parallel(self, urls: List[str], max_workers: int = 5) -> Dict[str, Dict]:
        """Process multiple URLs in parallel."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.extract_all_methods, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results[url] = result
                    logger.info(f"Processed {url}: {result['final_result']}")
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                    results[url] = {'error': str(e), 'final_result': None}
        
        return results
    
    def export_results(self, results: Dict[str, Dict], filename: str = 'company_names.csv'):
        """Export results to CSV."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'url', 'final_result', 'confidence_score', 'extraction_method',
                'og_site_name', 'application_name', 'title', 'cleaned_title',
                'h1', 'logo_alt', 'domain_based', 'timestamp'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for url, data in results.items():
                row = {field: data.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Results exported to {filename}")


def main():
    """Example usage of the advanced extractor."""
    test_urls = [
        "https://floy.health",
        "https://www.actimi.com",
        "https://getnutrio.shop",
        "https://stripe.com",
        "https://github.com",
        "floy.health",
    ]
    
    # Initialize extractor
    extractor = AdvancedCompanyNameExtractor(use_gpt_cleaning=False)
    
    print("\n" + "="*80)
    print("Advanced Company Name Extraction")
    print("="*80 + "\n")
    
    # Single URL processing
    print("Single URL Processing:")
    print("-" * 40)
    
    url = test_urls[0]
    result = extractor.extract_all_methods(url)
    
    print(f"\nURL: {url}")
    print(f"Company Name: {result['final_result']}")
    print(f"Confidence: {result['confidence_score']:.2f}")
    print(f"Method: {result['extraction_method']}")
    print("\nAll extracted values:")
    for key, value in result.items():
        if key not in ['final_result', 'confidence_score', 'extraction_method', 'timestamp', 'url'] and value:
            print(f"  - {key}: {value}")
    
    # Parallel processing
    print("\n\nParallel Processing:")
    print("-" * 40)
    
    results = extractor.process_urls_parallel(test_urls)
    
    for url, data in results.items():
        if 'error' not in data:
            print(f"\n{url}")
            print(f"  → {data['final_result']} (confidence: {data['confidence_score']:.2f}, method: {data['extraction_method']})")
    
    # Export results
    extractor.export_results(results)
    print(f"\n\nResults exported to company_names.csv")


if __name__ == "__main__":
    main()