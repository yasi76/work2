#!/usr/bin/env python3
"""
Product Extractor for Digital Health Startups
Extracts product names and types from validated startup URLs
Features: Web crawling, product identification, type classification, ground truth validation
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import logging
from typing import Dict, List, Optional, Tuple, Set
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Try to import optional dependencies
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except:
    HAS_SPACY = False
    logger.info("spaCy not available. Install with: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except:
    HAS_PLAYWRIGHT = False
    logger.info("Playwright not available. Install with: pip install playwright && playwright install")


class ProductExtractor:
    def __init__(self, timeout: int = 10, use_js: bool = False):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.use_js = use_js and HAS_PLAYWRIGHT
        self.ground_truth = self._load_ground_truth()
        self.extraction_stats = Counter()
        
        # Product paths to check
        self.product_paths = [
            '/products', '/solutions', '/services', '/apps', '/platform', '/plattform',
            '/angebot', '/angebote', '/produkte', '/leistungen', '/features',
            '/tools', '/modules', '/portfolio', '/offerings'
        ]
        
        # Product type keywords for classification
        self.product_type_keywords = {
            'app': ['app', 'application', 'mobile', 'ios', 'android', 'download'],
            'software': ['software', 'saas', 'cloud', 'web-based', 'online', 'digital'],
            'wearable': ['wearable', 'device', 'sensor', 'monitor', 'tracker', 'band', 'watch'],
            'service': ['service', 'consulting', 'therapy', 'coaching', 'training', 'support'],
            'platform': ['platform', 'plattform', 'portal', 'dashboard', 'system'],
            'tool': ['tool', 'utility', 'diagnostic', 'assessment', 'analyzer'],
            'hardware': ['hardware', 'equipment', 'device', 'kit', 'set', 'module'],
            'ai_tool': ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 'prediction']
        }
        
    def _load_ground_truth(self) -> Dict[str, Dict]:
        """Load ground truth product data"""
        # Ground truth from user's provided data
        product_url_dict = {
            "Acalta": "https://www.acalta.de",
            "Actimi Herzinsuffizienz Set": "https://www.actimi.com",
            "Actimi Notaufnahme-Set": "https://www.actimi.com",
            "Emmora": "https://www.emmora.de",
            "ALFA AI": "https://www.alfa-ai.com",
            "apheris": "https://www.apheris.com",
            "Aporize": "https://www.aporize.com",
            "Lena": "https://www.arztlena.com",
            "Aura": "https://www.aurahealth.tech",
            "Nutrio App": "https://shop.getnutrio.com",
            "Auta Health": "https://www.auta.health",
            "auvisus": "https://visioncheckout.com",
            "AVAL": "https://www.avayl.tech",
            "avi Impact": "https://www.avimedical.com/avi-impact",
            "BECURE": "https://de.becureglobal.com",
            "Belle App": "https://bellehealth.co/de",
            "brainjo": "https://www.brainjo.de",
            "Brea App": "https://brea.app",
            "Breathment": "https://breathment.com",
            "Caona Health": "https://de.caona.eu",
            "apoclip": "https://www.careanimations.de",
            "Climedo": "https://www.climedo.de",
            "Clinicserve": "https://www.cliniserve.de",
            "Cogthera App": "https://cogthera.de/#erfahren",
            "comuny": "https://www.comuny.de",
            "CureCurve": "https://curecurve.de/elina-app",
            "Cynteract": "https://www.cynteract.com/de/rehabilitation",
            "Declareme": "https://www.healthmeapp.de/de",
            "lab.capture": "https://deepeye.ai",
            "Denton Systems": "https://denton-systems.de",
            "derma2go": "https://www.derma2go.com",
            "dianovi": "https://www.dianovi.com",
            "Dopavision": "http://dopavision.com",
            "Empident": "https://www.empident.de",
            "eye2you": "https://eye2you.ai",
            "FitwHit": "https://www.fitwhit.de",
            "Floy Radiology": "https://www.floy.com",
            "fyzo Assistant": "https://fyzo.de/assistant",
            "fyzo coach": "https://fyzo.de/assistant",
            "gesund.de App": "https://www.gesund.de/app",
            "GLACIE": "https://www.glaice.de",
            "Einfach Retten App": "https://www.help-app.de",
            "GuideCare": "https://www.guidecare.de",
            "apodienste": "https://www.apodienste.com",
            "HELP": "https://www.help-app.de",
            "heynannyly": "https://www.heynanny.com",
            "inContAlert": "https://incontalert.de",
            "InformMe": "https://home.informme.info",
            "Kranus Lutera": "https://www.kranushealth.com/de/therapien/haeufiger-harndrang",
            "Kranus Mictera": "https://www.kranushealth.com/de/therapien/inkontinenz",
        }
        
        # Organize by URL for easier lookup
        ground_truth = defaultdict(list)
        for product_name, url in product_url_dict.items():
            # Normalize URL
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            ground_truth[base_url].append({
                'name': product_name,
                'type': self._classify_product_type_from_name(product_name)
            })
        
        return dict(ground_truth)
    
    def _classify_product_type_from_name(self, product_name: str) -> str:
        """Classify product type based on product name"""
        name_lower = product_name.lower()
        
        # Direct indicators in name
        if 'app' in name_lower:
            return 'app'
        elif 'set' in name_lower:
            return 'hardware'
        elif 'assistant' in name_lower or 'coach' in name_lower:
            return 'software'
        elif 'ai' in name_lower:
            return 'ai_tool'
        elif any(keyword in name_lower for keyword in ['system', 'systems']):
            return 'platform'
        
        return 'service'  # Default
    
    def extract_products_from_page(self, url: str, html_content: Optional[str] = None) -> Dict:
        """Extract products from a single page"""
        products = []
        
        try:
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                if self.use_js:
                    html_content = self._fetch_with_playwright(url)
                    soup = BeautifulSoup(html_content, 'html.parser')
                else:
                    response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                        return {'products': products, 'error': f'HTTP {response.status_code}'}
                    soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract potential product names
            raw_products = self._extract_raw_products(soup, url)
            
            # Classify each product
            for product_name in raw_products:
                product_type = self._classify_product(product_name, soup)
                products.append({
                    'name': product_name,
                    'type': product_type,
                    'source_url': url
                })
            
            return {'products': products}
            
        except Exception as e:
            logger.error(f"Error extracting products from {url}: {str(e)}")
            return {'products': products, 'error': str(e)}
    
    def _fetch_with_playwright(self, url: str) -> str:
        """Fetch page content using Playwright for JS rendering"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
                page.wait_for_timeout(2000)
                content = page.content()
            finally:
                browser.close()
                
        return content
    
    def _extract_raw_products(self, soup: BeautifulSoup, url: str) -> Set[str]:
        """Extract potential product names from page"""
        products = set()
        
        # Strategy 1: Look for product cards/tiles
        product_indicators = ['product', 'produkt', 'solution', 'lösung', 'service', 'app', 'tool']
        
        # Check divs with product-related classes
        for indicator in product_indicators:
            for element in soup.find_all(['div', 'section', 'article'], 
                                       class_=re.compile(indicator, re.IGNORECASE)):
                # Look for headings within these elements
                for heading in element.find_all(['h1', 'h2', 'h3', 'h4']):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 50:
                        products.add(text)
        
        # Strategy 2: Look for specific product patterns in headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)
            # Check if it mentions product keywords
            if any(keyword in text.lower() for keyword in ['app', 'platform', 'tool', 'service', 'system']):
                # Extract the product name (usually before the keyword)
                for keyword in ['app', 'platform', 'tool', 'service', 'system']:
                    if keyword in text.lower():
                        parts = text.lower().split(keyword)
                        if parts[0].strip():
                            product_name = text[:text.lower().find(keyword)].strip()
                            if product_name and len(product_name) > 2:
                                products.add(product_name)
        
        # Strategy 3: Extract from meta tags
        # og:title often contains product names
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            content = og_title['content']
            # Extract product-like names
            if any(keyword in content.lower() for keyword in self.product_type_keywords.keys()):
                products.add(content.split('-')[0].strip())
        
        # Strategy 4: Look for schema.org Product data
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                data = json.loads(script.string)
                products.update(self._extract_from_schema(data))
            except:
                pass
        
        # Strategy 5: Extract from lists of features/products
        for ul in soup.find_all('ul'):
            # Check if this list might contain products
            parent_text = ''
            if ul.parent:
                parent_text = ul.parent.get_text(strip=True).lower()
            
            if any(indicator in parent_text for indicator in ['product', 'solution', 'feature', 'tool']):
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 50:
                        # Check if it looks like a product name
                        if text[0].isupper() or any(keyword in text.lower() for keyword in self.product_type_keywords.keys()):
                            products.add(text)
        
        # Strategy 6: Use NLP if available
        if HAS_SPACY:
            # Extract from main content
            main_content = soup.find(['main', 'article']) or soup.find('body')
            if main_content:
                text = main_content.get_text(strip=True)[:5000]  # First 5000 chars
                doc = nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ in ["PRODUCT", "ORG"]:
                        # Check if it's followed by product keywords
                        following_text = text[ent.end_char:ent.end_char+20].lower()
                        if any(keyword in following_text for keyword in self.product_type_keywords.keys()):
                            products.add(ent.text.strip())
        
        return products
    
    def _extract_from_schema(self, data: any) -> Set[str]:
        """Extract product names from schema.org data"""
        products = set()
        
        if isinstance(data, dict):
            if data.get('@type') == 'Product' and data.get('name'):
                products.add(data['name'])
            elif data.get('@type') == 'SoftwareApplication' and data.get('name'):
                products.add(data['name'])
            elif '@graph' in data:
                for item in data['@graph']:
                    products.update(self._extract_from_schema(item))
        elif isinstance(data, list):
            for item in data:
                products.update(self._extract_from_schema(item))
        
        return products
    
    def _classify_product(self, product_name: str, soup: BeautifulSoup) -> str:
        """Classify the type of a product"""
        name_lower = product_name.lower()
        
        # Check product name against type keywords
        type_scores = Counter()
        
        for product_type, keywords in self.product_type_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    type_scores[product_type] += 2  # Higher weight for name match
        
        # Check context around product mentions
        for text in soup.find_all(text=re.compile(re.escape(product_name), re.IGNORECASE)):
            if text.parent:
                context = text.parent.get_text(strip=True).lower()
                for product_type, keywords in self.product_type_keywords.items():
                    for keyword in keywords:
                        if keyword in context:
                            type_scores[product_type] += 1
        
        # Return the most likely type
        if type_scores:
            return type_scores.most_common(1)[0][0]
        
        # Default classification based on patterns
        if 'app' in name_lower:
            return 'app'
        elif any(word in name_lower for word in ['assistant', 'coach', 'manager']):
            return 'software'
        elif any(word in name_lower for word in ['set', 'kit', 'device']):
            return 'hardware'
        
        return 'service'  # Default
    
    def extract_products_from_company(self, company_data: Dict) -> Dict:
        """Extract products for a single company"""
        url = company_data.get('final_url') or company_data.get('url', '')
        company_name = company_data.get('company_name', 'Unknown')
        
        if not url or not company_data.get('is_live', False):
            logger.warning(f"Skipping {company_name}: URL not live or missing")
            return {
                'company_name': company_name,
                'url': url,
                'products': [],
                'extraction_method': 'skipped'
            }
        
        all_products = []
        checked_urls = set()
        
        # Parse base URL
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check main page
        logger.info(f"Extracting products from {company_name} ({url})")
        main_result = self.extract_products_from_page(url)
        all_products.extend(main_result.get('products', []))
        checked_urls.add(url)
        
        # Check product-specific pages
        for path in self.product_paths:
            product_url = urljoin(base_url, path)
            if product_url not in checked_urls:
                try:
                    # Quick HEAD request to check if page exists
                    head_response = self.session.head(product_url, timeout=5, allow_redirects=True)
                    if head_response.status_code == 200:
                        logger.info(f"Checking product page: {product_url}")
                        result = self.extract_products_from_page(product_url)
                        all_products.extend(result.get('products', []))
                        checked_urls.add(product_url)
                        time.sleep(0.5)  # Be polite
                except:
                    pass
        
        # Deduplicate products by name
        unique_products = {}
        for product in all_products:
            name = product['name']
            if name not in unique_products:
                unique_products[name] = product
        
        # Check against ground truth
        ground_truth_products = self.ground_truth.get(base_url, [])
        found_gt_products = []
        missed_gt_products = []
        
        product_names = [p['name'].lower() for p in unique_products.values()]
        
        for gt_product in ground_truth_products:
            if gt_product['name'].lower() in product_names:
                found_gt_products.append(gt_product['name'])
            else:
                missed_gt_products.append(gt_product['name'])
        
        return {
            'company_name': company_name,
            'url': url,
            'product_names': list(unique_products.keys()),
            'product_types': {name: prod['type'] for name, prod in unique_products.items()},
            'products': list(unique_products.values()),
            'extraction_method': 'crawled',
            'pages_checked': len(checked_urls),
            'ground_truth_found': found_gt_products,
            'ground_truth_missed': missed_gt_products
        }


