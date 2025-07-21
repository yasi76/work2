#!/usr/bin/env python3
"""
🌍 Location Extractor for URLs
================================
Extract state, city, and location information from URLs using multiple approaches.
"""

import re
import urllib.request
import urllib.parse
import json
import time
from urllib.parse import urlparse
from typing import Dict, Optional, Tuple, List

class LocationExtractor:
    """Extract location information from URLs and website content."""
    
    def __init__(self):
        """Initialize location extractor with patterns and mappings."""
        # German state patterns (since many URLs are .de)
        self.german_states = {
            'baden-wurttemberg': 'Baden-Württemberg',
            'bavaria': 'Bavaria', 'bayern': 'Bavaria',
            'berlin': 'Berlin',
            'brandenburg': 'Brandenburg',
            'bremen': 'Bremen',
            'hamburg': 'Hamburg',
            'hesse': 'Hesse', 'hessen': 'Hesse',
            'lower-saxony': 'Lower Saxony', 'niedersachsen': 'Lower Saxony',
            'mecklenburg-vorpommern': 'Mecklenburg-Vorpommern',
            'north-rhine-westphalia': 'North Rhine-Westphalia', 'nrw': 'North Rhine-Westphalia',
            'rhineland-palatinate': 'Rhineland-Palatinate', 'rheinland-pfalz': 'Rhineland-Palatinate',
            'saarland': 'Saarland',
            'saxony': 'Saxony', 'sachsen': 'Saxony',
            'saxony-anhalt': 'Saxony-Anhalt', 'sachsen-anhalt': 'Saxony-Anhalt',
            'schleswig-holstein': 'Schleswig-Holstein',
            'thuringia': 'Thuringia', 'thuringen': 'Thuringia'
        }
        
        # Major German cities
        self.german_cities = {
            'berlin': 'Berlin',
            'hamburg': 'Hamburg',
            'munich': 'Munich', 'munchen': 'Munich',
            'cologne': 'Cologne', 'koln': 'Cologne',
            'frankfurt': 'Frankfurt',
            'stuttgart': 'Stuttgart',
            'dusseldorf': 'Düsseldorf',
            'dortmund': 'Dortmund',
            'essen': 'Essen',
            'leipzig': 'Leipzig',
            'bremen': 'Bremen',
            'dresden': 'Dresden',
            'hannover': 'Hannover',
            'nuremberg': 'Nuremberg', 'nurnberg': 'Nuremberg',
            'duisburg': 'Duisburg',
            'bochum': 'Bochum',
            'wuppertal': 'Wuppertal',
            'bielefeld': 'Bielefeld',
            'bonn': 'Bonn',
            'mannheim': 'Mannheim'
        }
        
        # US states abbreviations and names
        self.us_states = {
            'al': 'Alabama', 'alabama': 'Alabama',
            'ak': 'Alaska', 'alaska': 'Alaska',
            'az': 'Arizona', 'arizona': 'Arizona',
            'ar': 'Arkansas', 'arkansas': 'Arkansas',
            'ca': 'California', 'california': 'California',
            'co': 'Colorado', 'colorado': 'Colorado',
            'ct': 'Connecticut', 'connecticut': 'Connecticut',
            'de': 'Delaware', 'delaware': 'Delaware',
            'fl': 'Florida', 'florida': 'Florida',
            'ga': 'Georgia', 'georgia': 'Georgia',
            'hi': 'Hawaii', 'hawaii': 'Hawaii',
            'id': 'Idaho', 'idaho': 'Idaho',
            'il': 'Illinois', 'illinois': 'Illinois',
            'in': 'Indiana', 'indiana': 'Indiana',
            'ia': 'Iowa', 'iowa': 'Iowa',
            'ks': 'Kansas', 'kansas': 'Kansas',
            'ky': 'Kentucky', 'kentucky': 'Kentucky',
            'la': 'Louisiana', 'louisiana': 'Louisiana',
            'me': 'Maine', 'maine': 'Maine',
            'md': 'Maryland', 'maryland': 'Maryland',
            'ma': 'Massachusetts', 'massachusetts': 'Massachusetts',
            'mi': 'Michigan', 'michigan': 'Michigan',
            'mn': 'Minnesota', 'minnesota': 'Minnesota',
            'ms': 'Mississippi', 'mississippi': 'Mississippi',
            'mo': 'Missouri', 'missouri': 'Missouri',
            'mt': 'Montana', 'montana': 'Montana',
            'ne': 'Nebraska', 'nebraska': 'Nebraska',
            'nv': 'Nevada', 'nevada': 'Nevada',
            'nh': 'New Hampshire', 'new-hampshire': 'New Hampshire',
            'nj': 'New Jersey', 'new-jersey': 'New Jersey',
            'nm': 'New Mexico', 'new-mexico': 'New Mexico',
            'ny': 'New York', 'new-york': 'New York',
            'nc': 'North Carolina', 'north-carolina': 'North Carolina',
            'nd': 'North Dakota', 'north-dakota': 'North Dakota',
            'oh': 'Ohio', 'ohio': 'Ohio',
            'ok': 'Oklahoma', 'oklahoma': 'Oklahoma',
            'or': 'Oregon', 'oregon': 'Oregon',
            'pa': 'Pennsylvania', 'pennsylvania': 'Pennsylvania',
            'ri': 'Rhode Island', 'rhode-island': 'Rhode Island',
            'sc': 'South Carolina', 'south-carolina': 'South Carolina',
            'sd': 'South Dakota', 'south-dakota': 'South Dakota',
            'tn': 'Tennessee', 'tennessee': 'Tennessee',
            'tx': 'Texas', 'texas': 'Texas',
            'ut': 'Utah', 'utah': 'Utah',
            'vt': 'Vermont', 'vermont': 'Vermont',
            'va': 'Virginia', 'virginia': 'Virginia',
            'wa': 'Washington', 'washington': 'Washington',
            'wv': 'West Virginia', 'west-virginia': 'West Virginia',
            'wi': 'Wisconsin', 'wisconsin': 'Wisconsin',
            'wy': 'Wyoming', 'wyoming': 'Wyoming'
        }
        
        # Major US cities
        self.us_cities = {
            'new-york': 'New York', 'nyc': 'New York',
            'los-angeles': 'Los Angeles', 'la': 'Los Angeles',
            'chicago': 'Chicago',
            'houston': 'Houston',
            'phoenix': 'Phoenix',
            'philadelphia': 'Philadelphia',
            'san-antonio': 'San Antonio',
            'san-diego': 'San Diego',
            'dallas': 'Dallas',
            'san-jose': 'San Jose',
            'austin': 'Austin',
            'jacksonville': 'Jacksonville',
            'fort-worth': 'Fort Worth',
            'columbus': 'Columbus',
            'san-francisco': 'San Francisco',
            'charlotte': 'Charlotte',
            'indianapolis': 'Indianapolis',
            'seattle': 'Seattle',
            'denver': 'Denver',
            'washington': 'Washington D.C.', 'dc': 'Washington D.C.',
            'boston': 'Boston',
            'el-paso': 'El Paso',
            'detroit': 'Detroit',
            'nashville': 'Nashville',
            'portland': 'Portland',
            'memphis': 'Memphis',
            'oklahoma-city': 'Oklahoma City',
            'las-vegas': 'Las Vegas',
            'louisville': 'Louisville',
            'baltimore': 'Baltimore',
            'milwaukee': 'Milwaukee',
            'albuquerque': 'Albuquerque',
            'tucson': 'Tucson',
            'fresno': 'Fresno',
            'mesa': 'Mesa',
            'sacramento': 'Sacramento',
            'atlanta': 'Atlanta',
            'kansas-city': 'Kansas City',
            'colorado-springs': 'Colorado Springs',
            'miami': 'Miami',
            'raleigh': 'Raleigh',
            'omaha': 'Omaha',
            'long-beach': 'Long Beach',
            'virginia-beach': 'Virginia Beach',
            'oakland': 'Oakland',
            'minneapolis': 'Minneapolis',
            'tulsa': 'Tulsa',
            'arlington': 'Arlington',
            'tampa': 'Tampa',
            'new-orleans': 'New Orleans',
            'wichita': 'Wichita',
            'cleveland': 'Cleveland',
            'bakersfield': 'Bakersfield',
            'aurora': 'Aurora',
            'anaheim': 'Anaheim',
            'honolulu': 'Honolulu',
            'santa-ana': 'Santa Ana',
            'riverside': 'Riverside',
            'corpus-christi': 'Corpus Christi',
            'lexington': 'Lexington',
            'stockton': 'Stockton',
            'henderson': 'Henderson',
            'saint-paul': 'Saint Paul',
            'st-paul': 'Saint Paul',
            'cincinnati': 'Cincinnati',
            'pittsburgh': 'Pittsburgh'
        }
        
        # European cities (beyond Germany)
        self.european_cities = {
            'london': 'London',
            'paris': 'Paris',
            'madrid': 'Madrid',
            'rome': 'Rome',
            'amsterdam': 'Amsterdam',
            'vienna': 'Vienna',
            'brussels': 'Brussels',
            'dublin': 'Dublin',
            'lisbon': 'Lisbon',
            'stockholm': 'Stockholm',
            'copenhagen': 'Copenhagen',
            'oslo': 'Oslo',
            'helsinki': 'Helsinki',
            'zurich': 'Zurich',
            'geneva': 'Geneva',
            'prague': 'Prague',
            'budapest': 'Budapest',
            'warsaw': 'Warsaw',
            'barcelona': 'Barcelona',
            'milan': 'Milan',
            'naples': 'Naples',
            'turin': 'Turin',
            'marseille': 'Marseille',
            'lyon': 'Lyon',
            'toulouse': 'Toulouse',
            'nice': 'Nice',
            'gothenburg': 'Gothenburg',
            'malmo': 'Malmö'
        }
    
    def extract_from_url_path(self, url: str) -> Dict[str, Optional[str]]:
        """Extract location information from URL path and subdomain."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            # Combine domain and path for analysis
            full_text = f"{domain} {path}".replace('/', ' ').replace('-', ' ').replace('_', ' ')
            words = [word.strip() for word in full_text.split() if word.strip()]
            
            result = {
                'country': None,
                'state': None,
                'city': None,
                'method': 'url_analysis'
            }
            
            # Look for country indicators in domain
            if '.de' in domain or 'germany' in full_text or 'german' in full_text:
                result['country'] = 'Germany'
                
                # Look for German states and cities
                for word in words:
                    if word in self.german_states:
                        result['state'] = self.german_states[word]
                    if word in self.german_cities:
                        result['city'] = self.german_cities[word]
                        
            elif '.com' in domain or '.us' in domain:
                # Check for US indicators
                for word in words:
                    if word in self.us_states:
                        result['country'] = 'United States'
                        result['state'] = self.us_states[word]
                    if word in self.us_cities:
                        result['country'] = 'United States'
                        result['city'] = self.us_cities[word]
                        
            elif any(tld in domain for tld in ['.uk', '.fr', '.es', '.it', '.nl', '.se', '.no', '.dk', '.fi']):
                # European TLDs
                if '.uk' in domain:
                    result['country'] = 'United Kingdom'
                elif '.fr' in domain:
                    result['country'] = 'France'
                elif '.es' in domain:
                    result['country'] = 'Spain'
                elif '.it' in domain:
                    result['country'] = 'Italy'
                elif '.nl' in domain:
                    result['country'] = 'Netherlands'
                elif '.se' in domain:
                    result['country'] = 'Sweden'
                elif '.no' in domain:
                    result['country'] = 'Norway'
                elif '.dk' in domain:
                    result['country'] = 'Denmark'
                elif '.fi' in domain:
                    result['country'] = 'Finland'
                
                # Look for European cities
                for word in words:
                    if word in self.european_cities:
                        result['city'] = self.european_cities[word]
            
            return result
            
        except Exception as e:
            return {
                'country': None,
                'state': None,
                'city': None,
                'method': 'url_analysis',
                'error': str(e)
            }
    
    def extract_from_content(self, url: str) -> Dict[str, Optional[str]]:
        """Extract location information from website content."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8', errors='ignore').lower()
                    
                    result = {
                        'country': None,
                        'state': None,
                        'city': None,
                        'method': 'content_analysis'
                    }
                    
                    # Look for location keywords in content
                    # German locations
                    if any(word in content for word in ['deutschland', 'germany', 'berlin', 'münchen', 'hamburg']):
                        result['country'] = 'Germany'
                        
                        # Look for German cities in content
                        for key, city in self.german_cities.items():
                            if key in content or city.lower() in content:
                                result['city'] = city
                                break
                        
                        # Look for German states in content
                        for key, state in self.german_states.items():
                            if key in content or state.lower() in content:
                                result['state'] = state
                                break
                    
                    # US locations
                    elif any(word in content for word in ['united states', 'usa', 'america', 'california', 'new york', 'texas']):
                        result['country'] = 'United States'
                        
                        # Look for US cities in content
                        for key, city in self.us_cities.items():
                            if key in content or city.lower() in content:
                                result['city'] = city
                                break
                        
                        # Look for US states in content
                        for key, state in self.us_states.items():
                            if key in content or state.lower() in content:
                                result['state'] = state
                                break
                    
                    # European locations
                    elif any(word in content for word in ['united kingdom', 'england', 'london', 'france', 'paris']):
                        if any(word in content for word in ['united kingdom', 'england', 'london']):
                            result['country'] = 'United Kingdom'
                        elif any(word in content for word in ['france', 'paris']):
                            result['country'] = 'France'
                        
                        # Look for European cities in content
                        for key, city in self.european_cities.items():
                            if key in content or city.lower() in content:
                                result['city'] = city
                                break
                    
                    return result
                    
        except Exception as e:
            return {
                'country': None,
                'state': None,
                'city': None,
                'method': 'content_analysis',
                'error': str(e)
            }
        
        return {
            'country': None,
            'state': None,
            'city': None,
            'method': 'content_analysis',
            'error': 'Could not fetch content'
        }
    
    def extract_location_info(self, url: str) -> Dict[str, Optional[str]]:
        """Main method to extract location information from URL."""
        # Try URL analysis first (faster)
        url_result = self.extract_from_url_path(url)
        
        # If we found some location info from URL, return it
        if url_result.get('country') or url_result.get('state') or url_result.get('city'):
            return url_result
        
        # If URL analysis didn't yield results, try content analysis
        content_result = self.extract_from_content(url)
        
        # Combine results, preferring content analysis if it found more info
        final_result = url_result.copy()
        if content_result.get('country'):
            final_result['country'] = content_result['country']
        if content_result.get('state'):
            final_result['state'] = content_result['state']
        if content_result.get('city'):
            final_result['city'] = content_result['city']
        
        final_result['method'] = 'combined_analysis'
        
        return final_result
    
    def get_location_summary(self, location_info: Dict[str, Optional[str]]) -> str:
        """Generate a human-readable location summary."""
        parts = []
        if location_info.get('city'):
            parts.append(location_info['city'])
        if location_info.get('state'):
            parts.append(location_info['state'])
        if location_info.get('country'):
            parts.append(location_info['country'])
        
        if parts:
            return ', '.join(parts)
        else:
            return 'Location not determined'


def main():
    """Test the location extractor with some sample URLs."""
    extractor = LocationExtractor()
    
    test_urls = [
        'https://www.careanimations.de/',
        'https://bellehealth.co/de',
        'https://www.acalta.de',
        'https://www.climedo.de/',
        'https://visioncheckout.com',
        'https://www.actimi.com',
        'https://www.kranushealth.com/de/therapien/haeufiger-harndrang'
    ]
    
    print("🌍 Testing Location Extractor")
    print("=" * 50)
    
    for url in test_urls:
        print(f"\nURL: {url}")
        location_info = extractor.extract_location_info(url)
        summary = extractor.get_location_summary(location_info)
        print(f"Location: {summary}")
        print(f"Details: {location_info}")
        print("-" * 30)


if __name__ == "__main__":
    main()