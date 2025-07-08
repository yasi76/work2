"""
Utility functions for URL validation and healthcare content detection.
This module provides common functions used across the application.
"""

import re
import tldextract
from urllib.parse import urlparse, urljoin
from typing import List, Set, Optional
import ultimate_config as config

# Healthcare keywords for content detection
HEALTHCARE_KEYWORDS = [
    'health', 'medical', 'healthcare', 'medicine', 'clinic', 'hospital',
    'doctor', 'physician', 'patient', 'therapy', 'treatment', 'diagnosis',
    'pharmaceutical', 'biotech', 'medtech', 'digital health', 'telemedicine'
]

# Domains to exclude
EXCLUDED_DOMAINS = [
    'google.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com',
    'youtube.com', 'wikipedia.org', 'crunchbase.com', 'angel.co'
]

# URL patterns to exclude
EXCLUDED_PATTERNS = [
    '/login', '/signin', '/signup', '/register', '/auth', '/oauth',
    '/privacy', '/terms', '/contact', '/about/team', '/careers'
]


def clean_url(url: str) -> str:
    """
    Clean and normalize a URL by removing fragments and unnecessary parameters.
    
    Args:
        url (str): Raw URL to clean
        
    Returns:
        str: Cleaned URL
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove fragment (#) and common tracking parameters
    parsed = urlparse(url)
    # Remove fragment and common tracking parameters
    query_parts = []
    if parsed.query:
        for param in parsed.query.split('&'):
            if not any(tracking in param.lower() for tracking in ['utm_', 'fbclid', 'gclid']):
                query_parts.append(param)
    
    clean_query = '&'.join(query_parts)
    cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean_query:
        cleaned += f"?{clean_query}"
    
    return cleaned.rstrip('/')


def is_healthcare_related(text: str, url: str = "") -> bool:
    """
    Check if the given text or URL indicates healthcare-related content.
    
    Args:
        text (str): Text content to analyze (e.g., page title, description)
        url (str): URL to analyze for healthcare keywords
        
    Returns:
        bool: True if content appears healthcare-related
    """
    # Combine text and URL for analysis
    combined_text = f"{text} {url}".lower()
    
    # Check for healthcare keywords
    healthcare_score = 0
    for keyword in HEALTHCARE_KEYWORDS:
        if keyword.lower() in combined_text:
            healthcare_score += 1
    
    # Consider it healthcare-related if we find multiple keywords
    return healthcare_score >= 2


def should_exclude_url(url: str) -> bool:
    """
    Check if a URL should be excluded based on domain or path patterns.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL should be excluded
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Check excluded domains
        for excluded_domain in EXCLUDED_DOMAINS:
            if excluded_domain in domain:
                return True
        
        # Check excluded path patterns
        for pattern in EXCLUDED_PATTERNS:
            if pattern in path:
                return True
                
        return False
        
    except Exception:
        return True  # Exclude malformed URLs


def extract_domain(url: str) -> str:
    """
    Extract the main domain from a URL.
    
    Args:
        url (str): URL to extract domain from
        
    Returns:
        str: Extracted domain
    """
    try:
        extracted = tldextract.extract(url)
        return f"{extracted.domain}.{extracted.suffix}"
    except Exception:
        return ""


def deduplicate_urls(urls: List[str]) -> List[str]:
    """
    Remove duplicate URLs, keeping only unique domains and paths.
    
    Args:
        urls (List[str]): List of URLs to deduplicate
        
    Returns:
        List[str]: Deduplicated list of URLs
    """
    seen_urls = set()
    unique_urls = []
    
    for url in urls:
        cleaned = clean_url(url)
        if cleaned not in seen_urls and not should_exclude_url(cleaned):
            seen_urls.add(cleaned)
            unique_urls.append(cleaned)
    
    return unique_urls


def extract_urls_from_text(text: str, base_url: str = "") -> Set[str]:
    """
    Extract URLs from text using regex patterns.
    
    Args:
        text (str): Text to search for URLs
        base_url (str): Base URL for resolving relative URLs
        
    Returns:
        Set[str]: Set of extracted URLs
    """
    # Regex pattern for URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
    
    urls = set()
    
    # Find all URLs in text
    found_urls = re.findall(url_pattern, text)
    
    for url in found_urls:
        try:
            # Clean up the URL
            cleaned = clean_url(url)
            if cleaned:
                urls.add(cleaned)
        except Exception:
            continue
    
    return urls