def process_companies_file(input_file: str, output_prefix: str, max_workers: int = 5, 
                          use_js: bool = False, limit: Optional[int] = None):
    """Process companies file and extract products"""
    
    # Load companies data
    logger.info(f"Loading companies from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different input formats
    if isinstance(data, list):
        companies = data
    elif isinstance(data, dict) and 'urls' in data:
        companies = data['urls']
    else:
        companies = []
        for key, value in data.items():
            if isinstance(value, dict) and 'url' in value:
                companies.append(value)
    
    if limit:
        companies = companies[:limit]
    
    logger.info(f"Processing {len(companies)} companies")
    
    # Initialize extractor
    extractor = ProductExtractor(use_js=use_js)
    
    # Process companies in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_company = {
            executor.submit(extractor.extract_products_from_company, company): i
            for i, company in enumerate(companies)
        }
        
        for future in as_completed(future_to_company):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing company: {str(e)}")
    
    # Calculate statistics
    total_products = sum(len(r.get('product_names', [])) for r in results)
    companies_with_products = sum(1 for r in results if r.get('product_names'))
    
    # Ground truth statistics
    total_gt_found = sum(len(r.get('ground_truth_found', [])) for r in results)
    total_gt_missed = sum(len(r.get('ground_truth_missed', [])) for r in results)
    total_gt = total_gt_found + total_gt_missed
    
    # Product type distribution
    type_counter = Counter()
    for result in results:
        for product_type in result.get('product_types', {}).values():
            type_counter[product_type] += 1
    
    # Log summary
    logger.info("\n" + "="*50)
    logger.info("EXTRACTION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total companies processed: {len(results)}")
    logger.info(f"Companies with products found: {companies_with_products}")
    logger.info(f"Total products extracted: {total_products}")
    logger.info(f"Average products per company: {total_products/len(results):.1f}")
    
    if total_gt > 0:
        logger.info(f"\nGround Truth Validation:")
        logger.info(f"  Found: {total_gt_found}/{total_gt} ({total_gt_found/total_gt*100:.1f}%)")
        logger.info(f"  Missed: {total_gt_missed}/{total_gt} ({total_gt_missed/total_gt*100:.1f}%)")
    
    logger.info(f"\nProduct Type Distribution:")
    for product_type, count in type_counter.most_common():
        logger.info(f"  {product_type}: {count}")
    
    # Save results
    output_json = f"{output_prefix}_products.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved product data to {output_json}")
    
    # Save CSV
    output_csv = f"{output_prefix}_products.csv"
    csv_data = []
    for result in results:
        for product_name in result.get('product_names', []):
            csv_data.append({
                'company_name': result['company_name'],
                'company_url': result['url'],
                'product_name': product_name,
                'product_type': result['product_types'].get(product_name, 'unknown')
            })
    
    if csv_data:
        keys = csv_data[0].keys()
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_data)
        logger.info(f"Saved product CSV to {output_csv}")
    
    # Save statistics
    stats_file = f"{output_prefix}_product_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_companies': len(results),
            'companies_with_products': companies_with_products,
            'total_products': total_products,
            'avg_products_per_company': total_products/len(results) if results else 0,
            'product_type_distribution': dict(type_counter),
            'ground_truth_validation': {
                'found': total_gt_found,
                'missed': total_gt_missed,
                'total': total_gt,
                'accuracy': f"{total_gt_found/total_gt*100:.1f}%" if total_gt > 0 else "N/A"
            }
        }, f, indent=2)
    logger.info(f"Saved statistics to {stats_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract products from digital health startup websites')
    parser.add_argument('input_file', help='JSON file with company data (output from extract_company_names.py)')
    parser.add_argument('--output-prefix', default='products', help='Output file prefix')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximum parallel workers')
    parser.add_argument('--js', action='store_true', help='Use headless browser for JavaScript-heavy sites')
    parser.add_argument('--limit', type=int, help='Limit number of companies to process')
    
    args = parser.parse_args()
    
    process_companies_file(args.input_file, args.output_prefix, args.max_workers, args.js, args.limit)


if __name__ == "__main__":
    main()