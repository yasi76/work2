#!/usr/bin/env python3
"""
GOOGLE SEARCH-BASED STARTUP DISCOVERY
Uses Google search results to find digital health startups
Scrapes search results for real startup URLs
"""

import requests
import time
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
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = 3  # Respectful delay between searches
        self.found_urls = set()
        
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
        Extract real result URLs from Google HTML using the canonical /url?q=... links.
        Also supports a fallback for standard result container <div class="yuRUbf"><a ...>
        """
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Primary: /url?q=… links (both relative and absolute forms) and /url?url=
        for a in soup.select('a[href^="/url?"], a[href^="https://www.google.com/url?"]'):
            href = a.get("href", "")
            # Handle absolute Google redirect hrefs by stripping the domain
            if href.startswith("https://www.google.com/"):
                idx = href.find("/url?")
                if idx != -1:
                    href = href[idx:]
            # /url?q=<REAL_URL>&... or /url?url=<REAL_URL>&...
            m = re.search(r"/url\\?(?:q|url)=([^&]+)", href)
            if not m:
                continue
            real = unquote(m.group(1))
            if real.startswith("http"):
                urls.append(real)

        # Fallback: direct anchors under result container
        for a in soup.select("div.yuRUbf > a[href^='http']"):
            href = a.get("href", "")
            if href and href.startswith("http"):
                urls.append(href)

        # Deduplicate while keeping order
        seen = set()
        deduped = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped

    def search_google(self, query: str, num_results: int = 20) -> List[str]:
        """Search Google and extract URLs from results."""
        print(f"🔍 Searching Google for: '{query}'")
        try:
            # Respectful delay
            time.sleep(self.delay if getattr(self, "delay", None) else 2)

            # Use params that yield a simpler markup; add hl/gl for consistency
            params = {
                "q": query,
                "num": str(num_results),
                "hl": "en",
                "gl": "de",   # preference for DE results (tune if needed)
                "pws": "0",   # disable personalized search
                "udm": "14",  # simplified web results layout
            }

            headers = {
                "User-Agent": self.session.headers.get("User-Agent", "Mozilla/5.0"),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }

            # First request
            resp = self.session.get(
                "https://www.google.com/search",
                params=params,
                headers=headers,
                timeout=20,
                allow_redirects=True,
            )
            resp.raise_for_status()

            # Handle consent gate once
            if self._ensure_consent_cookie(resp):
                time.sleep(1.0)
                resp = self.session.get(
                    "https://www.google.com/search",
                    params=params,
                    headers=headers,
                    timeout=20,
                    allow_redirects=True,
                )
                resp.raise_for_status()

            # Basic bot/CAPTCHA page detection
            text = resp.text
            if "unusual traffic from your computer network" in text.lower():
                print("  ⚠️  Google blocked the request (CAPTCHA). Returning empty list.")
                return []

            # Extract URLs
            urls = self._extract_result_urls(text)

            # Filter obvious non-startup / aggregator domains
            exclude_domains = {
                "google.", "youtube.com", "facebook.com", "twitter.com", "linkedin.com",
                "wikipedia.org", "crunchbase.com", "angel.co", "techcrunch.com",
                "forbes.com", "reuters.com", "bloomberg.com",
            }

            def domain(u: str) -> str:
                try:
                    return urlparse(u).netloc.lower()
                except Exception:
                    return ""

            filtered = []
            seen_domains = set()
            for u in urls:
                d = domain(u)
                if not d or any(ex in d for ex in exclude_domains):
                    continue
                # Keep one URL per domain to avoid spammy duplicates
                if d not in seen_domains:
                    seen_domains.add(d)
                    filtered.append(u)

            limited = filtered[:15]
            print(f"  ✅ Found {len(limited)} potential startup URLs")
            return limited

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
        
        results = []
        for query in german_queries:
            urls = self.search_google(query)
            for url in urls:
                if url not in self.found_urls:
                    self.found_urls.add(url)
                    results.append({
                        'url': url,
                        'source': f'Google: {query}',
                        'confidence': 7,
                        'category': 'German Health Tech',
                        'country': 'Germany'
                    })
                    
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
        
        results = []
        for query in european_queries:
            urls = self.search_google(query)
            for url in urls:
                if url not in self.found_urls:
                    self.found_urls.add(url)
                    results.append({
                        'url': url,
                        'source': f'Google: {query}',
                        'confidence': 6,
                        'category': 'European Health Tech',
                        'country': 'Europe'
                    })
                    
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
        
        results = []
        for query in domain_queries:
            urls = self.search_google(query)
            for url in urls:
                if url not in self.found_urls:
                    self.found_urls.add(url)
                    results.append({
                        'url': url,
                        'source': f'Google: {query}',
                        'confidence': 6,
                        'category': 'Domain Specific',
                        'country': 'Various'
                    })
                    
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
        
        results = []
        for query in directory_queries:
            urls = self.search_google(query)
            for url in urls:
                if url not in self.found_urls:
                    self.found_urls.add(url)
                    # These might be directories, so lower confidence
                    results.append({
                        'url': url,
                        'source': f'Google: {query}',
                        'confidence': 5,
                        'category': 'Directory Listed',
                        'country': 'Various'
                    })
                    
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
    try:
        csv_file, json_file = main()
        print(f"\n🎊 Google search discovery completed successfully!")
    except KeyboardInterrupt:
        print(f"\n⚠️ Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during discovery: {str(e)}")