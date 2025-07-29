#!/usr/bin/env python3
"""
Script to find the location (Ort) for startup URLs.
First checks hardcoded mapping, then scrapes web pages if needed.
"""

import json
import csv
import re
import time
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# Create dictionary mapping URLs to cities
url_to_ort = dict(zip(urls, orts))


def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slashes and converting to lowercase."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    url = url.rstrip('/')
    return url.lower()


def load_german_cities() -> List[str]:
    """Load list of German cities from file or use a default set."""
    try:
        with open('german_cities.txt', 'r', encoding='utf-8') as f:
            cities = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(cities)} cities from german_cities.txt")
            return cities
    except FileNotFoundError:
        logger.warning("german_cities.txt not found, using default city list")
        # Default list of major German cities
        return [
            "Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main", "Stuttgart",
            "Düsseldorf", "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden",
            "Hannover", "Nürnberg", "Duisburg", "Bochum", "Wuppertal", "Bielefeld",
            "Bonn", "Münster", "Karlsruhe", "Mannheim", "Augsburg", "Wiesbaden",
            "Aachen", "Mönchengladbach", "Gelsenkirchen", "Braunschweig", "Chemnitz",
            "Kiel", "Krefeld", "Halle", "Magdeburg", "Freiburg im Breisgau",
            "Oberhausen", "Lübeck", "Erfurt", "Mainz", "Rostock", "Kassel",
            "Hagen", "Hamm", "Saarbrücken", "Mülheim an der Ruhr", "Potsdam",
            "Ludwigshafen am Rhein", "Oldenburg", "Leverkusen", "Osnabrück",
            "Solingen", "Heidelberg", "Herne", "Neuss", "Darmstadt", "Paderborn",
            "Regensburg", "Ingolstadt", "Würzburg", "Fürth", "Wolfsburg", "Offenbach am Main",
            "Ulm", "Heilbronn", "Pforzheim", "Göttingen", "Bottrop", "Trier",
            "Recklinghausen", "Reutlingen", "Bremerhaven", "Koblenz", "Bergisch Gladbach",
            "Jena", "Remscheid", "Erlangen", "Moers", "Siegen", "Hildesheim",
            "Salzgitter", "Cottbus", "Gütersloh", "Kaiserslautern", "Witten",
            "Schwerin", "Gera", "Iserlohn", "Esslingen am Neckar", "Zwickau",
            "Düren", "Ratingen", "Lünen", "Hanau", "Marl", "Flensburg",
            "Dessau-Roßlau", "Konstanz", "Ludwigsburg", "Velbert", "Minden",
            "Tübingen", "Villingen-Schwenningen", "Worms", "Neumünster", "Marburg",
            "Rheine", "Delmenhorst", "Bamberg", "Bayreuth", "Gießen", "Lüneburg",
            "Celle", "Aschaffenburg", "Dinslaken", "Lippstadt", "Landshut",
            "Herford", "Kempten", "Fulda", "Ravensburg", "Rüsselsheim am Main",
            "Bad Salzuflen", "Garbsen", "Weimar", "Schwäbisch Gmünd", "Wetzlar",
            "Passau", "Speyer", "Görlitz", "Frechen", "Gronau", "Sankt Augustin",
            "Rheda-Wiedenbrück", "Friedrichshafen", "Menden", "Göppingen",
            "Hofheim am Taunus", "Klosterlechfeld", "Breisach am Rhein", "Viersen",
            "Weinheim", "Seefeld", "Werneck"
        ]


def fetch_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch HTML content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def extract_city_from_html(html: str, cities: List[str]) -> Optional[str]:
    """Extract city name from HTML content using various patterns."""
    if not html:
        return None
    
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    
    # Remove script and style content
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Look for address tags
    address_elements = soup.find_all(['address', 'div'], class_=re.compile(r'address|contact|impressum|h-card', re.I))
    for elem in address_elements:
        elem_text = elem.get_text(separator=' ', strip=True)
        city = find_city_in_text(elem_text, cities)
        if city:
            return city
    
    # Look for PLZ + Stadt pattern (German postal code + city)
    plz_pattern = r'\b(\d{5})\s+([A-Za-zäöüÄÖÜß\s\-]+)'
    matches = re.findall(plz_pattern, text)
    for plz, potential_city in matches:
        potential_city = potential_city.strip()
        # Check if it matches any known city
        for city in cities:
            if city.lower() in potential_city.lower():
                return city
    
    # General search for city names in the entire text
    return find_city_in_text(text, cities)


