#!/usr/bin/env python3
"""
extract_locations.py - Extracts German/European city locations from startup URLs
Inputs: final_startup_urls.json
Outputs: finding_ort.json
"""

import json
import re
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LocationExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.location_mapping = {}
        
        # German and European cities
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
            'friedberg': 'Friedberg',
            'klosterlechfeld': 'Klosterlechfeld',
            
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
        
        # Contact/About page paths
        self.contact_paths = [
            '/impressum', '/imprint', '/kontakt', '/contact', 
            '/about', '/ueber-uns', '/uber-uns', '/about-us',
            '/unternehmen', '/company', '/standort', '/location'
        ]
    
    def extract_location_from_text(self, text: str) -> Optional[str]:
        """Extract city name from text"""
        text_lower = text.lower()
        
        # Check for German postal codes followed by city names
        postal_pattern = r'\b\d{5}\s+([A-Za-zäöüÄÖÜß\s\-]+)'
        matches = re.findall(postal_pattern, text)
        for match in matches:
            city = match.strip()
            city_lower = city.lower()
            if city_lower in self.city_mappings:
                return self.city_mappings[city_lower]
            elif len(city) > 3 and not city.isdigit():
                # Return the city name as-is if it looks valid
                return city.title()
        
        # Check for known city names in text
        for city_key, city_name in self.city_mappings.items():
            # Use word boundaries to avoid partial matches
            if re.search(rf'\b{re.escape(city_key)}\b', text_lower):
                return city_name
        
        return None
    
    def extract_from_structured_data(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract location from structured data"""
        # Check schema.org
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Direct address
                    if 'address' in data:
                        addr = data['address']
                        if isinstance(addr, dict) and 'addressLocality' in addr:
                            return addr['addressLocality']
                        elif isinstance(addr, str):
                            city = self.extract_location_from_text(addr)
                            if city:
                                return city
                    
                    # Location field
                    if 'location' in data:
                        loc = data['location']
                        if isinstance(loc, dict) and 'address' in loc:
                            addr = loc['address']
                            if isinstance(addr, dict) and 'addressLocality' in addr:
                                return addr['addressLocality']
            except:
                pass
        
        # Check meta tags
        location_meta = soup.find('meta', {'property': 'business:contact_data:locality'})
        if location_meta and location_meta.get('content'):
            return location_meta['content']
        
        # Check for address microformat
        address_elem = soup.find(['div', 'span'], {'itemprop': 'addressLocality'})
        if address_elem:
            return address_elem.get_text().strip()
        
        return None
    
    def extract_from_contact_pages(self, base_url: str) -> Optional[str]:
        """Try to extract location from contact/impressum pages"""
        for path in self.contact_paths:
            try:
                url = urljoin(base_url, path)
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try structured data first
                    location = self.extract_from_structured_data(soup)
                    if location:
                        return location
                    
                    # Then try text extraction
                    # Focus on specific sections
                    for section_id in ['impressum', 'contact', 'address', 'footer']:
                        section = soup.find(['div', 'section'], {'id': re.compile(section_id, re.I)})
                        if section:
                            text = section.get_text()
                            location = self.extract_location_from_text(text)
                            if location:
                                return location
                    
                    # Try the whole page text as last resort
                    text = soup.get_text()
                    location = self.extract_location_from_text(text[:5000])  # First 5000 chars
                    if location:
                        return location
            except:
                continue
        
        return None
    
    def extract_location(self, url: str) -> Optional[str]:
        """Extract location from URL"""
        try:
            # Get main page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try structured data
            location = self.extract_from_structured_data(soup)
            if location:
                return location
            
            # Try footer
            footer = soup.find('footer')
            if footer:
                text = footer.get_text()
                location = self.extract_location_from_text(text)
                if location:
                    return location
            
            # Try contact pages
            base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            location = self.extract_from_contact_pages(base_url)
            if location:
                return location
            
        except Exception as e:
            logger.error(f"Error extracting location from {url}: {str(e)}")
        
        return None
    
    def process_url(self, url: str):
        """Process a single URL"""
        location = self.extract_location(url)
        if location:
            self.location_mapping[url] = location
            logger.info(f"Found location: {url} -> {location}")
        else:
            logger.warning(f"No location found for: {url}")
    
    def run(self):
        """Run the extraction process"""
        # Load URLs
        try:
            with open('final_startup_urls.json', 'r', encoding='utf-8') as f:
                urls = json.load(f)
        except FileNotFoundError:
            logger.error("final_startup_urls.json not found. Run discover_urls.py first.")
            return
        
        logger.info(f"Processing {len(urls)} URLs for locations...")
        
        # Process URLs in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.process_url, url) for url in urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in thread: {str(e)}")
        
        # Save results
        with open('finding_ort.json', 'w', encoding='utf-8') as f:
            json.dump(self.location_mapping, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved locations for {len(self.location_mapping)} companies to finding_ort.json")


def main():
    extractor = LocationExtractor()
    extractor.run()


if __name__ == "__main__":
    main()