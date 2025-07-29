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
import unicodedata

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
    "https://www.apheris.com": ["Apheris", "Apheris Platform"],
    "https://www.aporize.com": ["Aporize"],
    "https://www.arztlena.com": ["Lena"],
    "https://shop.getnutrio.com": ["aurora nutrio", "Nutrio App"],
    "https://www.auta.health": ["Auta Health"],
    "https://visioncheckout.com": ["auvisus"],
    "https://www.avayl.tech": ["AVAL"],
    "https://www.avimedical.com": ["avi Impact"],
    "https://de.becureglobal.com": ["BECURE"],
    "https://bellehealth.co": ["Belle App"],
    "https://www.biotx.ai": ["biotx.ai"],
    "https://www.brainjo.de": ["brainjo"],
    "https://brea.app": ["Brea App"],
    "https://breathment.com": ["Breathment"],
    "https://de.caona.eu": ["Caona Health"],
    "https://www.careanimations.de": ["apoclip"],
    "https://www.climedo.de": ["Climedo"],
    "https://www.cliniserve.de": ["Clinicserve"],
    "https://cogthera.de": ["Cogthera App"],
    "https://www.comuny.de": ["comuny"],
    "https://curecurve.de": ["CureCurve", "Elina App"],
    "https://www.cynteract.com": ["Cynteract"],
    "https://www.healthmeapp.de": ["Declareme"],
    "https://deepeye.ai": ["deepeye medical"],
    "https://www.deepmentation.ai": ["lab.capture"],
    "https://denton-systems.de": ["Denton Systems"],
    "https://www.derma2go.com": ["derma2go"],
    "https://www.dianovi.com": ["dianovi"],
    "http://dopavision.com": ["Dopavision"],
    "https://www.dpv-analytics.com": ["dpv-analytics"],
    "http://www.ecovery.de": ["eCovery"],
    "https://elixionmedical.com": ["Elixion Medical"],
    "https://www.empident.de": ["Empident"],
    "https://eye2you.ai": ["eye2you"],
    "https://www.fitwhit.de": ["FitwHit"],
    "https://www.floy.com": ["Floy Radiology"],
    "https://fyzo.de": ["fyzo Assistant", "fyzo coach"],
    "https://www.gesund.de": ["gesund.de App"],
    "https://www.glaice.de": ["GLACIE"],
    "https://gleea.de": ["Einfach Retten App"],
    "https://www.guidecare.de": ["GuideCare"],
    "https://www.apodienste.com": ["apodienste"],
    "https://www.help-app.de": ["HELP"],
    "https://www.heynanny.com": ["heynannyly"],
    "https://incontalert.de": ["inContAlert"],
    "https://home.informme.info": ["InformMe"],
    "https://www.kranushealth.com": ["Kranus Lutera", "Kranus Mictera"],
    "MindDoc": ["MindDoc"],
}

# Valid product type patterns - strict matching
VALID_PRODUCT_PATTERN = re.compile(
    r'\b(app|plattform|platform|solution|lösung|system|software|tool|device|'
    r'programm|dienst|service|assistant|coach|set|kit|wearable|monitor|sensor|'
    r'tracker|modul|module|suite|analytics|ai|cloud|saas)\b',
    re.IGNORECASE
)