def find_city_in_text(text: str, cities: List[str]) -> Optional[str]:
    """Find a city name in text by matching against known cities."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Sort cities by length (descending) to match longer names first
    sorted_cities = sorted(cities, key=len, reverse=True)
    
    for city in sorted_cities:
        # Create regex pattern for the city name
        # Allow for word boundaries and handle special characters
        city_pattern = r'\b' + re.escape(city.lower()) + r'\b'
        if re.search(city_pattern, text_lower):
            return city
    
    return None


def scrape_location(url: str, cities: List[str]) -> Optional[str]:
    """Scrape location from URL by trying various pages."""
    base_url = normalize_url(url)
    
    # URLs to try
    paths_to_try = [
        '',  # Main page
        '/impressum',
        '/kontakt',
        '/contact',
        '/about-us',
        '/ueber-uns',
        '/about',
        '/uber-uns',
        '/imprint',
        '/legal',
    ]
    
    for path in paths_to_try:
        full_url = urljoin(base_url, path) if path else base_url
        logger.info(f"Trying to fetch: {full_url}")
        
        html = fetch_page(full_url)
        if html:
            city = extract_city_from_html(html, cities)
            if city:
                logger.info(f"Found city '{city}' for {url}")
                return city
        
        # Be polite to servers
        time.sleep(0.5)
    
    return None


def process_startups(input_file: str, cities: List[str]) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    """Process startup data from JSON file and find locations."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            startups = json.load(f)
    except FileNotFoundError:
        logger.error(f"File {input_file} not found")
        return {}, []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {input_file}")
        return {}, []
    
    url_to_ort_mapping = {}
    results = []
    
    # Process each startup
    for startup in startups:
        company_name = startup.get('company_name', '')
        url = startup.get('url', '')
        
        if not url:
            logger.warning(f"No URL for company: {company_name}")
            continue
        
        normalized_url = normalize_url(url)
        
        # Check if URL is in hardcoded mapping
        ort = None
        for hardcoded_url, hardcoded_ort in url_to_ort.items():
            if normalize_url(hardcoded_url) == normalized_url:
                ort = hardcoded_ort
                logger.info(f"Found {company_name} in hardcoded data: {ort}")
                break
        
        # If not found in hardcoded data, try scraping
        if not ort:
            logger.info(f"Scraping location for {company_name} ({url})")
            ort = scrape_location(url, cities)
            
            if not ort:
                logger.warning(f"Could not find location for {company_name} ({url})")
                ort = "Unknown"
        
        # Store results
        url_to_ort_mapping[url] = ort
        results.append({
            'company_name': company_name,
            'url': url,
            'ort': ort
        })
    
    return url_to_ort_mapping, results


def save_results(url_to_ort_mapping: Dict[str, str], results: List[Dict[str, str]]):
    """Save results to JSON and CSV files."""
    # Save JSON mapping
    with open('finding_ort.json', 'w', encoding='utf-8') as f:
        json.dump(url_to_ort_mapping, f, ensure_ascii=False, indent=2)
    logger.info("Saved URL to Ort mapping to finding_ort.json")
    
    # Save CSV
    with open('finding_ort.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'url', 'ort'])
        writer.writeheader()
        writer.writerows(results)
    logger.info("Saved results to finding_ort.csv")


def main():
    """Main function to orchestrate the location finding process."""
    logger.info("Starting location finding process...")
    
    # Load German cities
    cities = load_german_cities()
    
    # Process startups
    url_to_ort_mapping, results = process_startups('enhanced_products.json', cities)
    
    # Save results
    if url_to_ort_mapping:
        save_results(url_to_ort_mapping, results)
        logger.info(f"Processed {len(results)} companies")
    else:
        logger.error("No data processed")


if __name__ == "__main__":
    main()