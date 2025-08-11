#!/usr/bin/env python3
"""
GOOGLE SEARCH-BASED STARTUP DISCOVERY
Uses Google search results to find digital health startups
Scrapes search results for real startup URLs
"""

import requests
import time
import random
import re
from urllib.parse import urljoin, urlparse, quote_plus, unquote
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
from typing import List, Dict, Set

class GoogleSearchStartupFinder:
    def __init__(self):
        self.session = requests.Session()
        # Polite, persistent headers; UA will be rotated per request
        self.static_headers = {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }
        self.ua_pool = [
            # 6 modern desktop UAs
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; rv:11.0) like Gecko Edge/124.0",
        ]
        # Respectful randomized delay window between requests
        self.delay = (8, 15)
        self.found_urls = set()
        # Track last HTTP status to inform fallback logic
        self.last_http_status = None
    
    def _ensure_consent_cookie(self, resp):
        """
        If Google redirects to consent.google.com or the page contains a consent form,
        set a permissive CONSENT cookie and signal caller to retry once.
        """
        url = str(getattr(resp, "url", ""))
        text = resp.text if hasattr(resp, "text") else ""
        if "consent.google.com" in url or 'action="https://consent.google.com' in text:
            # Set a permissive consent cookie and tell caller to retry the search once
            self.session.cookies.set("CONSENT", "YES+cb", domain=".google.com")
            return True
        return False

    def _extract_result_urls(self, html):
        """
        Extract real result URLs from Google HTML using tightened selectors only:
        - anchors that contain an <h3> (a:has(h3)) with http hrefs
        """
        soup = BeautifulSoup(html, "html.parser")
        urls: List[str] = []

        # Tight modern selector: anchors that contain an <h3>
        for a in soup.select('a:has(h3)[href^="http"]'):
            href = a.get("href", "")
            if href and href.startswith("http"):
                urls.append(href)

        # Deduplicate while keeping order
        seen = set()
        deduped: List[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped

    def search_google(self, query: str, num_results: int = 10) -> List[str]:
        """Search Google and extract URLs from results with rate-limit awareness"""
        print(f"🔍 Searching Google for: '{query}'")
        try:
            params = {
                "q": query,
                "num": max(1, min(int(num_results or 10), 10)),
                "hl": "en",
                "gl": "de",
                "pws": "0",
            }

            base_url = "https://www.google.com/search"
            max_retries = 5
            base_backoff = 5.0

            # Initial polite delay
            time.sleep(random.uniform(*self.delay))

            for attempt in range(max_retries):
                # Rotate UA per attempt
                ua = random.choice(self.ua_pool)
                headers = {"User-Agent": ua, **self.static_headers}

                try:
                    resp = self.session.get(base_url, params=params, headers=headers, timeout=20)
                    self.last_http_status = getattr(resp, "status_code", None)
                except requests.RequestException as e:
                    # Network error; apply backoff and retry
                    self.last_http_status = None
                    if attempt < max_retries - 1:
                        sleep_s = base_backoff * (2 ** attempt) + random.uniform(0, 3)
                        sleep_s += random.uniform(*self.delay)
                        print(f"  ⚠️  Network error: {e}. Backing off {sleep_s:.1f}s…")
                        time.sleep(sleep_s)
                        self.session.cookies.clear()
                        continue
                    else:
                        print("  ⚠️  Network error and retries exhausted; returning empty.")
                        return []

                # Handle consent interstitial once by setting cookie and retrying immediately
                if self._ensure_consent_cookie(resp):
                    self.session.cookies.clear()
                    if attempt < max_retries - 1:
                        sleep_s = random.uniform(*self.delay)
                        print(f"  ⚠️  Consent flow detected. Sleeping {sleep_s:.1f}s and retrying…")
                        time.sleep(sleep_s)
                        continue
                    else:
                        print("  ⚠️  Consent flow and retries exhausted; returning empty.")
                        return []

                status = getattr(resp, "status_code", 0)
                if status in (429, 503):
                    self.last_http_status = status
                    if attempt < max_retries - 1:
                        sleep_s = base_backoff * (2 ** attempt) + random.uniform(0, 3)
                        sleep_s += random.uniform(*self.delay)
                        print(f"  ⚠️  Rate limited ({status}). Sleeping {sleep_s:.1f}s and rotating UA…")
                        time.sleep(sleep_s)
                        self.session.cookies.clear()
                        continue
                    else:
                        print("  ⚠️  Rate-limited, try later. Returning empty.")
                        return []

                try:
                    resp.raise_for_status()
                except Exception as e:
                    print(f"  ⚠️  HTTP error: {e}")
                    return []

                soup = BeautifulSoup(resp.content, "html.parser")

                # Extract URLs via tightened selectors only
                urls: List[str] = []
                seen: Set[str] = set()
                for a in soup.select('a:has(h3)[href^="http"]'):
                    href = a.get("href")
                    if href and href.startswith("http") and href not in seen:
                        urls.append(href)
                        seen.add(href)

                # Filter domains
                exclude_domains = {
                    "google.com", "google.de", "news.google.com", "youtube.com", "m.youtube.com",
                    "facebook.com", "twitter.com", "linkedin.com", "wikipedia.org",
                    "crunchbase.com", "angel.co", "techcrunch.com", "reuters.com", "bloomberg.com",
                    "webcache.googleusercontent.com"
                }

                allowed_tlds = (".com", ".de", ".io", ".ai", ".health", ".tech", ".app", ".eu", ".co")

                startup_urls: List[str] = []
                for url in urls:
                    try:
                        domain = urlparse(url).netloc.lower()
                    except Exception:
                        continue
                    if any(excl in domain for excl in exclude_domains):
                        continue
                    if domain.endswith(".google"):
                        continue
                    if any(tld in domain for tld in allowed_tlds):
                        startup_urls.append(url)

                print(f"  ✅ Found {len(startup_urls)} potential startup URLs")
                self.last_http_status = 200
                return startup_urls[:10]

            # If we get here, retries exhausted
            print("  ⚠️  Rate-limited, try later. Returning empty.")
            return []

        except Exception as e:
            print(f"  ⚠️  Error searching Google: {str(e)}")
            return []

    def discover_german_health_startups(self) -> List[Dict]:
        """Discover German digital health startups"""
        print("🇩🇪 Discovering German digital health startups...")
        
        german_queries = [
            "digital health startup Germany site:.de",
            "telemedicine startup Deutschland",
            "health tech company Berlin Munich",
            "medical AI startup Germany",
            "e-health startup Deutschland site:.de",
            "digital therapeutics Germany",
            "healthtech startup Berlin",
            "medtech company Germany innovation"
        ]
        
        results: List[Dict] = []
        for idx, query in enumerate(german_queries):
            urls = self.search_google(query, num_results=10)
            # Fallback to DDG on rate-limit or empty results
            if not urls or getattr(self, "last_http_status", None) in (429, 503):
                sleep_s = random.uniform(10, 20)
                print(f"  🔁 Google empty or rate-limited. Sleeping {sleep_s:.1f}s then trying DuckDuckGo…")
                time.sleep(sleep_s)
                try:
                    ddg = DuckDuckGoSearchStartupFinder()
                    urls = ddg.search_ddg(query, num_results=20)
                    source_label = f"DDG: {query}"
                except Exception:
                    urls = []
                    source_label = f"DDG: {query}"
            else:
                source_label = f"Google: {query}"
            if urls:
                for url in urls:
                    if url not in self.found_urls:
                        self.found_urls.add(url)
                        results.append({
                            'url': url,
                            'source': source_label,
                            'confidence': 7,
                            'category': 'German Health Tech',
                            'country': 'Germany'
                        })
                break  # Short-circuit after first successful query
            # Throttle between queries
            time.sleep(random.uniform(10, 20))
                    
        print(f"🇩🇪 Found {len(results)} German startup URLs")
        return results

    def discover_european_health_startups(self) -> List[Dict]:
        """Discover European digital health startups"""
        print("🇪🇺 Discovering European digital health startups...")
        
        european_queries = [
            "digital health startup Europe",
            "telemedicine company France UK Netherlands",
            "health tech startup Switzerland Austria",
            "medical AI Europe startup",
            "e-health platform Scandinavia",
            "digital therapeutics startup Nordic",
            "healthtech company Italy Spain",
            "health app startup Europe"
        ]
        
        results: List[Dict] = []
        for idx, query in enumerate(european_queries):
            urls = self.search_google(query, num_results=10)
            if not urls or getattr(self, "last_http_status", None) in (429, 503):
                sleep_s = random.uniform(10, 20)
                print(f"  🔁 Google empty or rate-limited. Sleeping {sleep_s:.1f}s then trying DuckDuckGo…")
                time.sleep(sleep_s)
                try:
                    ddg = DuckDuckGoSearchStartupFinder()
                    urls = ddg.search_ddg(query, num_results=20)
                    source_label = f"DDG: {query}"
                except Exception:
                    urls = []
                    source_label = f"DDG: {query}"
            else:
                source_label = f"Google: {query}"
            if urls:
                for url in urls:
                    if url not in self.found_urls:
                        self.found_urls.add(url)
                        results.append({
                            'url': url,
                            'source': source_label,
                            'confidence': 6,
                            'category': 'European Health Tech',
                            'country': 'Europe'
                        })
                break  # Short-circuit after first successful query
            time.sleep(random.uniform(10, 20))
                    
        print(f"🇪🇺 Found {len(results)} European startup URLs")
        return results

    def discover_specific_health_domains(self) -> List[Dict]:
        """Discover startups in specific health domains"""
        print("🎯 Discovering domain-specific health startups...")
        
        domain_queries = [
            "AI diagnostics startup Europe",
            "telemedicine platform Germany",
            "digital therapeutics app",
            "remote patient monitoring startup",
            "health data analytics company",
            "medical device software startup",
            "clinical trial platform Europe",
            "pharmacy automation startup"
        ]
        
        results: List[Dict] = []
        for idx, query in enumerate(domain_queries):
            urls = self.search_google(query, num_results=10)
            if not urls or getattr(self, "last_http_status", None) in (429, 503):
                sleep_s = random.uniform(10, 20)
                print(f"  🔁 Google empty or rate-limited. Sleeping {sleep_s:.1f}s then trying DuckDuckGo…")
                time.sleep(sleep_s)
                try:
                    ddg = DuckDuckGoSearchStartupFinder()
                    urls = ddg.search_ddg(query, num_results=20)
                    source_label = f"DDG: {query}"
                except Exception:
                    urls = []
                    source_label = f"DDG: {query}"
            else:
                source_label = f"Google: {query}"
            if urls:
                for url in urls:
                    if url not in self.found_urls:
                        self.found_urls.add(url)
                        results.append({
                            'url': url,
                            'source': source_label,
                            'confidence': 6,
                            'category': 'Domain Specific',
                            'country': 'Various'
                        })
                break  # Short-circuit after first successful query
            time.sleep(random.uniform(10, 20))
                    
        print(f"🎯 Found {len(results)} domain-specific startup URLs")
        return results

    def discover_startup_directories(self) -> List[Dict]:
        """Find startups through directory searches"""
        print("📁 Searching startup directories...")
        
        directory_queries = [
            "startup directory health tech Germany",
            "European health startup list",
            "digital health company directory",
            "medical technology startup database"
        ]
        
        results: List[Dict] = []
        for idx, query in enumerate(directory_queries):
            urls = self.search_google(query, num_results=10)
            if not urls or getattr(self, "last_http_status", None) in (429, 503):
                sleep_s = random.uniform(10, 20)
                print(f"  🔁 Google empty or rate-limited. Sleeping {sleep_s:.1f}s then trying DuckDuckGo…")
                time.sleep(sleep_s)
                try:
                    ddg = DuckDuckGoSearchStartupFinder()
                    urls = ddg.search_ddg(query, num_results=20)
                    source_label = f"DDG: {query}"
                except Exception:
                    urls = []
                    source_label = f"DDG: {query}"
            else:
                source_label = f"Google: {query}"
            if urls:
                for url in urls:
                    if url not in self.found_urls:
                        self.found_urls.add(url)
                        # These might be directories, so lower confidence
                        results.append({
                            'url': url,
                            'source': source_label,
                            'confidence': 5,
                            'category': 'Directory Listed',
                            'country': 'Various'
                        })
                break  # Short-circuit after first successful query
            time.sleep(random.uniform(10, 20))
                    
        print(f"📁 Found {len(results)} directory URLs")
        return results

    def validate_health_tech_urls(self, urls: List[Dict]) -> List[Dict]:
        """Validate that URLs are likely health tech companies"""
        print("🧪 Validating health tech relevance...")
        
        health_keywords = [
            'health', 'medical', 'medicine', 'clinic', 'hospital', 'patient', 
            'therapy', 'treatment', 'diagnostic', 'pharma', 'biotech',
            'telemedicine', 'digital health', 'e-health', 'medtech',
            'ai', 'artificial intelligence', 'data', 'analytics', 'platform'
        ]
        
        validated_urls = []
        
        for url_data in urls:
            url = url_data['url']
            domain = urlparse(url).netloc.lower()
            
            # Check if domain contains health-related keywords
            domain_health_score = sum(1 for keyword in health_keywords if keyword in domain)
            
            # Higher confidence for domains with health keywords
            if domain_health_score > 0:
                url_data['confidence'] = min(url_data['confidence'] + domain_health_score, 10)
                url_data['health_score'] = domain_health_score
                validated_urls.append(url_data)
            else:
                # Keep but with lower confidence
                url_data['health_score'] = 0
                validated_urls.append(url_data)
        
        print(f"🧪 Validated {len(validated_urls)} URLs")
        return validated_urls

    def get_user_hardcoded_urls(self) -> List[Dict]:
        """Get user's hardcoded URLs with highest priority"""
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
        for url in user_urls:
            results.append({
                'url': url,
                'source': 'User Verified',
                'confidence': 10,
                'category': 'Verified Health Tech',
                'country': 'Germany/Europe',
                'health_score': 10
            })
            self.found_urls.add(url)
            
        return results

    def discover_all_startups(self) -> Dict:
        """Main discovery method"""
        print("🚀 GOOGLE SEARCH-BASED STARTUP DISCOVERY")
        print("=" * 60)
        
        all_results = []
        
        # 1. User hardcoded URLs (highest priority)
        print("\n1️⃣ Loading user verified URLs...")
        user_results = self.get_user_hardcoded_urls()
        all_results.extend(user_results)
        
        # 2. German health startups
        print("\n2️⃣ Discovering German health startups...")
        german_results = self.discover_german_health_startups()
        all_results.extend(german_results)
        
        # 3. European health startups
        print("\n3️⃣ Discovering European health startups...")
        european_results = self.discover_european_health_startups()
        all_results.extend(european_results)
        
        # 4. Domain-specific startups
        print("\n4️⃣ Discovering domain-specific startups...")
        domain_results = self.discover_specific_health_domains()
        all_results.extend(domain_results)
        
        # 5. Directory searches
        print("\n5️⃣ Searching startup directories...")
        directory_results = self.discover_startup_directories()
        all_results.extend(directory_results)
        
        # Validate health tech relevance
        print("\n🧪 Validating health tech relevance...")
        validated_results = self.validate_health_tech_urls(all_results)
        
        # Remove duplicates and sort by confidence
        unique_results = []
        seen_urls = set()
        
        for result in sorted(validated_results, key=lambda x: x['confidence'], reverse=True):
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        # Prepare final results
        final_results = {
            'total_urls_discovered': len(unique_results),
            'urls': unique_results,
            'summary': {
                'user_verified': len(user_results),
                'german_startups': len(german_results),
                'european_startups': len(european_results),
                'domain_specific': len(domain_results),
                'directory_results': len(directory_results),
                'total_unique': len(unique_results)
            },
            'discovery_methods': [
                f"User Verified: {len(user_results)}",
                f"German Health Tech: {len(german_results)}",
                f"European Health Tech: {len(european_results)}",
                f"Domain Specific: {len(domain_results)}",
                f"Directory Searches: {len(directory_results)}"
            ]
        }
        
        print(f"\n📊 DISCOVERY COMPLETE!")
        print(f"🎯 Total unique URLs discovered: {len(unique_results)}")
        
        return final_results

    def save_results(self, results: Dict) -> tuple:
        """Save results to CSV and JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"google_search_discovery_{timestamp}.csv"
        json_filename = f"google_search_discovery_{timestamp}.json"
        
        # Save CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'source', 'confidence', 'category', 'country', 'health_score']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for url_data in results['urls']:
                writer.writerow(url_data)
        
        # Save JSON
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved:")
        print(f"  • CSV: {csv_filename}")
        print(f"  • JSON: {json_filename}")
        
        return csv_filename, json_filename

class DuckDuckGoSearchStartupFinder:
    """Simple HTML DuckDuckGo fallback client using the /html endpoint."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        ]
        self.static_headers = {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://duckduckgo.com/",
        }
        self.delay = (6, 12)

    def _filter_urls(self, urls: List[str]) -> List[str]:
        exclude_domains = {
            "duckduckgo.com", "google.com", "news.google.com", "youtube.com", "m.youtube.com",
            "facebook.com", "twitter.com", "linkedin.com", "wikipedia.org",
            "crunchbase.com", "angel.co", "techcrunch.com", "reuters.com", "bloomberg.com",
            "webcache.googleusercontent.com"
        }
        allowed_tlds = (".com", ".de", ".io", ".ai", ".health", ".tech", ".app", ".eu", ".co")
        kept: List[str] = []
        for url in urls:
            try:
                domain = urlparse(url).netloc.lower()
            except Exception:
                continue
            if any(excl in domain for excl in exclude_domains):
                continue
            if any(tld in domain for tld in allowed_tlds):
                kept.append(url)
        return kept

    def search_ddg(self, query: str, num_results: int = 20) -> List[str]:
        print(f"🔎 Fallback: DuckDuckGo for: '{query}'")
        try:
            time.sleep(random.uniform(*self.delay))
            ua = random.choice(self.ua_pool)
            headers = {"User-Agent": ua, **self.static_headers}
            url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            resp = self.session.get(url, headers=headers, timeout=20)
            if getattr(resp, "status_code", 0) in (429, 503):
                print("  ⚠️  DDG rate-limited; returning empty.")
                return []
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            raw_urls: List[str] = []
            for a in soup.select("a.result__a"):
                href = a.get("href", "")
                if not href:
                    continue
                # DDG HTML often uses /l/?uddg=<encoded_target>
                if href.startswith("/l/?") or href.startswith("https://duckduckgo.com/l/?"):
                    try:
                        from urllib.parse import parse_qs
                        qs = parse_qs(urlparse(href).query)
                        target = qs.get("uddg", [""])[0]
                        if target:
                            raw_urls.append(unquote(target))
                    except Exception:
                        continue
                elif href.startswith("http"):
                    raw_urls.append(href)
            # Dedupicate and filter
            seen = set()
            deduped: List[str] = []
            for u in raw_urls:
                if u not in seen:
                    seen.add(u)
                    deduped.append(u)
            filtered = self._filter_urls(deduped)
            print(f"  ✅ DDG extracted {len(filtered)} URLs")
            return filtered[: min(15, int(num_results or 20))]
        except Exception as exc:
            print(f"  ⚠️  Error searching DuckDuckGo: {exc}")
            return []

def main():
    """Main function"""
    print("🚀 GOOGLE SEARCH-BASED STARTUP DISCOVERY")
    print("=" * 60)
    print("🎯 Finding digital health startups through Google search")
    print("🆓 Using free search methods only")
    print("🌍 Focus: Germany and Europe")
    print("")
    
    # Initialize finder
    finder = GoogleSearchStartupFinder()
    
    # Run discovery
    results = finder.discover_all_startups()
    
    # Save results
    csv_file, json_file = finder.save_results(results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎉 GOOGLE SEARCH DISCOVERY COMPLETED!")
    print("=" * 60)
    print(f"📊 Total URLs discovered: {results['total_urls_discovered']}")
    print(f"📁 Files created: {csv_file}, {json_file}")
    
    print(f"\n🔍 Top 10 Discovered URLs:")
    for i, url_data in enumerate(results['urls'][:10], 1):
        print(f"  {i:2d}. {url_data['url']} ({url_data['category']}, confidence: {url_data['confidence']})")
    
    print(f"\n📊 Discovery Breakdown:")
    for method in results['discovery_methods']:
        print(f"  • {method}")
    
    print(f"\n✅ Ready for URL evaluation and company extraction!")
    
    return csv_file, json_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Single query test mode for debugging
        q = " ".join(sys.argv[1:]) or "digital health startup Germany site:.de"
        print(GoogleSearchStartupFinder().search_google(q, 10))
    else:
        try:
            csv_file, json_file = main()
            print(f"\n🎊 Google search discovery completed successfully!")
        except KeyboardInterrupt:
            print(f"\n⚠️ Discovery interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during discovery: {str(e)}")