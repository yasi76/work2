"""
Utility functions for URL validation and healthcare content detection.
This module provides common functions used across the application.
"""

import re
import tldextract
from urllib.parse import urlparse, urljoin
from typing import List, Set, Optional
import config


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
    for keyword in config.HEALTHCARE_KEYWORDS:
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
        for excluded_domain in config.EXCLUDED_DOMAINS:
            if excluded_domain in domain:
                return True
        
        # Check excluded path patterns
        for pattern in config.EXCLUDED_PATTERNS:
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