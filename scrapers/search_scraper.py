"""
Search Engine Scraper for Healthcare Startup Discovery System

This module uses search engines to discover healthcare startups
by searching for relevant terms and extracting company URLs
from search results.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse, quote_plus
import re
import time

from scrapers.base_scraper import BaseScraper
from models import CompanyInfo, ScrapingResult, SourceType
from config import SEARCH_ENGINES, GERMAN_SEARCH_QUERIES, HEALTHCARE_KEYWORDS

# Set up logging
logger = logging.getLogger(__name__)


class SearchScraper(BaseScraper):
    """
    Scraper that uses search engines to discover healthcare companies
    
    This scraper:
    - Performs targeted searches for healthcare startups
    - Extracts URLs from search results
    - Validates and filters results for relevance
    - Handles multiple search engines (Google, Bing, DuckDuckGo)
    """
    
    def __init__(self, delay: float = 3.0):
        """Initialize search scraper with conservative delay"""
        super().__init__(delay)
        
        # Search query templates
        self.search_queries = [
            # German/European healthcare startups
            "deutsche healthcare startups",
            "medizintechnik startups deutschland",
            "gesundheitstechnik unternehmen europa",
            "digital health startups germany",
            "european medtech companies",
            "biotech startups deutschland",
            "telemedizin startups europa",
            
            # English healthcare startup queries
            "healthcare startups europe",
            "medical technology companies germany",
            "digital health startups austria switzerland",
            "biotech companies netherlands belgium",
            "health tech startups scandinavia",
            "medical device companies france italy",
            "telemedicine startups eastern europe",
            
            # More specific queries
            '"healthcare startup" site:eu',
            '"medtech company" germany OR austria OR switzerland',
            '"digital health" startup "founded" 2020..2024',
            '"medical AI" company europe',
            '"health data" startup germany',
            '"clinical trial" platform europe',
            
            # Industry-specific queries
            "pharmaceutical startup europe",
            "diagnostic company germany",
            "rehabilitation technology startup",
            "mental health app europe",
            "fitness tracker company",
            "medical imaging startup",
            "genomics company europe",
            "precision medicine startup"
        ]
        
        # Search engine configurations
        self.search_configs = {
            'google': {
                'base_url': 'https://www.google.com/search',
                'params': {'q': '', 'num': 20, 'start': 0},
                'result_selector': 'div.g',
                'link_selector': 'h3 a',
                'title_selector': 'h3',
                'description_selector': '.VwiC3b'
            },
            'bing': {
                'base_url': 'https://www.bing.com/search',
                'params': {'q': '', 'count': 20, 'first': 1},
                'result_selector': '.b_algo',
                'link_selector': 'h2 a',
                'title_selector': 'h2',
                'description_selector': '.b_caption p'
            },
            'duckduckgo': {
                'base_url': 'https://duckduckgo.com/html',
                'params': {'q': '', 's': 0},
                'result_selector': '.result',
                'link_selector': '.result__title a',
                'title_selector': '.result__title',
                'description_selector': '.result__snippet'
            }
        }
        
        logger.info("SearchScraper initialized")
    
    async def scrape(self, search_engines: List[str] = None, max_results_per_query: int = 50) -> ScrapingResult:
        """
        Scrape search engines for healthcare companies
        
        Args:
            search_engines: List of search engines to use (default: all)
            max_results_per_query: Maximum results to collect per query
            
        Returns:
            ScrapingResult with discovered companies
        """
        start_time = asyncio.get_event_loop().time()
        
        if search_engines is None:
            search_engines = ['duckduckgo']  # Start with DuckDuckGo as it's more lenient
        
        result = ScrapingResult(
            source_type=SourceType.SEARCH_ENGINE,
            source_url=f"Search engines: {', '.join(search_engines)}"
        )
        
        try:
            all_companies = []
            all_urls = set()
            
            # Process each search engine
            for engine in search_engines:
                if engine not in self.search_configs:
                    logger.warning(f"Unknown search engine: {engine}")
                    continue
                
                logger.info(f"Scraping search engine: {engine}")
                
                try:
                    engine_urls = await self._scrape_search_engine(engine, max_results_per_query)
                    all_urls.update(engine_urls)
                    logger.info(f"Found {len(engine_urls)} URLs from {engine}")
                    
                except Exception as e:
                    logger.error(f"Error scraping search engine {engine}: {e}")
                    result.errors.append(f"Error scraping {engine}: {str(e)}")
            
            # Convert URLs to companies by visiting them
            logger.info(f"Processing {len(all_urls)} unique URLs")
            
            # Limit URLs to process (to avoid overwhelming)
            url_list = list(all_urls)
            if len(url_list) > 200:
                url_list = url_list[:200]
                logger.info(f"Limited to {len(url_list)} URLs for processing")
            
            # Process URLs concurrently
            companies = await self.process_urls_concurrently(url_list, SourceType.SEARCH_ENGINE)
            
            # Deduplicate companies
            unique_companies = self._deduplicate_companies(companies)
            
            for company in unique_companies:
                result.add_company(company)
            
            result.success = True
            logger.info(f"Search scraping completed. Found {len(unique_companies)} unique companies")
            
        except Exception as e:
            logger.error(f"Error in search scraping: {e}")
            result.success = False
            result.error_message = str(e)
        
        result.processing_time = asyncio.get_event_loop().time() - start_time
        return result
    
    async def _scrape_search_engine(self, engine: str, max_results_per_query: int) -> Set[str]:
        """
        Scrape a specific search engine
        
        Args:
            engine: Name of search engine
            max_results_per_query: Maximum results per query
            
        Returns:
            Set of discovered URLs
        """
        config = self.search_configs[engine]
        urls = set()
        
        for query in self.search_queries:
            try:
                logger.info(f"Searching {engine} for: {query}")
                query_urls = await self._search_query(engine, query, max_results_per_query)
                urls.update(query_urls)
                
                # Add delay between queries to be respectful
                await asyncio.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error searching {engine} for '{query}': {e}")
        
        return urls
    
    async def _search_query(self, engine: str, query: str, max_results: int) -> List[str]:
        """
        Perform a single search query
        
        Args:
            engine: Search engine name
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of URLs from search results
        """
        config = self.search_configs[engine]
        urls = []
        
        # Calculate number of pages needed
        results_per_page = config['params'].get('num', config['params'].get('count', 10))
        max_pages = min(5, (max_results + results_per_page - 1) // results_per_page)
        
        for page in range(max_pages):
            try:
                # Build search URL
                search_url = self._build_search_url(engine, query, page)
                
                # Get search results page
                html = await self.get_html_content(search_url)
                if not html:
                    break
                
                # Extract URLs from results
                page_urls = self._extract_urls_from_search_results(html, config)
                
                if not page_urls:
                    logger.info(f"No more results found for query '{query}' on page {page + 1}")
                    break
                
                urls.extend(page_urls)
                logger.debug(f"Found {len(page_urls)} URLs on page {page + 1} for query '{query}'")
                
                # Break if we have enough results
                if len(urls) >= max_results:
                    break
                
                # Add delay between pages
                await asyncio.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error on page {page + 1} for query '{query}': {e}")
                break
        
        return urls[:max_results]
    
    def _build_search_url(self, engine: str, query: str, page: int) -> str:
        """
        Build search URL for specific engine, query, and page
        
        Args:
            engine: Search engine name
            query: Search query
            page: Page number (0-based)
            
        Returns:
            Complete search URL
        """
        config = self.search_configs[engine]
        params = config['params'].copy()
        
        # Set query
        params['q'] = query
        
        # Set page/start parameter
        if engine == 'google':
            params['start'] = page * params['num']
        elif engine == 'bing':
            params['first'] = page * params['count'] + 1
        elif engine == 'duckduckgo':
            params['s'] = page * 30  # DuckDuckGo uses 30 results per page
        
        # Build URL
        param_string = '&'.join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
        return f"{config['base_url']}?{param_string}"
    
    def _extract_urls_from_search_results(self, html: str, config: Dict) -> List[str]:
        """
        Extract URLs from search results HTML
        
        Args:
            html: HTML content of search results page
            config: Search engine configuration
            
        Returns:
            List of extracted URLs
        """
        urls = []
        soup = self.parse_html(html)
        
        # Find result containers
        results = soup.select(config['result_selector'])
        
        for result in results:
            try:
                # Extract link
                link_element = result.select_one(config['link_selector'])
                if not link_element:
                    continue
                
                url = link_element.get('href', '')
                if not url:
                    continue
                
                # Clean Google redirect URLs
                if 'google.com' in url and '/url?' in url:
                    url = self._extract_google_redirect_url(url)
                
                # Clean Bing redirect URLs
                if 'bing.com' in url and '/ck/' in url:
                    url = self._extract_bing_redirect_url(url)
                
                # Validate URL
                if self.url_validator.is_valid_url(url):
                    # Check if URL seems relevant (basic filtering)
                    if self._is_potentially_relevant_url(url):
                        urls.append(url)
                
            except Exception as e:
                logger.debug(f"Error extracting URL from result: {e}")
        
        return urls
    
    def _extract_google_redirect_url(self, redirect_url: str) -> str:
        """Extract actual URL from Google redirect"""
        try:
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'url' in params:
                return params['url'][0]
            elif 'q' in params:
                return params['q'][0]
            
        except Exception:
            pass
        
        return redirect_url
    
    def _extract_bing_redirect_url(self, redirect_url: str) -> str:
        """Extract actual URL from Bing redirect"""
        try:
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(redirect_url)
            params = parse_qs(parsed.query)
            
            if 'u' in params:
                return params['u'][0]
            
        except Exception:
            pass
        
        return redirect_url
    
    def _is_potentially_relevant_url(self, url: str) -> bool:
        """
        Check if URL is potentially relevant for healthcare companies
        
        Args:
            url: URL to check
            
        Returns:
            True if potentially relevant
        """
        url_lower = url.lower()
        
        # Skip obvious non-company domains
        skip_domains = [
            'wikipedia.org', 'linkedin.com', 'facebook.com', 'twitter.com',
            'youtube.com', 'instagram.com', 'pinterest.com', 'reddit.com',
            'quora.com', 'stackoverflow.com', 'github.com', 'medium.com',
            'news.google.com', 'bing.com', 'duckduckgo.com'
        ]
        
        for skip_domain in skip_domains:
            if skip_domain in url_lower:
                return False
        
        # Skip obvious non-company paths
        skip_paths = [
            '/search', '/category', '/tag', '/archive', '/blog',
            '/news', '/press', '/media', '/about', '/contact',
            '/privacy', '/terms', '/legal', '/help', '/support'
        ]
        
        for skip_path in skip_paths:
            if skip_path in url_lower:
                return False
        
        # Positive signals for healthcare relevance
        positive_signals = [
            'health', 'medical', 'med', 'bio', 'pharma', 'clinic',
            'hospital', 'telemedicine', 'digital-health', 'medtech',
            'biotech', 'healthcare', 'wellness', 'fitness'
        ]
        
        # Check domain and path for positive signals
        for signal in positive_signals:
            if signal in url_lower:
                return True
        
        # If no clear positive signals, include it anyway for further analysis
        return True
    
    def _deduplicate_companies(self, companies: List[CompanyInfo]) -> List[CompanyInfo]:
        """
        Remove duplicate companies based on URL and name similarity
        
        Args:
            companies: List of companies to deduplicate
            
        Returns:
            List of unique companies
        """
        seen_urls = set()
        seen_names = set()
        unique_companies = []
        
        for company in companies:
            # Normalize for comparison
            url_key = company.url.lower().strip()
            name_key = company.name.lower().strip()
            
            # Skip exact duplicates
            if url_key in seen_urls or name_key in seen_names:
                continue
            
            # Check for similar names (simple approach)
            is_similar = False
            for existing_name in seen_names:
                if self._are_names_similar(name_key, existing_name):
                    is_similar = True
                    break
            
            if is_similar:
                continue
            
            seen_urls.add(url_key)
            seen_names.add(name_key)
            unique_companies.append(company)
        
        return unique_companies
    
    def _are_names_similar(self, name1: str, name2: str) -> bool:
        """
        Check if two company names are similar
        
        Args:
            name1: First company name
            name2: Second company name
            
        Returns:
            True if names are similar
        """
        # Simple similarity check based on common words
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        # Remove common business words
        business_words = {'gmbh', 'ag', 'ltd', 'inc', 'corp', 'company', 'technologies', 'solutions'}
        words1 -= business_words
        words2 -= business_words
        
        if not words1 or not words2:
            return False
        
        # Check overlap
        overlap = len(words1 & words2)
        min_words = min(len(words1), len(words2))
        
        # Consider similar if more than 70% of words overlap
        similarity = overlap / min_words if min_words > 0 else 0
        return similarity > 0.7