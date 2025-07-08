"""
Enhanced URL Discovery Module - Designed to find 500-2000+ healthcare companies
Uses comprehensive multi-language searches, better sources, and deeper crawling
"""

import asyncio
import aiohttp
import json
import time
import random
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote, urlparse
import enhanced_config as econfig
import utils

class EnhancedURLDiscoverer:
    """
    Enhanced discoverer that finds hundreds/thousands of healthcare URLs
    """
    
    def __init__(self):
        """Initialize with enhanced settings"""
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=15)  # Longer timeout
        self.headers = {'User-Agent': econfig.ENHANCED_SETTINGS.get('USER_AGENT', 
                       'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')}
        self.discovered_urls = set()
        self.processed_domains = set()
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=econfig.ENHANCED_SETTINGS['PARALLEL_SEARCHES']
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def enhanced_google_search(self, query: str, max_results: int = 100) -> Set[str]:
        """
        Enhanced Google search with better result extraction
        """
        urls = set()
        
        try:
            # Multiple search variations
            search_variations = [
                query,
                f"{query} startup",
                f"{query} company",
                f"{query} platform",
                f"{query} 2024",
                f"{query} funding",
            ]
            
            for variation in search_variations[:3]:  # Limit to avoid being blocked
                try:
                    encoded_query = quote(f"{variation} site:*.com OR site:*.de OR site:*.eu OR site:*.fr OR site:*.nl")
                    search_url = f"https://www.google.com/search?q={encoded_query}&num=20"
                    
                    headers = {
                        **self.headers,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5,de;q=0.3,fr;q=0.2',
                    }
                    
                    async with self.session.get(search_url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Better URL extraction
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                
                                # Extract actual URLs from Google redirects
                                if '/url?q=' in href:
                                    actual_url = href.split('/url?q=')[1].split('&')[0]
                                elif href.startswith('http'):
                                    actual_url = href
                                else:
                                    continue
                                
                                if actual_url.startswith('http'):
                                    cleaned_url = utils.clean_url(actual_url)
                                    if self._is_relevant_healthcare_url(cleaned_url):
                                        urls.add(cleaned_url)
                    
                    # Random delay to avoid being blocked
                    delay = random.uniform(
                        econfig.ENHANCED_SETTINGS['SEARCH_DELAY_MIN'],
                        econfig.ENHANCED_SETTINGS['SEARCH_DELAY_MAX']
                    )
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    print(f"Error in search variation '{variation}': {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in enhanced Google search for '{query}': {e}")
        
        return urls

    async def search_startup_databases(self) -> Set[str]:
        """
        Search comprehensive startup databases
        """
        urls = set()
        
        for database_url in econfig.ENHANCED_DISCOVERY_SOURCES['startup_databases']:
            try:
                print(f"Searching startup database: {database_url}")
                
                async with self.session.get(database_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract all URLs from the page
                        discovered_urls = utils.extract_urls_from_text(content)
                        
                        # Filter for healthcare-related URLs
                        for url in discovered_urls:
                            if self._is_relevant_healthcare_url(url):
                                urls.add(url)
                        
                        # Deep crawling - follow pagination or "load more" links
                        if econfig.ENHANCED_SETTINGS['ENABLE_DEEP_CRAWLING']:
                            deep_urls = await self._deep_crawl_page(content, database_url)
                            urls.update(deep_urls)
                
                await asyncio.sleep(1)  # Respectful delay
                
            except Exception as e:
                print(f"Error searching database {database_url}: {e}")
                continue
        
        return urls

    async def search_by_geography(self) -> Set[str]:
        """
        Search by specific European cities and regions
        """
        urls = set()
        
        city_queries = []
        for city in econfig.EUROPEAN_HEALTHCARE_HUBS:
            city_queries.extend([
                f"health tech startups {city}",
                f"digital health companies {city}",
                f"medical technology {city}",
                f"biotech startups {city}",
            ])
        
        # Limit to avoid overwhelming searches
        selected_queries = random.sample(city_queries, min(50, len(city_queries)))
        
        for query in selected_queries:
            try:
                search_results = await self.enhanced_google_search(query, max_results=20)
                urls.update(search_results)
                
                # Small delay between searches
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error in geographic search '{query}': {e}")
                continue
        
        return urls

    async def search_by_sector(self) -> Set[str]:
        """
        Search by specific healthcare sectors
        """
        urls = set()
        
        for sector, terms in econfig.HEALTHCARE_SECTORS.items():
            for term in terms:
                try:
                    # Search with European context
                    query = f"{term} companies Europe"
                    search_results = await self.enhanced_google_search(query, max_results=30)
                    urls.update(search_results)
                    
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    print(f"Error in sector search '{term}': {e}")
                    continue
        
        return urls

    async def search_multilingual(self) -> Set[str]:
        """
        Search using German, French, Dutch, and other European languages
        """
        urls = set()
        
        # German searches
        german_queries = [
            'digitale Gesundheit Unternehmen',
            'HealthTech Startups Deutschland',
            'Medizintechnik Firmen Berlin',
            'Telemedizin Anbieter Deutschland',
            'E-Health Startups München',
        ]
        
        # French searches  
        french_queries = [
            'entreprises santé numérique France',
            'startups health tech Paris',
            'télémédecine sociétés France',
        ]
        
        # Dutch searches
        dutch_queries = [
            'digitale zorg bedrijven Nederland',
            'health tech startups Amsterdam',
        ]
        
        all_multilingual = german_queries + french_queries + dutch_queries
        
        for query in all_multilingual:
            try:
                search_results = await self.enhanced_google_search(query, max_results=25)
                urls.update(search_results)
                
                await asyncio.sleep(0.4)
                
            except Exception as e:
                print(f"Error in multilingual search '{query}': {e}")
                continue
        
        return urls

    async def search_investment_news(self) -> Set[str]:
        """
        Search investment and news sites for healthcare companies
        """
        urls = set()
        
        news_sites = econfig.ENHANCED_DISCOVERY_SOURCES['healthcare_industry_sites']
        
        for site in news_sites:
            try:
                print(f"Searching news site: {site}")
                
                async with self.session.get(site) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract URLs mentioned in articles
                        discovered_urls = utils.extract_urls_from_text(content)
                        
                        for url in discovered_urls:
                            if self._is_relevant_healthcare_url(url):
                                urls.add(url)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error searching news site {site}: {e}")
                continue
        
        return urls

    def _is_relevant_healthcare_url(self, url: str) -> bool:
        """
        Enhanced relevance checking with multi-language support
        """
        if not url or utils.should_exclude_url(url):
            return False
        
        # Check domain for healthcare terms
        domain = utils.extract_domain(url).lower()
        
        # Enhanced keyword matching
        for keyword in econfig.ENHANCED_HEALTHCARE_KEYWORDS:
            if keyword.lower() in url.lower() or keyword.lower() in domain:
                return True
        
        return False

    async def _deep_crawl_page(self, content: str, base_url: str) -> Set[str]:
        """
        Deep crawl a page to find more company URLs
        """
        urls = set()
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for pagination or "load more" buttons
            pagination_links = soup.find_all('a', href=True)
            
            for link in pagination_links[:5]:  # Limit depth
                href = link.get('href', '')
                if any(word in href.lower() for word in ['page', 'more', 'next', 'companies']):
                    full_url = urljoin(base_url, href)
                    
                    try:
                        async with self.session.get(full_url) as response:
                            if response.status == 200:
                                sub_content = await response.text()
                                sub_urls = utils.extract_urls_from_text(sub_content)
                                
                                for url in sub_urls:
                                    if self._is_relevant_healthcare_url(url):
                                        urls.add(url)
                        
                        await asyncio.sleep(0.5)
                        
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"Error in deep crawling: {e}")
        
        return urls

    async def comprehensive_discovery(self) -> List[Dict]:
        """
        Run comprehensive discovery using all enhanced methods
        """
        print("=== ENHANCED URL Discovery Process ===")
        print("Targeting 500-2000+ healthcare companies across Europe")
        
        all_urls = set()
        
        # 1. Enhanced Google searches with comprehensive queries
        print("\n1. Running enhanced Google searches...")
        for i, query in enumerate(econfig.ENHANCED_SEARCH_QUERIES):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(econfig.ENHANCED_SEARCH_QUERIES)} queries")
            
            try:
                urls = await self.enhanced_google_search(query)
                all_urls.update(urls)
                
                # Progress update
                if len(all_urls) % 100 == 0:
                    print(f"  Found {len(all_urls)} URLs so far...")
                
            except Exception as e:
                print(f"  Error in query '{query}': {e}")
                continue
        
        print(f"Google searches found: {len(all_urls)} URLs")
        
        # 2. Search startup databases
        print("\n2. Searching startup databases...")
        try:
            database_urls = await self.search_startup_databases()
            all_urls.update(database_urls)
            print(f"Database searches found: {len(database_urls)} additional URLs")
        except Exception as e:
            print(f"Error in database search: {e}")
        
        # 3. Geographic searches
        print("\n3. Running geographic searches...")
        try:
            geo_urls = await self.search_by_geography()
            all_urls.update(geo_urls)
            print(f"Geographic searches found: {len(geo_urls)} additional URLs")
        except Exception as e:
            print(f"Error in geographic search: {e}")
        
        # 4. Sector-specific searches
        print("\n4. Running sector-specific searches...")
        try:
            sector_urls = await self.search_by_sector()
            all_urls.update(sector_urls)
            print(f"Sector searches found: {len(sector_urls)} additional URLs")
        except Exception as e:
            print(f"Error in sector search: {e}")
        
        # 5. Multilingual searches
        print("\n5. Running multilingual searches...")
        try:
            multilingual_urls = await self.search_multilingual()
            all_urls.update(multilingual_urls)
            print(f"Multilingual searches found: {len(multilingual_urls)} additional URLs")
        except Exception as e:
            print(f"Error in multilingual search: {e}")
        
        # 6. Investment and news sites
        print("\n6. Searching investment and news sites...")
        try:
            news_urls = await self.search_investment_news()
            all_urls.update(news_urls)
            print(f"News searches found: {len(news_urls)} additional URLs")
        except Exception as e:
            print(f"Error in news search: {e}")
        
        # Convert to result format
        results = []
        for url in all_urls:
            results.append({
                'url': url,
                'source': 'Enhanced Discovery',
                'is_live': None,
                'is_healthcare': None,
                'status_code': None,
                'title': '',
                'description': '',
                'error': None,
                'response_time': None
            })
        
        print(f"\n🎉 ENHANCED DISCOVERY COMPLETE!")
        print(f"Total unique URLs discovered: {len(results)}")
        print(f"Expected validation rate: 60-80% live")
        print(f"Expected healthcare rate: 40-60% healthcare-related")
        print(f"Estimated final results: {int(len(results) * 0.6 * 0.5)}-{int(len(results) * 0.8 * 0.6)} validated healthcare URLs")
        
        return results


async def discover_enhanced_urls() -> List[Dict]:
    """
    Main function to run enhanced URL discovery
    """
    async with EnhancedURLDiscoverer() as discoverer:
        return await discoverer.comprehensive_discovery()


if __name__ == "__main__":
    print("Testing Enhanced URL Discovery...")
    
    async def test_enhanced():
        results = await discover_enhanced_urls()
        print(f"\nTest complete! Found {len(results)} URLs")
        
        # Show sample results
        for i, result in enumerate(results[:10]):
            print(f"{i+1}. {result['url']}")
    
    asyncio.run(test_enhanced())