#!/usr/bin/env python3
"""
Digital Health Product Extractor
Extracts product names and categorizes product types from startup websites
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
from collections import Counter
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

# Ground truth product data
GROUND_TRUTH_PRODUCTS = {
    "https://www.acalta.de": ["Acalta"],
    "https://www.actimi.com": ["Actimi Herzinsuffizienz Set", "Actimi Notaufnahme-Set"],
    "https://www.emmora.de": ["Emmora"],
    "https://www.alfa-ai.com": ["ALFA AI"],
    "https://www.apheris.com": ["apheris"],
    "https://www.aporize.com/": ["Aporize"],
    "https://www.arztlena.com/": ["Lena"],
    "https://shop.getnutrio.com/": ["aurora nutrio", "Nutrio App"],
    "https://www.auta.health/": ["Auta Health"],
    "https://visioncheckout.com/": ["auvisus"],
    "https://www.avayl.tech/": ["AVAL"],
    "https://www.avimedical.com/avi-impact": ["avi Impact"],
    "https://de.becureglobal.com/": ["BECURE"],
    "https://bellehealth.co/de/": ["Belle App"],
    "https://www.biotx.ai/": ["biotx.ai"],
    "https://www.brainjo.de/": ["brainjo"],
    "https://brea.app/": ["Brea App"],
    "https://breathment.com/": ["Breathment"],
    "https://de.caona.eu/": ["Caona Health"],
    "https://www.careanimations.de/": ["apoclip"],
    "https://www.climedo.de/": ["Climedo"],
    "https://www.cliniserve.de/": ["Clinicserve"],
    "https://cogthera.de/#erfahren": ["Cogthera App"],
    "https://www.comuny.de/": ["comuny"],
    "https://curecurve.de/elina-app/": ["CureCurve"],
    "https://www.cynteract.com/de/rehabilitation": ["Cynteract"],
    "https://www.healthmeapp.de/de/": ["Declareme"],
    "https://deepeye.ai/": ["deepeye medical"],
    "https://www.deepmentation.ai/": ["lab.capture"],
    "https://denton-systems.de/": ["Denton Systems"],
    "https://www.derma2go.com/": ["derma2go"],
    "https://www.dianovi.com/": ["dianovi"],
    "http://dopavision.com/": ["Dopavision"],
    "https://www.dpv-analytics.com/": ["dpv-analytics"],
    "http://www.ecovery.de/": ["eCovery"],
    "https://elixionmedical.com/": ["Elixion Medical"],
    "https://www.empident.de/": ["Empident"],
    "https://eye2you.ai/": ["eye2you"],
    "https://www.fitwhit.de": ["FitwHit"],
    "https://www.floy.com/": ["Floy Radiology"],
    "https://fyzo.de/assistant/": ["fyzo Assistant", "fyzo coach"],
    "https://www.gesund.de/app": ["gesund.de App"],
    "https://www.glaice.de/": ["GLACIE"],
    "https://gleea.de/": ["Einfach Retten App"],
    "https://www.guidecare.de/": ["GuideCare"],
    "https://www.apodienste.com/": ["apodienste"],
    "https://www.help-app.de/": ["HELP"],
    "https://www.heynanny.com/": ["heynannyly"],
    "https://incontalert.de/": ["inContAlert"],
    "https://home.informme.info/": ["InformMe"],
    "https://www.kranushealth.com/de/therapien/haeufiger-harndrang": ["Kranus Lutera", "Kranus Mictera"],
    # Additional products from the ground truth list
    "MindDoc": ["MindDoc"],
    # Add more as needed
}

# Product type keywords and patterns
PRODUCT_TYPE_PATTERNS = {
    'app': [
        r'\bapp\b', r'\bapplication\b', r'\bmobile\b', r'\bios\b', r'\bandroid\b',
        r'\bdownload\b', r'\bplay store\b', r'\bapp store\b'
    ],
    'software': [
        r'\bsoftware\b', r'\bplatform\b', r'\bplattform\b', r'\bsystem\b', 
        r'\bcloud\b', r'\bsaas\b', r'\bweb\b', r'\bonline\b', r'\bdigital\b'
    ],
    'wearable': [
        r'\bwearable\b', r'\bdevice\b', r'\bsensor\b', r'\bmonitor\b', 
        r'\btracker\b', r'\bwatch\b', r'\bband\b', r'\bhardware\b'
    ],
    'set': [
        r'\bset\b', r'\bkit\b', r'\bbox\b', r'\bpackage\b', r'\bpaket\b'
    ],
    'service': [
        r'\bservice\b', r'\bconsulting\b', r'\bberatung\b', r'\btherapy\b',
        r'\btraining\b', r'\bcoaching\b', r'\bdienstleistung\b'
    ],
    'ai_tool': [
        r'\bai\b', r'\bartificial intelligence\b', r'\bmachine learning\b',
        r'\banalytics\b', r'\balgorithm\b', r'\bdiagnostic\b'
    ],
    'assistant': [
        r'\bassistant\b', r'\bcoach\b', r'\bhelper\b', r'\bguide\b'
    ]
}

# Product name indicators
PRODUCT_INDICATORS = [
    'App', 'Platform', 'Assistant', 'Coach', 'Module', 'Set', 'Tool', 
    'Service', 'System', 'Software', 'Device', 'Monitor', 'Tracker',
    'Suite', 'Solution', 'Pro', 'Plus', 'Premium', 'Basic'
]


class ProductExtractor:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.product_paths = [
            '/products', '/produkte', '/solutions', '/losungen', '/services',
            '/leistungen', '/apps', '/platform', '/plattform', '/angebot',
            '/angebote', '/software', '/tools', '/features'
        ]
        
    def extract_products_from_page(self, url: str, html_content: str = None) -> Dict:
        """Extract products from a single page"""
        products = {
            'found_products': [],
            'product_types': {},
            'extraction_methods': []
        }
        
        try:
            if not html_content:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code != 200:
                    return products
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Method 1: Extract from headings
            for tag in ['h1', 'h2', 'h3', 'h4']:
                for heading in soup.find_all(tag):
                    text = heading.get_text(strip=True)
                    if self._is_likely_product_name(text):
                        products['found_products'].append(text)
                        products['product_types'][text] = self._classify_product_type(text, html_content)
                        products['extraction_methods'].append(f'{tag}_heading')
            
            # Method 2: Extract from schema.org data
            schema_products = self._extract_from_schema(soup)
            for product in schema_products:
                if product not in products['found_products']:
                    products['found_products'].append(product)
                    products['product_types'][product] = self._classify_product_type(product, html_content)
                    products['extraction_methods'].append('schema.org')
            
            # Method 3: Extract from meta tags
            meta_products = self._extract_from_meta_tags(soup)
            for product in meta_products:
                if product not in products['found_products']:
                    products['found_products'].append(product)
                    products['product_types'][product] = self._classify_product_type(product, html_content)
                    products['extraction_methods'].append('meta_tags')
            
            # Method 4: Extract from product cards/tiles
            card_products = self._extract_from_cards(soup)
            for product in card_products:
                if product not in products['found_products']:
                    products['found_products'].append(product)
                    products['product_types'][product] = self._classify_product_type(product, html_content)
                    products['extraction_methods'].append('product_cards')
            
            # Method 5: Extract from lists
            list_products = self._extract_from_lists(soup)
            for product in list_products:
                if product not in products['found_products']:
                    products['found_products'].append(product)
                    products['product_types'][product] = self._classify_product_type(product, html_content)
                    products['extraction_methods'].append('lists')
            
        except Exception as e:
            logger.warning(f"Error extracting products from {url}: {str(e)}")
        
        return products
    
    def _is_likely_product_name(self, text: str) -> bool:
        """Check if text is likely a product name"""
        if not text or len(text) < 2 or len(text) > 50:
            return False
        
        # Skip common non-product phrases
        skip_phrases = [
            'contact', 'kontakt', 'impressum', 'about', 'über uns',
            'home', 'welcome', 'willkommen', 'privacy', 'datenschutz',
            'terms', 'agb', 'login', 'register', 'download'
        ]
        
        text_lower = text.lower()
        for phrase in skip_phrases:
            if phrase in text_lower:
                return False
        
        # Check for product indicators
        for indicator in PRODUCT_INDICATORS:
            if indicator.lower() in text_lower:
                return True
        
        # Check if it's a proper noun (capitalized)
        words = text.split()
        if any(word[0].isupper() for word in words if word):
            # Check if it contains at least one meaningful word
            if len([w for w in words if len(w) > 2]) > 0:
                return True
        
        return False
    
    def _classify_product_type(self, product_name: str, context: str = "") -> str:
        """Classify the product type based on name and context"""
        combined_text = f"{product_name} {context}".lower()
        
        # Check each product type pattern
        type_scores = {}
        for product_type, patterns in PRODUCT_TYPE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    score += 1
            if score > 0:
                type_scores[product_type] = score
        
        # Return the type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        # Default classification based on product name
        product_lower = product_name.lower()
        if 'app' in product_lower:
            return 'app'
        elif 'set' in product_lower:
            return 'set'
        elif 'assistant' in product_lower or 'coach' in product_lower:
            return 'assistant'
        elif any(word in product_lower for word in ['platform', 'plattform', 'system']):
            return 'software'
        
        return 'service'  # Default
    
    def _extract_from_schema(self, soup: BeautifulSoup) -> List[str]:
        """Extract product names from schema.org structured data"""
        products = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Handle different schema structures
                if isinstance(data, dict):
                    if data.get('@type') in ['Product', 'SoftwareApplication', 'MedicalDevice']:
                        if 'name' in data:
                            products.append(data['name'])
                    
                    # Check @graph
                    if '@graph' in data:
                        for item in data['@graph']:
                            if isinstance(item, dict) and item.get('@type') in ['Product', 'SoftwareApplication']:
                                if 'name' in item:
                                    products.append(item['name'])
                
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') in ['Product', 'SoftwareApplication']:
                            if 'name' in item:
                                products.append(item['name'])
                                
            except:
                pass
        
        return products
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract product names from meta tags"""
        products = []
        
        # Check og:title and og:site_name
        for prop in ['og:title', 'og:site_name', 'twitter:title']:
            meta = soup.find('meta', property=prop) or soup.find('meta', attrs={'name': prop})
            if meta and meta.get('content'):
                content = meta['content'].strip()
                if self._is_likely_product_name(content):
                    products.append(content)
        
        # Check application-name
        app_name = soup.find('meta', attrs={'name': 'application-name'})
        if app_name and app_name.get('content'):
            products.append(app_name['content'].strip())
        
        return products
    
    def _extract_from_cards(self, soup: BeautifulSoup) -> List[str]:
        """Extract products from card/tile structures"""
        products = []
        
        # Common card selectors
        card_selectors = [
            'div.product', 'div.feature', 'div.solution', 'div.service',
            'article.product', 'section.product', 'div.card', 'div.tile',
            'div.produkt', 'div.leistung', 'div.angebot'
        ]
        
        for selector in card_selectors:
            for card in soup.select(selector):
                # Look for product name in card headings
                for tag in ['h2', 'h3', 'h4', 'strong', 'b']:
                    heading = card.find(tag)
                    if heading:
                        text = heading.get_text(strip=True)
                        if self._is_likely_product_name(text):
                            products.append(text)
                            break
        
        return products
    
    def _extract_from_lists(self, soup: BeautifulSoup) -> List[str]:
        """Extract products from list structures"""
        products = []
        
        # Look for lists that might contain products
        for ul in soup.find_all('ul'):
            # Check if this looks like a product list
            list_text = ul.get_text().lower()
            if any(word in list_text for word in ['product', 'solution', 'feature', 'produkt', 'lösung']):
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if self._is_likely_product_name(text):
                        # Clean up the text
                        text = re.sub(r'^[•\-\*]\s*', '', text)  # Remove bullets
                        text = text.split(':')[0].strip()  # Take part before colon
                        if len(text) > 2 and len(text) < 50:
                            products.append(text)
        
        return products
    
    def discover_all_products(self, startup_data: Dict) -> Dict:
        """Discover all products for a startup by checking multiple pages"""
        url = startup_data.get('url', '')
        if not url:
            return startup_data
        
        all_products = set()
        all_types = {}
        methods_used = set()
        
        # First check the main page
        main_page_products = self.extract_products_from_page(url)
        all_products.update(main_page_products['found_products'])
        all_types.update(main_page_products['product_types'])
        methods_used.update(main_page_products['extraction_methods'])
        
        # Then check product-specific pages
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        for path in self.product_paths:
            try:
                product_url = urljoin(base_url, path)
                logger.info(f"Checking {product_url} for products")
                
                response = self.session.get(product_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    page_products = self.extract_products_from_page(product_url, response.text)
                    all_products.update(page_products['found_products'])
                    all_types.update(page_products['product_types'])
                    methods_used.update(page_products['extraction_methods'])
                    
                time.sleep(1)  # Rate limiting
                
            except:
                continue
        
        # Update startup data
        startup_data['product_names'] = list(all_products)
        startup_data['product_types'] = all_types
        startup_data['product_extraction_methods'] = list(methods_used)
        
        # Check against ground truth if available
        normalized_url = self._normalize_url_for_gt(url)
        if normalized_url in GROUND_TRUTH_PRODUCTS:
            startup_data['ground_truth_products'] = GROUND_TRUTH_PRODUCTS[normalized_url]
            startup_data['found_gt_products'] = [
                p for p in GROUND_TRUTH_PRODUCTS[normalized_url] 
                if any(p.lower() in found.lower() or found.lower() in p.lower() 
                      for found in all_products)
            ]
        
        return startup_data
    
    def _normalize_url_for_gt(self, url: str) -> str:
        """Normalize URL for ground truth lookup"""
        # Simple normalization - you might need to adjust based on your GT format
        parsed = urlparse(url.lower())
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
        
        # Check exact match first
        if normalized in GROUND_TRUTH_PRODUCTS:
            return normalized
        
        # Check without path
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if base_url in GROUND_TRUTH_PRODUCTS:
            return base_url
        
        # Check with www
        if not parsed.netloc.startswith('www.'):
            with_www = f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}".rstrip('/')
            if with_www in GROUND_TRUTH_PRODUCTS:
                return with_www
        
        return normalized


