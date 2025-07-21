#!/usr/bin/env python3
"""
IMPROVED STARTUP DISCOVERY SYSTEM
Addresses all major issues from the feedback:
- Robust search with fallbacks (Google → Bing → DuckDuckGo)
- Deep pagination support for startup directories
- URL health checks and validation
- Enhanced GitHub discovery with API tokens
- Separated output files by confidence level
- Progress bars and comprehensive logging
"""

import requests
import json
import csv
import time
import re
import os
from datetime import datetime
from typing import List, Dict, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
import random
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedStartupDiscovery:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        self.delay = 2
        self.found_urls = set()
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.all_discovered_urls = {
            'verified': [],
            'discovered': [],
            'generated': []
        }
        
        # Search engine success tracking for smart fallback ranking
        self.engine_success_rates = {
            'google': {'success': 0, 'attempts': 0},
            'bing': {'success': 0, 'attempts': 0},
            'duckduckgo': {'success': 0, 'attempts': 0}
        }
        
        # Health-related keywords for validation
        self.health_keywords = [
            'health', 'medical', 'medicine', 'clinic', 'hospital', 'patient', 
            'therapy', 'treatment', 'diagnostic', 'pharma', 'biotech',
            'telemedicine', 'digital health', 'e-health', 'medtech',
            'therapeutics', 'healthcare', 'wellness', 'rehabilitation',
            'ai', 'artificial intelligence', 'data analytics', 'platform'
        ]

    def canonicalize_domain(self, url: str) -> str:
        """Canonicalize domain to avoid duplicates (remove www, trailing paths, etc.)"""
        try:
            parsed = urlparse(url)
            # Remove www. prefix
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Use https as default scheme
            scheme = 'https'
            
            # Return canonical URL (domain only, no paths)
            canonical_url = f"{scheme}://{domain}"
            return canonical_url
        except Exception:
            return url
    
    def smart_delay(self, base_delay: float = None) -> None:
        """Enhanced throttling with random jitter to avoid bot detection"""
        if base_delay is None:
            base_delay = self.delay
        
        # Add random jitter (±25% of base delay)
        jitter = random.uniform(base_delay * 0.75, base_delay * 1.25)
        time.sleep(jitter)

    def check_url_health(self, url: str, timeout: int = 5) -> Dict:
        """Check if URL is alive and accessible"""
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            return {
                'is_alive': True,
                'status_code': response.status_code,
                'final_url': response.url,
                'content_length': len(response.content) if response.content else 0
            }
        except Exception as e:
            logger.warning(f"Skipped broken: {url} - {str(e)}")
            return {
                'is_alive': False,
                'status_code': None,
                'final_url': url,
                'error': str(e)
            }

    def validate_health_content(self, url: str) -> Dict:
        """Validate if the page content is health/med-related"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Extract text content
                text_content = soup.get_text().lower()
                
                # Count health keywords
                health_score = sum(1 for keyword in self.health_keywords if keyword in text_content)
                
                # Extract meta description for additional context
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                meta_content = meta_desc.get('content', '') if meta_desc else ''
                
                # Detect country from domain or content
                domain = urlparse(url).netloc
                country = self.detect_country(domain, text_content)
                
                return {
                    'health_score': health_score,
                    'is_health_related': health_score >= 3,
                    'meta_description': meta_content[:200],
                    'country': country,
                    'discovered_at': datetime.now().isoformat()
                }
        except Exception as e:
            logger.warning(f"Could not validate content for {url}: {str(e)}")
            
        return {
            'health_score': 0,
            'is_health_related': False,
            'meta_description': '',
            'country': 'Unknown',
            'discovered_at': datetime.now().isoformat()
        }

    def detect_country(self, domain: str, content: str) -> str:
        """Detect country from domain or content"""
        # Domain-based detection
        if '.de' in domain or 'germany' in domain:
            return 'Germany'
        elif '.fr' in domain or 'france' in domain:
            return 'France'
        elif '.uk' in domain or '.co.uk' in domain:
            return 'United Kingdom'
        elif '.nl' in domain or 'netherlands' in domain:
            return 'Netherlands'
        elif '.ch' in domain or 'switzerland' in domain:
            return 'Switzerland'
        elif '.se' in domain or 'sweden' in domain:
            return 'Sweden'
        elif '.dk' in domain or 'denmark' in domain:
            return 'Denmark'
        elif '.at' in domain or 'austria' in domain:
            return 'Austria'
        elif '.be' in domain or 'belgium' in domain:
            return 'Belgium'
        elif '.it' in domain or 'italy' in domain:
            return 'Italy'
        elif '.es' in domain or 'spain' in domain:
            return 'Spain'
        elif '.eu' in domain:
            return 'Europe'
        
        # Content-based detection (simple)
        country_indicators = {
            'germany': ['deutschland', 'german', 'berlin', 'munich', 'hamburg'],
            'france': ['france', 'french', 'paris', 'lyon'],
            'uk': ['london', 'british', 'england', 'scotland'],
            'netherlands': ['amsterdam', 'dutch', 'holland'],
            'switzerland': ['zurich', 'swiss', 'bern'],
            'sweden': ['stockholm', 'swedish'],
            'denmark': ['copenhagen', 'danish'],
            'austria': ['vienna', 'austrian'],
        }
        
        for country, indicators in country_indicators.items():
            if any(indicator in content for indicator in indicators):
                return country.title()
        
        return 'Europe'

    def get_search_engine_priority(self) -> List[str]:
        """Get search engines ordered by success rate (smart fallback ranking)"""
        engines = []
        for engine, stats in self.engine_success_rates.items():
            if stats['attempts'] > 0:
                success_rate = stats['success'] / stats['attempts']
                engines.append((engine, success_rate))
            else:
                # Default order for engines with no attempts
                engines.append((engine, 0.5))
        
        # Sort by success rate (descending)
        engines.sort(key=lambda x: x[1], reverse=True)
        return [engine[0] for engine in engines]
    
    def search_with_fallbacks(self, query: str, num_results: int = 20) -> List[str]:
        """Search with multiple search engines using smart fallback ranking"""
        logger.info(f"🔍 Searching for: '{query}'")
        
        # Get engines in priority order based on success rates
        engine_priority = self.get_search_engine_priority()
        
        search_methods = {
            'google': self.search_google,
            'bing': self.search_bing,
            'duckduckgo': self.search_duckduckgo
        }
        
        for engine in engine_priority:
            try:
                logger.info(f"  Trying {engine.title()}...")
                urls = search_methods[engine](query, num_results)
                if urls:
                    logger.info(f"  ✅ {engine.title()} found {len(urls)} results")
                    self.engine_success_rates[engine]['success'] += 1
                    return urls
                else:
                    logger.warning(f"  ⚠️ {engine.title()} returned no results")
            except Exception as e:
                logger.error(f"  ❌ {engine.title()} failed: {str(e)}")
            finally:
                self.engine_success_rates[engine]['attempts'] += 1
        
        logger.error("  ❌ All search engines failed")
        return []

    def search_google(self, query: str, num_results: int = 20) -> List[str]:
        """Improved Google search with better selectors"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            self.smart_delay()
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # Multiple selector strategies for robustness
            selectors_to_try = [
                'div.g a[href^="http"]',  # Modern Google
                'div.r a[href^="http"]',  # Classic Google
                'h3 a[href^="http"]',     # Header links
                'a[data-ved][href^="http"]',  # Data-ved links
                '.yuRUbf a[href^="http"]',     # New Google layout
                '.tF2Cxc a[href^="http"]'      # Another new layout
            ]
            
            for selector in selectors_to_try:
                if urls:
                    break
                    
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and href.startswith('http'):
                        clean_url = href.split('&')[0]
                        if clean_url not in urls:
                            urls.append(clean_url)
            
            return self.filter_search_results(urls)
            
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []

    def search_bing(self, query: str, num_results: int = 20) -> List[str]:
        """Bing search as fallback"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.bing.com/search?q={encoded_query}&count={num_results}"
            
            self.smart_delay()
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # Bing selectors
            selectors = [
                'h2 a[href^="http"]',
                '.b_algo h2 a[href^="http"]',
                '.b_title a[href^="http"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and href.startswith('http'):
                        if href not in urls:
                            urls.append(href)
            
            return self.filter_search_results(urls)
            
        except Exception as e:
            logger.error(f"Bing search failed: {str(e)}")
            return []

    def search_duckduckgo(self, query: str, num_results: int = 20) -> List[str]:
        """DuckDuckGo search as second fallback"""
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            self.smart_delay()
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            urls = []
            
            # DuckDuckGo selectors
            selectors = [
                '.result__a[href^="http"]',
                'a.result__url[href^="http"]',
                'h2 a[href^="http"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and href.startswith('http'):
                        if href not in urls:
                            urls.append(href)
            
            return self.filter_search_results(urls[:num_results])
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            return []

    def filter_search_results(self, urls: List[str]) -> List[str]:
        """Filter out irrelevant URLs from search results"""
        exclude_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'wikipedia.org', 'crunchbase.com', 'angel.co', 'techcrunch.com',
            'forbes.com', 'reuters.com', 'bloomberg.com', 'bing.com', 'duckduckgo.com'
        ]
        
        startup_urls = []
        for url in urls:
            domain = urlparse(url).netloc.lower()
            if not any(excluded in domain for excluded in exclude_domains):
                if any(tld in domain for tld in ['.com', '.de', '.io', '.ai', '.health', '.tech', '.app', '.eu', '.co', '.fr', '.uk', '.nl', '.ch', '.se', '.dk', '.at', '.be', '.it', '.es']):
                    startup_urls.append(url)
        
        return startup_urls

    def scrape_startup_directory_with_pagination(self, base_url: str, directory_name: str, max_pages: int = 10) -> List[Dict]:
        """Scrape startup directories with pagination support"""
        logger.info(f"🔍 Scraping {directory_name} with pagination (up to {max_pages} pages)...")
        results = []
        
        for page in tqdm(range(1, max_pages + 1), desc=f"Scraping {directory_name}"):
            try:
                # Try different pagination patterns
                page_urls = [
                    f"{base_url}?page={page}",
                    f"{base_url}&page={page}",
                    f"{base_url}/page/{page}",
                    f"{base_url}?p={page}",
                    f"{base_url}&p={page}"
                ]
                
                page_results = []
                for page_url in page_urls:
                    try:
                        self.smart_delay()
                        response = self.session.get(page_url, timeout=15)
                        response.raise_for_status()
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find links that look like startup websites
                        startup_patterns = [
                            r'https?://[^/]+\.(?:com|de|io|co|ai|health|tech|app|eu|fr|uk|nl|ch|se|dk|at|be|it|es)/?'
                        ]
                        
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if not href:
                                continue
                                
                            # Convert relative URLs to absolute
                            if href.startswith('/'):
                                href = urljoin(page_url, href)
                            
                            # Check if it matches startup patterns
                            for pattern in startup_patterns:
                                if re.match(pattern, href):
                                    domain = urlparse(href).netloc
                                    # Filter out directory sites and common platforms
                                    exclude_domains = ['startbase.com', 'eu-startups.com', 'startup-db.com', 
                                                     'crunchbase.com', 'linkedin.com', 'twitter.com', 'facebook.com',
                                                     'google.com', 'youtube.com']
                                    
                                    if not any(excluded in domain for excluded in exclude_domains):
                                        clean_url = f"https://{domain}"
                                        canonical_url = self.canonicalize_domain(clean_url)
                                        if canonical_url not in [r['url'] for r in page_results]:
                                            page_results.append({
                                                'url': canonical_url,
                                                'source': f'{directory_name} (Page {page})',
                                                'confidence': 7,
                                                'category': 'Directory Listed'
                                            })
                        
                        if page_results:
                            break  # Found results with this pagination pattern
                            
                    except Exception as e:
                        continue  # Try next pagination pattern
                
                if not page_results:
                    logger.info(f"  No results found on page {page}, stopping pagination")
                    break
                
                results.extend(page_results)
                logger.info(f"  Page {page}: Found {len(page_results)} URLs")
                
            except Exception as e:
                logger.error(f"Error scraping page {page} of {directory_name}: {str(e)}")
                break
        
        logger.info(f"✅ Found {len(results)} total URLs from {directory_name}")
        return results

    def search_github_with_token(self) -> List[Dict]:
        """Enhanced GitHub discovery with API token support"""
        logger.info("🔍 Searching GitHub for health tech projects...")
        results = []
        
        # Use more queries with API token
        github_queries = [
            'digital health startup',
            'telemedicine platform',
            'healthtech company',
            'medical AI startup',
            'health app germany',
            'european health tech'
        ]
        
        # Use all 6 queries if we have a token, otherwise limit to 2
        query_limit = len(github_queries) if self.github_token else 2
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
            logger.info(f"  ✅ Using GitHub API token for enhanced rate limits")
        else:
            logger.warning(f"  ⚠️ No GitHub token found, using anonymous access (limited to {query_limit} queries)")
        
        for i, query in enumerate(tqdm(github_queries[:query_limit], desc="GitHub queries")):
            try:
                self.smart_delay(1.0)  # Respectful delay with jitter
                api_url = f"https://api.github.com/search/repositories?q={query.replace(' ', '+')}&sort=stars&order=desc&per_page=30"
                
                response = self.session.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get('items', []):
                        # Check for homepage URL
                        homepage = repo.get('homepage')
                        if homepage and homepage.startswith('http'):
                            # Validate it's not just GitHub or common platforms
                            domain = urlparse(homepage).netloc
                            if not any(platform in domain for platform in ['github.com', 'gitlab.com', 'npmjs.com']):
                                canonical_url = self.canonicalize_domain(homepage)
                                results.append({
                                    'url': canonical_url,
                                    'source': f'GitHub: {query}',
                                    'confidence': 6,
                                    'category': 'GitHub Project',
                                    'github_stars': repo.get('stargazers_count', 0),
                                    'github_repo': repo.get('full_name', '')
                                })
                elif response.status_code == 403:
                    logger.warning("GitHub rate limit exceeded")
                    break
                else:
                    logger.warning(f"GitHub API error: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"GitHub search error: {str(e)}")
                continue
        
        logger.info(f"✅ Found {len(results)} URLs from GitHub")
        return results

    def generate_and_validate_domains(self) -> List[Dict]:
        """Generate potential domains and validate them before adding"""
        logger.info("🔍 Generating and validating potential health tech domains...")
        results = []
        
        # Generate potential combinations (reduced set)
        health_terms = ['health', 'med', 'care', 'doc', 'vital']
        tech_terms = ['tech', 'ai', 'app', 'digital', 'io']
        country_tlds = ['.de', '.com', '.io', '.ai', '.eu']
        
        potential_domains = []
        for health in health_terms:
            for tech in tech_terms:
                for tld in country_tlds:
                    potential_domains.extend([
                        f"https://{health}{tech}{tld}",
                        f"https://{health}-{tech}{tld}"
                    ])
        
        # Shuffle and limit
        random.shuffle(potential_domains)
        potential_domains = potential_domains[:50]  # Limit to 50 for testing
        
        logger.info(f"  Testing {len(potential_domains)} generated domains...")
        
        for domain in tqdm(potential_domains, desc="Validating domains"):
            canonical_domain = self.canonicalize_domain(domain)
            health_check = self.check_url_health(canonical_domain, timeout=3)
            if health_check['is_alive']:
                results.append({
                    'url': canonical_domain,
                    'source': 'Generated & Validated',
                    'confidence': 4,
                    'category': 'Generated Domain',
                    'status_code': health_check['status_code']
                })
        
        logger.info(f"✅ Found {len(results)} valid generated domains")
        return results

    def get_user_verified_urls(self) -> List[Dict]:
        """User's verified hardcoded URLs - highest priority"""
        logger.info("🔍 Loading user's verified hardcoded URLs...")
        
        user_urls = [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://www.emmora.de',
            'https://www.alfa-ai.com',
            'https://www.apheris.com',
            'https://www.aporize.com/',
            'https://www.arztlena.com/',
            'https://shop.getnutrio.com/',
            'https://www.auta.health/',
            'https://visioncheckout.com/',
            'https://www.avayl.tech/',
            'https://www.avimedical.com/avi-impact',
            'https://de.becureglobal.com/',
            'https://bellehealth.co/de/',
            'https://www.biotx.ai/',
            'https://www.brainjo.de/',
            'https://brea.app/',
            'https://breathment.com/',
            'https://de.caona.eu/',
            'https://www.careanimations.de/',
            'https://sfs-healthcare.com',
            'https://www.climedo.de/',
            'https://www.cliniserve.de/',
            'https://cogthera.de/#erfahren',
            'https://www.comuny.de/',
            'https://curecurve.de/elina-app/',
            'https://www.cynteract.com/de/rehabilitation',
            'https://www.healthmeapp.de/de/',
            'https://deepeye.ai/',
            'https://www.deepmentation.ai/',
            'https://denton-systems.de/',
            'https://www.derma2go.com/',
            'https://www.dianovi.com/',
            'http://dopavision.com/',
            'https://www.dpv-analytics.com/',
            'http://www.ecovery.de/',
            'https://elixionmedical.com/',
            'https://www.empident.de/',
            'https://eye2you.ai/',
            'https://www.fitwhit.de',
            'https://www.floy.com/',
            'https://fyzo.de/assistant/',
            'https://www.gesund.de/app',
            'https://www.glaice.de/',
            'https://gleea.de/',
            'https://www.guidecare.de/',
            'https://www.apodienste.com/',
            'https://www.help-app.de/',
            'https://www.heynanny.com/',
            'https://incontalert.de/',
            'https://home.informme.info/',
            'https://www.kranushealth.com/de/therapien/haeufiger-harndrang',
            'https://www.kranushealth.com/de/therapien/inkontinenz'
        ]
        
        results = []
        logger.info(f"  Validating {len(user_urls)} verified URLs...")
        
        for url in tqdm(user_urls, desc="Validating verified URLs"):
            canonical_url = self.canonicalize_domain(url)
            health_check = self.check_url_health(canonical_url)
            validation = self.validate_health_content(canonical_url) if health_check['is_alive'] else {}
            
            result = {
                'url': canonical_url,
                'source': 'User Verified',
                'confidence': 10,
                'category': 'Verified Health Tech',
                'method': 'Hardcoded',
                **health_check,
                **validation
            }
            results.append(result)
            self.found_urls.add(canonical_url)
        
        logger.info(f"✅ Processed {len(results)} verified user URLs")
        return results

    def discover_all_startups(self) -> Dict:
        """Main discovery method with all improvements"""
        logger.info("🚀 IMPROVED STARTUP DISCOVERY SYSTEM")
        logger.info("=" * 60)
        start_time = time.time()
        
        # 1. User verified URLs (highest priority)
        logger.info("\n1️⃣ USER VERIFIED URLs")
        verified_results = self.get_user_verified_urls()
        self.all_discovered_urls['verified'] = verified_results
        
        # 2. Enhanced directory scraping with pagination
        logger.info("\n2️⃣ STARTUP DIRECTORIES (with pagination)")
        directory_results = []
        directories = [
            {
                'url': 'https://www.startbase.de/companies?industries=healthcare',
                'name': 'Startbase Healthcare'
            },
            {
                'url': 'https://www.deutsche-startups.de/category/healthtech/',
                'name': 'Deutsche Startups HealthTech'
            }
        ]
        
        for directory in directories:
            try:
                dir_results = self.scrape_startup_directory_with_pagination(
                    directory['url'], directory['name'], max_pages=5
                )
                directory_results.extend(dir_results)
            except Exception as e:
                logger.error(f"Error with {directory['name']}: {str(e)}")
        
        # 3. Enhanced GitHub discovery
        logger.info("\n3️⃣ GITHUB DISCOVERY (enhanced)")
        github_results = self.search_github_with_token()
        
        # 4. Search engine discovery with fallbacks
        logger.info("\n4️⃣ SEARCH ENGINE DISCOVERY (with fallbacks)")
        search_results = []
        search_queries = [
            "digital health startup Germany site:.de",
            "telemedicine startup Deutschland",
            "health tech company Berlin Munich",
            "medical AI startup Germany",
            "e-health startup Deutschland"
        ]
        
        for query in tqdm(search_queries, desc="Search queries"):
            urls = self.search_with_fallbacks(query, 15)
            for url in urls:
                canonical_url = self.canonicalize_domain(url)
                if canonical_url not in self.found_urls:
                    self.found_urls.add(canonical_url)
                    search_results.append({
                        'url': canonical_url,
                        'source': f'Search: {query}',
                        'confidence': 6,
                        'category': 'Search Engine',
                        'method': 'Search'
                    })
        
        # 5. Generated and validated domains
        logger.info("\n5️⃣ GENERATED DOMAINS (validated)")
        generated_results = self.generate_and_validate_domains()
        
        # Combine discovered and generated results
        discovered_results = directory_results + github_results + search_results
        self.all_discovered_urls['discovered'] = discovered_results
        self.all_discovered_urls['generated'] = generated_results
        
        # 6. Health validation for discovered URLs
        logger.info("\n6️⃣ HEALTH CONTENT VALIDATION")
        logger.info("  Validating discovered URLs for health relevance...")
        
        for result in tqdm(discovered_results, desc="Validating content"):
            if result['url'] not in [r['url'] for r in verified_results]:
                health_check = self.check_url_health(result['url'])
                validation = self.validate_health_content(result['url']) if health_check['is_alive'] else {}
                
                result.update(health_check)
                result.update(validation)
                
                # Adjust confidence based on health relevance
                if validation.get('is_health_related', False):
                    result['confidence'] = min(result['confidence'] + 2, 10)
        
        # 7. Final consolidation
        all_results = verified_results + discovered_results + generated_results
        
        # Remove duplicates using canonicalized URLs
        unique_results = []
        seen_canonical_urls = set()
        for result in sorted(all_results, key=lambda x: x['confidence'], reverse=True):
            canonical_url = self.canonicalize_domain(result['url'])
            if canonical_url not in seen_canonical_urls:
                seen_canonical_urls.add(canonical_url)
                result['url'] = canonical_url  # Ensure URL is canonical
                unique_results.append(result)
        
        end_time = time.time()
        
        # Prepare final results with search engine performance stats
        engine_stats = {}
        for engine, stats in self.engine_success_rates.items():
            if stats['attempts'] > 0:
                engine_stats[engine] = {
                    'success_rate': round(stats['success'] / stats['attempts'], 2),
                    'attempts': stats['attempts'],
                    'successes': stats['success']
                }
        
        final_results = {
            'total_urls_discovered': len(unique_results),
            'discovery_time_seconds': round(end_time - start_time, 2),
            'urls': unique_results,
            'engine_performance': engine_stats,
            'summary': {
                'verified': len(verified_results),
                'discovered': len(discovered_results),
                'generated': len(generated_results),
                'total_unique': len(unique_results),
                'alive_urls': len([r for r in unique_results if r.get('is_alive', True)]),
                'health_related': len([r for r in unique_results if r.get('is_health_related', True)])
            }
        }
        
        logger.info(f"\n📊 DISCOVERY COMPLETE! ({final_results['discovery_time_seconds']}s)")
        logger.info(f"🎯 Total URLs: {final_results['total_urls_discovered']}")
        logger.info(f"✅ Alive URLs: {final_results['summary']['alive_urls']}")
        logger.info(f"🏥 Health-related: {final_results['summary']['health_related']}")
        
        # Log search engine performance
        if engine_stats:
            logger.info("🔍 Search Engine Performance:")
            for engine, stats in engine_stats.items():
                logger.info(f"  {engine.title()}: {stats['success_rate']} success rate ({stats['successes']}/{stats['attempts']})")
        
        return final_results

    def save_separated_results(self, results: Dict) -> Dict:
        """Save results to separate files by confidence level"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_created = {}
        
        # Separate results by type
        verified_urls = [r for r in results['urls'] if r.get('method') == 'Hardcoded' or r['confidence'] >= 9]
        discovered_urls = [r for r in results['urls'] if 5 <= r['confidence'] < 9]
        generated_urls = [r for r in results['urls'] if r['confidence'] < 5]
        
        # Save verified URLs
        verified_filename = f"verified_startups_{timestamp}.csv"
        self.save_csv(verified_urls, verified_filename)
        files_created['verified'] = verified_filename
        
        # Save discovered URLs
        discovered_filename = f"discovered_startups_{timestamp}.csv"
        self.save_csv(discovered_urls, discovered_filename)
        files_created['discovered'] = discovered_filename
        
        # Save generated URLs
        generated_filename = f"generated_startups_{timestamp}.csv"
        self.save_csv(generated_urls, generated_filename)
        files_created['generated'] = generated_filename
        
        # Save comprehensive JSON
        json_filename = f"comprehensive_results_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        files_created['json'] = json_filename
        
        # Save summary report
        report_filename = f"discovery_summary_{timestamp}.txt"
        self.save_summary_report(results, report_filename, files_created)
        files_created['report'] = report_filename
        
        return files_created

    def save_csv(self, urls: List[Dict], filename: str):
        """Save URLs to CSV file"""
        if not urls:
            return
            
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'source', 'confidence', 'category', 'method', 'is_alive', 
                         'status_code', 'health_score', 'is_health_related', 'country', 'discovered_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for url_data in urls:
                writer.writerow(url_data)

    def save_summary_report(self, results: Dict, filename: str, files_created: Dict):
        """Save comprehensive summary report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🚀 IMPROVED STARTUP DISCOVERY REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Discovery Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Discovery Time: {results['discovery_time_seconds']} seconds\n")
            f.write(f"Total URLs Discovered: {results['total_urls_discovered']}\n\n")
            
            f.write("📊 SUMMARY STATISTICS:\n")
            for key, value in results['summary'].items():
                f.write(f"  • {key.replace('_', ' ').title()}: {value}\n")
            
            f.write(f"\n📁 FILES CREATED:\n")
            for file_type, filename in files_created.items():
                count = len([r for r in results['urls'] if 
                           (file_type == 'verified' and (r.get('method') == 'Hardcoded' or r['confidence'] >= 9)) or
                           (file_type == 'discovered' and 5 <= r['confidence'] < 9) or
                           (file_type == 'generated' and r['confidence'] < 5)])
                f.write(f"  • {file_type.title()}: {filename} ({count} URLs)\n")
            
            f.write(f"\n🔝 TOP 20 HIGHEST CONFIDENCE URLs:\n")
            top_urls = sorted(results['urls'], key=lambda x: x['confidence'], reverse=True)[:20]
            for i, url_data in enumerate(top_urls, 1):
                status = "✅" if url_data.get('is_alive', True) else "❌"
                health = "🏥" if url_data.get('is_health_related', False) else "❓"
                f.write(f"  {i:2d}. {status}{health} {url_data['url']} (confidence: {url_data['confidence']})\n")
            
            f.write(f"\n📈 IMPROVEMENTS IMPLEMENTED:\n")
            f.write("  ✅ Robust search with fallbacks (Google → Bing → DuckDuckGo)\n")
            f.write("  ✅ Deep pagination support for startup directories\n") 
            f.write("  ✅ URL health checks and validation\n")
            f.write("  ✅ Enhanced GitHub discovery with API tokens\n")
            f.write("  ✅ Separated output files by confidence level\n")
            f.write("  ✅ Progress bars and comprehensive logging\n")
            f.write("  ✅ Content validation for health relevance\n")
            f.write("  ✅ Country detection from domains and content\n")

