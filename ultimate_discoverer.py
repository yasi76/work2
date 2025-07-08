"""
ULTIMATE Healthcare URL Discovery System
Advanced multi-source discovery designed to find 2000-5000+ healthcare companies

Features:
- 100+ comprehensive healthcare databases
- Government and regulatory sources
- Advanced web scraping with pagination
- Smart filtering and deduplication
- Parallel processing for maximum speed
- Multi-language support
- Geographic and sector-specific searches
"""

import asyncio
import aiohttp
import json
import time
import random
import re
from typing import List, Dict, Set, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote, urlparse, parse_qs
import ultimate_config as uconfig
import utils
from concurrent.futures import ThreadPoolExecutor
import threading


class UltimateURLDiscoverer:
    """
    Ultimate healthcare URL discoverer using advanced techniques
    """
    
    def __init__(self):
        """Initialize with ultimate settings"""
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=20)  # Longer timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8,fr;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.discovered_urls = set()
        self.processed_domains = set()
        self.discovery_stats = {}
        self.lock = threading.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=uconfig.ULTIMATE_SETTINGS['PARALLEL_SEARCHES'],
            limit_per_host=5,
            ttl_dns_cache=300,
            use_dns_cache=True,
            ssl=False  # Disable SSL verification for problematic sites
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

    def _is_ultimate_healthcare_url(self, url: str, content: str = "") -> Tuple[bool, int]:
        """
        Ultimate healthcare URL validation with scoring system
        Returns (is_healthcare, score)
        """
        if not url or utils.should_exclude_url(url):
            return False, 0
        
        # Exclude non-company domains
        domain = utils.extract_domain(url).lower()
        excluded_domains = [
            'google.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'instagram.com',
            'youtube.com', 'wikipedia.org', 'crunchbase.com', 'angel.co', 'github.com',
            'techcrunch.com', 'forbes.com', 'bloomberg.com', 'reuters.com', 'bbc.com',
            'cnn.com', 'medium.com', 'reddit.com', 'stackoverflow.com'
        ]
        
        for excluded in excluded_domains:
            if excluded in domain:
                return False, 0
        
        # Block platform subdomains
        if any(platform in url.lower() for platform in [
            'accounts.', 'consent.', 'login.', 'signin.', 'auth.', 'oauth.',
            'api.', 'cdn.', 'mail.', 'email.', 'support.', 'help.', 'blog.',
            'news.', 'press.', 'media.', 'investor.', 'career.', 'job.'
        ]):
            return False, 0
        
        # Advanced scoring system
        healthcare_score = 0
        combined_text = f"{url} {domain} {content}".lower()
        
        # Core healthcare indicators (3 points each)
        core_keywords = [
            'health', 'medical', 'medicine', 'clinic', 'hospital', 'pharma',
            'biotech', 'medtech', 'therapeutic', 'therapy', 'patient', 'doctor',
            'physician', 'healthcare', 'telemedicine', 'telehealth', 'diagnostic'
        ]
        
        for keyword in core_keywords:
            if keyword in combined_text:
                healthcare_score += 3
                
        # Multi-language healthcare terms (2 points each)
        multilang_keywords = [
            'gesundheit', 'medizin', 'arzt', 'klinik', 'krankenhaus',  # German
            'santé', 'médecine', 'médecin', 'clinique', 'hôpital',     # French
            'gezondheid', 'geneeskunde', 'arts', 'ziekenhuis',         # Dutch
            'salud', 'medicina', 'médico', 'clínica', 'hospital',      # Spanish
            'salute', 'medicina', 'medico', 'clinica', 'ospedale'      # Italian
        ]
        
        for keyword in multilang_keywords:
            if keyword in combined_text:
                healthcare_score += 2
                
        # Technology + healthcare combinations (4 points each)
        tech_health_combos = [
            'digital health', 'health tech', 'medical ai', 'healthcare ai',
            'digital therapeutics', 'health analytics', 'medical device',
            'clinical software', 'medical technology', 'health platform'
        ]
        
        for combo in tech_health_combos:
            if combo in combined_text:
                healthcare_score += 4
                
        # Company indicators (1 point each)
        company_indicators = [
            'gmbh', 'ltd', 'inc', 'corp', 'ag', 'sa', 'bv', 'ab', 'oy',
            'company', 'solutions', 'technologies', 'systems', 'platform'
        ]
        
        for indicator in company_indicators:
            if indicator in combined_text:
                healthcare_score += 1
                
        # Determine if healthcare based on score
        min_score = uconfig.ULTIMATE_SETTINGS['MIN_HEALTHCARE_SCORE']
        is_healthcare = healthcare_score >= min_score
        
        return is_healthcare, healthcare_score

    async def _advanced_web_scraping(self, url: str, max_depth: int = 3) -> Set[str]:
        """
        Advanced web scraping with pagination and deep crawling
        """
        discovered_urls = set()
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return discovered_urls
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract all URLs from the page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = urljoin(url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Clean and validate URL
                    cleaned_url = utils.clean_url(full_url)
                    if cleaned_url:
                        is_healthcare, score = self._is_ultimate_healthcare_url(cleaned_url, link.get_text())
                        if is_healthcare:
                            discovered_urls.add(cleaned_url)
                
                # Look for pagination and "load more" functionality
                if max_depth > 0:
                    pagination_urls = await self._find_pagination_urls(soup, url)
                    
                    for page_url in pagination_urls[:5]:  # Limit pagination crawling
                        try:
                            sub_urls = await self._advanced_web_scraping(page_url, max_depth - 1)
                            discovered_urls.update(sub_urls)
                            await asyncio.sleep(0.5)  # Rate limiting
                        except Exception:
                            continue
                
                # Look for member directories, company lists, etc.
                directory_links = await self._find_directory_links(soup, url)
                for dir_url in directory_links[:3]:
                    try:
                        sub_urls = await self._advanced_web_scraping(dir_url, max_depth - 1)
                        discovered_urls.update(sub_urls)
                        await asyncio.sleep(0.5)
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
        return discovered_urls

    async def _find_pagination_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find pagination URLs (next, page 2, 3, etc.)
        """
        pagination_urls = []
        
        # Common pagination patterns
        pagination_selectors = [
            'a[href*="page"]',
            'a[href*="Page"]', 
            'a[href*="next"]',
            'a[href*="Next"]',
            'a.next',
            'a.pagination',
            'a[aria-label*="Next"]',
            'a[aria-label*="Page"]'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links[:3]:  # Limit to avoid infinite crawling
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    pagination_urls.append(full_url)
        
        # Look for numbered pagination
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Check if it's a numbered page
            if text.isdigit() and int(text) <= 10:  # Pages 1-10 only
                full_url = urljoin(base_url, href)
                pagination_urls.append(full_url)
        
        return list(set(pagination_urls))

    async def _find_directory_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find links to member directories, company lists, etc.
        """
        directory_urls = []
        
        # Look for directory-related links
        directory_keywords = [
            'member', 'company', 'companies', 'directory', 'list', 'portfolio',
            'partners', 'clients', 'participants', 'exhibitor', 'speaker',
            'mitglieder', 'unternehmen', 'firmen',  # German
            'membres', 'entreprises', 'sociétés',    # French
            'leden', 'bedrijven'                     # Dutch
        ]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().lower()
            
            for keyword in directory_keywords:
                if keyword in text or keyword in href.lower():
                    full_url = urljoin(base_url, href)
                    directory_urls.append(full_url)
                    break
        
        return list(set(directory_urls))

    async def search_government_databases(self) -> Set[str]:
        """
        Search government and regulatory databases
        """
        print("🏛️  Searching government & regulatory databases...")
        urls = set()
        
        for database_url in uconfig.ULTIMATE_HEALTHCARE_SOURCES['government_databases']:
            try:
                print(f"   Processing: {database_url}")
                
                discovered_urls = await self._advanced_web_scraping(
                    database_url, 
                    max_depth=uconfig.ULTIMATE_SETTINGS['CRAWL_DEPTH']
                )
                urls.update(discovered_urls)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(1, 2))
                
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print(f"   Found {len(urls)} URLs from government databases")
        return urls

    async def search_industry_directories(self) -> Set[str]:
        """
        Search all industry directories (medtech, pharma, digital health)
        """
        print("🏭 Searching industry directories...")
        urls = set()
        
        # Combine all directory types
        all_directories = []
        all_directories.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['medtech_directories'])
        all_directories.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['pharma_directories'])
        all_directories.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['digital_health_directories'])
        all_directories.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['healthcare_chambers'])
        
        # Process directories in parallel
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def process_directory(directory_url):
            async with semaphore:
                try:
                    print(f"   Processing: {directory_url}")
                    
                    discovered_urls = await self._advanced_web_scraping(
                        directory_url,
                        max_depth=uconfig.ULTIMATE_SETTINGS['CRAWL_DEPTH']
                    )
                    
                    return discovered_urls
                    
                except Exception as e:
                    print(f"   Error: {e}")
                    return set()
        
        # Run directory searches in parallel
        tasks = [process_directory(url) for url in all_directories]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, set):
                urls.update(result)
        
        print(f"   Found {len(urls)} URLs from industry directories")
        return urls

    async def search_startup_ecosystems(self) -> Set[str]:
        """
        Search startup databases and accelerator portfolios
        """
        print("🚀 Searching startup ecosystems...")
        urls = set()
        
        # Combine startup sources
        startup_sources = []
        startup_sources.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['startup_databases'])
        startup_sources.extend(uconfig.ULTIMATE_HEALTHCARE_SOURCES['accelerator_portfolios'])
        
        for source_url in startup_sources:
            try:
                print(f"   Processing: {source_url}")
                
                discovered_urls = await self._advanced_web_scraping(
                    source_url,
                    max_depth=2  # Slightly less depth for startup sites
                )
                urls.update(discovered_urls)
                
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print(f"   Found {len(urls)} URLs from startup ecosystems")
        return urls

    async def search_research_institutions(self) -> Set[str]:
        """
        Search research institutions and university spin-offs
        """
        print("🎓 Searching research institutions...")
        urls = set()
        
        for research_url in uconfig.ULTIMATE_HEALTHCARE_SOURCES['research_institutions']:
            try:
                print(f"   Processing: {research_url}")
                
                discovered_urls = await self._advanced_web_scraping(
                    research_url,
                    max_depth=2
                )
                urls.update(discovered_urls)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print(f"   Found {len(urls)} URLs from research institutions")
        return urls

    async def search_conference_exhibitors(self) -> Set[str]:
        """
        Search healthcare conference exhibitor lists
        """
        print("🏢 Searching conference exhibitors...")
        urls = set()
        
        for conference_url in uconfig.ULTIMATE_HEALTHCARE_SOURCES['conference_directories']:
            try:
                print(f"   Processing: {conference_url}")
                
                discovered_urls = await self._advanced_web_scraping(
                    conference_url,
                    max_depth=2
                )
                urls.update(discovered_urls)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print(f"   Found {len(urls)} URLs from conferences")
        return urls

    async def search_investment_sources(self) -> Set[str]:
        """
        Search investment and funding databases
        """
        print("💰 Searching investment sources...")
        urls = set()
        
        for investment_url in uconfig.ULTIMATE_HEALTHCARE_SOURCES['investment_databases']:
            try:
                print(f"   Processing: {investment_url}")
                
                discovered_urls = await self._advanced_web_scraping(
                    investment_url,
                    max_depth=2
                )
                urls.update(discovered_urls)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"   Error: {e}")
                continue
        
        print(f"   Found {len(urls)} URLs from investment sources")
        return urls

    async def comprehensive_ultimate_discovery(self) -> List[Dict]:
        """
        Run comprehensive ultimate discovery using all advanced methods
        """
        print("🎯 ULTIMATE Healthcare URL Discovery Process")
        print("=" * 60)
        print(f"Target: {uconfig.ULTIMATE_SETTINGS['MAX_TOTAL_URLS_TARGET']:,} healthcare companies")
        print(f"Sources: {sum(len(sources) for sources in uconfig.ULTIMATE_HEALTHCARE_SOURCES.values())} databases")
        print(f"Cities: {len(uconfig.ULTIMATE_EUROPEAN_CITIES)} European cities")
        print(f"Sectors: {len(uconfig.ULTIMATE_HEALTHCARE_SECTORS)} healthcare specialties")
        print()
        
        all_urls = set()
        
        # Phase 1: Government & Regulatory Databases (Highest Quality)
        try:
            gov_urls = await self.search_government_databases()
            all_urls.update(gov_urls)
            print(f"📊 Phase 1 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 1 error: {e}")
        
        # Phase 2: Industry Directories & Chambers
        try:
            industry_urls = await self.search_industry_directories()
            all_urls.update(industry_urls)
            print(f"📊 Phase 2 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 2 error: {e}")
        
        # Phase 3: Startup Ecosystems & Accelerators
        try:
            startup_urls = await self.search_startup_ecosystems()
            all_urls.update(startup_urls)
            print(f"📊 Phase 3 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 3 error: {e}")
        
        # Phase 4: Research Institutions
        try:
            research_urls = await self.search_research_institutions()
            all_urls.update(research_urls)
            print(f"📊 Phase 4 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 4 error: {e}")
        
        # Phase 5: Conference Exhibitors
        try:
            conference_urls = await self.search_conference_exhibitors()
            all_urls.update(conference_urls)
            print(f"📊 Phase 5 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 5 error: {e}")
        
        # Phase 6: Investment & Funding Sources
        try:
            investment_urls = await self.search_investment_sources()
            all_urls.update(investment_urls)
            print(f"📊 Phase 6 complete: {len(all_urls):,} total URLs")
        except Exception as e:
            print(f"Phase 6 error: {e}")
        
        # Convert to result format with enhanced scoring
        results = []
        print(f"\n🔍 Final validation and scoring...")
        
        for url in all_urls:
            is_healthcare, score = self._is_ultimate_healthcare_url(url)
            if is_healthcare:
                results.append({
                    'url': url,
                    'source': 'Ultimate Discovery',
                    'healthcare_score': score,
                    'is_live': None,
                    'is_healthcare': None,
                    'status_code': None,
                    'title': '',
                    'description': '',
                    'error': None,
                    'response_time': None
                })
        
        # Sort by healthcare score (highest first)
        results.sort(key=lambda x: x['healthcare_score'], reverse=True)
        
        print(f"\n🎉 ULTIMATE DISCOVERY COMPLETE!")
        print("=" * 60)
        print(f"📊 DISCOVERY STATISTICS:")
        print(f"   Total URLs discovered: {len(all_urls):,}")
        print(f"   Healthcare URLs (filtered): {len(results):,}")
        print(f"   Average healthcare score: {sum(r['healthcare_score'] for r in results) / len(results):.1f}")
        print(f"   Discovery efficiency: {len(results)/len(all_urls)*100:.1f}%")
        print()
        print(f"🎯 TARGET ACHIEVEMENT:")
        target = uconfig.ULTIMATE_SETTINGS['MAX_TOTAL_URLS_TARGET']
        if len(results) >= target:
            print(f"   ✅ SUCCESS! Found {len(results):,} URLs (target: {target:,})")
        elif len(results) >= target * 0.5:
            print(f"   🟡 GOOD! Found {len(results):,} URLs (target: {target:,})")
        else:
            print(f"   🔴 PARTIAL: Found {len(results):,} URLs (target: {target:,})")
        
        print(f"\n⏭️  Next: URL validation and final filtering")
        
        return results


async def discover_ultimate_healthcare_urls() -> List[Dict]:
    """
    Main function to run ultimate healthcare URL discovery
    """
    async with UltimateURLDiscoverer() as discoverer:
        return await discoverer.comprehensive_ultimate_discovery()


if __name__ == "__main__":
    print("🎯 Testing Ultimate Healthcare URL Discovery...")
    
    async def test_ultimate():
        results = await discover_ultimate_healthcare_urls()
        print(f"\n✅ Test complete! Found {len(results):,} healthcare URLs")
        
        # Show top 10 results
        print(f"\n🏆 Top 10 Healthcare URLs (by score):")
        for i, result in enumerate(results[:10], 1):
            print(f"{i:2d}. {result['url']} (score: {result['healthcare_score']})")
    
    asyncio.run(test_ultimate())