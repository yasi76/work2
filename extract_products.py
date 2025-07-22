#!/usr/bin/env python3
"""
Product Extractor for Digital Health Startups
Extracts product names and types from validated startup URLs
Features: Web crawling, product identification, type classification, ground truth validation
Enhanced with: Caching, confidence scoring, sitemap support, fuzzy matching
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin, urlunparse
import logging
from typing import Dict, List, Optional, Tuple, Set
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
import os
import hashlib
import pickle
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

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


class URLNormalizer:
    """Normalize URLs for consistent matching"""
    
    @staticmethod
    def normalize(url: str) -> str:
        """Normalize URL for comparison"""
        if not url:
            return ""
        
        # Parse URL
        parsed = urlparse(url.lower())
        
        # Remove www prefix
        netloc = parsed.netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Remove trailing slash from path
        path = parsed.path.rstrip('/')
        if not path:
            path = ''
        
        # Reconstruct normalized URL
        normalized = urlunparse((
            parsed.scheme or 'https',
            netloc,
            path,
            '',  # params
            '',  # query
            ''   # fragment
        ))
        
        return normalized


class HTMLCache:
    """Simple HTML content cache to avoid re-downloading"""
    
    def __init__(self, cache_dir: str = '.cache', max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, url: str) -> str:
        """Get cache file path for URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.pkl")
    
    def get(self, url: str) -> Optional[str]:
        """Get cached HTML content"""
        cache_path = self._get_cache_path(url)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                # Check if cache is still valid
                if datetime.now() - data['timestamp'] < self.max_age:
                    logger.debug(f"Cache hit for {url}")
                    return data['content']
                else:
                    logger.debug(f"Cache expired for {url}")
            except Exception as e:
                logger.warning(f"Error reading cache for {url}: {e}")
        
        return None
    
    def set(self, url: str, content: str):
        """Cache HTML content"""
        cache_path = self._get_cache_path(url)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'url': url,
                    'content': content,
                    'timestamp': datetime.now()
                }, f)
            logger.debug(f"Cached content for {url}")
        except Exception as e:
            logger.warning(f"Error caching content for {url}: {e}")


