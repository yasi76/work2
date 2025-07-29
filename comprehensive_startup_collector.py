#!/usr/bin/env python3
"""
Comprehensive Digital Health Startup Data Collector
Merges hardcoded lists, GT data, web searches, and extracts company information
"""

import json
import csv
import time
import re
import requests
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveStartupCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.all_urls = set()
        self.startup_data = {}
        
        # Load existing data
        self.ground_truth_companies = self._load_ground_truth_companies()
        self.ground_truth_products = self._load_ground_truth_products()
        self.domain_name_map = self._load_domain_map()
        self.hardcoded_urls = self._load_hardcoded_urls()
        
        # Location mappings for German/European cities
        self.city_mappings = {
            # Major German cities
            'berlin': 'Berlin',
            'münchen': 'München',
            'munich': 'München',
            'hamburg': 'Hamburg',
            'frankfurt': 'Frankfurt',
            'köln': 'Köln',
            'cologne': 'Köln',
            'stuttgart': 'Stuttgart',
            'düsseldorf': 'Düsseldorf',
            'dortmund': 'Dortmund',
            'essen': 'Essen',
            'leipzig': 'Leipzig',
            'bremen': 'Bremen',
            'dresden': 'Dresden',
            'hannover': 'Hannover',
            'nürnberg': 'Nürnberg',
            'nuremberg': 'Nürnberg',
            'duisburg': 'Duisburg',
            'bochum': 'Bochum',
            'wuppertal': 'Wuppertal',
            'bielefeld': 'Bielefeld',
            'bonn': 'Bonn',
            'münster': 'Münster',
            'mannheim': 'Mannheim',
            'augsburg': 'Augsburg',
            'wiesbaden': 'Wiesbaden',
            'mönchengladbach': 'Mönchengladbach',
            'gelsenkirchen': 'Gelsenkirchen',
            'aachen': 'Aachen',
            'braunschweig': 'Braunschweig',
            'chemnitz': 'Chemnitz',
            'kiel': 'Kiel',
            'krefeld': 'Krefeld',
            'halle': 'Halle',
            'magdeburg': 'Magdeburg',
            'freiburg': 'Freiburg',
            'oberhausen': 'Oberhausen',
            'lübeck': 'Lübeck',
            'erfurt': 'Erfurt',
            'rostock': 'Rostock',
            'mainz': 'Mainz',
            'kassel': 'Kassel',
            'hagen': 'Hagen',
            'hamm': 'Hamm',
            'saarbrücken': 'Saarbrücken',
            'mülheim': 'Mülheim',
            'herne': 'Herne',
            'ludwigshafen': 'Ludwigshafen',
            'osnabrück': 'Osnabrück',
            'solingen': 'Solingen',
            'leverkusen': 'Leverkusen',
            'oldenburg': 'Oldenburg',
            'potsdam': 'Potsdam',
            'neuss': 'Neuss',
            'heidelberg': 'Heidelberg',
            'darmstadt': 'Darmstadt',
            'regensburg': 'Regensburg',
            'würzburg': 'Würzburg',
            'wolfsburg': 'Wolfsburg',
            'göttingen': 'Göttingen',
            'recklinghausen': 'Recklinghausen',
            'heilbronn': 'Heilbronn',
            'ingolstadt': 'Ingolstadt',
            'ulm': 'Ulm',
            'pforzheim': 'Pforzheim',
            'bottrop': 'Bottrop',
            'offenbach': 'Offenbach',
            'fürth': 'Fürth',
            'remscheid': 'Remscheid',
            'reutlingen': 'Reutlingen',
            'moers': 'Moers',
            'koblenz': 'Koblenz',
            'erlangen': 'Erlangen',
            'siegen': 'Siegen',
            'trier': 'Trier',
            'jena': 'Jena',
            'bremerhaven': 'Bremerhaven',
            'hildesheim': 'Hildesheim',
            'cottbus': 'Cottbus',
            
            # European cities
            'paris': 'Paris',
            'london': 'London',
            'barcelona': 'Barcelona',
            'madrid': 'Madrid',
            'amsterdam': 'Amsterdam',
            'vienna': 'Vienna',
            'wien': 'Vienna',
            'zurich': 'Zurich',
            'zürich': 'Zurich',
            'geneva': 'Geneva',
            'genève': 'Geneva',
            'copenhagen': 'Copenhagen',
            'københavn': 'Copenhagen',
            'stockholm': 'Stockholm',
            'oslo': 'Oslo',
            'helsinki': 'Helsinki',
            'brussels': 'Brussels',
            'bruxelles': 'Brussels',
            'lisbon': 'Lisbon',
            'lisboa': 'Lisbon',
            'prague': 'Prague',
            'praha': 'Prague',
            'warsaw': 'Warsaw',
            'warszawa': 'Warsaw',
            'budapest': 'Budapest',
            'dublin': 'Dublin',
            'milan': 'Milan',
            'milano': 'Milan',
            'rome': 'Rome',
            'roma': 'Rome',
            'athens': 'Athens'
        }
    
    def _load_ground_truth_companies(self) -> Dict[str, str]:
        """Load ground truth company names"""
        return {
            "https://www.acalta.de": "Acalta GmbH",
            "https://www.actimi.com": "Actimi GmbH",
            "https://www.emmora.de": "Ahorn AG",
            "https://www.alfa-ai.com": "ALFA AI GmbH",
            "https://www.apheris.com": "apheris AI GmbH",
            "https://www.aporize.com/": "Aporize",
            "https://www.arztlena.com/": "Artificy GmbH",
            "https://shop.getnutrio.com/": "Aurora Life Sciene GmbH",
            "https://www.auta.health/": "Auta Health UG",
            "https://visioncheckout.com/": "auvisus GmbH",
            "https://www.avayl.tech/": "AVAYL GmbH",
            "https://www.avimedical.com/avi-impact": "Avi Medical Operations GmbH",
            "https://de.becureglobal.com/": "BECURE GmbH",
            "https://bellehealth.co/de/": "Belle Health GmbH",
            "https://www.biotx.ai/": "biotx.ai GmbH",
            "https://www.brainjo.de/": "brainjo GmbH",
            "https://brea.app/": "Brea Health GmbH",
            "https://breathment.com/": "Breathment GmbH",
            "https://de.caona.eu/": "Caona Health GmbH",
            "https://www.careanimations.de/": "CAREANIMATIONS GmbH",
            "https://sfs-healthcare.com": "Change IT Solutions GmbH",
            "https://www.climedo.de/": "Climedo Health GmbH",
            "https://www.cliniserve.de/": "Clinicserve GmbH",
            "https://cogthera.de/#erfahren": "Cogthera GmbH",
            "https://www.comuny.de/": "comuny GmbH",
            "https://curecurve.de/elina-app/": "CureCurve Medical AI GmbH",
            "https://www.cynteract.com/de/rehabilitation": "Cynteract GmbH",
            "https://www.healthmeapp.de/de/": "Declareme GmbH",
            "https://deepeye.ai/": "deepeye medical GmbH",
            "https://www.deepmentation.ai/": "deepmentation UG",
            "https://denton-systems.de/": "Denton Systems GmbH",
            "https://www.derma2go.com/": "derma2go Deutschland GmbH",
            "https://www.dianovi.com/": "dianovi GmbH (ehem. MySympto)",
            "http://dopavision.com/": "Dopavision GmbH",
            "https://www.dpv-analytics.com/": "dpv-analytics GmbH",
            "http://www.ecovery.de/": "eCovery GmbH",
            "https://elixionmedical.com/": "Elixion Medical",
            "https://www.empident.de/": "Empident GmbH",
            "https://eye2you.ai/": "eye2you",
            "https://www.fitwhit.de": "FitwHit & LABOR FÜR BIOMECHANIK der JLU-Gießen",
            "https://www.floy.com/": "Floy GmbH",
            "https://fyzo.de/assistant/": "fyzo GmbH",
            "https://www.gesund.de/app": "gesund.de GmbH & Co. KG",
            "https://www.glaice.de/": "GLACIE Health UG",
            "https://gleea.de/": "Gleea Educational Software GmbH",
            "https://www.guidecare.de/": "GuideCare GmbH",
            "https://www.apodienste.com/": "Healthy Codes GmbH",
            "https://www.help-app.de/": "Help Mee Schmerztherapie GmbH",
            "https://www.heynanny.com/": "heynannyly GmbH",
            "https://incontalert.de/": "inContAlert GmbH",
            "https://home.informme.info/": "InformMe GmbH",
            "https://www.kranushealth.com/de/therapien/haeufiger-harndrang": "Kranus Health GmbH",
            "https://www.kranushealth.com/de/therapien/inkontinenz": "Kranus Health GmbH",
        }
    
    def _load_ground_truth_products(self) -> Dict[str, List[str]]:
        """Load ground truth product names"""
        return {
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
    
    def _load_domain_map(self) -> Dict[str, str]:
        """Load domain to company name mappings"""
        try:
            with open('domain_name_map.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_hardcoded_urls(self) -> List[str]:
        """Load hardcoded URLs from the discovery script"""
        return [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://www.emmora.de',
            'https://www.alfa-ai.com',
            'https://www.apheris.com',
            'https://www.aporize.com/',
            'https://www.arztlena.com/',
            'https://shop.getnutrio.com/',
            'https://www.auta.health/',
            'https://visioncheckout.com/',
            'https://www.avayl.tech/',
            'https://www.avimedical.com/avi-impact',
            'https://de.becureglobal.com/',
            'https://bellehealth.co/de/',
            'https://www.biotx.ai/',
            'https://www.brainjo.de/',
            'https://brea.app/',
            'https://breathment.com/',
            'https://de.caona.eu/',
            'https://www.careanimations.de/',
            'https://sfs-healthcare.com',
            'https://www.climedo.de/',
            'https://www.cliniserve.de/',
            'https://cogthera.de/#erfahren',
            'https://www.comuny.de/',
            'https://curecurve.de/elina-app/',
            'https://www.cynteract.com/de/rehabilitation',
            'https://www.healthmeapp.de/de/',
            'https://deepeye.ai/',
            'https://www.deepmentation.ai/',
            'https://denton-systems.de/',
            'https://www.derma2go.com/',
            'https://www.dianovi.com/',
            'http://dopavision.com/',
            'https://www.dpv-analytics.com/',
            'http://www.ecovery.de/',
            'https://elixionmedical.com/',
            'https://www.empident.de/',
            'https://eye2you.ai/',
            'https://www.fitwhit.de',
            'https://www.floy.com/',
            'https://fyzo.de/assistant/',
            'https://www.gesund.de/app',
            'https://www.glaice.de/',
            'https://gleea.de/',
            'https://www.guidecare.de/',
            'https://www.apodienste.com/',
            'https://www.help-app.de/',
            'https://www.heynanny.com/',
            'https://incontalert.de/',
            'https://home.informme.info/',
            'https://www.kranushealth.com/de/therapien/haeufiger-harndrang',
            'https://www.kranushealth.com/de/therapien/inkontinenz'
        ]
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent comparison"""
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        return url
    
    def extract_location_from_page(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        """Extract location from webpage content"""
        location = None
        
        # Check structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'address' in data:
                        addr = data['address']
                        if isinstance(addr, dict) and 'addressLocality' in addr:
                            location = addr['addressLocality']
                            break
                        elif isinstance(addr, str):
                            # Parse string address
                            parts = addr.split(',')
                            for part in parts:
                                city = self._extract_city_from_text(part.strip())
                                if city:
                                    location = city
                                    break
            except:
                pass
        
        # Check meta tags
        if not location:
            location_meta = soup.find('meta', {'property': 'business:contact_data:locality'})
            if location_meta:
                location = location_meta.get('content')
        
        # Check footer and contact sections
        if not location:
            for section in ['footer', 'contact', 'impressum', 'kontakt', 'about']:
                section_elem = soup.find(['div', 'section'], {'id': re.compile(section, re.I)})
                if not section_elem:
                    section_elem = soup.find(['div', 'section'], {'class': re.compile(section, re.I)})
                
                if section_elem:
                    text = section_elem.get_text()
                    city = self._extract_city_from_text(text)
                    if city:
                        location = city
                        break
        
        return location
    
    def _extract_city_from_text(self, text: str) -> Optional[str]:
        """Extract city name from text using known city list"""
        text_lower = text.lower()
        
        # Check for German postal codes followed by city names
        postal_pattern = r'\b\d{5}\s+([A-Za-zäöüÄÖÜß\s\-]+)'
        matches = re.findall(postal_pattern, text)
        for match in matches:
            city = match.strip()
            city_lower = city.lower()
            if city_lower in self.city_mappings:
                return self.city_mappings[city_lower]
            elif len(city) > 3:  # Likely a city name
                return city.title()
        
        # Check for known city names
        for city_key, city_name in self.city_mappings.items():
            if city_key in text_lower:
                return city_name
        
        return None
    
    def fetch_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_company_info(self, url: str) -> Dict[str, any]:
        """Extract company information from URL"""
        info = {
            'url': url,
            'company_name': None,
            'product_names': [],
            'location': None,
            'found_in_gt': False
        }
        
        # Check ground truth first
        normalized_url = self.normalize_url(url)
        for gt_url, company_name in self.ground_truth_companies.items():
            if self.normalize_url(gt_url) == normalized_url:
                info['company_name'] = company_name
                info['found_in_gt'] = True
                break
        
        for gt_url, products in self.ground_truth_products.items():
            if self.normalize_url(gt_url) == normalized_url:
                info['product_names'] = products
                break
        
        # Check domain map
        if not info['company_name']:
            domain = urlparse(url).netloc.replace('www.', '')
            if domain in self.domain_name_map:
                info['company_name'] = self.domain_name_map[domain]
        
        # Fetch page for additional info
        soup = self.fetch_page_content(url)
        if soup:
            # Extract location
            info['location'] = self.extract_location_from_page(url, soup)
            
            # Extract company name if not found
            if not info['company_name']:
                # Try meta tags
                og_title = soup.find('meta', {'property': 'og:site_name'})
                if og_title:
                    info['company_name'] = og_title.get('content')
                else:
                    # Try title
                    title = soup.find('title')
                    if title:
                        title_text = title.get_text().strip()
                        # Clean common patterns
                        title_text = re.sub(r'\s*[\-\|]\s*(Home|Start|Welcome).*$', '', title_text, flags=re.I)
                        info['company_name'] = title_text
        
        return info
    
    def search_additional_startups(self) -> List[str]:
        """Search for additional digital health startups"""
        additional_urls = []
        
        # Add curated startup URLs
        curated_urls = [
            # German Digital Health Leaders
            'https://www.ada.com',
            'https://www.doctolib.de',
            'https://www.kaia-health.com',
            'https://www.teleclinic.com',
            'https://www.zavamed.com',
            'https://www.medwing.com',
            'https://www.felmo.de',
            'https://www.viomedo.de',
            'https://www.caresyntax.com',
            'https://www.merantix.com',
            'https://www.contextflow.com',
            'https://www.heartkinetics.com',
            'https://www.samedi.de',
            'https://www.medigene.com',
            'https://www.smartpatient.eu',
            
            # European Digital Health
            'https://www.doctolib.fr',
            'https://www.livi.co.uk',
            'https://www.babylon.com',
            'https://www.echo.co.uk',
            'https://www.accurx.com',
            'https://www.zava.com',
            'https://www.medgate.ch',
            'https://www.kry.se',
            'https://www.medadom.com',
            'https://www.qare.fr',
            
            # Additional German startups
            'https://www.neosfer.de',
            'https://www.preventicus.com',
            'https://www.thryve.health',
            'https://www.xim.ai',
            'https://www.lindera.de',
            'https://www.kenbi.eu',
            'https://www.mindable.health',
            'https://www.inveox.com',
            'https://www.medipee.com',
            'https://www.skinly.de',
            'https://www.tinnitracks.com',
            'https://www.mediteo.com',
            'https://www.mika.health',
            'https://www.sonormed.de',
            'https://www.vitadock.com'
        ]
        
        additional_urls.extend(curated_urls)
        return additional_urls
    
    def process_all_sources(self):
        """Process all data sources and merge"""
        logger.info("Starting comprehensive startup data collection...")
        
        # 1. Add hardcoded URLs
        logger.info("Processing hardcoded URLs...")
        for url in self.hardcoded_urls:
            self.all_urls.add(url)
        
        # 2. Add ground truth URLs
        logger.info("Processing ground truth URLs...")
        for url in self.ground_truth_companies.keys():
            self.all_urls.add(url)
        
        # 3. Search for additional startups
        logger.info("Searching for additional startups...")
        additional_urls = self.search_additional_startups()
        for url in additional_urls:
            self.all_urls.add(url)
        
        # 4. Process all URLs
        logger.info(f"Processing {len(self.all_urls)} unique URLs...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.extract_company_info, url): url 
                           for url in self.all_urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    info = future.result()
                    self.startup_data[url] = info
                    logger.info(f"Processed: {url}")
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
    
    def generate_output_files(self):
        """Generate all required output files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Final startup URLs
        final_urls = sorted(list(self.all_urls))
        with open('final_startup_urls.json', 'w', encoding='utf-8') as f:
            json.dump(final_urls, f, indent=2, ensure_ascii=False)
        
        # 2. Company name mapping
        company_mapping = {}
        for url, data in self.startup_data.items():
            if data.get('company_name'):
                company_mapping[url] = data['company_name']
        
        with open('company_name_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(company_mapping, f, indent=2, ensure_ascii=False)
        
        # 3. Product names
        product_mapping = {}
        for url, data in self.startup_data.items():
            if data.get('product_names'):
                product_mapping[url] = data['product_names']
        
        with open('product_names.json', 'w', encoding='utf-8') as f:
            json.dump(product_mapping, f, indent=2, ensure_ascii=False)
        
        # 4. Location mapping
        location_mapping = {}
        for url, data in self.startup_data.items():
            if data.get('location'):
                location_mapping[url] = data['location']
        
        with open('finding_ort.json', 'w', encoding='utf-8') as f:
            json.dump(location_mapping, f, indent=2, ensure_ascii=False)
        
        # 5. Summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        total_urls = len(self.all_urls)
        urls_with_company = sum(1 for data in self.startup_data.values() if data.get('company_name'))
        urls_with_products = sum(1 for data in self.startup_data.values() if data.get('product_names'))
        urls_with_location = sum(1 for data in self.startup_data.values() if data.get('location'))
        gt_coverage = sum(1 for data in self.startup_data.values() if data.get('found_in_gt'))
        
        report_content = f"""
Digital Health Startup Discovery - Summary Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================

Total URLs discovered: {total_urls}

Data Coverage:
- URLs with company names: {urls_with_company} ({urls_with_company/total_urls*100:.1f}%)
- URLs with product names: {urls_with_products} ({urls_with_products/total_urls*100:.1f}%)
- URLs with locations: {urls_with_location} ({urls_with_location/total_urls*100:.1f}%)

Ground Truth Coverage:
- GT companies included: {len(self.ground_truth_companies)}
- GT products included: {len(self.ground_truth_products)}
- URLs found in GT: {gt_coverage} ({gt_coverage/total_urls*100:.1f}%)

Data Sources:
- Hardcoded URLs: {len(self.hardcoded_urls)}
- Ground Truth URLs: {len(self.ground_truth_companies)}
- Additional discovered: {total_urls - len(self.hardcoded_urls) - len(self.ground_truth_companies)}

Location Distribution:
"""
        # Count locations
        location_counts = {}
        for data in self.startup_data.values():
            loc = data.get('location')
            if loc:
                location_counts[loc] = location_counts.get(loc, 0) + 1
        
        for location, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
            report_content += f"  - {location}: {count}\n"
        
        report_content += f"\nUnknown locations: {total_urls - urls_with_location}\n"
        
        with open('summary_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info("Summary report generated")
    
    def run(self):
        """Run the complete collection process"""
        self.process_all_sources()
        self.generate_output_files()
        logger.info("Data collection completed successfully!")


def main():
    collector = ComprehensiveStartupCollector()
    collector.run()


if __name__ == "__main__":
    main()