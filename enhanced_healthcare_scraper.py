#!/usr/bin/env python3
"""
Enhanced Healthcare Company Directory Scraper
===============================================

A comprehensive web scraper for extracting German healthcare companies from multiple 
high-quality directory sources. This scraper intelligently avoids duplicates and 
provides detailed company information.

Features:
- Multiple high-quality data sources (BVMed, SPECTARIS, Digital Health Hub, etc.)
- Intelligent deduplication to avoid existing companies
- Selenium support for JavaScript-heavy websites
- Comprehensive data extraction (name, website, description, location, etc.)
- Flexible configuration options
- Robust error handling and logging

Usage:
    python enhanced_healthcare_scraper.py [options]

Author: Healthcare Data Extraction System
Version: 2.0
"""

# Standard library imports (always available)
import time
import re
import json
import csv
import argparse
import sys
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict
from pathlib import Path

# Optional external library imports (graceful degradation)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthcareCompany:
    """
    Data class representing a healthcare company with all relevant information.
    
    This class stores comprehensive information about healthcare companies
    extracted from various directory sources.
    """
    name: str                    # Company name (required)
    website: str = ""           # Company website URL
    description: str = ""       # Company description/summary
    location: str = ""          # Company location (city, country)
    category: str = ""          # Business category (e.g., Medical Technology)
    source_directory: str = ""  # URL of the directory where company was found
    employees: str = ""         # Number of employees (if available)
    funding: str = ""           # Funding information (if available)
    city: str = ""              # Extracted city name
    founded: str = ""           # Founded date (if available)
    phone: str = ""             # Phone number (if available)
    email: str = ""             # Email address (if available)
    tags: List[str] = None      # Tags for categorization
    
    def __post_init__(self):
        """Initialize tags list if not provided."""
        if self.tags is None:
            self.tags = []

