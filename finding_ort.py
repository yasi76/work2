#!/usr/bin/env python3
"""
Script to find and map German cities (Ort) to startup URLs.
Uses hardcoded mappings first, then scrapes websites for location information.
"""

import json
import csv
import re
import time
from urllib.parse import urlparse, urljoin
try:
    import requests
except ImportError:
    print("Error: requests module not found. Please install python3-requests")
    exit(1)
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 module not found. Please install python3-bs4")
    exit(1)
from typing import Dict, List, Optional, Tuple


# Hardcoded URLs and their corresponding cities
urls = [
    "https://www.acalta.de",
    "https://www.actimi.com",
    "https://www.emmora.de",
    "https://www.alfa-ai.com",
    "https://www.apheris.com",
    "https://www.aporize.com",
    "https://www.arztlena.com",
    "https://shop.getnutrio.com",
    "https://www.auta.health",
    "https://visioncheckout.com",
    "https://www.avayl.tech",
    "https://www.avimedical.com",
    "https://de.becureglobal.com",
    "https://bellehealth.co",
    "https://www.biotx.ai",
    "https://www.brainjo.de",
    "https://brea.app",
    "https://breathment.com",
    "https://de.caona.eu",
    "https://www.careanimations.de",
    "https://www.climedo.de",
    "https://www.cliniserve.de",
    "https://cogthera.de",
    "https://www.comuny.de",
    "https://curecurve.de",
    "https://www.cynteract.com",
    "https://www.healthmeapp.de",
    "https://deepeye.ai",
    "https://www.deepmentation.ai",
    "https://denton-systems.de",
    "https://www.derma2go.com",
    "https://www.dianovi.com",
    "http://dopavision.com",
    "https://www.dpv-analytics.com",
    "http://www.ecovery.de",
    "https://elixionmedical.com",
    "https://www.empident.de",
    "https://eye2you.ai",
    "https://www.fitwhit.de",
    "https://www.floy.com",
    "https://fyzo.de",
    "https://www.gesund.de",
    "https://www.glaice.de",
    "https://gleea.de",
    "https://www.guidecare.de",
    "https://www.apodienste.com",
    "https://www.help-app.de",
    "https://www.heynanny.com",
    "https://incontalert.de",
    "https://home.informme.info",
    "https://www.kranushealth.com",
    "MindDoc",
]

orts = [
    "Erlangen", "Stuttgart", "Stuttgart", "Berlin", "München", "Berlin", "Hamburg", "Hofheim am Taunus",
    "Berlin", "Darmstadt", "München", "Karlsruhe", "Berlin", "München", "Mannheim", "Seefeld",
    "Potsdam", "Regensburg", "Berlin", "Breisach am Rhein", "Viersen", "Düsseldorf", "Freiburg im Breisgau",
    "München", "München", "München", "Weinheim", "Mannheim", "Aachen", "Heidelberg", "München", "Leipzig",
    "Potsdam", "München", "Darmstadt", "Berlin", "Hamburg", "Leipzig", "München", "München", "Tübingen",
    "Gießen", "München", "Werneck", "Werneck", "München", "München", "Klosterlechfeld", "Frankfurt am Main",
    "München", "Hamburg", "München"
]

# Create the hardcoded mapping
url_to_ort = dict(zip(urls, orts))