def process_startups_file(input_file: str, output_prefix: str, max_workers: int = 5):
    """Process startup file to extract products"""
    
    logger.info(f"Loading startups from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different input formats
    if isinstance(data, list):
        startups = data
    elif isinstance(data, dict) and 'urls' in data:
        startups = data['urls']
    else:
        startups = []
        for key, value in data.items():
            if isinstance(value, dict) and 'url' in value:
                startups.append(value)
    
    logger.info(f"Processing {len(startups)} startups for product extraction")
    
    extractor = ProductExtractor()
    
    # Process with parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_startup = {
            executor.submit(extractor.discover_all_products, startup): i
            for i, startup in enumerate(startups)
        }
        
        for future in as_completed(future_to_startup):
            idx = future_to_startup[future]
            try:
                startups[idx] = future.result()
            except Exception as e:
                logger.error(f"Error processing startup: {str(e)}")
    
    # Calculate statistics
    total_products = sum(len(s.get('product_names', [])) for s in startups)
    with_products = sum(1 for s in startups if s.get('product_names'))
    
    # Ground truth statistics
    gt_coverage = 0
    total_gt_products = 0
    found_gt_products = 0
    
    for startup in startups:
        if 'ground_truth_products' in startup:
            total_gt_products += len(startup['ground_truth_products'])
            found_gt_products += len(startup.get('found_gt_products', []))
            if startup.get('found_gt_products'):
                gt_coverage += 1
    
    # Log summary
    logger.info("\n" + "="*50)
    logger.info("PRODUCT EXTRACTION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total startups processed: {len(startups)}")
    logger.info(f"Startups with products found: {with_products}")
    logger.info(f"Total products discovered: {total_products}")
    
    if total_gt_products > 0:
        logger.info(f"\nGround Truth Coverage:")
        logger.info(f"GT products found: {found_gt_products}/{total_gt_products} ({found_gt_products/total_gt_products*100:.1f}%)")
        logger.info(f"Startups with GT matches: {gt_coverage}")
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    
    # Save full JSON
    output_json = f"{output_prefix}_products_{timestamp}.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(startups, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved products data to {output_json}")
    
    # Save CSV summary
    output_csv = f"{output_prefix}_products_{timestamp}.csv"
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['company_name', 'url', 'product_names', 'product_types', 
                     'ground_truth_products', 'found_gt_products']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for startup in startups:
            row = startup.copy()
            row['product_names'] = '; '.join(startup.get('product_names', []))
            row['product_types'] = json.dumps(startup.get('product_types', {}))
            if 'ground_truth_products' in startup:
                row['ground_truth_products'] = '; '.join(startup['ground_truth_products'])
                row['found_gt_products'] = '; '.join(startup.get('found_gt_products', []))
            writer.writerow(row)
    
    logger.info(f"Saved CSV summary to {output_csv}")
    
    # Save product catalog
    catalog_file = f"{output_prefix}_product_catalog_{timestamp}.txt"
    with open(catalog_file, 'w', encoding='utf-8') as f:
        f.write("DIGITAL HEALTH PRODUCT CATALOG\n")
        f.write("="*50 + "\n\n")
        
        for startup in startups:
            if startup.get('product_names'):
                company = startup.get('company_name', 'Unknown')
                f.write(f"\n{company}\n")
                f.write("-"*len(company) + "\n")
                
                for product in startup['product_names']:
                    product_type = startup.get('product_types', {}).get(product, 'Unknown')
                    f.write(f"  • {product} ({product_type})\n")
                
                f.write(f"  URL: {startup.get('url', 'N/A')}\n")
    
    logger.info(f"Saved product catalog to {catalog_file}")


def main():
    parser = argparse.ArgumentParser(description='Extract product names from digital health startups')
    parser.add_argument('input_file', help='JSON file with startup data')
    parser.add_argument('--output-prefix', default='startups', help='Output file prefix')
    parser.add_argument('--max-workers', type=int, default=5, help='Maximum parallel workers')
    
    args = parser.parse_args()
    
    process_startups_file(args.input_file, args.output_prefix, args.max_workers)


if __name__ == "__main__":
    main()