#!/usr/bin/env python3
"""
IMPROVED Healthcare Web Scraper
Finds German digital health companies like the user discovered
"""

import requests
import time
import re
import json
import csv
from typing import List, Set, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote
import random


class ImprovedHealthcareScraper:
    """
    Much improved scraper focused on German digital health companies
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.discovered_companies = set()
        
        # Add the user's verified companies as starting points
        self.verified_companies = self._load_user_verified_companies()

    def _load_user_verified_companies(self) -> Set[str]:
        """Load the verified companies the user provided"""
        companies = {
            "https://www.emmora.de/",
            "https://www.apheris.com/", 
            "https://aporize.com/",
            "https://www.aurahealth.tech/",
            "https://www.avayl.tech/",
            "https://becureglobal.com/",
            "https://www.brainjo.de/",
            "https://www.careanimations.de/",
            "https://sfs-healthcare.com/",
            "https://www.climedo.de/",
            "https://www.cliniserve.de/",
            "https://www.comuny.de/",
            "https://www.healthmeapp.de/",
            "https://deepeye.ai/",
            "https://www.deepmentation.ai/",
            "https://denton-systems.de/",
            "https://www.derma2go.com/",
            "https://www.dianovi.com/",
            "https://dopavision.com/",
            "https://www.dpv-analytics.com/",
            "https://www.ecovery.de/",
            "https://elixionmedical.com/",
            "https://www.empident.de/",
            "https://www.fitwhit.de/",
            "https://www.glaice.de/",
            "https://gleea.de/",
            "https://www.guidecare.de/",
            "https://www.apodienste.com/",
            "https://www.help-app.de/",
            "https://www.heynanny.com/",
            "https://incontalert.de/",
            "https://home.informme.info/",
            "https://www.kranushealth.com/"
        }
        print(f"🎯 Starting with {len(companies)} verified companies provided by user")
        return companies

    def _is_healthcare_company(self, url: str, text: str = "") -> bool:
        """Improved healthcare company detection"""
        combined = f"{url} {text}".lower()
        
        # German + English healthcare keywords
        healthcare_keywords = [
            # English
            'health', 'medical', 'medicine', 'pharma', 'biotech', 'medtech',
            'clinic', 'hospital', 'therapy', 'diagnostic', 'care', 'patient',
            'doctor', 'physician', 'laboratory', 'clinical', 'drug', 'treatment',
            # German specific
            'gesundheit', 'medizin', 'arzt', 'klinik', 'therapie', 'patient',
            'behandlung', 'diagnose', 'pflege', 'heilung', 'pharma', 'biotech',
            'medtech', 'digital health', 'e-health', 'telemedizin', 'telemedicine',
            # Digital health specific
            'healthtech', 'health tech', 'health app', 'medical app', 'fitness',
            'wellness', 'mental health', 'nutrition', 'diet', 'workout',
            'rehabilitation', 'monitoring', 'tracking', 'ai health', 'health ai'
        ]
        
        # Domain patterns that suggest healthcare
        healthcare_domains = [
            'health', 'medical', 'med', 'care', 'pharma', 'bio', 'clinic',
            'hospital', 'doctor', 'patient', 'therapy', 'diagnostics',
            'gesundheit', 'medizin', 'klinik', 'arzt'
        ]
        
        # Exclude non-healthcare
        exclude_keywords = [
            'linkedin', 'facebook', 'twitter', 'youtube', 'instagram', 'wikipedia',
            'google', 'amazon', 'microsoft', 'apple', 'news', 'blog', 'forum',
            'github', 'stackoverflow'
        ]
        
        # Check exclusions first
        for exclude in exclude_keywords:
            if exclude in combined:
                return False
        
        # Check domain for healthcare indicators
        try:
            domain = urlparse(url).netloc.replace('www.', '').lower()
            for pattern in healthcare_domains:
                if pattern in domain:
                    return True
        except:
            pass
        
        # Check healthcare keywords
        return any(keyword in combined for keyword in healthcare_keywords)

    def scrape_german_startup_directories(self) -> Set[str]:
        """Scrape German startup directories for health companies"""
        print("   🇩🇪 German Startup Directories")
        companies = set()
        
        directories = [
            "https://www.deutsche-startups.de/category/health/",
            "https://startup-directory.de/startups?category=health",
            "https://www.gruenderszene.de/datenbank?categories=health",
            "https://www.startbase.de/search?q=health",
            "https://www.berlin-startup-jobs.com/companies?categories=healthcare",
            "https://www.healthcapital.de/unternehmen/",
            "https://www.health-innovation-hub.de/portfolio/"
        ]
        
        for directory in directories:
            try:
                print(f"      📋 Scraping: {urlparse(directory).netloc}")
                response = self.session.get(directory, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract all links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Convert relative URLs
                        if href.startswith('/'):
                            href = urljoin(directory, href)
                        
                        # Check if it's an external company website
                        if (href.startswith('http') and 
                            self._is_external_company_url(href, directory) and
                            self._is_healthcare_company(href, link.get_text())):
                            companies.add(href)
                    
                    # Extract URLs from text content  
                    text_urls = self._extract_urls_from_text(response.text)
                    for url in text_urls:
                        if (self._is_external_company_url(url, directory) and
                            self._is_healthcare_company(url)):
                            companies.add(url)
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"      ⚠️ Error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_digital_health_platforms(self) -> Set[str]:
        """Scrape digital health specific platforms"""
        print("   💻 Digital Health Platforms")
        companies = set()
        
        platforms = [
            "https://www.healthcarestartuphub.de/startups",
            "https://www.digitale-gesundheit.de/unternehmen/",
            "https://digital-health-germany.de/companies/",
            "https://www.e-health-com.de/unternehmen/",
            "https://www.bmwi.de/Redaktion/DE/Dossier/digital-health.html",
            "https://www.health-innovation-portal.de/unternehmen/",
            "https://www.medica.de/de/Aussteller_Produkte/Ausstellerverzeichnis"
        ]
        
        for platform in platforms:
            try:
                print(f"      💻 Scraping: {urlparse(platform).netloc}")
                response = self.session.get(platform, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for company links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        if href.startswith('/'):
                            href = urljoin(platform, href)
                        
                        if (href.startswith('http') and 
                            self._is_external_company_url(href, platform) and
                            self._is_healthcare_company(href, link.get_text())):
                            companies.add(href)
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"      ⚠️ Error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_accelerator_portfolios(self) -> Set[str]:
        """Scrape health accelerator and incubator portfolios"""
        print("   🚀 Health Accelerators & Incubators")
        companies = set()
        
        accelerators = [
            "https://www.rocket-internet.com/companies/",
            "https://www.techstars.com/portfolio",
            "https://www.plug-and-play.com/portfolio/",
            "https://www.healthinnovationhub.de/portfolio/",
            "https://www.astrazeneca.de/innovation/innovation-challenges.html",
            "https://www.boehringer-ingelheim.com/innovation",
            "https://www.roche.de/innovation/partnering/",
            "https://www.bayer.de/innovation/",
            "https://www.merck.de/innovation/"
        ]
        
        for accelerator in accelerators:
            try:
                print(f"      🚀 Scraping: {urlparse(accelerator).netloc}")
                response = self.session.get(accelerator, timeout=15)
                
                if response.status_code == 200:
                    # Extract URLs from text content
                    text_urls = self._extract_urls_from_text(response.text)
                    for url in text_urls:
                        if (self._is_external_company_url(url, accelerator) and
                            self._is_healthcare_company(url)):
                            companies.add(url)
                
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(f"      ⚠️ Error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_healthcare_conferences(self) -> Set[str]:
        """Scrape healthcare conference exhibitor lists"""
        print("   🎪 Healthcare Conferences")  
        companies = set()
        
        conferences = [
            "https://www.medica.de/de/Aussteller_Produkte/Ausstellerverzeichnis",
            "https://www.dmea.de/de/aussteller-produkte/ausstellerverzeichnis/",
            "https://www.healthcareunbound.com/exhibitors/",
            "https://www.conhit.de/de/aussteller/ausstellerverzeichnis/",
            "https://www.digital-health-world.de/aussteller/"
        ]
        
        for conference in conferences:
            try:
                print(f"      🎪 Scraping: {urlparse(conference).netloc}")
                response = self.session.get(conference, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for exhibitor company links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        if href.startswith('/'):
                            href = urljoin(conference, href)
                        
                        if (href.startswith('http') and 
                            self._is_external_company_url(href, conference) and
                            self._is_healthcare_company(href, link.get_text())):
                            companies.add(href)
                
                time.sleep(random.uniform(4, 7))
                
            except Exception as e:
                print(f"      ⚠️ Error: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def scrape_alternative_search_engines(self) -> Set[str]:
        """Use alternative search engines that might be less protected"""
        print("   🔍 Alternative Search Engines")
        companies = set()
        
        # Alternative search engines  
        search_engines = [
            ("https://duckduckgo.com/html/?q=", "german healthcare startups"),
            ("https://duckduckgo.com/html/?q=", "digital health germany"),
            ("https://duckduckgo.com/html/?q=", "medtech startups deutschland"),
            ("https://www.bing.com/search?q=", "health tech companies germany"),
            ("https://www.bing.com/search?q=", "digital health deutschland"),
        ]
        
        for search_base, query in search_engines:
            try:
                print(f"      🔍 Searching: {query}")
                search_url = f"{search_base}{quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract search result links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Clean up search result URLs
                        if href.startswith('http') and self._is_healthcare_company(href, link.get_text()):
                            companies.add(href)
                
                time.sleep(random.uniform(5, 10))  # Longer delays for search engines
                
            except Exception as e:
                print(f"      ⚠️ Search failed: {str(e)[:50]}")
                continue
        
        print(f"      ✅ Found {len(companies)} companies")
        return companies

    def _is_external_company_url(self, url: str, source_url: str) -> bool:
        """Check if URL is external company website (not the source site)"""
        try:
            url_domain = urlparse(url).netloc.replace('www.', '')
            source_domain = urlparse(source_url).netloc.replace('www.', '')
            return url_domain != source_domain and len(url_domain) > 4
        except:
            return False

    def _extract_urls_from_text(self, text: str) -> Set[str]:
        """Extract URLs from text content with better patterns"""
        url_patterns = [
            r'https?://[^\s<>"\']+\.[a-z]{2,}',
            r'www\.[^\s<>"\']+\.[a-z]{2,}',
            r'[a-zA-Z0-9.-]+\.(?:com|de|org|net|eu|tech|ai|health|care)',
        ]
        
        urls = set()
        for pattern in url_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean and normalize URL
                url = match.rstrip('.,;:!?)')
                if not url.startswith('http'):
                    url = f"https://{url}"
                try:
                    parsed = urlparse(url)
                    if parsed.netloc and len(parsed.netloc) > 4:
                        urls.add(url)
                except:
                    continue
        
        return urls

    def validate_user_companies(self) -> Dict[str, bool]:
        """Validate the companies the user provided"""
        print("🔍 Validating user-provided companies...")
        results = {}
        
        for url in self.verified_companies:
            try:
                print(f"   🔍 Checking: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('title')
                    title_text = title.text if title else ""
                    
                    # Check if it's actually a healthcare company
                    is_healthcare = self._is_healthcare_company(url, title_text)
                    results[url] = is_healthcare
                    
                    if is_healthcare:
                        print(f"      ✅ Valid healthcare company: {title_text[:50]}")
                    else:
                        print(f"      ❌ Not healthcare: {title_text[:50]}")
                else:
                    results[url] = False
                    print(f"      ❌ Not accessible (status {response.status_code})")
                
                time.sleep(1)
                
            except Exception as e:
                results[url] = False
                print(f"      ❌ Error: {str(e)[:50]}")
        
        valid_count = sum(1 for valid in results.values() if valid)
        print(f"✅ Validation complete: {valid_count}/{len(results)} companies are valid")
        
        return results

    def run_improved_discovery(self) -> List[str]:
        """Run improved healthcare discovery"""
        print("🚀 IMPROVED HEALTHCARE WEB SCRAPER")
        print("=" * 80)
        print("🎯 Focused on German digital health companies")
        print("🔍 Using specialized healthcare directories and platforms")
        print("📊 Starting with user-verified companies as seed data")
        print()
        
        start_time = time.time()
        
        # 1. Validate user companies first
        print("🔍 Phase 1: Validate User Companies")
        validation_results = self.validate_user_companies()
        valid_user_companies = {url for url, valid in validation_results.items() if valid}
        self.discovered_companies.update(valid_user_companies)
        
        # 2. German startup directories
        print("\n🔍 Phase 2: German Startup Discovery")
        try:
            startup_results = self.scrape_german_startup_directories()
            self.discovered_companies.update(startup_results)
        except Exception as e:
            print(f"   ⚠️ Startup scraping failed: {str(e)[:50]}")
        
        # 3. Digital health platforms
        print("\n🔍 Phase 3: Digital Health Platforms")
        try:
            platform_results = self.scrape_digital_health_platforms()
            self.discovered_companies.update(platform_results)
        except Exception as e:
            print(f"   ⚠️ Platform scraping failed: {str(e)[:50]}")
        
        # 4. Accelerator portfolios
        print("\n🔍 Phase 4: Accelerator Portfolios")
        try:
            accelerator_results = self.scrape_accelerator_portfolios()
            self.discovered_companies.update(accelerator_results)
        except Exception as e:
            print(f"   ⚠️ Accelerator scraping failed: {str(e)[:50]}")
        
        # 5. Healthcare conferences
        print("\n🔍 Phase 5: Healthcare Conferences")
        try:
            conference_results = self.scrape_healthcare_conferences()
            self.discovered_companies.update(conference_results)
        except Exception as e:
            print(f"   ⚠️ Conference scraping failed: {str(e)[:50]}")
        
        # 6. Alternative search engines
        print("\n🔍 Phase 6: Alternative Search Engines")
        try:
            search_results = self.scrape_alternative_search_engines()
            self.discovered_companies.update(search_results)
        except Exception as e:
            print(f"   ⚠️ Search scraping failed: {str(e)[:50]}")
        
        # Clean and deduplicate
        cleaned_companies = self._clean_and_deduplicate(list(self.discovered_companies))
        
        runtime = time.time() - start_time
        
        print(f"\n🎉 IMPROVED DISCOVERY COMPLETE!")
        print("=" * 80)
        print(f"📊 RESULTS:")
        print(f"   Companies discovered: {len(cleaned_companies)}")
        print(f"   User-verified companies: {len(valid_user_companies)}")
        print(f"   Newly discovered: {len(cleaned_companies) - len(valid_user_companies)}")
        print(f"   Runtime: {runtime:.1f} seconds")
        print(f"   Sources: German startups, Digital health, Accelerators, Conferences, Search")
        
        return cleaned_companies

    def _clean_and_deduplicate(self, companies: List[str]) -> List[str]:
        """Clean and deduplicate company list"""
        cleaned = []
        seen_domains = set()
        
        for url in companies:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '').lower()
                
                if domain not in seen_domains and len(domain) > 4:
                    seen_domains.add(domain)
                    cleaned.append(url)
            except:
                continue
        
        return cleaned

    def save_results(self, companies: List[str]):
        """Save discovered companies"""
        if not companies:
            print("❌ No companies to save")
            return
        
        print(f"\n💾 Saving {len(companies)} companies...")
        
        # Save to CSV with additional info
        csv_filename = "improved_discovered_companies.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Domain', 'Country', 'User_Verified'])
            
            for url in companies:
                try:
                    domain = urlparse(url).netloc.replace('www.', '')
                    country = 'Germany' if '.de' in domain else 'International'
                    user_verified = 'Yes' if url in self.verified_companies else 'No'
                    writer.writerow([url, domain, country, user_verified])
                except:
                    continue
        
        # Save to JSON
        json_filename = "improved_discovered_companies.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'discovery_method': 'Improved Web Scraping',
                'total_companies': len(companies),
                'user_verified_count': len([c for c in companies if c in self.verified_companies]),
                'companies': companies
            }, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to {csv_filename}")
        print(f"   ✅ Saved to {json_filename}")


if __name__ == "__main__":
    print("🚀 IMPROVED Healthcare Web Scraper")
    print("Focused on German digital health companies!")
    print()
    
    scraper = ImprovedHealthcareScraper()
    companies = scraper.run_improved_discovery()
    
    if companies:
        print(f"\n📊 DISCOVERED COMPANIES (first 30):")
        for i, company in enumerate(companies[:30], 1):
            marker = "👤" if company in scraper.verified_companies else "🆕"
            print(f"{i:2d}. {marker} {company}")
        
        if len(companies) > 30:
            print(f"... and {len(companies) - 30} more!")
        
        scraper.save_results(companies)
        
        print(f"\n🎉 SUCCESS!")
        print(f"Found {len(companies)} healthcare companies")
        print("👤 = User verified, 🆕 = Newly discovered")
    else:
        print("\n😞 No companies discovered")