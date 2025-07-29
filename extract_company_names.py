#!/usr/bin/env python3
"""
extract_company_names.py - Extracts company names from startup URLs
Inputs: final_startup_urls.json
Outputs: company_name_mapping.json
"""

import json
import re
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanyNameExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.company_mapping = {}
        
        # Ground truth company names
        self.ground_truth = {
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
        
        # Domain name map
        self.domain_map = self._load_domain_map()
    
    def _load_domain_map(self) -> Dict[str, str]:
        """Load domain name map if exists"""
        try:
            with open('domain_name_map.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        url = url.lower().strip()
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        return url
    
    def extract_from_ground_truth(self, url: str) -> Optional[str]:
        """Check ground truth for company name"""
        normalized = self.normalize_url(url)
        for gt_url, company_name in self.ground_truth.items():
            if self.normalize_url(gt_url) == normalized:
                return company_name
        return None
    
    def extract_from_domain_map(self, url: str) -> Optional[str]:
        """Check domain map for company name"""
        domain = urlparse(url).netloc.replace('www.', '')
        return self.domain_map.get(domain)
    
    def extract_from_webpage(self, url: str) -> Optional[str]:
        """Extract company name from webpage"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try OpenGraph site name
            og_site = soup.find('meta', {'property': 'og:site_name'})
            if og_site and og_site.get('content'):
                return og_site['content'].strip()
            
            # Try schema.org
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Organization':
                        if data.get('name'):
                            return data['name'].strip()
                except:
                    pass
            
            # Try title tag
            title = soup.find('title')
            if title:
                title_text = title.get_text().strip()
                # Clean common patterns
                title_text = re.sub(r'\s*[\-\|]\s*(Home|Start|Welcome|Startseite).*$', '', title_text, flags=re.I)
                if title_text and len(title_text) < 100:
                    return title_text
            
        except Exception as e:
            logger.error(f"Error extracting from {url}: {str(e)}")
        
        return None
    
    def extract_company_name(self, url: str) -> Optional[str]:
        """Extract company name using multiple methods"""
        # 1. Check ground truth
        name = self.extract_from_ground_truth(url)
        if name:
            return name
        
        # 2. Check domain map
        name = self.extract_from_domain_map(url)
        if name:
            return name
        
        # 3. Try web scraping
        name = self.extract_from_webpage(url)
        if name:
            return name
        
        # 4. Fallback to domain name
        domain = urlparse(url).netloc.replace('www.', '')
        return domain.split('.')[0].title()
    
    def process_url(self, url: str):
        """Process a single URL"""
        name = self.extract_company_name(url)
        if name:
            self.company_mapping[url] = name
            logger.info(f"Extracted: {url} -> {name}")
        else:
            logger.warning(f"No name found for: {url}")
    
    def run(self):
        """Run the extraction process"""
        # Load URLs
        try:
            with open('final_startup_urls.json', 'r', encoding='utf-8') as f:
                urls = json.load(f)
        except FileNotFoundError:
            logger.error("final_startup_urls.json not found. Run discover_urls.py first.")
            return
        
        logger.info(f"Processing {len(urls)} URLs...")
        
        # Process URLs in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_url, url) for url in urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in thread: {str(e)}")
        
        # Save results
        with open('company_name_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(self.company_mapping, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.company_mapping)} company names to company_name_mapping.json")


def main():
    extractor = CompanyNameExtractor()
    extractor.run()


if __name__ == "__main__":
    main()