def main():
    """Main function to run the improved startup discovery"""
    logger.info("🚀 IMPROVED STARTUP DISCOVERY SYSTEM")
    logger.info("=" * 60)
    logger.info("🎯 All major issues addressed:")
    logger.info("  • Robust search with fallbacks + smart ranking")
    logger.info("  • Deep pagination support")
    logger.info("  • URL health checks + domain canonicalization")
    logger.info("  • Enhanced GitHub discovery")
    logger.info("  • Separated output files")
    logger.info("  • Progress bars and comprehensive logging")
    logger.info("  • Smart throttling with jitter")
    logger.info("")
    
    # Check for GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        logger.info(f"✅ GitHub API token found - enhanced discovery enabled")
    else:
        logger.warning(f"⚠️ No GitHub token found - limited to anonymous access")
        logger.info(f"  Set GITHUB_TOKEN environment variable for better results")
    
    logger.info("")
    
    try:
        # Initialize and run discovery
        discoverer = ImprovedStartupDiscovery()
        results = discoverer.discover_all_startups()
        
        # Save separated results
        files = discoverer.save_separated_results(results)
        
        logger.info(f"\n✨ SUCCESS! Discovery completed in {results['discovery_time_seconds']}s")
        logger.info(f"📁 Files created:")
        for file_type, filename in files.items():
            logger.info(f"  • {filename}")
        
        logger.info(f"\n📋 Next steps:")
        logger.info(f"  1. Review verified URLs in: {files['verified']}")
        logger.info(f"  2. Validate discovered URLs in: {files['discovered']}")
        logger.info(f"  3. Check generated URLs in: {files['generated']}")
        logger.info(f"  4. Use comprehensive data from: {files['json']}")
        
        return files
        
    except KeyboardInterrupt:
        logger.warning(f"\n⚠️ Discovery interrupted by user")
        return None
    except Exception as e:
        logger.error(f"Error during discovery: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
    if results:
        logger.info(f"\n🎊 Improved discovery completed successfully!")
    else:
        logger.warning(f"\n⚠️ Discovery completed with issues")