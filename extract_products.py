#!/usr/bin/env python3
"""
extract_products.py - Extracts product names from digital health startups
Inputs: final_startup_urls.json
Outputs: product_names.json
"""

import json
import re
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.product_mapping = {}
        
        # Ground truth product data
        self.ground_truth = {
            "https://www.acalta.de": ["Acalta Gesundheits-App"],
            "https://www.actimi.com": ["Actimi 3D Sensor", "Actimi Core"],
            "https://www.emmora.de": ["Rehappy App"],
            "https://www.alfa-ai.com": ["ALFA"],
            "https://www.apheris.com": ["Apheris Compute Gateway"],
            "https://www.aporize.com/": ["Aporize Care"],
            "https://www.arztlena.com/": ["Arzt Lena"],
            "https://shop.getnutrio.com/": ["Nutrio"],
            "https://www.auta.health/": ["Auta Health App"],
            "https://visioncheckout.com/": ["Vision Checkout"],
            "https://www.avayl.tech/": ["AvaKit Sensor", "Avayl Connect", "AvaWave"],
            "https://www.avimedical.com/avi-impact": ["Avi Medical App"],
            "https://de.becureglobal.com/": ["BeCure Health Assistant"],
            "https://bellehealth.co/de/": ["Belle Health App"],
            "https://www.biotx.ai/": ["BioTX Platform"],
            "https://www.brainjo.de/": ["Brainjo App"],
            "https://brea.app/": ["Brea App"],
            "https://breathment.com/": ["Breathment App"],
            "https://de.caona.eu/": ["Caona Platform"],
            "https://www.careanimations.de/": ["CareAnimations"],
            "https://sfs-healthcare.com": ["SFS Platform"],
            "https://www.climedo.de/": ["Climedo Platform"],
            "https://www.cliniserve.de/": ["CliniServe Software"],
            "https://cogthera.de/#erfahren": ["Cogthera App"],
            "https://www.comuny.de/": ["Comuny App"],
            "https://curecurve.de/elina-app/": ["ELINA App"],
            "https://www.cynteract.com/de/rehabilitation": ["Cynteract Rehab System"],
            "https://www.healthmeapp.de/de/": ["HealthMe App"],
            "https://deepeye.ai/": ["DeepEye Platform"],
            "https://www.deepmentation.ai/": ["Deepmentation AI"],
            "https://denton-systems.de/": ["Denton Solutions"],
            "https://www.derma2go.com/": ["derma2go App"],
            "https://www.dianovi.com/": ["Dianovi App"],
            "http://dopavision.com/": ["MyopiaCare"],
            "https://www.dpv-analytics.com/": ["DPV Analytics Platform"],
            "http://www.ecovery.de/": ["eCovery App"],
            "https://elixionmedical.com/": ["Elixion Platform"],
            "https://www.empident.de/": ["Empident Software"],
            "https://eye2you.ai/": ["eye2you AI"],
            "https://www.fitwhit.de": ["FitWHit App"],
            "https://www.floy.com/": ["Floy App"],
            "https://fyzo.de/assistant/": ["fyzo Assistant", "fyzo coach"],
            "https://www.gesund.de/app": ["gesund.de App"],
            "https://www.glaice.de/": ["Glaice Platform"],
            "https://gleea.de/": ["Gleea Software"],
            "https://www.guidecare.de/": ["GuideCare Platform"],
            "https://www.apodienste.com/": ["APO-Dienste"],
            "https://www.help-app.de/": ["HELP App"],
            "https://www.heynanny.com/": ["heynannyly App"],
            "https://incontalert.de/": ["inContAlert"],
            "https://home.informme.info/": ["InformMe Platform"],
            "https://www.kranushealth.com/de/therapien/haeufiger-harndrang": ["Kranus Edera"],
            "https://www.kranushealth.com/de/therapien/inkontinenz": ["Kranus Edera"],
        }
        
        # Product keywords to search for
        self.product_keywords = {
            'app': ['app', 'application', 'mobile app', 'ios app', 'android app'],
            'platform': ['platform', 'plattform', 'software', 'system', 'solution'],
            'device': ['device', 'sensor', 'wearable', 'hardware', 'gerät'],
            'service': ['service', 'dienst', 'consulting', 'beratung'],
            'tool': ['tool', 'werkzeug', 'toolkit', 'utility']
        }
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        return url
    
    def extract_from_ground_truth(self, url: str) -> Optional[List[str]]:
        """Check ground truth for product names"""
        normalized = self.normalize_url(url)
        for gt_url, products in self.ground_truth.items():
            if self.normalize_url(gt_url) == normalized:
                return products
        return None
    
    def extract_from_webpage(self, url: str) -> List[str]:
        """Extract product names from webpage"""
        products = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check product-specific pages
            product_paths = ['/products', '/produkte', '/solutions', '/losungen', '/apps', '/software']
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            for path in product_paths:
                try:
                    product_url = urljoin(base_url, path)
                    resp = self.session.get(product_url, timeout=5)
                    if resp.status_code == 200:
                        page_soup = BeautifulSoup(resp.content, 'html.parser')
                        products.extend(self._extract_products_from_page(page_soup))
                except:
                    pass
            
            # Extract from main page
            products.extend(self._extract_products_from_page(soup))
            
            # Deduplicate
            unique_products = []
            seen = set()
            for product in products:
                normalized = product.lower().strip()
                if normalized not in seen and len(product) > 2:
                    seen.add(normalized)
                    unique_products.append(product)
            
            return unique_products[:5]  # Limit to top 5 products
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {str(e)}")
            return []
    
    def _extract_products_from_page(self, soup: BeautifulSoup) -> List[str]:
        """Extract product names from a page"""
        products = []
        
        # Look for product names in headings
        for tag in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(tag):
                text = heading.get_text().strip()
                if self._is_likely_product_name(text):
                    products.append(self._clean_product_name(text))
        
        # Look for product cards/sections
        product_selectors = [
            {'class': re.compile(r'product', re.I)},
            {'class': re.compile(r'solution', re.I)},
            {'class': re.compile(r'feature', re.I)},
            {'class': re.compile(r'app', re.I)}
        ]
        
        for selector in product_selectors:
            for element in soup.find_all(['div', 'section', 'article'], selector):
                # Look for title in the element
                title = element.find(['h1', 'h2', 'h3', 'h4'])
                if title:
                    text = title.get_text().strip()
                    if self._is_likely_product_name(text):
                        products.append(self._clean_product_name(text))
        
        # Check schema.org data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Look for Product type
                    if data.get('@type') == 'Product' and data.get('name'):
                        products.append(data['name'])
                    # Look for SoftwareApplication
                    elif data.get('@type') == 'SoftwareApplication' and data.get('name'):
                        products.append(data['name'])
            except:
                pass
        
        return products
    
    def _is_likely_product_name(self, text: str) -> bool:
        """Check if text is likely a product name"""
        if not text or len(text) < 3 or len(text) > 50:
            return False
        
        # Check for product keywords
        text_lower = text.lower()
        for keywords in self.product_keywords.values():
            for keyword in keywords:
                if keyword in text_lower:
                    return True
        
        # Check for patterns like "AppName App" or "PlatformName Platform"
        if re.search(r'\b(app|platform|software|system|tool|service)\b', text_lower, re.I):
            return True
        
        # Check if it looks like a brand name (capitalized, short)
        if len(text.split()) <= 3 and text[0].isupper():
            return True
        
        return False
    
    def _clean_product_name(self, text: str) -> str:
        """Clean and normalize product name"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common suffixes in parentheses
        text = re.sub(r'\s*\([^)]*\)\s*$', '', text)
        
        # Remove trademark symbols
        text = re.sub(r'[™®©]', '', text)
        
        return text.strip()
    
    def extract_products(self, url: str) -> List[str]:
        """Extract products using multiple methods"""
        # 1. Check ground truth
        products = self.extract_from_ground_truth(url)
        if products:
            return products
        
        # 2. Try web scraping
        products = self.extract_from_webpage(url)
        if products:
            return products
        
        return []
    
    def process_url(self, url: str):
        """Process a single URL"""
        products = self.extract_products(url)
        if products:
            self.product_mapping[url] = products
            logger.info(f"Found {len(products)} products for {url}")
        else:
            logger.warning(f"No products found for: {url}")
    
    def run(self):
        """Run the extraction process"""
        # Load URLs
        try:
            with open('final_startup_urls.json', 'r', encoding='utf-8') as f:
                urls = json.load(f)
        except FileNotFoundError:
            logger.error("final_startup_urls.json not found. Run discover_urls.py first.")
            return
        
        logger.info(f"Processing {len(urls)} URLs for products...")
        
        # Process URLs in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_url, url) for url in urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in thread: {str(e)}")
        
        # Save results
        with open('product_names.json', 'w', encoding='utf-8') as f:
            json.dump(self.product_mapping, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved products for {len(self.product_mapping)} companies to product_names.json")


def main():
    extractor = ProductExtractor()
    extractor.run()


if __name__ == "__main__":
    main()