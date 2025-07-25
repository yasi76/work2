#!/usr/bin/env python3
"""
Enhanced Product Extractor for Digital Health Startups
Addresses key issues: JS rendering, false negatives, weak extraction, and classification
Features: Advanced JS support, UI pattern detection, fuzzy GT matching, embeddings
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin, urlunparse
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
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
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import fuzzywuzzy with proper handling
try:
    from fuzzywuzzy import fuzz, process
except ImportError:
    # Create a simple fallback
    class FuzzFallback:
        @staticmethod
        def ratio(s1, s2):
            return SequenceMatcher(None, s1, s2).ratio() * 100
        
        @staticmethod
        def token_set_ratio(s1, s2):
            # Simple token comparison
            tokens1 = set(s1.lower().split())
            tokens2 = set(s2.lower().split())
            if not tokens1 or not tokens2:
                return 0
            intersection = len(tokens1 & tokens2)
            union = len(tokens1 | tokens2)
            return (intersection / union) * 100 if union > 0 else 0
        
        @staticmethod
        def partial_ratio(s1, s2):
            # Simple substring check
            s1_lower = s1.lower()
            s2_lower = s2.lower()
            if s1_lower in s2_lower or s2_lower in s1_lower:
                return 90
            return SequenceMatcher(None, s1, s2).ratio() * 100
    
    fuzz = FuzzFallback()
    print("Warning: FuzzyWuzzy not available. Using fallback. Install with: pip install fuzzywuzzy python-Levenshtein")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    logger.info("Playwright not available. Install with: pip install playwright && playwright install chromium")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except:
    HAS_SELENIUM = False
    logger.info("Selenium not available. Install with: pip install selenium")

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    HAS_EMBEDDINGS = False
    logger.info("Sentence transformers not available. Install with: pip install sentence-transformers")


class EnhancedProductExtractor:
    def __init__(self, timeout: int = 15, use_js: str = 'auto', use_cache: bool = True):
        """
        Initialize enhanced extractor
        
        Args:
            timeout: Request/render timeout in seconds
            use_js: 'always', 'never', 'auto' (auto tries HTML first, then JS)
            use_cache: Whether to cache downloaded content
        """
        self.timeout = timeout
        self.use_js = use_js
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.use_cache = use_cache
        self.cache = HTMLCache() if use_cache else None
        self.extraction_stats = Counter()
        self.url_normalizer = URLNormalizer()  # Initialize before using
        self.ground_truth = self._load_ground_truth()  # Now can use url_normalizer
        
        # Enhanced product paths
        self.product_paths = [
            '/products', '/solutions', '/services', '/apps', '/platform', '/plattform',
            '/angebot', '/angebote', '/produkte', '/leistungen', '/features',
            '/tools', '/modules', '/portfolio', '/offerings', '/loesungen',
            '/produits', '/servicios', '/productos', '/unsere-produkte',
            '/what-we-do', '/what-we-offer', '/our-solutions', '/our-products'
        ]
        
        # UI pattern selectors for product extraction
        self.product_selectors = [
            # Class-based selectors
            '.product-card', '.product-tile', '.product-item', '.product-box',
            '.solution-card', '.solution-tile', '.app-card', '.service-card',
            '.offering-card', '.feature-card', '.tool-card',
            # ID-based selectors
            '#products', '#solutions', '#our-products', '#product-list',
            # Data attribute selectors
            '[data-product]', '[data-solution]', '[data-service]',
            # Semantic HTML
            'article.product', 'section.products', 'div[itemtype*="Product"]',
            # Common patterns
            '.card h3', '.tile h3', '.box h3', '.item h3',
            '.swiper-slide h3', '.carousel-item h3', '.slider-item h3'
        ]
        
        # Enhanced product type keywords with weights
        self.product_type_keywords = {
            'app': {
                'keywords': ['app', 'application', 'mobile', 'ios', 'android', 'download', 
                            'anwendung', 'applikation', 'smartphone', 'tablet'],
                'weight': 1.0
            },
            'software': {
                'keywords': ['software', 'saas', 'cloud', 'web-based', 'online', 'digital', 
                            'plattform', 'platform', 'system', 'lösung', 'solution'],
                'weight': 0.9
            },
            'wearable': {
                'keywords': ['wearable', 'device', 'sensor', 'monitor', 'tracker', 'band', 
                            'watch', 'gerät', 'armband', 'uhr'],
                'weight': 1.0
            },
            'hardware': {
                'keywords': ['hardware', 'equipment', 'device', 'kit', 'set', 'module', 
                            'ausstattung', 'gerät', 'komponente', 'box'],
                'weight': 0.95
            },
            'service': {
                'keywords': ['service', 'consulting', 'therapy', 'coaching', 'training', 
                            'support', 'dienstleistung', 'beratung', 'betreuung'],
                'weight': 0.8
            },
            'platform': {
                'keywords': ['platform', 'plattform', 'portal', 'dashboard', 'system', 
                            'plateforme', 'ecosystem', 'suite'],
                'weight': 0.9
            },
            'ai_tool': {
                'keywords': ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 
                            'prediction', 'ki', 'künstliche intelligenz', 'ml', 'neural'],
                'weight': 1.0
            }
        }
        
        # Generic product names to filter (expanded)
        self.generic_product_names = {
            'our app', 'unsere app', 'the app', 'die app', 'our platform', 'unsere plattform',
            'our solution', 'unsere lösung', 'notre application', 'nuestra aplicación',
            'our product', 'unser produkt', 'the platform', 'die plattform',
            'our service', 'unser service', 'our tool', 'unser werkzeug',
            'app', 'platform', 'solution', 'service', 'tool', 'product',
            'deine plattform', 'your platform', 'the solution', 'die lösung',
            'unser angebot', 'our offering', 'nos services', 'nuestros servicios'
        }
        
        # Initialize browser driver if needed
        self._init_browser()
        
    def _init_browser(self):
        """Initialize browser for JS rendering"""
        self.browser = None
        self.browser_type = None
        
        if self.use_js == 'never':
            return
            
        if HAS_PLAYWRIGHT:
            self.browser_type = 'playwright'
            logger.info("Using Playwright for JS rendering")
        elif HAS_SELENIUM:
            self.browser_type = 'selenium'
            logger.info("Using Selenium for JS rendering")
        else:
            if self.use_js == 'always':
                logger.warning("JS rendering requested but no browser available")
            self.use_js = 'never'
    
    def _render_with_js(self, url: str) -> Optional[str]:
        """Render page with JavaScript support"""
        try:
            if self.browser_type == 'playwright':
                return self._render_with_playwright(url)
            elif self.browser_type == 'selenium':
                return self._render_with_selenium(url)
            else:
                return None
        except Exception as e:
            logger.error(f"JS rendering failed for {url}: {e}")
            return None
    
    def _render_with_playwright(self, url: str) -> str:
        """Render with Playwright"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            try:
                # Navigate and wait for content
                page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
                
                # Wait for common product selectors
                for selector in self.product_selectors[:5]:
                    try:
                        page.wait_for_selector(selector, timeout=2000)
                        break
                    except:
                        continue
                
                # Scroll to trigger lazy loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                
                # Get final content
                content = page.content()
                
            finally:
                browser.close()
                
        return content
    
    def _render_with_selenium(self, url: str) -> str:
        """Render with Selenium"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(url)
            
            # Wait for common elements
            wait = WebDriverWait(driver, self.timeout)
            for selector in self.product_selectors[:5]:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            # Scroll for lazy loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            return driver.page_source
            
        finally:
            driver.quit()
    
    def _load_ground_truth(self) -> Dict[str, List[Dict]]:
        """Load and normalize ground truth with fuzzy matching preparation"""
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
            "DocRobin": "https://www.docrobin.com",
        }
        
        # Organize by normalized URL
        ground_truth = defaultdict(list)
        for product_name, url in product_url_dict.items():
            normalized_url = self.url_normalizer.normalize(url)
            ground_truth[normalized_url].append({
                'name': product_name,
                'type': self._classify_product_type_from_name(product_name),
                'original_url': url,
                'tokens': set(product_name.lower().split()),  # For token matching
                'normalized_name': re.sub(r'[^\w\s]', '', product_name.lower())  # For fuzzy matching
            })
        
        return dict(ground_truth)
    
    def _extract_with_selectors(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract products using UI pattern selectors"""
        products = []
        
        for selector in self.product_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    # Look for product names in the element
                    name = None
                    
                    # Try to find heading
                    heading = elem.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if heading:
                        name = heading.get_text(strip=True)
                    elif elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        name = elem.get_text(strip=True)
                    else:
                        # Check for title or name attributes
                        name = elem.get('title') or elem.get('data-product-name') or elem.get_text(strip=True)
                    
                    if name and len(name) > 2 and len(name) < 100:
                        # Extract additional context
                        context = elem.get_text(strip=True)[:200]
                        
                        products.append({
                            'name': name,
                            'confidence': 0.85,
                            'method': f'selector_{selector}',
                            'context': context
                        })
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
        
        return products
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract from structured data (JSON-LD, microdata)"""
        products = []
        
        # JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                products.extend(self._parse_structured_data(data))
            except:
                pass
        
        # Microdata
        items = soup.find_all(attrs={'itemtype': re.compile(r'schema\.org/(Product|SoftwareApplication|MedicalDevice)', re.I)})
        for item in items:
            name_elem = item.find(attrs={'itemprop': 'name'})
            if name_elem:
                products.append({
                    'name': name_elem.get_text(strip=True),
                    'confidence': 0.95,
                    'method': 'microdata'
                })
        
        return products
    
    def _parse_structured_data(self, data: Any, depth: int = 0) -> List[Dict]:
        """Recursively parse structured data"""
        products = []
        
        if depth > 5:  # Prevent infinite recursion
            return products
        
        if isinstance(data, dict):
            # Check type
            data_type = data.get('@type', '')
            if isinstance(data_type, list):
                data_type = ' '.join(data_type)
            
            # Check if it's a product-like type
            product_types = ['Product', 'SoftwareApplication', 'MobileApplication', 
                           'WebApplication', 'MedicalDevice', 'Service', 'CreativeWork']
            
            if any(pt in data_type for pt in product_types) and data.get('name'):
                products.append({
                    'name': data['name'],
                    'confidence': 0.95,
                    'method': 'structured_data',
                    'type_hint': data_type
                })
            
            # Recurse through values
            for value in data.values():
                if isinstance(value, (dict, list)):
                    products.extend(self._parse_structured_data(value, depth + 1))
                    
        elif isinstance(data, list):
            for item in data:
                products.extend(self._parse_structured_data(item, depth + 1))
        
        return products
    
    def _fuzzy_match_ground_truth(self, extracted_names: List[str], ground_truth_products: List[Dict]) -> Tuple[List[str], List[str]]:
        """Fuzzy match extracted names against ground truth"""
        found = []
        missed = list(ground_truth_products)
        
        for gt_product in ground_truth_products[:]:
            gt_name = gt_product['name']
            gt_normalized = gt_product['normalized_name']
            gt_tokens = gt_product['tokens']
            
            best_match = None
            best_score = 0
            
            for extracted in extracted_names:
                extracted_normalized = re.sub(r'[^\w\s]', '', extracted.lower())
                extracted_tokens = set(extracted.lower().split())
                
                # Multiple matching strategies
                scores = []
                
                # 1. Fuzzy string matching
                scores.append(fuzz.ratio(gt_normalized, extracted_normalized) / 100)
                scores.append(fuzz.token_set_ratio(gt_name, extracted) / 100)
                scores.append(fuzz.partial_ratio(gt_name, extracted) / 100)
                
                # 2. Token overlap (Jaccard similarity)
                if gt_tokens and extracted_tokens:
                    jaccard = len(gt_tokens & extracted_tokens) / len(gt_tokens | extracted_tokens)
                    scores.append(jaccard)
                
                # 3. Sequence matching
                scores.append(SequenceMatcher(None, gt_normalized, extracted_normalized).ratio())
                
                # Use max score
                score = max(scores) if scores else 0
                
                if score > best_score:
                    best_score = score
                    best_match = extracted
            
            # Threshold for match
            if best_score >= 0.75:  # 75% similarity
                found.append(gt_name)
                missed.remove(gt_product)
                logger.debug(f"Matched '{gt_name}' with '{best_match}' (score: {best_score:.2f})")
        
        return found, [m['name'] for m in missed]
    
    def _classify_with_context(self, product_name: str, context: str) -> str:
        """Enhanced classification using context and embeddings"""
        name_lower = product_name.lower()
        context_lower = context.lower()
        
        # Calculate scores for each type
        type_scores = Counter()
        
        for product_type, info in self.product_type_keywords.items():
            keywords = info['keywords']
            weight = info['weight']
            
            # Name matching
            for keyword in keywords:
                if keyword in name_lower:
                    type_scores[product_type] += 2 * weight
                
                # Context matching
                if keyword in context_lower:
                    type_scores[product_type] += 1 * weight
        
        # Use embeddings if available
        if HAS_EMBEDDINGS and type_scores:
            try:
                # Get embeddings
                text_embedding = embedding_model.encode(f"{product_name} {context[:200]}")
                
                # Compare with type keyword embeddings
                for product_type, info in self.product_type_keywords.items():
                    type_text = ' '.join(info['keywords'][:5])
                    type_embedding = embedding_model.encode(type_text)
                    
                    # Cosine similarity
                    similarity = np.dot(text_embedding, type_embedding) / (
                        np.linalg.norm(text_embedding) * np.linalg.norm(type_embedding)
                    )
                    
                    type_scores[product_type] += similarity * 3
            except:
                pass
        
        # Return best type or default
        if type_scores:
            return type_scores.most_common(1)[0][0]
        
        # Default based on patterns
        if 'app' in name_lower:
            return 'app'
        elif any(word in name_lower for word in ['set', 'kit', 'device', 'gerät']):
            return 'hardware'
        elif any(word in name_lower for word in ['assistant', 'coach', 'system']):
            return 'software'
        
        return 'service'
    
    def extract_products_from_page(self, url: str) -> Dict:
        """Extract products with enhanced methods"""
        products = []
        html_content = None
        
        try:
            # Try cache first
            if self.cache:
                html_content = self.cache.get(url)
            
            # Fetch content
            if not html_content:
                if self.use_js == 'always':
                    html_content = self._render_with_js(url)
                elif self.use_js == 'auto':
                    # Try HTML first
                    response = self.session.get(url, timeout=self.timeout)
                    if response.status_code == 200:
                        html_content = response.text
                        
                        # Check if we got meaningful content
                        soup = BeautifulSoup(html_content, 'html.parser')
                        initial_products = self._extract_all_products(soup, url)
                        
                        # If no products found, try JS rendering
                        if not initial_products and self.browser_type:
                            logger.info(f"No products found with HTML, trying JS rendering for {url}")
                            html_content = self._render_with_js(url)
                else:  # never
                    response = self.session.get(url, timeout=self.timeout)
                    if response.status_code == 200:
                        html_content = response.text
            
            if not html_content:
                return {'products': [], 'error': 'Failed to fetch content'}
            
            # Cache if enabled
            if self.cache and html_content:
                self.cache.set(url, html_content)
            
            # Parse and extract
            soup = BeautifulSoup(html_content, 'html.parser')
            products = self._extract_all_products(soup, url)
            
            return {'products': products}
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            return {'products': products, 'error': str(e)}
    
    def _extract_all_products(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract products using all methods"""
        all_products = []
        
        # Method 1: UI selectors (highest priority for JS-rendered content)
        selector_products = self._extract_with_selectors(soup)
        all_products.extend(selector_products)
        
        # Method 2: Structured data
        structured_products = self._extract_structured_data(soup)
        all_products.extend(structured_products)
        
        # Method 3: Enhanced heading analysis
        heading_products = self._extract_from_headings(soup)
        all_products.extend(heading_products)
        
        # Method 4: Link analysis
        link_products = self._extract_from_links(soup, url)
        all_products.extend(link_products)
        
        # Method 5: NLP extraction
        if HAS_SPACY:
            nlp_products = self._extract_with_nlp(soup)
            all_products.extend(nlp_products)
        
        # Filter and validate
        valid_products = []
        seen_names = set()
        
        for product in all_products:
            name = product['name'].strip()
            name_lower = name.lower()
            
            # Skip if already seen (exact match)
            if name_lower in seen_names:
                continue
            
            # Skip generic names
            if name_lower in self.generic_product_names:
                continue
            
            # Additional validation
            if len(name) < 2 or len(name) > 100:
                continue
            
            # Skip if it's a sentence
            if name_lower.startswith(('this is', 'we are', 'welcome to', 'learn more')):
                continue
            
            seen_names.add(name_lower)
            valid_products.append(product)
        
        # Merge similar products
        merged_products = self._merge_similar_products(valid_products)
        
        # Classify products with context
        for product in merged_products:
            if 'type' not in product:
                product['type'] = self._classify_with_context(
                    product['name'], 
                    product.get('context', '')
                )
        
        return merged_products
    
    def _extract_from_headings(self, soup: BeautifulSoup) -> List[Dict]:
        """Enhanced heading extraction"""
        products = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)
            
            # Skip if too long/short
            if len(text) < 3 or len(text) > 60:
                continue
            
            # Get context
            parent = heading.parent
            context = parent.get_text(strip=True)[:300] if parent else ''
            
            # Check if it's likely a product
            confidence = 0.5
            
            # Boost confidence based on indicators
            text_lower = text.lower()
            if any(kw in text_lower for kw in ['app', 'platform', 'tool', 'system', 'service']):
                confidence += 0.2
            
            # Check parent classes
            if parent:
                parent_classes = ' '.join(parent.get('class', []))
                if any(ind in parent_classes for ind in ['product', 'solution', 'feature', 'offering']):
                    confidence += 0.3
            
            # Check for product-like patterns
            if text[0].isupper() and not text.isupper():  # Proper case
                confidence += 0.1
            
            if confidence >= 0.6:
                products.append({
                    'name': text,
                    'confidence': confidence,
                    'method': 'heading',
                    'context': context
                })
        
        return products
    
    def _extract_from_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract products from link patterns"""
        products = []
        
        # Look for product-like links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            if not text or len(text) < 3:
                continue
            
            # Check if href indicates a product
            if any(pattern in href.lower() for pattern in ['/product/', '/app/', '/tool/', '/solution/']):
                products.append({
                    'name': text,
                    'confidence': 0.7,
                    'method': 'link_pattern',
                    'context': href
                })
        
        return products
    
    def _extract_with_nlp(self, soup: BeautifulSoup) -> List[Dict]:
        """NLP-based extraction"""
        products = []
        
        # Get main content
        main_content = soup.find(['main', 'article']) or soup.find('body')
        if not main_content:
            return products
        
        text = main_content.get_text(strip=True)[:10000]  # Limit to 10k chars
        doc = nlp(text)
        
        # Look for product-like entities
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG", "WORK_OF_ART"]:
                # Get surrounding context
                start = max(0, ent.start_char - 100)
                end = min(len(text), ent.end_char + 100)
                context = text[start:end]
                
                # Check if context suggests it's a product
                context_lower = context.lower()
                is_product = any(kw in context_lower for kw in 
                               ['product', 'app', 'platform', 'solution', 'tool', 'service'])
                
                if is_product:
                    products.append({
                        'name': ent.text.strip(),
                        'confidence': 0.7,
                        'method': 'nlp',
                        'context': context
                    })
        
        return products
    
    def _merge_similar_products(self, products: List[Dict]) -> List[Dict]:
        """Merge similar products using fuzzy matching"""
        if not products:
            return products
        
        merged = []
        used = set()
        
        for i, product in enumerate(products):
            if i in used:
                continue
            
            # Start a group with this product
            group = [product]
            name1 = product['name'].lower()
            
            # Find similar products
            for j, other in enumerate(products[i+1:], i+1):
                if j in used:
                    continue
                
                name2 = other['name'].lower()
                
                # Calculate similarity
                similarity = fuzz.ratio(name1, name2) / 100
                
                if similarity >= 0.85:
                    group.append(other)
                    used.add(j)
            
            # Merge group
            if len(group) > 1:
                # Choose best from group (highest confidence)
                best = max(group, key=lambda x: x.get('confidence', 0))
                best['alternative_names'] = [p['name'] for p in group if p['name'] != best['name']]
                best['merged_count'] = len(group)
                # Boost confidence for merged products
                best['confidence'] = min(1.0, best.get('confidence', 0.5) + 0.1)
                merged.append(best)
            else:
                merged.append(product)
        
        return merged
    
    def extract_products_from_company(self, company_data: Dict) -> Dict:
        """Extract products for a company with enhanced methods"""
        url = company_data.get('final_url') or company_data.get('url', '')
        company_name = company_data.get('company_name', 'Unknown')
        
        if not url or not company_data.get('is_live', False):
            return {
                'company_name': company_name,
                'url': url,
                'products': [],
                'extraction_method': 'skipped',
                'reason': 'URL not live or missing'
            }
        
        all_products = []
        checked_urls = set()
        
        # Normalize URLs
        normalized_url = self.url_normalizer.normalize(url)
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Extract from main page
        logger.info(f"Extracting products from {company_name} ({url})")
        main_result = self.extract_products_from_page(url)
        all_products.extend(main_result.get('products', []))
        checked_urls.add(url)
        
        # Get additional URLs
        urls_to_check = set()
        
        # Add standard product paths
        for path in self.product_paths:
            urls_to_check.add(urljoin(base_url, path))
        
        # Try sitemap
        sitemap_urls = self._extract_from_sitemap(base_url)
        urls_to_check.update(sitemap_urls)
        
        # Check additional pages (limit to prevent overwhelming)
        checked_count = 0
        for check_url in urls_to_check:
            if check_url in checked_urls or checked_count >= 5:
                break
            
            try:
                # Quick check if page exists
                head_response = self.session.head(check_url, timeout=5, allow_redirects=True)
                if head_response.status_code == 200:
                    logger.info(f"Checking: {check_url}")
                    result = self.extract_products_from_page(check_url)
                    all_products.extend(result.get('products', []))
                    checked_urls.add(check_url)
                    checked_count += 1
                    time.sleep(1)  # Be polite
            except:
                pass
        
        # Deduplicate all products
        final_products = self._merge_similar_products(all_products)
        
        # Prepare output
        product_names = [p['name'] for p in final_products]
        
        # Ground truth validation with fuzzy matching
        ground_truth_products = self.ground_truth.get(normalized_url, [])
        found_gt, missed_gt = self._fuzzy_match_ground_truth(product_names, ground_truth_products)
        
        return {
            'company_name': company_name,
            'url': url,
            'normalized_url': normalized_url,
            'products': final_products,
            'product_names': product_names,
            'product_types': {p['name']: p.get('type', 'unknown') for p in final_products},
            'extraction_method': 'enhanced',
            'pages_checked': len(checked_urls),
            'ground_truth_found': found_gt,
            'ground_truth_missed': missed_gt,
            'js_rendering_used': self.use_js != 'never',
            'confidence_scores': {p['name']: p.get('confidence', 0.5) for p in final_products}
        }
    
    def _extract_from_sitemap(self, base_url: str) -> List[str]:
        """Extract URLs from sitemap"""
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
                    root = ET.fromstring(response.content)
                    
                    # Extract URLs
                    namespaces = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    for loc in root.findall('.//sm:url/sm:loc', namespaces):
                        url = loc.text
                        if any(kw in url.lower() for kw in ['product', 'solution', 'tool', 'app']):
                            urls.append(url)
                    
                    if urls:
                        break
            except:
                pass
        
        return urls[:5]  # Limit to 5
    
    def _classify_product_type_from_name(self, name: str) -> str:
        """Basic classification from name"""
        name_lower = name.lower()
        
        if 'app' in name_lower:
            return 'app'
        elif any(w in name_lower for w in ['set', 'kit', 'device', 'gerät']):
            return 'hardware'
        elif any(w in name_lower for w in ['assistant', 'coach', 'system']):
            return 'software'
        elif 'ai' in name_lower:
            return 'ai_tool'
        
        return 'service'


class URLNormalizer:
    """URL normalization utilities"""
    
    @staticmethod
    def normalize(url: str) -> str:
        if not url:
            return ""
        
        parsed = urlparse(url.lower())
        
        # Remove www
        netloc = parsed.netloc
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Remove trailing slash
        path = parsed.path.rstrip('/')
        
        # Reconstruct
        return urlunparse((
            parsed.scheme or 'https',
            netloc,
            path,
            '', '', ''
        ))


class HTMLCache:
    """HTML caching system"""
    
    def __init__(self, cache_dir: str = '.cache', max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, url: str) -> str:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.pkl")
    
    def get(self, url: str) -> Optional[str]:
        cache_path = self._get_cache_path(url)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                
                if datetime.now() - data['timestamp'] < self.max_age:
                    return data['content']
            except:
                pass
        
        return None
    
    def set(self, url: str, content: str):
        cache_path = self._get_cache_path(url)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({
                    'url': url,
                    'content': content,
                    'timestamp': datetime.now()
                }, f)
        except:
            pass


def process_companies(input_file: str, output_prefix: str = 'enhanced', 
                     max_workers: int = 3, use_js: str = 'auto',
                     limit: Optional[int] = None, use_cache: bool = True):
    """Process companies with enhanced extraction"""
    
    # Load data
    logger.info(f"Loading companies from {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        companies = data
    elif isinstance(data, dict) and 'urls' in data:
        companies = data['urls']
    else:
        companies = []
        for value in data.values():
            if isinstance(value, dict) and 'url' in value:
                companies.append(value)
    
    if limit:
        companies = companies[:limit]
    
    logger.info(f"Processing {len(companies)} companies with JS rendering: {use_js}")
    
    # Initialize extractor
    extractor = EnhancedProductExtractor(use_js=use_js, use_cache=use_cache)
    
    # Process companies
    results = []
    
    # Use less workers for JS rendering to avoid resource issues
    if use_js != 'never':
        max_workers = min(max_workers, 2)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(extractor.extract_products_from_company, company): i
            for i, company in enumerate(companies)
        }
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                
                # Log progress
                company_name = result.get('company_name', 'Unknown')
                products_found = len(result.get('products', []))
                gt_found = len(result.get('ground_truth_found', []))
                gt_total = gt_found + len(result.get('ground_truth_missed', []))
                
                if gt_total > 0:
                    logger.info(f"{company_name}: {products_found} products found, GT: {gt_found}/{gt_total}")
                else:
                    logger.info(f"{company_name}: {products_found} products found")
                    
            except Exception as e:
                logger.error(f"Error processing company: {e}")
    
    # Calculate statistics
    total_products = sum(len(r.get('products', [])) for r in results)
    companies_with_products = sum(1 for r in results if r.get('products'))
    
    # Ground truth stats
    total_gt_found = sum(len(r.get('ground_truth_found', [])) for r in results)
    total_gt_missed = sum(len(r.get('ground_truth_missed', [])) for r in results)
    total_gt = total_gt_found + total_gt_missed
    
    # Confidence distribution
    all_confidences = []
    for r in results:
        all_confidences.extend(r.get('confidence_scores', {}).values())
    
    confidence_bins = Counter()
    for conf in all_confidences:
        bin_name = f"{int(conf * 10) / 10:.1f}"
        confidence_bins[bin_name] += 1
    
    # Log summary
    logger.info("\n" + "="*60)
    logger.info("ENHANCED EXTRACTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total companies processed: {len(results)}")
    logger.info(f"Companies with products: {companies_with_products}")
    logger.info(f"Total products extracted: {total_products}")
    
    if total_gt > 0:
        logger.info(f"\nGround Truth Validation:")
        logger.info(f"  Found: {total_gt_found}/{total_gt} ({total_gt_found/total_gt*100:.1f}%)")
        logger.info(f"  Missed: {total_gt_missed}/{total_gt} ({total_gt_missed/total_gt*100:.1f}%)")
        
        # Show missed products
        if total_gt_missed > 0:
            logger.info("\nMissed GT products:")
            for r in results:
                if r.get('ground_truth_missed'):
                    logger.info(f"  {r['company_name']}: {', '.join(r['ground_truth_missed'])}")
    
    logger.info(f"\nConfidence Distribution:")
    for bin_name in sorted(confidence_bins.keys()):
        logger.info(f"  {bin_name}: {confidence_bins[bin_name]}")
    
    # Save results
    output_json = f"{output_prefix}_products.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved results to {output_json}")
    
    # Save CSV
    output_csv = f"{output_prefix}_products.csv"
    csv_rows = []
    for result in results:
        for product in result.get('products', []):
            csv_rows.append({
                'company_name': result['company_name'],
                'company_url': result['url'],
                'product_name': product['name'],
                'product_type': product.get('type', 'unknown'),
                'confidence': product.get('confidence', 0.5),
                'extraction_method': product.get('method', 'unknown'),
                'is_ground_truth': product['name'] in result.get('ground_truth_found', [])
            })
    
    if csv_rows:
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)
        logger.info(f"Saved CSV to {output_csv}")
    
    # Save stats
    stats = {
        'extraction_config': {
            'js_rendering': use_js,
            'cache_enabled': use_cache,
            'max_workers': max_workers
        },
        'summary': {
            'total_companies': len(results),
            'companies_with_products': companies_with_products,
            'total_products': total_products,
            'avg_products_per_company': total_products / len(results) if results else 0
        },
        'ground_truth_validation': {
            'found': total_gt_found,
            'missed': total_gt_missed,
            'total': total_gt,
            'accuracy': f"{total_gt_found/total_gt*100:.1f}%" if total_gt > 0 else "N/A"
        },
        'confidence_distribution': dict(confidence_bins),
        'missed_products_detail': {
            r['company_name']: r['ground_truth_missed'] 
            for r in results if r.get('ground_truth_missed')
        }
    }
    
    stats_file = f"{output_prefix}_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved statistics to {stats_file}")


def main():
    parser = argparse.ArgumentParser(description='Enhanced product extraction with JS rendering and fuzzy matching')
    parser.add_argument('input_file', help='JSON file with company data')
    parser.add_argument('--output-prefix', default='enhanced', help='Output file prefix')
    parser.add_argument('--js', choices=['always', 'never', 'auto'], default='auto',
                       help='JavaScript rendering mode (default: auto)')
    parser.add_argument('--max-workers', type=int, default=3, help='Max parallel workers')
    parser.add_argument('--limit', type=int, help='Limit companies to process')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--clear-cache', action='store_true', help='Clear cache before running')
    
    args = parser.parse_args()
    
    # Clear cache if requested
    if args.clear_cache and os.path.exists('.cache'):
        import shutil
        shutil.rmtree('.cache')
        logger.info("Cleared cache")
    
    # Check dependencies
    if args.js != 'never' and not (HAS_PLAYWRIGHT or HAS_SELENIUM):
        logger.warning("JS rendering requested but no browser driver available")
        logger.warning("Install playwright: pip install playwright && playwright install chromium")
        logger.warning("Or install selenium: pip install selenium")
    
    process_companies(
        args.input_file,
        args.output_prefix,
        args.max_workers,
        args.js,
        args.limit,
        use_cache=not args.no_cache
    )


if __name__ == "__main__":
    main()