class EnhancedHealthcareScraper:
    """
    Enhanced scraper for German healthcare company directories.
    
    This class provides comprehensive scraping capabilities for multiple
    healthcare directory sources with intelligent deduplication and
    robust error handling.
    """
    
    def __init__(self, use_selenium: bool = True, use_beautifulsoup: bool = True):
        """
        Initialize the scraper with configuration options.
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript-heavy sites
            use_beautifulsoup: Whether to use BeautifulSoup for HTML parsing
        """
        # Check available dependencies
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.use_beautifulsoup = use_beautifulsoup and BEAUTIFULSOUP_AVAILABLE
        self.use_requests = REQUESTS_AVAILABLE
        
        # Initialize requests session if available
        if self.use_requests:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
        else:
            self.session = None
        
        # Configure Selenium if available and requested
        self.driver = None
        if self.use_selenium:
            self._setup_selenium()
        
        # Load existing companies to avoid duplicates
        self.known_companies = self._load_known_companies()
        self.extracted_companies = []
        
        # Log configuration
        logger.info(f"Scraper initialized:")
        logger.info(f"  - Requests: {'Enabled' if self.use_requests else 'Disabled'}")
        logger.info(f"  - Selenium: {'Enabled' if self.use_selenium else 'Disabled'}")
        logger.info(f"  - BeautifulSoup: {'Enabled' if self.use_beautifulsoup else 'Disabled'}")
        logger.info(f"  - Known companies: {len(self.known_companies)}")
        
        # Warn if no web libraries available
        if not self.use_requests and not self.use_selenium:
            logger.warning("No web scraping libraries available. Install 'requests' or 'selenium' for full functionality.")
            
    def _setup_selenium(self):
        """
        Setup Selenium WebDriver for JavaScript-heavy sites.
        
        Configures Chrome in headless mode with optimal settings for scraping.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')           # Run in background
            chrome_options.add_argument('--no-sandbox')         # Bypass OS security model
            chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
            chrome_options.add_argument('--disable-gpu')        # Disable GPU acceleration
            chrome_options.add_argument('--window-size=1920,1080')  # Set window size
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Avoid detection
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
            logger.warning("Continuing without Selenium support")
            self.use_selenium = False
    
    def _load_known_companies(self) -> Set[str]:
        """
        Load known companies to avoid duplicates.
        
        Returns:
            Set of known company domains to filter out during scraping
        """
        # Your existing healthcare companies (add more as needed)
        known_websites = {
            'acalta.de', 'actimi.com', 'emmora.de', 'alfa-ai.com', 'apheris.com',
            'aporize.com', 'arztlena.com', 'getnutrio.com', 'auta.health',
            'visioncheckout.com', 'avayl.tech', 'avimedical.com', 'becureglobal.com',
            'bellehealth.co', 'biotx.ai', 'brainjo.de', 'brea.app', 'breathment.com',
            'caona.eu', 'careanimations.de', 'sfs-healthcare.com', 'climedo.de',
            'cliniserve.de', 'cogthera.de', 'comuny.de', 'curecurve.de',
            'cynteract.com', 'healthmeapp.de', 'deepeye.ai', 'deepmentation.ai',
            'denton-systems.de', 'derma2go.com', 'dianovi.com', 'dopavision.com',
            'dpv-analytics.com', 'ecovery.de', 'elixionmedical.com', 'empident.de',
            'eye2you.ai', 'fitwhit.de', 'floy.com', 'fyzo.de', 'gesund.de',
            'glaice.de', 'gleea.de', 'guidecare.de', 'apodienste.com',
            'help-app.de', 'heynanny.com', 'incontalert.de', 'informme.info',
            'kranushealth.com'
        }
        return known_websites
    
    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """
        Fetch webpage content using requests library.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        if not self.use_requests or not self.session:
            return None
            
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.debug(f"Failed to fetch {url} with requests: {e}")
            return None
    
    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """
        Fetch webpage content using Selenium WebDriver.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        if not self.use_selenium or not self.driver:
            return None
            
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            return self.driver.page_source
        except Exception as e:
            logger.debug(f"Failed to fetch {url} with Selenium: {e}")
            return None
    
    def _parse_html(self, html: str):
        """
        Parse HTML content using BeautifulSoup if available.
        
        Args:
            html: HTML content to parse
            
        Returns:
            BeautifulSoup object or None if parsing failed
        """
        if not self.use_beautifulsoup or not html:
            return None
            
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.debug(f"Failed to parse HTML with BeautifulSoup: {e}")
            return None
    
    def extract_from_bvmed(self) -> List[HealthcareCompany]:
        """
        Extract companies from BVMed - German Medical Technology Association.
        
        BVMed is the official association for medical technology companies in Germany.
        This method scrapes their member directory to find healthcare companies.
        
        Returns:
            List of HealthcareCompany objects found on BVMed
        """
        companies = []
        
        try:
            logger.info("Scraping BVMed directory...")
            url = "https://www.bvmed.de/de/unternehmen/mitgliedsunternehmen"
            
            # Try Selenium first for JavaScript-heavy content
            html = self._fetch_with_selenium(url)
            if not html:
                html = self._fetch_with_requests(url)
                
            if html:
                soup = self._parse_html(html)
                if soup:
                    # Look for company listings using multiple selectors
                    company_selectors = [
                        'div.company-item', 'div.member-item', 'div.company-card', 
                        'tr.company-row', 'div.mitglied', 'div.unternehmen'
                    ]
                    
                    for selector in company_selectors:
                        elements = soup.select(selector)
                        if elements:
                            logger.info(f"Found {len(elements)} elements with selector: {selector}")
                            
                            for element in elements:
                                company = self._extract_company_from_element(element, url)
                                if company:
                                    company.category = "Medical Technology"
                                    company.tags = ["BVMed", "Medical Device", "German"]
                                    companies.append(company)
                            break
                    
                    # Fallback: look for any external links that might be companies
                    if not companies:
                        external_links = soup.find_all('a', href=True)
                        for link in external_links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            
                            if self._is_company_link(href, text):
                                company = HealthcareCompany(
                                    name=text,
                                    website=href,
                                    source_directory=url,
                                    location="Germany",
                                    category="Medical Technology",
                                    tags=["BVMed", "Medical Device", "German"]
                                )
                                companies.append(company)
            
            logger.info(f"Extracted {len(companies)} companies from BVMed")
            
        except Exception as e:
            logger.error(f"Error scraping BVMed: {str(e)}")
        
        return companies
    
    def extract_from_spectaris(self) -> List[HealthcareCompany]:
        """
        Extract companies from SPECTARIS - German Industry Association.
        
        SPECTARIS represents companies in optics, photonics, analytical and medical technologies.
        This method scrapes their member directory for healthcare-related companies.
        
        Returns:
            List of HealthcareCompany objects found on SPECTARIS
        """
        companies = []
        
        try:
            logger.info("Scraping SPECTARIS directory...")
            url = "https://www.spectaris.de/mitglieder/"
            
            # Fetch webpage content
            html = self._fetch_with_requests(url)
            if not html:
                html = self._fetch_with_selenium(url)
                
            if html:
                soup = self._parse_html(html)
                if soup:
                    # Look for member listings
                    member_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'member|company|mitglied', re.I))
                    
                    for element in member_elements:
                        company = self._extract_company_from_element(element, url)
                        if company:
                            company.category = "Optics/Medical Technology"
                            company.tags = ["SPECTARIS", "Medical Technology", "German"]
                            companies.append(company)
            
            logger.info(f"Extracted {len(companies)} companies from SPECTARIS")
            
        except Exception as e:
            logger.error(f"Error scraping SPECTARIS: {str(e)}")
        
        return companies
    
    def extract_from_digital_health_hub(self) -> List[HealthcareCompany]:
        """
        Extract companies from Digital Health Hub Berlin.
        
        Digital Health Hub is a startup ecosystem focusing on digital health innovations.
        This method scrapes their startup directory for healthcare companies.
        
        Returns:
            List of HealthcareCompany objects found on Digital Health Hub
        """
        companies = []
        
        try:
            logger.info("Scraping Digital Health Hub...")
            url = "https://digitalhealthhub.de/startups/"
            
            # This site likely requires JavaScript, so try Selenium first
            html = self._fetch_with_selenium(url)
            if not html:
                html = self._fetch_with_requests(url)
                
            if html:
                soup = self._parse_html(html)
                if soup:
                    # Look for startup cards
                    startup_selectors = [
                        'div.startup-card', 'div.company-card', 'div.member-card',
                        'div.startup', 'div.company'
                    ]
                    
                    for selector in startup_selectors:
                        elements = soup.select(selector)
                        if elements:
                            for element in elements:
                                company = self._extract_company_from_element(element, url)
                                if company:
                                    company.location = "Berlin"
                                    company.category = "Digital Health"
                                    company.tags = ["Digital Health Hub", "Startup", "Berlin"]
                                    companies.append(company)
                            break
            
            logger.info(f"Extracted {len(companies)} companies from Digital Health Hub")
            
        except Exception as e:
            logger.error(f"Error scraping Digital Health Hub: {str(e)}")
        
        return companies
    
    def extract_from_biom_cluster(self) -> List[HealthcareCompany]:
        """
        Extract companies from BioM - Bavaria Biotech Cluster.
        
        BioM is the leading biotech cluster in Bavaria, Germany.
        This method scrapes their company directory for biotech companies.
        
        Returns:
            List of HealthcareCompany objects found on BioM
        """
        companies = []
        
        try:
            logger.info("Scraping BioM cluster directory...")
            url = "https://www.bio-m.org/de/unternehmen/"
            
            html = self._fetch_with_requests(url)
            if not html:
                html = self._fetch_with_selenium(url)
                
            if html:
                soup = self._parse_html(html)
                if soup:
                    # Look for company listings
                    company_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'company|unternehmen|member', re.I))
                    
                    for element in company_elements:
                        company = self._extract_company_from_element(element, url)
                        if company:
                            company.location = "Bavaria"
                            company.category = "Biotechnology"
                            company.tags = ["BioM", "Biotech", "Bavaria"]
                            companies.append(company)
            
            logger.info(f"Extracted {len(companies)} companies from BioM")
            
        except Exception as e:
            logger.error(f"Error scraping BioM: {str(e)}")
        
        return companies
    
    def extract_from_ehealth_initiative(self) -> List[HealthcareCompany]:
        """
        Extract companies from eHealth Initiative Germany.
        
        eHealth Initiative is a network of digital health companies in Germany.
        This method scrapes their member directory for eHealth companies.
        
        Returns:
            List of HealthcareCompany objects found on eHealth Initiative
        """
        companies = []
        
        try:
            logger.info("Scraping eHealth Initiative...")
            url = "https://www.ehealth-initiative.de/mitglieder/"
            
            html = self._fetch_with_requests(url)
            if not html:
                html = self._fetch_with_selenium(url)
                
            if html:
                soup = self._parse_html(html)
                if soup:
                    # Look for member listings
                    member_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'member|mitglied|company', re.I))
                    
                    for element in member_elements:
                        company = self._extract_company_from_element(element, url)
                        if company:
                            company.category = "eHealth"
                            company.tags = ["eHealth Initiative", "Digital Health", "German"]
                            companies.append(company)
            
            logger.info(f"Extracted {len(companies)} companies from eHealth Initiative")
            
        except Exception as e:
            logger.error(f"Error scraping eHealth Initiative: {str(e)}")
        
        return companies
    
    def extract_from_healthcare_blogs(self) -> List[HealthcareCompany]:
        """
        Extract companies from healthcare startup blogs and articles.
        
        This method scrapes various healthcare blogs and articles that mention
        German healthcare startups and companies.
        
        Returns:
            List of HealthcareCompany objects found in healthcare blogs
        """
        companies = []
        
        # List of healthcare blogs and articles
        blog_urls = [
            "https://www.healthtech.de/startups/",
            "https://www.e-health-com.de/details-news/digital-health-startups-in-deutschland/",
            "https://www.digitale-gesundheit.de/startups/",
            "https://www.medtech-zwo.de/nachrichten/maerkte-und-trends/startup-landscape-deutschland.html"
        ]
        
        for url in blog_urls:
            try:
                logger.info(f"Scraping healthcare blog: {urlparse(url).netloc}")
                
                html = self._fetch_with_requests(url)
                if not html:
                    html = self._fetch_with_selenium(url)
                    
                if html:
                    soup = self._parse_html(html)
                    if soup:
                        # Look for company mentions in headings and emphasized text
                        company_mentions = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
                        
                        for mention in company_mentions:
                            text = mention.get_text(strip=True)
                            
                            if self._is_valid_company_name(text):
                                # Look for nearby links that might be the company website
                                parent = mention.parent
                                website = ""
                                description = ""
                                
                                if parent:
                                    # Search for links in the same section
                                    links = parent.find_all('a', href=True)
                                    for link in links:
                                        href = link.get('href')
                                        if self._is_company_website(href):
                                            website = href
                                            break
                                    
                                    # Extract description from surrounding text
                                    desc_text = parent.get_text(strip=True)
                                    if len(desc_text) > len(text):
                                        description = desc_text[:300]
                                
                                if self._is_new_company(website):
                                    company = HealthcareCompany(
                                        name=text,
                                        website=website,
                                        description=description,
                                        location="Germany",
                                        source_directory=url,
                                        category="Healthcare Startup",
                                        tags=["Blog Mention", "Startup", "German"]
                                    )
                                    companies.append(company)
                
                time.sleep(3)  # Rate limiting between blog requests
                
            except Exception as e:
                logger.error(f"Error scraping {urlparse(url).netloc}: {str(e)}")
        
        return companies
    
    def _extract_company_from_element(self, element, source_url: str) -> Optional[HealthcareCompany]:
        """
        Extract company information from a DOM element.
        
        This method attempts to extract company information from various HTML elements
        using multiple selectors and patterns.
        
        Args:
            element: BeautifulSoup element containing company information
            source_url: URL of the source where element was found
            
        Returns:
            HealthcareCompany object or None if extraction failed
        """
        try:
            # Try to find company name using various selectors
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5',
                '.company-name', '.startup-name', '.name',
                'strong', 'b', 'a[href]'
            ]
            
            name = ""
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    if self._is_valid_company_name(name):
                        break
            
            if not name or not self._is_valid_company_name(name):
                return None
            
            # Try to find website using various selectors
            website = ""
            website_selectors = [
                'a[href^="http"]', 'a[href^="https"]',
                '.website a', '.url a', '.link a'
            ]
            
            for selector in website_selectors:
                link_element = element.select_one(selector)
                if link_element:
                    href = link_element.get('href')
                    if self._is_company_website(href):
                        website = href
                        break
            
            # Extract description from various elements
            description = ""
            desc_selectors = [
                '.description', '.summary', '.about',
                'p', '.content', '.text'
            ]
            
            for selector in desc_selectors:
                desc_element = element.select_one(selector)
                if desc_element:
                    desc_text = desc_element.get_text(strip=True)
                    if len(desc_text) > 20:
                        description = desc_text[:300]
                        break
            
            # Extract location information
            location = "Germany"  # Default location
            location_selectors = [
                '.location', '.city', '.address',
                '[class*="location"]', '[class*="city"]'
            ]
            
            for selector in location_selectors:
                loc_element = element.select_one(selector)
                if loc_element:
                    loc_text = loc_element.get_text(strip=True)
                    if loc_text and len(loc_text) < 50:
                        location = loc_text
                        break
            
            # Check if this is a new company (not in our known list)
            if website and self._normalize_domain(website) in self.known_companies:
                return None
            
            # Create and return company object
            company = HealthcareCompany(
                name=name,
                website=website,
                description=description,
                location=location,
                source_directory=source_url,
                category="Healthcare"  # Default category
            )
            
            return company
            
        except Exception as e:
            logger.debug(f"Error extracting company from element: {str(e)}")
            return None
    
    def _is_company_link(self, url: str, text: str) -> bool:
        """
        Check if URL and text represent a company link.
        
        Args:
            url: URL to check
            text: Link text to check
            
        Returns:
            True if this appears to be a company link, False otherwise
        """
        if not url or len(url) < 8:
            return False
        
        # Skip non-company domains
        skip_domains = [
            'google.', 'facebook.', 'twitter.', 'linkedin.', 'youtube.',
            'github.', 'crunchbase.', 'xing.', 'wikipedia.', 'blog.',
            'medium.', 'news.', 'reddit.', 'instagram.', 'pinterest.'
        ]
        
        url_lower = url.lower()
        for skip in skip_domains:
            if skip in url_lower:
                return False
        
        # Must have company TLD
        company_tlds = ['.com', '.de', '.org', '.net', '.eu', '.co.uk', '.co', '.io', '.ai', '.health']
        has_tld = any(tld in url_lower for tld in company_tlds)
        
        # Text should look like a company name
        text_valid = len(text) > 2 and text.lower() not in [
            'website', 'visit', 'more', 'link', 'here', 'click', 'read',
            'learn', 'see', 'view', 'go', 'check', 'find'
        ]
        
        return has_tld and text_valid
    
    def _is_valid_company_name(self, name: str) -> bool:
        """
        Check if text looks like a valid company name.
        
        Args:
            name: Text to validate as company name
            
        Returns:
            True if text appears to be a valid company name, False otherwise
        """
        if not name or len(name) < 3 or len(name) > 100:
            return False
        
        # Skip common non-company words
        skip_words = [
            'read more', 'click here', 'learn more', 'contact', 'about',
            'home', 'news', 'blog', 'search', 'menu', 'login', 'register',
            'privacy', 'terms', 'imprint', 'impressum', 'datenschutz',
            'mitglied', 'member', 'directory', 'verzeichnis'
        ]
        
        name_lower = name.lower()
        for skip in skip_words:
            if skip in name_lower:
                return False
        
        # Look for company indicators
        company_indicators = [
            'gmbh', 'ag', 'inc', 'ltd', 'corp', 'llc', 'group', 'systems',
            'solutions', 'technologies', 'health', 'medical', 'care',
            'tech', 'bio', 'pharma', 'therapeutics', 'diagnostics',
            'medizin', 'gesundheit', 'technologie'
        ]
        
        has_indicator = any(indicator in name_lower for indicator in company_indicators)
        
        # Or looks like a proper name (starts with capital)
        looks_proper = name[0].isupper() and not name.isupper()
        
        # Should have letters
        has_letters = any(c.isalpha() for c in name)
        
        # Not too many numbers
        num_count = sum(1 for c in name if c.isdigit())
        mostly_letters = num_count < len(name) / 2
        
        return has_letters and mostly_letters and (has_indicator or looks_proper)
    
    def _is_company_website(self, url: str) -> bool:
        """
        Check if URL appears to be a company website.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL appears to be a company website, False otherwise
        """
        if not url or len(url) < 8:
            return False
        
        # Skip non-company domains
        skip_domains = [
            'google.', 'facebook.', 'twitter.', 'linkedin.', 'youtube.',
            'github.', 'crunchbase.', 'xing.', 'wikipedia.', 'blog.',
            'medium.', 'news.', 'instagram.', 'pinterest.'
        ]
        
        url_lower = url.lower()
        for skip in skip_domains:
            if skip in url_lower:
                return False
        
        # Must have company TLD
        company_tlds = ['.com', '.de', '.org', '.net', '.eu', '.co.uk', '.co', '.io', '.ai', '.health']
        has_tld = any(tld in url_lower for tld in company_tlds)
        
        return has_tld
    
    def _is_new_company(self, website: str) -> bool:
        """
        Check if company is new (not in known list).
        
        Args:
            website: Company website URL
            
        Returns:
            True if company is new, False if already known
        """
        if not website:
            return True
        
        domain = self._normalize_domain(website)
        return domain not in self.known_companies
    
    def _normalize_domain(self, url: str) -> str:
        """
        Normalize domain for comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized domain string
        """
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def enhance_companies_with_details(self, companies: List[HealthcareCompany]) -> List[HealthcareCompany]:
        """
        Enhance companies with additional details.
        
        This method attempts to find missing information for companies,
        such as websites, and cleans up existing data.
        
        Args:
            companies: List of companies to enhance
            
        Returns:
            List of enhanced companies
        """
        enhanced = []
        
        logger.info(f"Enhancing {len(companies)} companies with additional details...")
        
        for i, company in enumerate(companies):
            if i % 50 == 0:
                logger.info(f"Enhanced {i}/{len(companies)} companies...")
            
            enhanced_company = company
            
            # Try to find website if missing
            if not company.website:
                website = self._find_company_website(company.name)
                if website:
                    enhanced_company.website = website
            
            # Clean up company name
            enhanced_company.name = self._clean_company_name(company.name)
            
            # Extract city from location if not already set
            if company.location and not company.city:
                enhanced_company.city = self._extract_city(company.location)
            
            # Only add if the company has valid information
            if enhanced_company.name and len(enhanced_company.name) > 2:
                enhanced.append(enhanced_company)
            
            # Rate limiting to avoid overwhelming servers
            if i % 20 == 0:
                time.sleep(1)
        
        return enhanced
    
    def _find_company_website(self, company_name: str) -> str:
        """
        Try to find company website by guessing common URL patterns.
        
        Args:
            company_name: Name of the company
            
        Returns:
            Found website URL or empty string if not found
        """
        # Skip if we can't make web requests
        if not self.use_requests or not self.session:
            return ""
            
        # Create clean version of company name for URL guessing
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        
        # Common URL patterns for German companies
        potential_urls = [
            f"https://www.{clean_name}.de",
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.de",
            f"https://{clean_name}.com",
            f"https://www.{clean_name}.health",
            f"https://www.{clean_name}.io"
        ]
        
        for url in potential_urls:
            try:
                response = self.session.head(url, timeout=5)
                if response.status_code in [200, 301, 302]:
                    return url
            except:
                continue
        
        return ""
    
    def _clean_company_name(self, name: str) -> str:
        """
        Clean up company name by removing unnecessary prefixes/suffixes.
        
        Args:
            name: Raw company name
            
        Returns:
            Cleaned company name
        """
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove common prefixes that aren't part of company name
        prefixes = ['unternehmen:', 'company:', 'startup:', 'member:', 'mitglied:']
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name
    
    def _extract_city(self, location: str) -> str:
        """
        Extract city name from location string.
        
        Args:
            location: Location string
            
        Returns:
            Extracted city name
        """
        if not location:
            return ""
        
        # Common German cities
        cities = [
            'Berlin', 'Hamburg', 'München', 'Munich', 'Köln', 'Cologne',
            'Frankfurt', 'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen',
            'Leipzig', 'Bremen', 'Dresden', 'Hannover', 'Nürnberg'
        ]
        
        for city in cities:
            if city.lower() in location.lower():
                return city
        
        # If no known city found, return the location as-is
        return location
    
    def run_extraction(self, sources: List[str] = None) -> List[HealthcareCompany]:
        """
        Run the complete extraction process.
        
        Args:
            sources: List of specific sources to scrape (optional)
            
        Returns:
            List of extracted and enhanced companies
        """
        logger.info("🚀 STARTING ENHANCED HEALTHCARE DIRECTORY EXTRACTION")
        logger.info("=" * 80)
        
        # Warn if no web capabilities
        if not self.use_requests and not self.use_selenium:
            logger.warning("⚠️  No web scraping libraries available!")
            logger.warning("   Install 'requests' and 'beautifulsoup4' for basic functionality")
            logger.warning("   Install 'selenium' for JavaScript-heavy sites")
            logger.warning("   Returning sample data for demonstration...")
            return self._generate_sample_companies()
        
        all_companies = []
        
        # Define all available extraction methods
        extraction_methods = [
            ("BVMed - Medical Technology Association", "bvmed", self.extract_from_bvmed),
            ("SPECTARIS - Industry Association", "spectaris", self.extract_from_spectaris),
            ("Digital Health Hub Berlin", "digital_health_hub", self.extract_from_digital_health_hub),
            ("BioM - Bavaria Biotech Cluster", "biom", self.extract_from_biom_cluster),
            ("eHealth Initiative Germany", "ehealth", self.extract_from_ehealth_initiative),
            ("Healthcare Startup Blogs", "blogs", self.extract_from_healthcare_blogs)
        ]
        
        # Filter methods based on requested sources
        if sources:
            extraction_methods = [
                (name, code, method) for name, code, method in extraction_methods 
                if code in sources
            ]
        
        # Execute extractions with error handling
        for phase_name, _, method in extraction_methods:
            logger.info(f"🔍 Phase: {phase_name}")
            try:
                companies = method()
                all_companies.extend(companies)
                logger.info(f"✅ Extracted {len(companies)} companies from {phase_name}")
            except Exception as e:
                logger.error(f"❌ Error in {phase_name}: {str(e)}")
                # Continue with other sources even if one fails
                continue
            
            # Rate limiting between phases
            time.sleep(5)
        
        # Remove duplicates
        unique_companies = self._remove_duplicates(all_companies)
        logger.info(f"📊 Total unique companies: {len(unique_companies)}")
        
        # Enhance companies with additional details
        logger.info("🔍 Enhancing companies with additional details...")
        enhanced_companies = self.enhance_companies_with_details(unique_companies)
        
        return enhanced_companies
    
    def _generate_sample_companies(self) -> List[HealthcareCompany]:
        """
        Generate sample companies for demonstration when no web libraries available.
        
        Returns:
            List of sample HealthcareCompany objects
        """
        sample_companies = [
            HealthcareCompany(
                name="Sample MedTech GmbH",
                website="https://sample-medtech.de",
                description="Sample medical technology company (generated for demonstration)",
                location="Berlin, Germany",
                category="Medical Technology",
                source_directory="sample://demonstration",
                tags=["Sample", "Demo", "Medical Technology"]
            ),
            HealthcareCompany(
                name="Demo Healthcare Systems",
                website="https://demo-healthcare.com",
                description="Demo healthcare company (generated for demonstration)",
                location="Munich, Germany",
                category="Healthcare Systems",
                source_directory="sample://demonstration",
                tags=["Sample", "Demo", "Healthcare"]
            ),
            HealthcareCompany(
                name="Test Biotech AG",
                website="https://test-biotech.de",
                description="Test biotechnology company (generated for demonstration)",
                location="Hamburg, Germany",
                category="Biotechnology",
                source_directory="sample://demonstration",
                tags=["Sample", "Demo", "Biotech"]
            )
        ]
        
        logger.info("Generated 3 sample companies for demonstration")
        return sample_companies
    
    def _remove_duplicates(self, companies: List[HealthcareCompany]) -> List[HealthcareCompany]:
        """
        Remove duplicate companies based on name and website.
        
        Args:
            companies: List of companies to deduplicate
            
        Returns:
            List of unique companies
        """
        seen = set()
        unique = []
        
        for company in companies:
            # Create key for deduplication using name and domain
            key = (
                company.name.lower().strip(),
                self._normalize_domain(company.website)
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(company)
        
        return unique
    
    def save_results(self, companies: List[HealthcareCompany], output_dir: str = "output") -> List[Dict]:
        """
        Save extraction results to CSV and JSON files.
        
        Args:
            companies: List of companies to save
            output_dir: Directory to save results
            
        Returns:
            List of company dictionaries
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Convert to dictionary format for saving
        company_dicts = []
        for company in companies:
            company_dict = asdict(company)
            company_dict['domain'] = self._normalize_domain(company.website)
            company_dicts.append(company_dict)
        
        # Save to CSV file
        csv_file = output_path / "healthcare_companies.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON file
        json_file = output_path / "healthcare_companies.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Results saved to {csv_file} and {json_file}")
        
        return company_dicts
    
    def __del__(self):
        """Cleanup Selenium driver when scraper is destroyed."""
        if self.driver:
            self.driver.quit()

