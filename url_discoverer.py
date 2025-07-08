"""
URL discovery module for finding new healthcare-related URLs from various sources.
Searches Google, public directories, and healthcare news websites.
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import config
import utils


class URLDiscoverer:
    """
    Discovers new healthcare-related URLs from various online sources.
    """
    
    def __init__(self):
        """Initialize the URL discoverer with session settings."""
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        self.headers = {'User-Agent': config.USER_AGENT}
        self.discovered_urls = set()
        
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=config.MAX_CONCURRENT_REQUESTS)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def search_google(self, query: str, max_results: int = 20) -> Set[str]:
        """
        Search Google for URLs related to the query.
        Note: This uses a basic search approach. For production, consider using Google Custom Search API.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            Set[str]: Set of discovered URLs
        """
        urls = set()
        
        try:
            # Construct Google search URL
            encoded_query = quote(query + " site:*.com OR site:*.de OR site:*.eu")
            search_url = f"https://www.google.com/search?q={encoded_query}&num={min(max_results, 20)}"
            
            print(f"Searching Google for: {query}")
            
            # Add some headers to look more like a browser
            headers = {
                **self.headers,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find all links in search results
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/url?q='):
                            # Extract the actual URL from Google's redirect
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                            if actual_url.startswith('http'):
                                cleaned_url = utils.clean_url(actual_url)
                                if not utils.should_exclude_url(cleaned_url):
                                    urls.add(cleaned_url)
                
                # Add delay to be respectful to Google
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"Error searching Google for '{query}': {e}")
        
        return urls
    
    async def search_crunchbase_public(self, search_term: str = "healthcare") -> Set[str]:
        """
        Search Crunchbase public pages for healthcare companies.
        This searches publicly available Crunchbase pages.
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            Set[str]: Set of discovered URLs
        """
        urls = set()
        
        try:
            # Search Crunchbase for healthcare companies
            crunchbase_search_url = f"https://www.crunchbase.com/discover/organization.companies/field/organizations/categories/{search_term}"
            
            print(f"Searching Crunchbase for: {search_term}")
            
            async with self.session.get(crunchbase_search_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract URLs from the page content
                    discovered_urls = utils.extract_urls_from_text(content)
                    
                    # Filter for relevant healthcare URLs
                    for url in discovered_urls:
                        if utils.is_healthcare_related('', url) and not utils.should_exclude_url(url):
                            urls.add(url)
                            
        except Exception as e:
            print(f"Error searching Crunchbase: {e}")
        
        return urls
    
    async def search_healthcare_news_sites(self) -> Set[str]:
        """
        Search healthcare news and industry websites for company URLs.
        
        Returns:
            Set[str]: Set of discovered URLs
        """
        urls = set()
        
        # List of healthcare news and industry websites to search
        news_sites = [
            "https://healthcareitnews.com/",
            "https://www.mobihealthnews.com/",
            "https://www.healthtech.org/",
            "https://www.digitalhealth.net/",
            "https://healthtechmagazine.net/"
        ]
        
        try:
            for site_url in news_sites:
                try:
                    print(f"Searching healthcare news site: {site_url}")
                    
                    async with self.session.get(site_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Extract URLs from the page
                            discovered_urls = utils.extract_urls_from_text(content, site_url)
                            
                            # Filter for healthcare-related external URLs
                            for url in discovered_urls:
                                if (utils.is_healthcare_related('', url) and 
                                    not utils.should_exclude_url(url) and
                                    utils.extract_domain(url) != utils.extract_domain(site_url)):
                                    urls.add(url)
                    
                    # Be respectful with delays
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error searching {site_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in healthcare news search: {e}")
        
        return urls
    
    async def search_angellist_public(self) -> Set[str]:
        """
        Search AngelList public pages for startup URLs.
        
        Returns:
            Set[str]: Set of discovered URLs
        """
        urls = set()
        
        try:
            # Search AngelList for healthcare startups
            angellist_url = "https://angel.co/companies?markets[]=digital-health"
            
            print("Searching AngelList for healthcare startups...")
            
            async with self.session.get(angellist_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract URLs from the page
                    discovered_urls = utils.extract_urls_from_text(content)
                    
                    # Filter for relevant URLs
                    for url in discovered_urls:
                        if (utils.is_healthcare_related('', url) and 
                            not utils.should_exclude_url(url)):
                            urls.add(url)
                            
        except Exception as e:
            print(f"Error searching AngelList: {e}")
        
        return urls
    
    async def discover_from_all_sources(self) -> List[Dict]:
        """
        Discover URLs from all available sources concurrently.
        
        Returns:
            List[Dict]: List of discovered URLs with source information
        """
        print("=== URL Discovery Process ===")
        
        all_tasks = []
        
        # Google search tasks
        for query in config.GOOGLE_SEARCH_QUERIES:
            task = self.search_google(query)
            all_tasks.append(('Google SERP', task))
        
        # Other source tasks
        all_tasks.extend([
            ('Crunchbase public page', self.search_crunchbase_public('healthcare')),
            ('Crunchbase public page', self.search_crunchbase_public('digital-health')),
            ('Healthcare news sites', self.search_healthcare_news_sites()),
            ('AngelList public page', self.search_angellist_public())
        ])
        
        print(f"Starting {len(all_tasks)} discovery tasks...")
        
        # Run all tasks concurrently
        results = []
        for source, task in all_tasks:
            try:
                discovered_urls = await task
                for url in discovered_urls:
                    results.append({
                        'url': url,
                        'source': source,
                        'is_live': None,  # Will be validated later
                        'is_healthcare': None,  # Will be validated later
                        'status_code': None,
                        'title': '',
                        'description': '',
                        'error': None,
                        'response_time': None
                    })
                print(f"Found {len(discovered_urls)} URLs from {source}")
            except Exception as e:
                print(f"Error in {source}: {e}")
        
        # Remove duplicates while preserving source information
        unique_results = []
        seen_urls = set()
        
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        print(f"Total unique URLs discovered: {len(unique_results)}")
        return unique_results


async def discover_new_urls() -> List[Dict]:
    """
    Main function to discover new healthcare URLs from various sources.
    
    Returns:
        List[Dict]: List of discovered URLs with metadata
    """
    async with URLDiscoverer() as discoverer:
        return await discoverer.discover_from_all_sources()


# Example usage and testing
if __name__ == "__main__":
    print("Testing URL discoverer...")
    
    async def test_discovery():
        """Test the URL discovery functionality."""
        async with URLDiscoverer() as discoverer:
            # Test Google search
            google_results = await discoverer.search_google("digital health Germany", 5)
            print(f"Google search found {len(google_results)} URLs")
            for url in list(google_results)[:3]:
                print(f"  - {url}")
            
            # Test healthcare news sites
            news_results = await discoverer.search_healthcare_news_sites()
            print(f"Healthcare news sites found {len(news_results)} URLs")
            for url in list(news_results)[:3]:
                print(f"  - {url}")
    
    asyncio.run(test_discovery())