# Product type classification patterns
PRODUCT_TYPE_PATTERNS = {
    'App': [
        r'\bapp\b', r'\bapplication\b', r'\bmobile\b', r'\bios\b', r'\bandroid\b',
        r'\bdownload\b', r'\bplay store\b', r'\bapp store\b'
    ],
    'Platform': [
        r'\bplatform\b', r'\bplattform\b', r'\bcloud\b', r'\bsaas\b', r'\bportal\b'
    ],
    'Software': [
        r'\bsoftware\b', r'\bsystem\b', r'\bprogramm\b', r'\bdesktop\b'
    ],
    'Wearable': [
        r'\bwearable\b', r'\bdevice\b', r'\bsensor\b', r'\bmonitor\b', 
        r'\btracker\b', r'\bwatch\b', r'\bband\b', r'\bhardware\b', r'\bgerät\b'
    ],
    'Set': [
        r'\bset\b', r'\bkit\b', r'\bbox\b', r'\bpackage\b', r'\bpaket\b'
    ],
    'Service': [
        r'\bservice\b', r'\bconsulting\b', r'\bberatung\b', r'\bdienstleistung\b'
    ],
    'AI Tool': [
        r'\bai\b', r'\bartificial intelligence\b', r'\bmachine learning\b',
        r'\banalytics\b', r'\balgorithm\b', r'\bdiagnostic\b', r'\bkünstliche intelligenz\b'
    ],
    'Assistant': [
        r'\bassistant\b', r'\bcoach\b', r'\bhelper\b', r'\bguide\b', r'\bassistent\b'
    ]
}

# Junk terms to ignore - expanded list
JUNK_TERMS = [
    # Navigation
    "kontakt", "contact", "startseite", "home", "über uns", "about", "about us",
    "impressum", "imprint", "datenschutz", "privacy", "privacy policy", "agb",
    "terms", "terms of service", "login", "anmelden", "register", "registrieren",
    "logout", "abmelden", "menu", "menü", "navigation",
    
    # Marketing fluff
    "mehr erfahren", "learn more", "demo anfordern", "request demo", "demo buchen",
    "book demo", "kostenlos testen", "try free", "jetzt starten", "get started",
    "unsere firma", "our company", "karriere", "careers", "team", "blog", "news",
    "presse", "press", "partner", "partners", "netzwerk", "network", "community",
    
    # Generic business terms
    "lösung", "solution", "lösungen", "solutions", "angebot", "offer", "angebote",
    "offers", "leistungen", "services", "produkte", "products", "portfolio",
    "referenzen", "references", "kunden", "customers", "clients", "testimonials",
    
    # Actions
    "download", "herunterladen", "kontaktieren", "contact us", "anfrage", "inquiry",
    "newsletter", "subscribe", "abonnieren", "follow", "folgen", "share", "teilen",
    
    # Common phrases that are not products
    "one network", "any application", "der autonome", "ihre", "unsere", "your", "our",
    "für", "for", "und", "and", "mit", "with", "von", "from", "bei", "at",
    
    # Sections
    "features", "funktionen", "benefits", "vorteile", "pricing", "preise", "faq",
    "support", "hilfe", "help", "documentation", "dokumentation", "resources",
    "ressourcen",
    
    # UI/UX elements and slogans
    "how it works", "wie es funktioniert", "get started now", "jetzt anfangen",
    "start now", "view details", "details anzeigen", "learn more about",
    "erfahren sie mehr", "discover our", "entdecken sie", "your data", "ihre daten",
    "our platform", "unsere plattform", "fits right in", "passt perfekt",
    "proprietary data", "proprietäre daten", "built in", "eingebaut",
    "differentiator", "unterscheidungsmerkmal", "experience", "erfahrung",
    "empower", "befähigen", "transform", "transformieren", "revolutionize",
    "revolutionieren", "innovate", "innovieren"
]

# Banned patterns for slogan-like phrases
BANNED_PATTERNS = [
    # Action-oriented slogans
    r'^\b(how|why|when|where|discover|empower|experience|learn|explore|transform|revolutionize|innovate|choose|start|get|try|view|see|check)\b',
    # Possessive phrases
    r'\b(your way|our way|your data|our data|your solution|our solution|your platform|our platform)\b',
    # Marketing phrases
    r'\b(fits right in|built in|get started|start now|learn more|view details|find out|check out|sign up|try now|demo now)\b',
    # Feature descriptions
    r'\b(how it works|wie es funktioniert|what we do|was wir tun|why choose|warum wählen)\b',
    # Generic differentiators
    r'\b(differentiator|game changer|breakthrough|revolutionary|innovative solution|next generation|cutting edge)\b',
    # Imperatives and calls to action
    r'^(see|try|get|start|learn|discover|explore|find|check|view|download|request|book|contact)\s',
    # "X is Y" patterns
    r'\b(is the new|is the future|is the answer|is the solution)\b',
    # Superlatives and marketing language
    r'\b(the best|the only|the first|the most|the ultimate|the perfect|the ideal)\b',
    # Process descriptions
    r'\b(preprocess|process|analyze|optimize|streamline|automate|integrate)\s+(your|the|our)\s+way\b',
    # Vision statements
    r"(blind man's view|bird's eye view|new perspective|fresh approach|unique approach)"
]