def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slashes and ensuring consistent format."""
    if not url:
        return url
    
    # Handle special case for MindDoc
    if url == "MindDoc":
        return url
    
    # Parse URL
    parsed = urlparse(url)
    
    # Reconstruct URL without trailing slash
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
    
    return normalized


def load_german_cities() -> List[str]:
    """Load list of German cities from file."""
    try:
        with open('german_cities.txt', 'r', encoding='utf-8') as f:
            cities = [line.strip() for line in f if line.strip()]
        return cities
    except FileNotFoundError:
        print("Warning: german_cities.txt not found. Using basic city list.")
        # Fallback to a basic list of major German cities
        return [
            "Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main", "Stuttgart",
            "Düsseldorf", "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden",
            "Hannover", "Nürnberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld",
            "Bonn", "Münster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden",
            "Gelsenkirchen", "Mönchengladbach", "Braunschweig", "Chemnitz", "Kiel",
            "Aachen", "Halle", "Magdeburg", "Freiburg im Breisgau", "Krefeld",
            "Lübeck", "Oberhausen", "Erfurt", "Mainz", "Rostock", "Kassel",
            "Hagen", "Hamm", "Saarbrücken", "Mülheim an der Ruhr", "Potsdam",
            "Ludwigshafen am Rhein", "Oldenburg", "Leverkusen", "Osnabrück",
            "Solingen", "Heidelberg", "Herne", "Neuss", "Darmstadt", "Paderborn",
            "Regensburg", "Ingolstadt", "Würzburg", "Fürth", "Wolfsburg", "Offenbach am Main",
            "Ulm", "Heilbronn", "Pforzheim", "Göttingen", "Bottrop", "Trier",
            "Recklinghausen", "Reutlingen", "Bremerhaven", "Koblenz", "Bergisch Gladbach",
            "Jena", "Remscheid", "Erlangen", "Moers", "Siegen", "Hildesheim",
            "Salzgitter", "Cottbus", "Gera", "Schwerin", "Rüsselsheim am Main",
            "Hofheim am Taunus", "Viersen", "Breisach am Rhein", "Seefeld",
            "Weinheim", "Tübingen", "Gießen", "Werneck", "Klosterlechfeld"
        ]


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch webpage content with proper error handling."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_city_from_html(html: str, cities: List[str]) -> Optional[str]:
    """Extract German city name from HTML content using various patterns."""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    
    # Create regex pattern for German postal codes followed by city names
    plz_pattern = r'\b(\d{5})\s+([A-ZÄÖÜa-zäöüß\s\-]+)'
    
    # Look for cities in various contexts
    found_cities = set()
    
    # 1. Check for postal code patterns
    plz_matches = re.findall(plz_pattern, text)
    for plz, potential_city in plz_matches:
        potential_city = potential_city.strip()
        # Check if it matches any known city
        for city in cities:
            if city.lower() in potential_city.lower():
                found_cities.add(city)
                break
    
    # 2. Look for cities in address-related tags
    address_tags = soup.find_all(['address', 'div', 'p', 'span'], 
                                 class_=re.compile(r'address|location|contact|impressum|h-card', re.I))
    for tag in address_tags:
        tag_text = tag.get_text()
        for city in cities:
            # Case-insensitive word boundary search
            if re.search(r'\b' + re.escape(city) + r'\b', tag_text, re.I):
                found_cities.add(city)
    
    # 3. Look for cities in the entire text with word boundaries
    for city in cities:
        # Use word boundaries to avoid partial matches
        if re.search(r'\b' + re.escape(city) + r'\b', text, re.I):
            found_cities.add(city)
    
    # 4. Special patterns for German addresses
    # Look for patterns like "in München" or "aus Berlin"
    location_patterns = [
        r'(?:in|aus|zu|bei)\s+(' + '|'.join(re.escape(city) for city in cities) + r')\b',
        r'\b(' + '|'.join(re.escape(city) for city in cities) + r')\s*(?:,\s*(?:Deutschland|Germany))',
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.I)
        for match in matches:
            # Find the exact city name from our list
            for city in cities:
                if city.lower() == match.lower():
                    found_cities.add(city)
                    break
    
    # Return the most likely city (could be improved with scoring)
    if found_cities:
        # Prefer longer city names (more specific)
        return max(found_cities, key=len)
    
    return None


def find_city_for_url(url: str, cities: List[str]) -> Optional[str]:
    """Try to find city for a given URL by checking various pages."""
    # Normalize the URL
    normalized_url = normalize_url(url)
    
    # Special handling for MindDoc
    if normalized_url == "MindDoc":
        return None
    
    # URLs to try
    paths_to_try = ['', '/impressum', '/kontakt', '/contact', '/about-us', '/ueber-uns']
    
    for path in paths_to_try:
        try:
            if path:
                full_url = urljoin(normalized_url + '/', path.lstrip('/'))
            else:
                full_url = normalized_url
            
            print(f"Trying: {full_url}")
            html = fetch_page(full_url)
            
            if html:
                city = extract_city_from_html(html, cities)
                if city:
                    print(f"Found city '{city}' at {full_url}")
                    return city
            
            # Be respectful with rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {full_url}: {e}")
            continue
    
    return None


def main():
    """Main function to process URLs and find their cities."""
    # Load German cities
    print("Loading German cities...")
    german_cities = load_german_cities()
    print(f"Loaded {len(german_cities)} cities")
    
    # Load startup data from JSON
    try:
        with open('enhanced_products.json', 'r', encoding='utf-8') as f:
            startups = json.load(f)
        print(f"Loaded {len(startups)} startups from enhanced_products.json")
    except FileNotFoundError:
        print("enhanced_products.json not found. Creating sample file...")
        # Create a sample file for demonstration
        sample_startups = [
            {"company_name": "Acalta", "url": "https://www.acalta.de"},
            {"company_name": "Example Startup", "url": "https://example.com"},
            {"company_name": "MindDoc", "url": "MindDoc"}
        ]
        with open('enhanced_products.json', 'w', encoding='utf-8') as f:
            json.dump(sample_startups, f, indent=2, ensure_ascii=False)
        startups = sample_startups
    
    # Process each startup
    results = []
    url_to_ort_final = {}
    
    for startup in startups:
        company_name = startup.get('company_name', '')
        url = startup.get('url', '')
        
        if not url:
            print(f"Skipping {company_name}: No URL provided")
            continue
        
        # Normalize URL for lookup
        normalized_url = normalize_url(url)
        
        # Check if we have a hardcoded mapping
        ort = None
        for hardcoded_url, hardcoded_ort in url_to_ort.items():
            if normalize_url(hardcoded_url) == normalized_url:
                ort = hardcoded_ort
                print(f"Found hardcoded mapping for {url}: {ort}")
                break
        
        # If not found in hardcoded mappings, try to scrape
        if not ort:
            print(f"No hardcoded mapping for {url}, attempting to scrape...")
            ort = find_city_for_url(url, german_cities)
            
            if not ort:
                print(f"Could not find city for {url}")
                ort = "Unknown"
        
        # Store results
        results.append({
            'company_name': company_name,
            'url': url,
            'ort': ort
        })
        url_to_ort_final[normalized_url] = ort
    
    # Save results to JSON
    with open('finding_ort.json', 'w', encoding='utf-8') as f:
        json.dump(url_to_ort_final, f, indent=2, ensure_ascii=False)
    print(f"Saved URL to Ort mapping to finding_ort.json")
    
    # Save results to CSV
    with open('finding_ort.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'url', 'ort'])
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved results to finding_ort.csv")
    
    # Print summary
    print(f"\nProcessed {len(results)} companies")
    unknown_count = sum(1 for r in results if r['ort'] == 'Unknown')
    print(f"Successfully found cities for {len(results) - unknown_count} companies")
    print(f"Could not find cities for {unknown_count} companies")


if __name__ == "__main__":
    main()