class ProductExtractor:
    def __init__(self, timeout: int = 10, use_js: bool = False, use_cache: bool = True):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.use_js = use_js and HAS_PLAYWRIGHT
        self.use_cache = use_cache
        self.cache = HTMLCache() if use_cache else None
        self.ground_truth = self._load_ground_truth()
        self.extraction_stats = Counter()
        self.url_normalizer = URLNormalizer()
        
        # Product paths to check
        self.product_paths = [
            '/products', '/solutions', '/services', '/apps', '/platform', '/plattform',
            '/angebot', '/angebote', '/produkte', '/leistungen', '/features',
            '/tools', '/modules', '/portfolio', '/offerings', '/loesungen',
            '/produits', '/servicios', '/productos'  # French, Spanish
        ]
        
        # Multi-language product type keywords
        self.product_type_keywords = {
            'app': ['app', 'application', 'mobile', 'ios', 'android', 'download', 'anwendung'],
            'software': ['software', 'saas', 'cloud', 'web-based', 'online', 'digital', 'plattform'],
            'wearable': ['wearable', 'device', 'sensor', 'monitor', 'tracker', 'band', 'watch', 'gerät'],
            'service': ['service', 'consulting', 'therapy', 'coaching', 'training', 'support', 'dienstleistung', 'beratung'],
            'platform': ['platform', 'plattform', 'portal', 'dashboard', 'system', 'plateforme'],
            'tool': ['tool', 'utility', 'diagnostic', 'assessment', 'analyzer', 'werkzeug'],
            'hardware': ['hardware', 'equipment', 'device', 'kit', 'set', 'module', 'ausstattung'],
            'ai_tool': ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 'prediction', 'ki', 'künstliche intelligenz']
        }
        
        # Generic product names to filter out (multi-language)
        self.generic_product_names = {
            'our app', 'unsere app', 'the app', 'die app', 'our platform', 'unsere plattform',
            'our solution', 'unsere lösung', 'notre application', 'nuestra aplicación',
            'our product', 'unser produkt', 'the platform', 'die plattform',
            'our service', 'unser service', 'our tool', 'unser werkzeug',
            'app', 'platform', 'solution', 'service', 'tool', 'product'
        }
        
        # Extended schema.org types
        self.schema_product_types = [
            'Product', 'SoftwareApplication', 'MobileApplication', 'WebApplication',
            'MedicalDevice', 'MedicalEntity', 'MedicalService', 'CreativeWork',
            'Service', 'DigitalDocument', 'Dataset'
        ]
        
    def _load_ground_truth(self) -> Dict[str, List[Dict]]:
        """Load and normalize ground truth product data"""
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
        
        # Organize by normalized URL for easier lookup
        ground_truth = defaultdict(list)
        for product_name, url in product_url_dict.items():
            # Normalize URL for consistent matching
            normalized_url = self.url_normalizer.normalize(url)
            ground_truth[normalized_url].append({
                'name': product_name,
                'type': self._classify_product_type_from_name(product_name),
                'original_url': url
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
    
    def _is_likely_product_name(self, name: str, confidence_threshold: float = 0.5) -> Tuple[bool, float]:
        """Check if a string is likely a product name with confidence score"""
        if not name or len(name) < 2:
            return False, 0.0
        
        name_lower = name.lower().strip()
        
        # Check against generic names
        if name_lower in self.generic_product_names:
            return False, 0.0
        
        # Calculate confidence score
        confidence = 1.0
        
        # Penalize very short names
        if len(name) < 4:
            confidence *= 0.7
        
        # Penalize very long names (likely sentences)
        if len(name) > 50:
            confidence *= 0.5
        
        # Penalize if starts with lowercase (unless it's a known pattern like "eye2you")
        if name[0].islower() and not re.search(r'\d', name):
            confidence *= 0.8
        
        # Boost if contains product keywords
        for keyword_list in self.product_type_keywords.values():
            if any(keyword in name_lower for keyword in keyword_list):
                confidence *= 1.2
                break
        
        # Penalize if it's just a common word
        common_words = {'the', 'our', 'your', 'this', 'that', 'with', 'from', 'about'}
        if name_lower in common_words:
            confidence *= 0.1
        
        # Check for sentence patterns (penalize)
        if re.search(r'^(this is|we are|our|the)', name_lower):
            confidence *= 0.3
        
        # Boost for trademark symbols
        if '®' in name or '™' in name or '©' in name:
            confidence *= 1.5
        
        # Normalize confidence to 0-1 range
        confidence = min(1.0, max(0.0, confidence))
        
        return confidence >= confidence_threshold, confidence
    
    def _fuzzy_match_products(self, products: List[Dict], threshold: float = 0.85) -> List[Dict]:
        """Deduplicate similar product names using fuzzy matching"""
        if not products:
            return products
        
        # Group similar products
        groups = []
        used = set()
        
        for i, product in enumerate(products):
            if i in used:
                continue
            
            group = [product]
            name1 = product['name'].lower()
            
            for j, other in enumerate(products[i+1:], i+1):
                if j in used:
                    continue
                
                name2 = other['name'].lower()
                similarity = SequenceMatcher(None, name1, name2).ratio()
                
                if similarity >= threshold:
                    group.append(other)
                    used.add(j)
            
            groups.append(group)
        
        # Select best product from each group (highest confidence)
        deduplicated = []
        for group in groups:
            best = max(group, key=lambda p: p.get('confidence', 0.5))
            # Merge information from similar products
            if len(group) > 1:
                best['alternative_names'] = [p['name'] for p in group if p['name'] != best['name']]
                best['merged_from'] = len(group)
            deduplicated.append(best)
        
        return deduplicated
    
    def _extract_from_sitemap(self, base_url: str) -> List[str]:
        """Extract URLs from sitemap.xml"""
        urls = []
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/sitemap.xml.gz')
        ]
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=5)
                if response.status_code == 200:
                    # Parse XML
                    root = ET.fromstring(response.content)
                    
                    # Handle different sitemap formats
                    namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    
                    # Look for URLs
                    for url_elem in root.findall('.//sm:url/sm:loc', namespaces):
                        url = url_elem.text
                        # Filter for product-related URLs
                        if any(path in url.lower() for path in ['product', 'solution', 'service', 'tool']):
                            urls.append(url)
                    
                    # Also check without namespace
                    for url_elem in root.findall('.//url/loc'):
                        url = url_elem.text
                        if any(path in url.lower() for path in ['product', 'solution', 'service', 'tool']):
                            urls.append(url)
                    
                    if urls:
                        logger.info(f"Found {len(urls)} product URLs in sitemap")
                        break
                        
            except Exception as e:
                logger.debug(f"Could not fetch sitemap from {sitemap_url}: {e}")
        
        return urls[:10]  # Limit to 10 URLs to avoid overwhelming
    
    def extract_products_from_page(self, url: str, html_content: Optional[str] = None) -> Dict:
        """Extract products from a single page with confidence scoring"""
        products = []
        
        try:
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                # Check cache first
                if self.cache:
                    cached_content = self.cache.get(url)
                    if cached_content:
                        soup = BeautifulSoup(cached_content, 'html.parser')
                    else:
                        html_content = self._fetch_page(url)
                        if html_content:
                            self.cache.set(url, html_content)
                            soup = BeautifulSoup(html_content, 'html.parser')
                        else:
                            return {'products': products, 'error': 'Failed to fetch'}
                else:
                    html_content = self._fetch_page(url)
                    if html_content:
                        soup = BeautifulSoup(html_content, 'html.parser')
                    else:
                        return {'products': products, 'error': 'Failed to fetch'}
            
            # Extract potential product names with confidence
            raw_products = self._extract_raw_products_with_confidence(soup, url)
            
            # Filter by confidence and classify each product
            for product_data in raw_products:
                product_name = product_data['name']
                confidence = product_data['confidence']
                
                # Additional validation
                is_valid, adjusted_confidence = self._is_likely_product_name(product_name, 0.3)
                if not is_valid:
                    continue
                
                # Combine confidences
                final_confidence = (confidence + adjusted_confidence) / 2
                
                product_type = self._classify_product(product_name, soup)
                products.append({
                    'name': product_name,
                    'type': product_type,
                    'source_url': url,
                    'confidence': final_confidence,
                    'extraction_method': product_data.get('method', 'unknown')
                })
            
            # Deduplicate similar products
            products = self._fuzzy_match_products(products)
            
            return {'products': products}
            
        except Exception as e:
            logger.error(f"Error extracting products from {url}: {str(e)}")
            return {'products': products, 'error': str(e)}
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content"""
        try:
            if self.use_js:
                return self._fetch_with_playwright(url)
            else:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return None
    
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
    
    def _extract_raw_products_with_confidence(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract potential product names with confidence scores"""
        products = []
        
        # Strategy 1: Look for product cards/tiles (high confidence)
        product_indicators = ['product', 'produkt', 'solution', 'lösung', 'service', 'app', 'tool']
        
        for indicator in product_indicators:
            for element in soup.find_all(['div', 'section', 'article'], 
                                       class_=re.compile(indicator, re.IGNORECASE)):
                for heading in element.find_all(['h1', 'h2', 'h3', 'h4']):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 50:
                        products.append({
                            'name': text,
                            'confidence': 0.8,
                            'method': 'product_card'
                        })
        
        # Strategy 2: Headings with product keywords (medium confidence)
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)
            if any(keyword in text.lower() for keyword in ['app', 'platform', 'tool', 'service', 'system']):
                for keyword in ['app', 'platform', 'tool', 'service', 'system']:
                    if keyword in text.lower():
                        parts = text.lower().split(keyword)
                        if parts[0].strip():
                            product_name = text[:text.lower().find(keyword)].strip()
                            if product_name and len(product_name) > 2:
                                products.append({
                                    'name': product_name,
                                    'confidence': 0.7,
                                    'method': 'heading_keyword'
                                })
        
        # Strategy 3: Meta tags (high confidence)
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title and og_title.get('content'):
            content = og_title['content']
            if any(keyword in content.lower() for keyword in self.product_type_keywords.keys()):
                name = content.split('-')[0].strip()
                if name:
                    products.append({
                        'name': name,
                        'confidence': 0.9,
                        'method': 'og_title'
                    })
        
        # Strategy 4: Enhanced schema.org (very high confidence)
        schema_products = self._extract_from_schema_enhanced(soup)
        for product in schema_products:
            products.append({
                'name': product,
                'confidence': 0.95,
                'method': 'schema_org'
            })
        
        # Strategy 5: Lists with context (medium confidence)
        for ul in soup.find_all('ul'):
            parent_text = ''
            if ul.parent:
                parent_text = ul.parent.get_text(strip=True).lower()
            
            if any(indicator in parent_text for indicator in ['product', 'solution', 'feature', 'tool']):
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 50:
                        if text[0].isupper() or any(keyword in text.lower() for keyword in self.product_type_keywords.keys()):
                            products.append({
                                'name': text,
                                'confidence': 0.6,
                                'method': 'list_item'
                            })
        
        # Strategy 6: NLP extraction (variable confidence)
        if HAS_SPACY:
            nlp_products = self._extract_with_nlp(soup)
            products.extend(nlp_products)
        
        return products
    
    def _extract_from_schema_enhanced(self, soup: BeautifulSoup) -> Set[str]:
        """Enhanced schema.org extraction supporting more types"""
        products = set()
        
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                data = json.loads(script.string)
                products.update(self._extract_from_schema_data(data))
            except:
                pass
        
        return products
    
    def _extract_from_schema_data(self, data: any) -> Set[str]:
        """Recursively extract product names from schema data"""
        products = set()
        
        if isinstance(data, dict):
            # Check for any of our extended product types
            if data.get('@type') in self.schema_product_types and data.get('name'):
                products.add(data['name'])
            
            # Also check for arrays of types
            types = data.get('@type', [])
            if isinstance(types, list):
                for t in types:
                    if t in self.schema_product_types and data.get('name'):
                        products.add(data['name'])
                        break
            
            # Recurse through nested structures
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    products.update(self._extract_from_schema_data(value))
                    
        elif isinstance(data, list):
            for item in data:
                products.update(self._extract_from_schema_data(item))
        
        return products
    
    def _extract_with_nlp(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract products using NLP with confidence"""
        products = []
        
        main_content = soup.find(['main', 'article']) or soup.find('body')
        if main_content:
            text = main_content.get_text(strip=True)[:5000]
            doc = nlp(text)
            
            for ent in doc.ents:
                if ent.label_ in ["PRODUCT", "ORG"]:
                    # Check context
                    start = max(0, ent.start_char - 50)
                    end = min(len(text), ent.end_char + 50)
                    context = text[start:end].lower()
                    
                    # Calculate confidence based on context
                    confidence = 0.5
                    if any(keyword in context for keyword in self.product_type_keywords.keys()):
                        confidence = 0.7
                    
                    products.append({
                        'name': ent.text.strip(),
                        'confidence': confidence,
                        'method': 'nlp'
                    })
        
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
    
    def extract_products_from_company(self, company_data: Dict, save_snippets: bool = False) -> Dict:
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
        
        # Normalize base URL
        normalized_url = self.url_normalizer.normalize(url)
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check main page
        logger.info(f"Extracting products from {company_name} ({url})")
        main_result = self.extract_products_from_page(url)
        all_products.extend(main_result.get('products', []))
        checked_urls.add(url)
        
        # Try to get URLs from sitemap
        sitemap_urls = self._extract_from_sitemap(base_url)
        
        # Combine sitemap URLs with standard product paths
        urls_to_check = set(sitemap_urls)
        for path in self.product_paths:
            urls_to_check.add(urljoin(base_url, path))
        
        # Check additional pages
        for check_url in urls_to_check:
            if check_url not in checked_urls:
                try:
                    # Quick HEAD request to check if page exists
                    head_response = self.session.head(check_url, timeout=5, allow_redirects=True)
                    if head_response.status_code == 200:
                        logger.info(f"Checking product page: {check_url}")
                        result = self.extract_products_from_page(check_url)
                        all_products.extend(result.get('products', []))
                        checked_urls.add(check_url)
                        time.sleep(0.5)  # Be polite
                except:
                    pass
        
        # Deduplicate products using fuzzy matching
        unique_products = self._fuzzy_match_products(all_products)
        
        # Sort by confidence
        unique_products.sort(key=lambda p: p.get('confidence', 0), reverse=True)
        
        # Check against ground truth
        ground_truth_products = self.ground_truth.get(normalized_url, [])
        found_gt_products = []
        missed_gt_products = []
        
        product_names_lower = [p['name'].lower() for p in unique_products]
        
        for gt_product in ground_truth_products:
            # Try exact match first
            if gt_product['name'].lower() in product_names_lower:
                found_gt_products.append(gt_product['name'])
            else:
                # Try fuzzy match
                found = False
                for product in unique_products:
                    similarity = SequenceMatcher(None, gt_product['name'].lower(), product['name'].lower()).ratio()
                    if similarity >= 0.85:
                        found_gt_products.append(gt_product['name'])
                        found = True
                        break
                
                if not found:
                    missed_gt_products.append(gt_product['name'])
        
        result = {
            'company_name': company_name,
            'url': url,
            'normalized_url': normalized_url,
            'product_names': [p['name'] for p in unique_products],
            'product_types': {p['name']: p['type'] for p in unique_products},
            'products': unique_products,
            'extraction_method': 'crawled',
            'pages_checked': len(checked_urls),
            'ground_truth_found': found_gt_products,
            'ground_truth_missed': missed_gt_products,
            'confidence_scores': {p['name']: p.get('confidence', 0.5) for p in unique_products}
        }
        
        # Optionally save HTML snippets for validation
        if save_snippets and unique_products:
            snippets_dir = f"snippets/{company_name.replace('/', '_')}"
            os.makedirs(snippets_dir, exist_ok=True)
            
            for i, product in enumerate(unique_products[:5]):  # Save top 5
                snippet_file = f"{snippets_dir}/product_{i+1}_{product['name'].replace('/', '_')}.txt"
                with open(snippet_file, 'w', encoding='utf-8') as f:
                    f.write(f"Product: {product['name']}\n")
                    f.write(f"Type: {product['type']}\n")
                    f.write(f"Confidence: {product.get('confidence', 0):.2f}\n")
                    f.write(f"Method: {product.get('extraction_method', 'unknown')}\n")
                    f.write(f"Source: {product.get('source_url', 'unknown')}\n")
        
        return result


def process_companies_file(input_file: str, output_prefix: str, max_workers: int = 5, 
                          use_js: bool = False, limit: Optional[int] = None,
                          use_cache: bool = True, save_snippets: bool = False):
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
    extractor = ProductExtractor(use_js=use_js, use_cache=use_cache)
    
    # Process companies in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_company = {
            executor.submit(extractor.extract_products_from_company, company, save_snippets): i
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
    
    # Confidence distribution
    confidence_bins = Counter()
    for result in results:
        for confidence in result.get('confidence_scores', {}).values():
            bin_name = f"{int(confidence * 10) / 10:.1f}-{int(confidence * 10 + 1) / 10:.1f}"
            confidence_bins[bin_name] += 1
    
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
    
    logger.info(f"\nConfidence Score Distribution:")
    for bin_name in sorted(confidence_bins.keys()):
        logger.info(f"  {bin_name}: {confidence_bins[bin_name]}")
    
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
                'product_type': result['product_types'].get(product_name, 'unknown'),
                'confidence': result.get('confidence_scores', {}).get(product_name, 0.5),
                'in_ground_truth': product_name in result.get('ground_truth_found', [])
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
            'confidence_distribution': dict(confidence_bins),
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
    parser.add_argument('--no-cache', action='store_true', help='Disable HTML caching')
    parser.add_argument('--save-snippets', action='store_true', help='Save HTML snippets for validation')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before running')
    
    args = parser.parse_args()
    
    # Clear cache if requested
    if args.clear_cache and os.path.exists('.cache'):
        import shutil
        shutil.rmtree('.cache')
        logger.info("Cleared cache")
    
    process_companies_file(
        args.input_file, 
        args.output_prefix, 
        args.max_workers, 
        args.js, 
        args.limit,
        use_cache=not args.no_cache,
        save_snippets=args.save_snippets
    )


if __name__ == "__main__":
    main()