def is_valid_url_format(url: str) -> bool:
    """
    Check if a URL has a valid format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL format is valid
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
    except Exception:
        return False


def get_base_url(url: str) -> str:
    """
    Get the base URL (scheme + netloc) from a full URL.
    
    Args:
        url (str): Full URL
        
    Returns:
        str: Base URL
    """
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return ""


def normalize_text(text: str) -> str:
    """
    Normalize text for consistent analysis.
    
    Args:
        text (str): Text to normalize
        
    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and convert to lowercase
    normalized = ' '.join(text.split()).lower()
    
    # Remove special characters but keep basic punctuation
    normalized = re.sub(r'[^\w\s.,;:!?-]', ' ', normalized)
    
    return normalized


def get_ultimate_country_estimate(url: str, title: str = "", description: str = "") -> str:
    """
    Ultimate country estimation using advanced detection methods
    """
    url_lower = url.lower()
    domain = extract_domain(url).lower()
    combined_text = f"{url} {title} {description}".lower()
    
    # Enhanced country detection with multiple indicators
    country_indicators = {
        'Germany': [
            # Domain patterns
            '.de', '.com.de',
            # Language indicators
            'deutschland', 'german', 'deutsch', 'berlin', 'munich', 'münchen',
            'hamburg', 'frankfurt', 'cologne', 'köln', 'stuttgart', 'düsseldorf',
            'gmbh', 'ug', 'ag',
            # German healthcare terms
            'gesundheit', 'medizin', 'arzt', 'krankenhaus', 'klinik'
        ],
        'France': [
            '.fr', '.com.fr', 'france', 'french', 'français', 'paris', 'lyon',
            'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg', 'sa', 'sarl',
            'santé', 'médecine', 'médecin', 'hôpital', 'clinique'
        ],
        'Netherlands': [
            '.nl', '.com.nl', 'netherlands', 'dutch', 'nederland', 'amsterdam',
            'rotterdam', 'hague', 'utrecht', 'eindhoven', 'bv', 'nv',
            'gezondheid', 'geneeskunde', 'arts', 'ziekenhuis'
        ],
        'United Kingdom': [
            '.uk', '.co.uk', '.org.uk', 'britain', 'british', 'england', 'scotland',
            'wales', 'london', 'manchester', 'birmingham', 'glasgow', 'liverpool',
            'leeds', 'sheffield', 'edinburgh', 'bristol', 'cardiff', 'ltd', 'plc'
        ],
        'Switzerland': [
            '.ch', '.com.ch', 'switzerland', 'swiss', 'schweiz', 'suisse', 'svizzera',
            'zurich', 'zürich', 'geneva', 'genève', 'basel', 'lausanne', 'bern'
        ],
        'Spain': [
            '.es', '.com.es', 'spain', 'spanish', 'españa', 'madrid', 'barcelona',
            'valencia', 'seville', 'sevilla', 'zaragoza', 'málaga', 'sl', 'sau',
            'salud', 'medicina', 'médico', 'hospital', 'clínica'
        ],
        'Italy': [
            '.it', '.com.it', 'italy', 'italian', 'italia', 'rome', 'roma', 'milan',
            'milano', 'naples', 'napoli', 'turin', 'torino', 'palermo', 'genoa',
            'bologna', 'florence', 'firenze', 'spa', 'srl',
            'salute', 'medicina', 'medico', 'ospedale', 'clinica'
        ],
        'Sweden': [
            '.se', '.com.se', 'sweden', 'swedish', 'sverige', 'stockholm',
            'gothenburg', 'göteborg', 'malmö', 'uppsala', 'ab',
            'hälsa', 'medicin', 'sjukhus', 'läkare'
        ],
        'Denmark': [
            '.dk', '.com.dk', 'denmark', 'danish', 'danmark', 'copenhagen',
            'københavn', 'aarhus', 'odense', 'aalborg', 'a/s', 'aps',
            'sundhed', 'medicin', 'sygehus', 'læge'
        ],
        'Norway': [
            '.no', '.com.no', 'norway', 'norwegian', 'norge', 'oslo', 'bergen',
            'trondheim', 'stavanger', 'as', 'asa',
            'helse', 'medisin', 'sykehus', 'lege'
        ],
        'Finland': [
            '.fi', '.com.fi', 'finland', 'finnish', 'suomi', 'helsinki',
            'tampere', 'turku', 'oulu', 'oy', 'oyj',
            'terveys', 'lääketiede', 'sairaala', 'lääkäri'
        ],
        'Belgium': [
            '.be', '.com.be', 'belgium', 'belgian', 'belgië', 'belgique',
            'brussels', 'brussel', 'bruxelles', 'antwerp', 'antwerpen',
            'ghent', 'gent', 'charleroi', 'liège', 'sprl', 'bvba'
        ],
        'Austria': [
            '.at', '.com.at', 'austria', 'austrian', 'österreich', 'vienna',
            'wien', 'salzburg', 'innsbruck', 'linz', 'graz'
        ],
        'Ireland': [
            '.ie', '.com.ie', 'ireland', 'irish', 'dublin', 'cork', 'galway',
            'waterford', 'limerick'
        ],
        'Portugal': [
            '.pt', '.com.pt', 'portugal', 'portuguese', 'lisbon', 'lisboa',
            'porto', 'braga', 'coimbra'
        ]
    }
    
    # Score each country based on indicators found
    country_scores = {}
    for country, indicators in country_indicators.items():
        score = 0
        for indicator in indicators:
            if indicator in combined_text:
                # Domain extensions get higher scores
                if indicator.startswith('.'):
                    score += 5
                # City names get medium scores
                elif any(city in indicator for city in ['berlin', 'paris', 'london', 'amsterdam']):
                    score += 3
                # Other indicators get base scores
                else:
                    score += 1
        
        if score > 0:
            country_scores[country] = score
    
    # Return country with highest score
    if country_scores:
        best_country = max(country_scores, key=country_scores.get)
        return best_country
    
    # Fallback detection
    if '.eu' in domain:
        return 'European Union'
    elif any(tld in domain for tld in ['.com', '.org', '.net']):
        return 'International'
    else:
        return 'Other'