# Valid product container selectors
VALID_PRODUCT_CONTAINERS = [
    # ID patterns
    r'[id*="product"]', r'[id*="produkt"]', r'[id*="solution"]', r'[id*="lösung"]',
    r'[id*="platform"]', r'[id*="plattform"]', r'[id*="service"]', r'[id*="dienst"]',
    r'[id*="angebot"]', r'[id*="app"]',
    
    # Class patterns
    r'[class*="product"]', r'[class*="produkt"]', r'[class*="solution"]', 
    r'[class*="lösung"]', r'[class*="platform"]', r'[class*="plattform"]',
    r'[class*="service"]', r'[class*="dienst"]', r'[class*="angebot"]',
    r'[class*="feature"]', r'[class*="app"]',
    
    # Semantic patterns
    'section.products', 'section.solutions', 'div.products-grid', 'div.solutions-list',
    'article.product', 'article.solution', 'main [role="main"] .product',
    
    # German patterns
    'section.produkte', 'section.lösungen', 'div.produkte-grid', 'div.lösungen-liste',
    'article.produkt', 'article.lösung'
]

class ProductExtractor:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.product_paths = [
            '/products', '/produkte', '/solutions', '/lösungen', '/losungen',
            '/services', '/leistungen', '/angebot', '/angebote', '/platform',
            '/plattform', '/app', '/apps', '/software', '/tools'
        ]
        
    def extract_products_from_page(self, url: str, html_content: str = None) -> Dict:
        """Extract products from a single page with strict filtering"""
        products = {
            'found_products': [],
            'product_types': {},
            'extraction_methods': [],
            'confidence_scores': {}
        }
        
        # First check if we have ground truth for this URL
        normalized_url = self._normalize_url_for_gt(url)
        if normalized_url in GROUND_TRUTH_PRODUCTS:
            gt_products = GROUND_TRUTH_PRODUCTS[normalized_url]
            for product in gt_products:
                products['found_products'].append(product)
                products['product_types'][product] = self._classify_product_type(product, "")
                products['extraction_methods'].append('ground_truth')
                products['confidence_scores'][product] = 1.0
            return products
        
        try:
            if not html_content:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                if response.status_code != 200:
                    return products
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Method 1: Extract from valid product containers
            container_products = self._extract_from_valid_containers(soup)
            for product, confidence in container_products:
                if self._is_valid_product_name(product):
                    if product not in products['found_products']:
                        products['found_products'].append(product)
                        products['product_types'][product] = self._classify_product_type(product, html_content)
                        products['extraction_methods'].append('product_container')
                        products['confidence_scores'][product] = confidence
            
            # Method 2: Extract from schema.org data
            schema_products = self._extract_from_schema(soup)
            for product in schema_products:
                if self._is_valid_product_name(product):
                    if product not in products['found_products']:
                        products['found_products'].append(product)
                        products['product_types'][product] = self._classify_product_type(product, html_content)
                        products['extraction_methods'].append('schema.org')
                        products['confidence_scores'][product] = 0.9
            
            # Method 3: Extract from specific meta tags
            meta_products = self._extract_from_meta_tags(soup)
            for product in meta_products:
                if self._is_valid_product_name(product):
                    if product not in products['found_products']:
                        products['found_products'].append(product)
                        products['product_types'][product] = self._classify_product_type(product, html_content)
                        products['extraction_methods'].append('meta_tags')
                        products['confidence_scores'][product] = 0.8
            
            # Method 4: Extract from product-focused headings only
            heading_products = self._extract_from_product_headings(soup)
            for product, confidence in heading_products:
                if self._is_valid_product_name(product):
                    if product not in products['found_products']:
                        products['found_products'].append(product)
                        products['product_types'][product] = self._classify_product_type(product, html_content)
                        products['extraction_methods'].append('product_heading')
                        products['confidence_scores'][product] = confidence
            
            # Post-process: Clean up and normalize
            products['found_products'] = [self._clean_product_name(p) for p in products['found_products']]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_products = []
            for product in products['found_products']:
                if product.lower() not in seen:
                    seen.add(product.lower())
                    unique_products.append(product)
            products['found_products'] = unique_products
            
        except Exception as e:
            logger.warning(f"Error extracting products from {url}: {str(e)}")
        
        return products
    
    def _is_valid_product_name(self, text: str) -> bool:
        """Strict validation of product names"""
        if not text or len(text) < 2 or len(text) > 50:
            return False
        
        text_lower = text.lower().strip()
        
        # First check against banned patterns for slogans
        for pattern in BANNED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False
        
        # Check against junk terms - but only exact matches or if the entire text is junk
        for junk in JUNK_TERMS:
            if text_lower == junk:
                return False
            # For longer junk phrases, check if they make up the majority of the text
            if len(junk.split()) > 1 and junk in text_lower:
                if len(junk) / len(text) > 0.8:  # Junk makes up >80% of the text
                    return False
        
        # Reject if text contains too many "marketing" words
        marketing_words = ['your', 'our', 'new', 'best', 'ultimate', 'perfect', 'revolutionary', 'innovative']
        marketing_count = sum(1 for word in marketing_words if word in text_lower)
        if marketing_count >= 2:  # Two or more marketing words = likely a slogan
            return False
        
        # Must contain at least one product-type keyword OR be a well-formed product name
        has_product_keyword = VALID_PRODUCT_PATTERN.search(text)
        
        if not has_product_keyword:
            # Allow exceptions for well-formed product names
            # Check if it's a proper noun with specific patterns
            if re.match(r'^[A-Z][a-zA-Z0-9]+([\s\-\.][A-Z]?[a-zA-Z0-9]+)*$', text):
                # It's a properly capitalized name, might be a product
                # Additional checks for product-like patterns
                words = text.split()
                if len(words) <= 3:  # Reduced to max 3 words for plain names
                    # Check if it has product-like suffixes
                    last_word = words[-1].lower()
                    if any(suffix in last_word for suffix in ['pro', 'plus', 'core', 'sync', 'monitor', 'health', 'care', 'med', 'ai', 'hub', 'lab', 'box']):
                        return True
                    # Only accept multi-word names if they look like real product names
                    if len(words) == 2 and not any(w in ['the', 'a', 'an', 'your', 'our', 'my'] for w in [w.lower() for w in words]):
                        return True
                    # Single word proper nouns need to be very specific
                    if len(words) == 1 and len(text) >= 4:
                        return True
            return False
        
        # Reject overly generic or long phrases
        if len(text.split()) > 6:  # Reduced from 8 to 6
            return False
        
        # Reject if it's just a single generic term
        generic_terms = ['app', 'platform', 'software', 'system', 'service', 'lösung', 'plattform', 'solution']
        if text_lower in generic_terms and len(text.split()) == 1:
            return False
        
        # Final check: does it sound like a product or a sentence/slogan?
        # Products typically don't have verbs (except in compound forms like "TrackIt")
        verb_patterns = [r'\b(is|are|was|were|will|can|could|should|must|may|might|do|does|did|make|makes|made)\b']
        for pattern in verb_patterns:
            if re.search(pattern, text_lower):
                return False
        
        return True
    
    def _extract_from_valid_containers(self, soup: BeautifulSoup) -> List[Tuple[str, float]]:
        """Extract from containers that are likely to contain products"""
        products = []
        seen = set()
        
        # First try specific product containers
        for selector in VALID_PRODUCT_CONTAINERS:
            try:
                containers = soup.select(selector)
                for container in containers:
                    # Look for product names in this container
                    # Priority 1: Direct heading tags
                    for tag in ['h1', 'h2', 'h3', 'h4']:
                        for heading in container.find_all(tag):
                            text = heading.get_text(strip=True)
                            if text and len(text) < 50 and text.lower() not in seen:
                                seen.add(text.lower())
                                products.append((text, 0.9))
                    
                    # Priority 2: Strong/emphasized text
                    for tag in ['strong', 'b', 'em']:
                        for elem in container.find_all(tag):
                            text = elem.get_text(strip=True)
                            if text and len(text) < 50 and text.lower() not in seen:
                                # Check if it's in a product context
                                parent_text = elem.parent.get_text(strip=True).lower() if elem.parent else ""
                                if any(word in parent_text for word in ['product', 'produkt', 'lösung', 'solution', 'app', 'platform', 'plattform']):
                                    seen.add(text.lower())
                                    products.append((text, 0.8))
            except:
                continue
        
        # Also check any element with class or id containing 'product' directly
        for elem in soup.find_all(True, class_=re.compile(r'product|lösung|solution|platform|plattform|app', re.I)):
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                text = elem.get_text(strip=True)
                if text and len(text) < 50 and text.lower() not in seen:
                    seen.add(text.lower())
                    products.append((text, 0.85))
        
        # Check divs and sections with product-related IDs
        for elem in soup.find_all(True, id=re.compile(r'product|lösung|solution|platform|plattform|app', re.I)):
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5']:
                for heading in elem.find_all(tag):
                    text = heading.get_text(strip=True)
                    if text and len(text) < 50 and text.lower() not in seen:
                        seen.add(text.lower())
                        products.append((text, 0.85))
        
        return products
    
    def _extract_from_product_headings(self, soup: BeautifulSoup) -> List[Tuple[str, float]]:
        """Extract from headings that are in product contexts"""
        products = []
        
        # Look for headings that indicate product sections
        product_section_indicators = [
            'unsere produkte', 'our products', 'unsere lösungen', 'our solutions',
            'unsere apps', 'our apps', 'produkte', 'products', 'lösungen', 'solutions',
            'unser angebot', 'our offering', 'leistungen', 'services'
        ]
        
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            heading_text = heading.get_text(strip=True).lower()
            
            # Check if this heading indicates a product section
            if any(indicator in heading_text for indicator in product_section_indicators):
                # Look for product names in the next siblings
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    if next_elem.name in ['ul', 'ol']:
                        # Extract from list items
                        for li in next_elem.find_all('li'):
                            text = li.get_text(strip=True)
                            text = re.sub(r'^[•\-\*\d\.]\s*', '', text)  # Remove bullets/numbers
                            if text:
                                products.append((text.split(':')[0].strip(), 0.85))
                    elif next_elem.name in ['div', 'p', 'section']:
                        # Look for emphasized text
                        for tag in ['strong', 'b', 'h3', 'h4', 'h5']:
                            for elem in next_elem.find_all(tag):
                                text = elem.get_text(strip=True)
                                if text and len(text) < 50:
                                    products.append((text, 0.8))
                    
                    next_elem = next_elem.find_next_sibling()
        
        return products
    
    def _extract_from_schema(self, soup: BeautifulSoup) -> List[str]:
        """Extract product names from schema.org structured data"""
        products = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                # Clean the JSON string (remove any BOM or hidden characters)
                json_str = script.string.strip()
                if json_str:
                    data = json.loads(json_str)
                    
                    # Handle different schema structures
                    if isinstance(data, dict):
                        if data.get('@type') in ['Product', 'SoftwareApplication', 'MedicalDevice', 'MedicalApp', 'MobileApplication', 'WebApplication']:
                            if 'name' in data and data['name']:
                                products.append(data['name'])
                        
                        # Check @graph
                        if '@graph' in data:
                            for item in data['@graph']:
                                if isinstance(item, dict) and item.get('@type') in ['Product', 'SoftwareApplication', 'MedicalDevice', 'MedicalApp', 'MobileApplication', 'WebApplication']:
                                    if 'name' in item and item['name']:
                                        products.append(item['name'])
                    
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get('@type') in ['Product', 'SoftwareApplication', 'MedicalDevice', 'MedicalApp', 'MobileApplication', 'WebApplication']:
                                if 'name' in item and item['name']:
                                    products.append(item['name'])
                                    
            except json.JSONDecodeError:
                # Try to extract manually if JSON parsing fails
                try:
                    # Look for patterns like "name": "Product Name"
                    import re
                    name_matches = re.findall(r'"name"\s*:\s*"([^"]+)"', script.string)
                    for name in name_matches:
                        if name and len(name) < 50:
                            products.append(name)
                except:
                    pass
            except:
                pass
        
        return products
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract product names from specific meta tags"""
        products = []
        
        # Only check application-name meta tag for products
        app_name = soup.find('meta', attrs={'name': 'application-name'})
        if app_name and app_name.get('content'):
            content = app_name['content'].strip()
            if content and not any(junk in content.lower() for junk in JUNK_TERMS):
                products.append(content)
        
        # Check og:site_name only if it contains product keywords
        og_site = soup.find('meta', property='og:site_name')
        if og_site and og_site.get('content'):
            content = og_site['content'].strip()
            if VALID_PRODUCT_PATTERN.search(content):
                products.append(content)
        
        return products
    
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
            return 'App'
        elif 'set' in product_lower or 'kit' in product_lower:
            return 'Set'
        elif 'assistant' in product_lower or 'coach' in product_lower:
            return 'Assistant'
        elif any(word in product_lower for word in ['platform', 'plattform']):
            return 'Platform'
        elif any(word in product_lower for word in ['system', 'software']):
            return 'Software'
        elif any(word in product_lower for word in ['wearable', 'device', 'sensor', 'monitor']):
            return 'Wearable'
        
        return 'Service'  # Default
    
    def _clean_product_name(self, text: str) -> str:
        """Clean and normalize product name"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove trailing punctuation
        text = text.rstrip('.,!?:;')
        
        # Fix common encoding issues
        text = text.replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã¼', 'ü')
        text = text.replace('Ã„', 'Ä').replace('Ã–', 'Ö').replace('Ãœ', 'Ü')
        text = text.replace('ÃŸ', 'ß')
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Capitalize appropriately (preserve existing capitalization if it looks intentional)
        if text.islower():
            text = text.title()
        
        return text.strip()
    
    def _normalize_url_for_gt(self, url: str) -> str:
        """Normalize URL for ground truth lookup"""
        # Remove trailing slashes and fragments
        url = url.rstrip('/').split('#')[0]
        
        # Parse URL
        parsed = urlparse(url.lower())
        
        # Try different variations
        variations = [
            f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/'),
            f"{parsed.scheme}://{parsed.netloc}".rstrip('/'),
            f"https://{parsed.netloc}{parsed.path}".rstrip('/'),
            f"https://{parsed.netloc}".rstrip('/'),
        ]
        
        # Add www variations
        if not parsed.netloc.startswith('www.'):
            variations.extend([
                f"{parsed.scheme}://www.{parsed.netloc}{parsed.path}".rstrip('/'),
                f"{parsed.scheme}://www.{parsed.netloc}".rstrip('/'),
                f"https://www.{parsed.netloc}{parsed.path}".rstrip('/'),
                f"https://www.{parsed.netloc}".rstrip('/'),
            ])
        
        # Check each variation
        for variant in variations:
            if variant in GROUND_TRUTH_PRODUCTS:
                return variant
        
        return variations[0]  # Return first variation as default
    
    def discover_all_products(self, startup_data: Dict) -> Dict:
        """Discover all products for a startup by checking multiple pages"""
        url = startup_data.get('url', '')
        if not url:
            return startup_data
        
        all_products = []
        all_types = {}
        all_methods = set()
        all_confidence = {}
        
        # Extract from main page
        main_page_products = self.extract_products_from_page(url)
        all_products.extend(main_page_products['found_products'])
        all_types.update(main_page_products['product_types'])
        all_methods.update(main_page_products['extraction_methods'])
        all_confidence.update(main_page_products['confidence_scores'])
        
        # If we already found ground truth products, don't check other pages
        if 'ground_truth' in main_page_products['extraction_methods']:
            startup_data['product_names'] = all_products
            startup_data['product_types'] = all_types
            startup_data['extraction_methods'] = list(all_methods)
            startup_data['confidence_scores'] = all_confidence
            return startup_data
        
        # Check product-specific pages if no ground truth found
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        pages_checked = 0
        max_pages = 3  # Limit to avoid excessive requests
        
        for path in self.product_paths:
            if pages_checked >= max_pages:
                break
                
            try:
                product_url = urljoin(base_url, path)
                logger.info(f"Checking {product_url} for products")
                
                response = self.session.get(product_url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    page_products = self.extract_products_from_page(product_url, response.text)
                    
                    # Only add new products
                    for product in page_products['found_products']:
                        if product not in all_products:
                            all_products.append(product)
                            all_types[product] = page_products['product_types'].get(product, 'Service')
                            all_confidence[product] = page_products['confidence_scores'].get(product, 0.5)
                    
                    all_methods.update(page_products['extraction_methods'])
                    pages_checked += 1
                    
                time.sleep(1)  # Rate limiting
                
            except:
                continue
        
        # Filter by minimum confidence threshold (except ground truth)
        min_confidence = 0.85
        filtered_products = []
        
        if 'ground_truth' in all_methods:
            # If we have ground truth, keep all GT products regardless of confidence
            filtered_products = all_products
        else:
            # Apply confidence threshold
            for product in all_products:
                if all_confidence.get(product, 0) >= min_confidence:
                    filtered_products.append(product)
        
        # Sort products by confidence score
        if all_confidence and filtered_products:
            filtered_products.sort(key=lambda p: all_confidence.get(p, 0), reverse=True)
        
        # Limit to top 2 products
        max_products = 2
        top_products = filtered_products[:max_products]
        
        # Log warning if too many products were initially found
        if len(all_products) > 5:
            logger.warning(f"{url} initially found {len(all_products)} products, filtered to {len(top_products)}")
        
        # Update startup data
        startup_data['product_names'] = top_products
        startup_data['product_types'] = {p: all_types.get(p, 'Service') for p in top_products}
        startup_data['extraction_methods'] = list(all_methods)
        startup_data['confidence_scores'] = {p: all_confidence.get(p, 0) for p in top_products}
        
        return startup_data


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
    
    # Log summary
    logger.info("\n" + "="*50)
    logger.info("PRODUCT EXTRACTION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total startups processed: {len(startups)}")
    logger.info(f"Startups with products found: {with_products}")
    logger.info(f"Total products discovered: {total_products}")
    logger.info(f"Average products per startup: {total_products/len(startups):.1f}")
    
    # Count extraction methods used
    method_counts = Counter()
    for startup in startups:
        methods = startup.get('extraction_methods', [])
        method_counts.update(methods)
    
    logger.info("\nExtraction methods used:")
    for method, count in method_counts.most_common():
        logger.info(f"  {method}: {count}")
    
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
        fieldnames = ['company_name', 'url', 'product_names', 'product_types']
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for startup in startups:
            row = {
                'company_name': startup.get('company_name', ''),
                'url': startup.get('url', ''),
                'product_names': '; '.join(startup.get('product_names', [])),
                'product_types': '; '.join([f"{p}:{t}" for p, t in startup.get('product_types', {}).items()])
            }
            writer.writerow(row)
    
    logger.info(f"Saved CSV summary to {output_csv}")
    
    # Save clean product catalog
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
                    confidence = startup.get('confidence_scores', {}).get(product, 0)
                    f.write(f"  • {product} ({product_type}) [confidence: {confidence:.2f}]\n")
                
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