def main():
    """
    Main execution function with command-line argument support.
    
    This function handles command-line arguments and runs the scraper
    with the specified configuration.
    """
    # Setup command-line argument parser
    parser = argparse.ArgumentParser(
        description='Enhanced Healthcare Company Directory Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_healthcare_scraper.py
  python enhanced_healthcare_scraper.py --no-selenium
  python enhanced_healthcare_scraper.py --sources bvmed spectaris
  python enhanced_healthcare_scraper.py --max-companies 500 --output-dir results
        """
    )
    
    # Add command-line arguments
    parser.add_argument(
        '--no-selenium', 
        action='store_true', 
        help='Run without Selenium (faster but may miss some data)'
    )
    parser.add_argument(
        '--output-dir', 
        default='output', 
        help='Output directory for results (default: output)'
    )
    parser.add_argument(
        '--sources', 
        nargs='*', 
        choices=['bvmed', 'spectaris', 'digital_health_hub', 'biom', 'ehealth', 'blogs'],
        help='Specific sources to scrape (default: all)'
    )
    parser.add_argument(
        '--max-companies', 
        type=int, 
        default=1000,
        help='Maximum number of companies to extract (default: 1000)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create scraper instance
    use_selenium = not args.no_selenium
    scraper = EnhancedHealthcareScraper(use_selenium=use_selenium)
    
    # Log configuration
    logger.info("🚀 STARTING ENHANCED HEALTHCARE SCRAPER")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  - Requests: {'Enabled' if scraper.use_requests else 'Disabled'}")
    logger.info(f"  - Selenium: {'Enabled' if scraper.use_selenium else 'Disabled'}")
    logger.info(f"  - BeautifulSoup: {'Enabled' if scraper.use_beautifulsoup else 'Disabled'}")
    logger.info(f"  - Output directory: {args.output_dir}")
    logger.info(f"  - Max companies: {args.max_companies}")
    logger.info(f"  - Sources: {args.sources or 'All'}")
    logger.info("=" * 60)
    
    # Run extraction
    start_time = time.time()
    
    try:
        # Run scraper with specified sources
        companies = scraper.run_extraction(sources=args.sources)
        
        # Limit results if specified
        if len(companies) > args.max_companies:
            companies = companies[:args.max_companies]
            logger.info(f"⚠️  Limited results to {args.max_companies} companies")
        
        # Save results
        if companies:
            company_dicts = scraper.save_results(companies, args.output_dir)
            
            # Calculate runtime
            runtime = time.time() - start_time
            
            # Display summary statistics
            with_websites = sum(1 for c in company_dicts if c['website'])
            german_companies = sum(1 for c in company_dicts if 'germany' in c['location'].lower())
            
            # Count by source
            sources = {}
            for c in company_dicts:
                source = urlparse(c['source_directory']).netloc
                sources[source] = sources.get(source, 0) + 1
            
            logger.info("🎉 EXTRACTION COMPLETE!")
            logger.info("=" * 60)
            logger.info(f"📊 FINAL RESULTS:")
            logger.info(f"   Total companies: {len(companies)}")
            logger.info(f"   With websites: {with_websites} ({with_websites/len(companies)*100:.1f}%)")
            logger.info(f"   German companies: {german_companies}")
            logger.info(f"   Runtime: {runtime:.1f} seconds")
            logger.info(f"   Rate: {len(companies)/runtime:.2f} companies/second")
            
            logger.info("📈 BREAKDOWN BY SOURCE:")
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"   {source}: {count} companies")
            
            # Show sample companies
            logger.info("\n🏢 SAMPLE COMPANIES:")
            for i, company in enumerate(companies[:5], 1):
                logger.info(f"   {i}. {company.name}")
                if company.website:
                    logger.info(f"      🌐 {company.website}")
                if company.location:
                    logger.info(f"      📍 {company.location}")
                if company.category:
                    logger.info(f"      🏷️  {company.category}")
                logger.info("")
            
            logger.info("✅ Results saved successfully!")
            
        else:
            logger.error("❌ No companies were extracted")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⚠️  Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()