def classify_healthcare_sector(url: str, title: str = "", description: str = "") -> str:
    """
    Classify healthcare companies by sector/specialty
    """
    combined_text = f"{url} {title} {description}".lower()
    
    sector_keywords = {
        'Digital Therapeutics': ['digital therapeutics', 'dtx', 'prescription app', 'therapeutic app'],
        'Telemedicine': ['telemedicine', 'telehealth', 'remote consultation', 'virtual care', 'online doctor'],
        'Medical Devices': ['medical device', 'medical equipment', 'implant', 'prosthetic', 'monitor'],
        'Health Analytics': ['health analytics', 'medical data', 'health insights', 'clinical analytics'],
        'Mental Health': ['mental health', 'psychology', 'psychiatry', 'therapy', 'behavioral health'],
        'AI/ML Health': ['medical ai', 'healthcare ai', 'machine learning', 'artificial intelligence'],
        'Biotech': ['biotech', 'biotechnology', 'pharmaceutical', 'drug development', 'clinical trial'],
        'Medical Imaging': ['medical imaging', 'radiology', 'mri', 'ct scan', 'ultrasound', 'x-ray'],
        'Chronic Care': ['chronic disease', 'diabetes', 'hypertension', 'copd', 'heart disease'],
        'Women\'s Health': ['womens health', 'fertility', 'pregnancy', 'reproductive health'],
        'Elderly Care': ['elderly care', 'senior health', 'aging', 'geriatric', 'dementia'],
        'Pediatric': ['pediatric', 'children health', 'infant care', 'neonatal'],
        'Surgery Tech': ['surgical', 'surgery', 'robotic surgery', 'minimally invasive'],
        'Digital Pharmacy': ['digital pharmacy', 'e-pharmacy', 'medication management'],
        'Fitness/Wellness': ['fitness', 'wellness', 'nutrition', 'exercise', 'lifestyle']
    }
    
    for sector, keywords in sector_keywords.items():
        for keyword in keywords:
            if keyword in combined_text:
                return sector
    
    return 'General Healthcare'