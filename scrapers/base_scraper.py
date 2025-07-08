"""
Base Scraper for Healthcare Startup Discovery System

This module provides the base class and common functionality
for all specific scraper implementations.
"""

import asyncio
import aiohttp
import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import random

from models import CompanyInfo, ScrapingResult, SourceType, Country
from nlp_processor import HealthcareNLPProcessor
from url_validator import URLValidator
from config import (
    DEFAULT_DELAY, MAX_CONCURRENT_REQUESTS, RETRY_ATTEMPTS, 
    TIMEOUT, USER_AGENTS, EXCLUDED_DOMAINS
)

# Set up logging
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers
    
    This class provides common functionality including:
    - Async HTTP requests with rate limiting
    - HTML parsing
    - NLP processing for healthcare relevance
    - URL validation and cleaning
    - Error handling and retries
    """
    
    def __init__(self, delay: float = DEFAULT_DELAY):
        """
        Initialize the base scraper
        
        Args:
            delay: Delay between requests in seconds
        """
        self.delay = delay
        self.nlp_processor = HealthcareNLPProcessor()
        self.url_validator = URLValidator()
        self.session = None
        self.user_agents = USER_AGENTS
        self.current_user_agent_index = 0
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'companies_found': 0,
            'urls_processed': 0
        }
        
        logger.info(f"{self.__class__.__name__} initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=TIMEOUT),
            connector=aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_user_agent(self) -> str:
        """Get next user agent for rotation"""
        user_agent = self.user_agents[self.current_user_agent_index]
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    async def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[aiohttp.ClientResponse]:
        """
        Make an HTTP request with retries and rate limiting
        
        Args:
            url: URL to request
            method: HTTP method
            **kwargs: Additional arguments for the request
            
        Returns:
            Response object or None if failed
        """
        if not self.session:
            raise RuntimeError("Scraper must be used as async context manager")
        
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self.get_user_agent()
        kwargs['headers'] = headers
        
        for attempt in range(RETRY_ATTEMPTS):
            try:
                self.stats['requests_made'] += 1
                
                # Add delay for rate limiting
                if self.delay > 0:
                    await asyncio.sleep(self.delay + random.uniform(0, 0.5))
                
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status == 200:
                        self.stats['successful_requests'] += 1
                        return response
                    elif response.status == 429:  # Rate limited
                        wait_time = min(60, 2 ** attempt)
                        logger.warning(f"Rate limited for {url}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout for {url} (attempt {attempt + 1})")
            except Exception as e:
                logger.error(f"Error requesting {url} (attempt {attempt + 1}): {e}")
            
            if attempt < RETRY_ATTEMPTS - 1:
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
        
        self.stats['failed_requests'] += 1
        return None
    
    async def get_html_content(self, url: str) -> Optional[str]:
        """
        Get HTML content from URL
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        response = await self.make_request(url)
        if response:
            try:
                content = await response.text()
                return content
            except Exception as e:
                logger.error(f"Error reading content from {url}: {e}")
        return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup
        
        Args:
            html: HTML content string
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'html.parser')
    
    def extract_urls_from_html(self, html: str, base_url: str) -> List[str]:
        """
        Extract all URLs from HTML content
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative URLs
            
        Returns:
            List of absolute URLs
        """
        soup = self.parse_html(html)
        urls = []
        
        # Extract from anchor tags
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if self.url_validator.is_valid_url(absolute_url):
                urls.append(absolute_url)
        
        # Extract from other elements that might contain URLs
        for element in soup.find_all(['link', 'script'], src=True):
            src = element.get('src')
            if src:
                absolute_url = urljoin(base_url, src)
                if self.url_validator.is_valid_url(absolute_url):
                    urls.append(absolute_url)
        
        return urls
    
    def extract_text_content(self, html: str) -> str:
        """
        Extract clean text content from HTML
        
        Args:
            html: HTML content
            
        Returns:
            Clean text content
        """
        soup = self.parse_html(html)
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_company_info_from_html(self, html: str, url: str, source_type: SourceType) -> Optional[CompanyInfo]:
        """
        Extract company information from HTML content
        
        Args:
            html: HTML content
            url: Source URL
            source_type: Type of source
            
        Returns:
            CompanyInfo object if healthcare relevant, None otherwise
        """
        text_content = self.extract_text_content(html)
        
        if not text_content:
            return None
        
        # Use NLP processor to analyze content
        confidence_score, matched_keywords, detected_countries = self.nlp_processor.calculate_overall_confidence(
            text_content, url
        )
        
        # Check if healthcare relevant
        if not self.nlp_processor.is_healthcare_relevant(text_content, url):
            return None
        
        # Try to extract company name
        soup = self.parse_html(html)
        company_name = self._extract_company_name(soup, text_content)
        
        if not company_name:
            return None
        
        # Determine country
        country = Country.UNKNOWN
        if detected_countries:
            country_mapping = {
                'germany': Country.GERMANY,
                'austria': Country.AUSTRIA,
                'switzerland': Country.SWITZERLAND,
                'netherlands': Country.NETHERLANDS,
                'belgium': Country.BELGIUM,
                'france': Country.FRANCE,
                'italy': Country.ITALY,
                'spain': Country.SPAIN,
                'portugal': Country.PORTUGAL,
                'poland': Country.POLAND,
                'united_kingdom': Country.UNITED_KINGDOM,
                'czech_republic': Country.CZECH_REPUBLIC,
                'hungary': Country.HUNGARY,
                'romania': Country.ROMANIA,
                'bulgaria': Country.BULGARIA,
                'croatia': Country.CROATIA,
                'slovenia': Country.SLOVENIA,
                'slovakia': Country.SLOVAKIA,
                'estonia': Country.ESTONIA,
                'latvia': Country.LATVIA,
                'lithuania': Country.LITHUANIA,
                'finland': Country.FINLAND,
                'sweden': Country.SWEDEN,
                'denmark': Country.DENMARK,
                'norway': Country.NORWAY,
                'ireland': Country.IRELAND
            }
            
            for detected_country in detected_countries:
                if detected_country in country_mapping:
                    country = country_mapping[detected_country]
                    break
        
        # Create company info
        try:
            company_info = CompanyInfo(
                name=company_name,
                url=self.url_validator.clean_url(url),
                description=text_content[:500],  # Truncate description
                country=country,
                source_type=source_type,
                source_url=url,
                confidence_score=confidence_score,
                keywords_matched=matched_keywords
            )
            
            self.stats['companies_found'] += 1
            return company_info
            
        except ValueError as e:
            logger.warning(f"Error creating CompanyInfo for {url}: {e}")
            return None
    
    def _extract_company_name(self, soup: BeautifulSoup, text_content: str) -> str:
        """
        Extract company name from HTML soup and text content
        
        Args:
            soup: BeautifulSoup object
            text_content: Clean text content
            
        Returns:
            Company name or empty string
        """
        # Try title tag first
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if title and len(title) < 100:
                # Clean up common title patterns
                company_name = title.split('|')[0].split('-')[0].strip()
                if company_name:
                    return company_name
        
        # Try meta tags
        meta_tags = soup.find_all('meta', attrs={'name': ['title', 'application-name', 'og:title']})
        for meta in meta_tags:
            content = meta.get('content', '').strip()
            if content and len(content) < 100:
                return content
        
        # Try h1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags[:3]:  # Check first 3 h1 tags
            h1_text = h1.get_text().strip()
            if h1_text and len(h1_text) < 100:
                return h1_text
        
        # Use NLP processor as fallback
        extracted_name = self.nlp_processor.extract_company_name_from_text(text_content)
        if extracted_name:
            return extracted_name
        
        # If all else fails, use domain name
        parsed_url = urlparse(soup.find('base', href=True)['href'] if soup.find('base', href=True) else '')
        if parsed_url.netloc:
            domain_parts = parsed_url.netloc.split('.')
            if len(domain_parts) >= 2:
                return domain_parts[-2].capitalize()
        
        return ""
    
    async def process_urls_concurrently(self, urls: List[str], source_type: SourceType) -> List[CompanyInfo]:
        """
        Process multiple URLs concurrently with rate limiting
        
        Args:
            urls: List of URLs to process
            source_type: Type of source
            
        Returns:
            List of discovered companies
        """
        companies = []
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def process_single_url(url: str) -> Optional[CompanyInfo]:
            async with semaphore:
                try:
                    self.stats['urls_processed'] += 1
                    html = await self.get_html_content(url)
                    if html:
                        return self.extract_company_info_from_html(html, url, source_type)
                except Exception as e:
                    logger.error(f"Error processing {url}: {e}")
                return None
        
        # Create tasks for all URLs
        tasks = [process_single_url(url) for url in urls]
        
        # Process in batches to avoid overwhelming servers
        batch_size = MAX_CONCURRENT_REQUESTS
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results = await asyncio.gather(*batch, return_exceptions=True)
            
            for result in results:
                if isinstance(result, CompanyInfo):
                    companies.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in batch processing: {result}")
        
        return companies
    
    @abstractmethod
    async def scrape(self, **kwargs) -> ScrapingResult:
        """
        Abstract method that must be implemented by all scrapers
        
        Returns:
            ScrapingResult with discovered companies
        """
        pass
    
    def get_stats(self) -> Dict[str, int]:
        """Get scraping statistics"""
        return self.stats.copy()