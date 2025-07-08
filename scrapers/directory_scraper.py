"""
Directory Scraper for Healthcare Startup Discovery System

This module scrapes startup directories like Crunchbase, AngelList,
and other startup listing websites to discover healthcare companies.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import re
import json

from scrapers.base_scraper import BaseScraper
from models import CompanyInfo, ScrapingResult, SourceType
from config import STARTUP_DIRECTORIES, HEALTHCARE_KEYWORDS, GERMAN_SEARCH_QUERIES

# Set up logging
logger = logging.getLogger(__name__)


class DirectoryScraper(BaseScraper):
    """
    Scraper for startup directories and company listing websites
    
    This scraper handles various startup directories including:
    - Crunchbase
    - AngelList (Wellfound)
    - F6S
    - EU-Startups
    - German-Startups
    - Healthcare-specific directories
    """
    
    def __init__(self, delay: float = 2.0):
        """Initialize directory scraper with conservative delay"""
        super().__init__(delay)
        
        # Directory-specific configurations
        self.directory_configs = {
            'crunchbase.com': {
                'search_patterns': [
                    '/search/organizations.csv?field_ids=name,website,short_description,location_identifiers&category_name=Health Care',
                    '/search/organizations.csv?field_ids=name,website,short_description,location_identifiers&category_name=Biotechnology',
                    '/search/organizations.csv?field_ids=name,website,short_description,location_identifiers&category_name=Medical Device',
                ],
                'company_selectors': {
                    'name': '.identifier-label',
                    'description': '.description',
                    'website': 'a[href*="redirect_to"]',
                    'location': '.location'
                }
            },
            'angel.co': {
                'search_patterns': [
                    '/companies?keywords=healthcare',
                    '/companies?keywords=medtech',
                    '/companies?keywords=digital+health',
                    '/companies?keywords=biotech'
                ],
                'company_selectors': {
                    'name': '.startup-link',
                    'description': '.pitch',
                    'website': '.startup-website',
                    'location': '.location'
                }
            },
            'f6s.com': {
                'search_patterns': [
                    '/companies?keywords=healthcare',
                    '/companies?keywords=health+tech',
                    '/companies?keywords=medical+technology'
                ],
                'company_selectors': {
                    'name': '.company-name',
                    'description': '.company-description',
                    'website': '.company-website',
                    'location': '.company-location'
                }
            }
        }
        
        logger.info("DirectoryScraper initialized")
    
    async def scrape(self, directories: List[str] = None, max_pages: int = 10) -> ScrapingResult:
        """
        Scrape startup directories for healthcare companies
        
        Args:
            directories: List of directory URLs to scrape (uses default if None)
            max_pages: Maximum pages to scrape per directory
            
        Returns:
            ScrapingResult with discovered companies
        """
        start_time = asyncio.get_event_loop().time()
        
        if directories is None:
            directories = STARTUP_DIRECTORIES
        
        result = ScrapingResult(
            source_type=SourceType.DIRECTORY,
            source_url=f"Multiple directories: {', '.join(directories)}"
        )
        
        try:
            all_companies = []
            
            # Process each directory
            for directory_url in directories:
                logger.info(f"Scraping directory: {directory_url}")
                
                try:
                    companies = await self._scrape_directory(directory_url, max_pages)
                    all_companies.extend(companies)
                    logger.info(f"Found {len(companies)} companies from {directory_url}")
                    
                except Exception as e:
                    logger.error(f"Error scraping directory {directory_url}: {e}")
                    result.errors.append(f"Error scraping {directory_url}: {str(e)}")
            
            # Deduplicate companies by URL
            unique_companies = self._deduplicate_companies(all_companies)
            
            for company in unique_companies:
                result.add_company(company)
            
            result.success = True
            logger.info(f"Directory scraping completed. Found {len(unique_companies)} unique companies")
            
        except Exception as e:
            logger.error(f"Error in directory scraping: {e}")
            result.success = False
            result.error_message = str(e)
        
        result.processing_time = asyncio.get_event_loop().time() - start_time
        return result
    
    async def _scrape_directory(self, directory_url: str, max_pages: int) -> List[CompanyInfo]:
        """
        Scrape a single directory
        
        Args:
            directory_url: URL of the directory to scrape
            max_pages: Maximum pages to scrape
            
        Returns:
            List of discovered companies
        """
        companies = []
        domain = urlparse(directory_url).netloc.lower()
        
        # Get directory-specific configuration
        config = self._get_directory_config(domain)
        
        if not config:
            # Generic scraping approach
            companies = await self._scrape_generic_directory(directory_url, max_pages)
        else:
            # Directory-specific scraping
            companies = await self._scrape_specific_directory(directory_url, config, max_pages)
        
        return companies
    
    def _get_directory_config(self, domain: str) -> Optional[Dict]:
        """Get configuration for specific directory"""
        for config_domain, config in self.directory_configs.items():
            if config_domain in domain:
                return config
        return None
    
    async def _scrape_specific_directory(self, base_url: str, config: Dict, max_pages: int) -> List[CompanyInfo]:
        """
        Scrape directory using specific configuration
        
        Args:
            base_url: Base URL of directory
            config: Directory-specific configuration
            max_pages: Maximum pages to scrape
            
        Returns:
            List of discovered companies
        """
        companies = []
        
        # Try each search pattern
        for search_pattern in config.get('search_patterns', []):
            search_url = urljoin(base_url, search_pattern)
            logger.info(f"Searching: {search_url}")
            
            try:
                page_companies = await self._scrape_search_results(
                    search_url, config.get('company_selectors', {}), max_pages
                )
                companies.extend(page_companies)
                
            except Exception as e:
                logger.error(f"Error scraping search pattern {search_pattern}: {e}")
        
        return companies
    
    async def _scrape_search_results(self, search_url: str, selectors: Dict, max_pages: int) -> List[CompanyInfo]:
        """
        Scrape search results from a directory
        
        Args:
            search_url: URL of search results
            selectors: CSS selectors for extracting company info
            max_pages: Maximum pages to scrape
            
        Returns:
            List of discovered companies
        """
        companies = []
        
        for page in range(1, max_pages + 1):
            try:
                # Build paginated URL
                paginated_url = self._build_paginated_url(search_url, page)
                
                # Get page content
                html = await self.get_html_content(paginated_url)
                if not html:
                    break
                
                # Extract companies from page
                page_companies = self._extract_companies_from_page(html, selectors, paginated_url)
                
                if not page_companies:
                    logger.info(f"No companies found on page {page}, stopping")
                    break
                
                companies.extend(page_companies)
                logger.info(f"Found {len(page_companies)} companies on page {page}")
                
                # Break if we've found enough companies
                if len(companies) >= 1000:  # Reasonable limit
                    logger.info("Reached company limit, stopping pagination")
                    break
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return companies
    
    def _build_paginated_url(self, base_url: str, page: int) -> str:
        """Build URL for specific page"""
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        
        # Add page parameter (different directories use different parameter names)
        if 'crunchbase.com' in parsed.netloc:
            query_params['page'] = [str(page)]
        elif 'angel.co' in parsed.netloc:
            query_params['page'] = [str(page)]
        elif 'f6s.com' in parsed.netloc:
            query_params['page'] = [str(page)]
        else:
            # Generic approach
            query_params['page'] = [str(page)]
        
        # Rebuild URL
        new_query = urlencode(query_params, doseq=True)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
    
    def _extract_companies_from_page(self, html: str, selectors: Dict, source_url: str) -> List[CompanyInfo]:
        """
        Extract company information from a search results page
        
        Args:
            html: HTML content of the page
            selectors: CSS selectors for company data
            source_url: URL of the source page
            
        Returns:
            List of CompanyInfo objects
        """
        companies = []
        soup = self.parse_html(html)
        
        # Find all company containers (try common patterns)
        company_containers = (
            soup.find_all(class_=re.compile(r'company|startup|organization|item|card', re.I)) or
            soup.find_all('tr') or  # Table rows
            soup.find_all(class_=re.compile(r'result|listing', re.I))
        )
        
        for container in company_containers:
            try:
                company_info = self._extract_single_company(container, selectors, source_url)
                if company_info:
                    companies.append(company_info)
            except Exception as e:
                logger.debug(f"Error extracting company from container: {e}")
        
        return companies
    
    def _extract_single_company(self, container, selectors: Dict, source_url: str) -> Optional[CompanyInfo]:
        """
        Extract single company information from HTML container
        
        Args:
            container: BeautifulSoup element containing company info
            selectors: CSS selectors for company data
            source_url: URL of the source page
            
        Returns:
            CompanyInfo object or None
        """
        try:
            # Extract basic information
            name_element = container.select_one(selectors.get('name', ''))
            name = name_element.get_text().strip() if name_element else ""
            
            # Skip if no name
            if not name:
                return None
            
            # Extract description
            desc_element = container.select_one(selectors.get('description', ''))
            description = desc_element.get_text().strip() if desc_element else ""
            
            # Extract website URL
            website_element = container.select_one(selectors.get('website', ''))
            website_url = ""
            
            if website_element:
                if website_element.name == 'a':
                    href = website_element.get('href', '')
                    # Handle redirect URLs (common in directories)
                    if 'redirect' in href or 'go.to' in href:
                        # Try to extract actual URL from redirect
                        website_url = self._extract_url_from_redirect(href)
                    else:
                        website_url = href
                else:
                    website_url = website_element.get_text().strip()
            
            # Clean and validate URL
            if website_url:
                website_url = self.url_validator.clean_url(website_url)
                if not self.url_validator.is_valid_url(website_url):
                    website_url = ""
            
            # Skip if no valid website URL
            if not website_url:
                return None
            
            # Check healthcare relevance using description
            combined_text = f"{name} {description}"
            confidence_score, matched_keywords, detected_countries = self.nlp_processor.calculate_overall_confidence(
                combined_text, website_url
            )
            
            # Only include if healthcare relevant
            if not self.nlp_processor.is_healthcare_relevant(combined_text, website_url):
                return None
            
            # Determine country
            from models import Country
            country = Country.UNKNOWN
            if detected_countries:
                # Simple mapping for common countries
                if 'germany' in detected_countries:
                    country = Country.GERMANY
                elif 'austria' in detected_countries:
                    country = Country.AUSTRIA
                elif 'switzerland' in detected_countries:
                    country = Country.SWITZERLAND
                # Add more mappings as needed
            
            # Create CompanyInfo object
            company_info = CompanyInfo(
                name=name,
                url=website_url,
                description=description,
                country=country,
                source_type=SourceType.DIRECTORY,
                source_url=source_url,
                confidence_score=confidence_score,
                keywords_matched=matched_keywords
            )
            
            return company_info
            
        except Exception as e:
            logger.debug(f"Error extracting company info: {e}")
            return None
    
    def _extract_url_from_redirect(self, redirect_url: str) -> str:
        """Extract actual URL from redirect URL"""
        try:
            parsed = urlparse(redirect_url)
            query_params = parse_qs(parsed.query)
            
            # Common redirect parameter names
            for param_name in ['url', 'u', 'redirect', 'to', 'target']:
                if param_name in query_params:
                    return query_params[param_name][0]
            
            # If no redirect parameter found, return original
            return redirect_url
            
        except Exception:
            return redirect_url
    
    async def _scrape_generic_directory(self, directory_url: str, max_pages: int) -> List[CompanyInfo]:
        """
        Generic scraping approach for unknown directories
        
        Args:
            directory_url: URL of directory
            max_pages: Maximum pages to scrape
            
        Returns:
            List of discovered companies
        """
        companies = []
        
        try:
            # Get main page content
            html = await self.get_html_content(directory_url)
            if not html:
                return companies
            
            # Extract all URLs from the page
            urls = self.extract_urls_from_html(html, directory_url)
            
            # Filter URLs that might be company pages
            company_urls = self._filter_potential_company_urls(urls)
            
            # Limit the number of URLs to process
            if len(company_urls) > 100:
                company_urls = company_urls[:100]
            
            # Process URLs concurrently
            discovered_companies = await self.process_urls_concurrently(
                company_urls, SourceType.DIRECTORY
            )
            
            companies.extend(discovered_companies)
            
        except Exception as e:
            logger.error(f"Error in generic directory scraping: {e}")
        
        return companies
    
    def _filter_potential_company_urls(self, urls: List[str]) -> List[str]:
        """
        Filter URLs that might be company pages
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            List of potential company URLs
        """
        potential_urls = []
        
        for url in urls:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Skip obvious non-company pages
            if any(skip in path for skip in [
                '/blog/', '/news/', '/press/', '/about/', '/contact/',
                '/search/', '/category/', '/tag/', '/archive/',
                '/login/', '/register/', '/user/', '/profile/'
            ]):
                continue
            
            # Look for patterns that suggest company pages
            if any(pattern in path for pattern in [
                '/company/', '/startup/', '/organization/',
                '/companies/', '/startups/', '/orgs/'
            ]):
                potential_urls.append(url)
            
            # Also include if URL contains healthcare keywords
            if any(keyword in url.lower() for keyword in ['health', 'medical', 'med', 'bio']):
                potential_urls.append(url)
        
        return potential_urls
    
    def _deduplicate_companies(self, companies: List[CompanyInfo]) -> List[CompanyInfo]:
        """
        Remove duplicate companies based on URL and name
        
        Args:
            companies: List of companies to deduplicate
            
        Returns:
            List of unique companies
        """
        seen_urls = set()
        seen_names = set()
        unique_companies = []
        
        for company in companies:
            # Create unique identifiers
            url_key = company.url.lower().strip()
            name_key = company.name.lower().strip()
            
            # Skip if we've already seen this URL or very similar name
            if url_key in seen_urls:
                continue
            
            if name_key in seen_names:
                continue
            
            seen_urls.add(url_key)
            seen_names.add(name_key)
            unique_companies.append(company)
        
        return unique_companies