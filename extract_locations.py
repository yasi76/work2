#!/usr/bin/env python3
"""
Extract Locations Script
Inputs: final_startup_urls.json
Outputs: finding_ort.json
🧠 Finds German/European city using contact/impressum pages, structured data, and regex.
"""

import json
import re
from urllib.parse import urljoin
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
import time


class LocationExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # German and European cities
        self.major_cities = {
            'Berlin', 'München', 'Munich', 'Hamburg', 'Frankfurt', 'Köln', 'Cologne',
            'Stuttgart', 'Düsseldorf', 'Leipzig', 'Dresden', 'Hannover', 'Nürnberg',
            'Nuremberg', 'Bremen', 'Heidelberg', 'Mannheim', 'Karlsruhe', 'Bonn',
            'Münster', 'Augsburg', 'Potsdam', 'Darmstadt', 'Freiburg', 'Mainz',
            'Paris', 'London', 'Amsterdam', 'Vienna', 'Wien', 'Zurich', 'Zürich',
            'Brussels', 'Brüssel', 'Stockholm', 'Copenhagen', 'København', 'Oslo',
            'Helsinki', 'Dublin', 'Barcelona', 'Madrid', 'Milan', 'Milano', 'Rome',
            'Roma', 'Prague', 'Praha', 'Warsaw', 'Warszawa', 'Budapest'
        }
        
    def load_urls(self) -> Dict:
        """Load URLs from discovery output"""
        print("📁 Loading URLs from final_startup_urls.json...")
        try:
            with open('final_startup_urls.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {data['total_urls']} URLs")
            return data
        except FileNotFoundError:
            print("❌ Error: final_startup_urls.json not found!")
            print("Please run discover_urls.py first")
            return None
            
    def find_impressum_link(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Find impressum/imprint/contact page"""
        impressum_terms = ['impressum', 'imprint', 'kontakt', 'contact', 'about', 'über uns']
        
        for link in soup.find_all('a', href=True):
            link_text = link.text.lower().strip()
            href = link['href'].lower()
            
            if any(term in link_text or term in href for term in impressum_terms):
                return urljoin(base_url, link['href'])
                
        return None
        
    def extract_from_structured_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract location from structured data"""
        location_info = {}
        
        # Look for JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for address
                    if 'address' in data:
                        addr = data['address']
                        if isinstance(addr, dict):
                            location_info['city'] = addr.get('addressLocality', '')
                            location_info['country'] = addr.get('addressCountry', '')
                            location_info['postal_code'] = addr.get('postalCode', '')
                            
                    # Check for location
                    if 'location' in data and isinstance(data['location'], dict):
                        loc = data['location']
                        if 'address' in loc and isinstance(loc['address'], dict):
                            location_info['city'] = loc['address'].get('addressLocality', '')
                            location_info['country'] = loc['address'].get('addressCountry', '')
                            
            except:
                pass
                
        return location_info if location_info else None
        
    def extract_from_text(self, text: str) -> Optional[Dict]:
        """Extract location using regex patterns"""
        location_info = {}
        
        # German postal code pattern (5 digits)
        postal_pattern = r'\b(\d{5})\s+([A-Za-zÄÖÜäöüß\s\-]+)'
        postal_matches = re.findall(postal_pattern, text)
        
        for postal, city in postal_matches:
            # Check if city name looks valid
            city = city.strip()
            if len(city) > 2 and len(city) < 30:
                location_info['postal_code'] = postal
                location_info['city'] = city
                location_info['country'] = 'Germany'
                break
                
        # Look for city names
        for city in self.major_cities:
            if re.search(rf'\b{city}\b', text, re.IGNORECASE):
                location_info['city'] = city
                # Infer country from city
                if city in ['Berlin', 'München', 'Munich', 'Hamburg', 'Frankfurt', 'Köln', 'Cologne']:
                    location_info['country'] = 'Germany'
                elif city in ['Vienna', 'Wien']:
                    location_info['country'] = 'Austria'
                elif city in ['Zurich', 'Zürich']:
                    location_info['country'] = 'Switzerland'
                elif city in ['Paris']:
                    location_info['country'] = 'France'
                elif city in ['London']:
                    location_info['country'] = 'United Kingdom'
                break
                
        return location_info if location_info else None
        
    def extract_location(self, url: str) -> Dict:
        """Extract location information from URL"""
        location_data = {
            'city': None,
            'country': None,
            'postal_code': None,
            'extraction_method': None,
            'confidence': 0
        }
        
        try:
            # Fetch main page
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try structured data first
            structured_location = self.extract_from_structured_data(soup)
            if structured_location and structured_location.get('city'):
                location_data.update(structured_location)
                location_data['extraction_method'] = 'structured_data'
                location_data['confidence'] = 9
                return location_data
                
            # Look for impressum/contact page
            impressum_url = self.find_impressum_link(soup, url)
            if impressum_url:
                try:
                    imp_response = requests.get(impressum_url, headers=self.headers, timeout=10)
                    imp_soup = BeautifulSoup(imp_response.text, 'html.parser')
                    
                    # Extract from impressum text
                    text = imp_soup.get_text()
                    text_location = self.extract_from_text(text)
                    if text_location and text_location.get('city'):
                        location_data.update(text_location)
                        location_data['extraction_method'] = 'impressum'
                        location_data['confidence'] = 8
                        return location_data
                except:
                    pass
                    
            # Try main page text as fallback
            main_text = soup.get_text()
            text_location = self.extract_from_text(main_text)
            if text_location and text_location.get('city'):
                location_data.update(text_location)
                location_data['extraction_method'] = 'main_page_text'
                location_data['confidence'] = 6
                return location_data
                
        except Exception as e:
            print(f"  ⚠️ Error fetching {url}: {str(e)}")
            
        return location_data
        
    def extract_all_locations(self) -> Dict:
        """Extract locations for all URLs"""
        data = self.load_urls()
        if not data:
            return None
            
        print("\n🔍 Extracting locations...")
        print("=" * 50)
        
        results = []
        total = len(data['urls'])
        
        for i, url_data in enumerate(data['urls'], 1):
            url = url_data['url']
            print(f"\n[{i}/{total}] Processing {url}")
            
            location = self.extract_location(url)
            
            if location['city']:
                print(f"  ✅ Location: {location['city']}, {location['country']}")
                print(f"     Method: {location['extraction_method']} (confidence: {location['confidence']})")
            else:
                print(f"  ⚠️ No location found")
                
            results.append({
                'url': url,
                'location': location,
                'source': url_data.get('source', 'Unknown'),
                'url_confidence': url_data.get('confidence', 0)
            })
            
            # Rate limiting
            if i < total:
                time.sleep(0.5)
                
        # Calculate statistics
        found_locations = len([r for r in results if r['location']['city']])
        german_locations = len([r for r in results if r['location']['country'] == 'Germany'])
        
        # Save results
        output = {
            'timestamp': data['timestamp'],
            'total_urls': len(results),
            'urls_with_location': found_locations,
            'german_locations': german_locations,
            'extraction_methods': {
                'structured_data': len([r for r in results if r['location']['extraction_method'] == 'structured_data']),
                'impressum': len([r for r in results if r['location']['extraction_method'] == 'impressum']),
                'main_page_text': len([r for r in results if r['location']['extraction_method'] == 'main_page_text']),
                'not_found': len([r for r in results if not r['location']['city']])
            },
            'locations': results
        }
        
        with open('finding_ort.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Extraction complete!")
        print(f"📊 URLs with location: {found_locations}/{len(results)}")
        print(f"📊 German locations: {german_locations}")
        print(f"📁 Output saved to: finding_ort.json")
        
        return output


def main():
    """Main function"""
    extractor = LocationExtractor()
    extractor.extract_all_locations()


if __name__ == "__main__":
    main()