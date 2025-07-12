#!/usr/bin/env python3
"""
Enhanced Healthcare Company Directory Scraper
Scrapes multiple high-quality German healthcare company directories
"""

import requests
import time
import re
import json
import csv
from typing import List, Dict, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HealthcareCompany:
    name: str
    website: str = ""
    description: str = ""
    location: str = ""
    category: str = ""
    source_directory: str = ""
    employees: str = ""
    funding: str = ""
    city: str = ""
    founded: str = ""
    phone: str = ""
    email: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class EnhancedHealthcareScraper:
    """
    Enhanced scraper for German healthcare company directories
    """
    
    def __init__(self, use_selenium: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.use_selenium = use_selenium
        self.driver = None
        if use_selenium:
            self._setup_selenium()
        
        self.known_companies = self._load_known_companies()
        self.extracted_companies = []
        
    def _setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
    
    def _load_known_companies(self) -> Set[str]:
        """Load known companies to avoid duplicates"""
        known_websites = {
            'acalta.de', 'actimi.com', 'emmora.de', 'alfa-ai.com', 'apheris.com',
            'aporize.com', 'arztlena.com', 'getnutrio.com', 'auta.health',
            'visioncheckout.com', 'avayl.tech', 'avimedical.com', 'becureglobal.com',
            'bellehealth.co', 'biotx.ai', 'brainjo.de', 'brea.app', 'breathment.com',
            'caona.eu', 'careanimations.de', 'sfs-healthcare.com', 'climedo.de',
            'cliniserve.de', 'cogthera.de', 'comuny.de', 'curecurve.de',
            'cynteract.com', 'healthmeapp.de', 'deepeye.ai', 'deepmentation.ai',
            'denton-systems.de', 'derma2go.com', 'dianovi.com', 'dopavision.com',
            'dpv-analytics.com', 'ecovery.de', 'elixionmedical.com', 'empident.de',
            'eye2you.ai', 'fitwhit.de', 'floy.com', 'fyzo.de', 'gesund.de',
            'glaice.de', 'gleea.de', 'guidecare.de', 'apodienste.com',
            'help-app.de', 'heynanny.com', 'incontalert.de', 'informme.info',
            'kranushealth.com'
        }
        return known_websites
    
    def extract_from_bvmed(self) -> List[HealthcareCompany]:
        """Extract from BVMed - German Medical Technology Association"""
        companies = []
        
        try:
            logger.info("Scraping BVMed directory...")
            url = "https://www.bvmed.de/de/unternehmen/mitgliedsunternehmen"
            
            if self.use_selenium and self.driver:
                self.driver.get(url)
                time.sleep(3)
                
                # Look for company listings
                company_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "div.company-item, div.member-item, div.company-card, tr.company-row")
                
                for element in company_elements:
                    try:
                        # Extract company name
                        name_element = element.find_element(By.CSS_SELECTOR, 
                            "h3, h4, .company-name, .member-name, td.name")
                        name = name_element.text.strip()
                        
                        if not self._is_valid_company_name(name):
                            continue
                        
                        # Extract website
                        website = ""
                        try:
                            website_element = element.find_element(By.CSS_SELECTOR, 
                                "a[href^='http'], .website a, .url a")
                            website = website_element.get_attribute('href')
                        except NoSuchElementException:
                            pass
                        
                        # Extract description
                        description = ""
                        try:
                            desc_element = element.find_element(By.CSS_SELECTOR, 
                                ".description, .summary, p")
                            description = desc_element.text.strip()[:300]
                        except NoSuchElementException:
                            pass
                        
                        # Extract location
                        location = "Germany"
                        try:
                            location_element = element.find_element(By.CSS_SELECTOR, 
                                ".location, .address, .city")
                            location = location_element.text.strip()
                        except NoSuchElementException:
                            pass
                        
                        if self._is_new_company(website):
                            company = HealthcareCompany(
                                name=name,
                                website=website,
                                description=description,
                                location=location,
                                source_directory=url,
                                category="Medical Technology",
                                tags=["BVMed", "Medical Device", "German"]
                            )
                            companies.append(company)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting company from BVMed element: {e}")
                        continue
            
            logger.info(f"Extracted {len(companies)} companies from BVMed")
            
        except Exception as e:
            logger.error(f"Error scraping BVMed: {str(e)}")
        
        return companies
    
    def extract_from_spectaris(self) -> List[HealthcareCompany]:
        """Extract from SPECTARIS - German Industry Association"""
        companies = []
        
        try:
            logger.info("Scraping SPECTARIS directory...")
            url = "https://www.spectaris.de/mitglieder/"
            
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for member listings
                member_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'member|company|mitglied', re.I))
                
                for element in member_elements:
                    try:
                        # Extract company name
                        name_element = element.find(['h3', 'h4', 'td', 'strong'])
                        if not name_element:
                            continue
                        
                        name = name_element.get_text(strip=True)
                        if not self._is_valid_company_name(name):
                            continue
                        
                        # Extract website
                        website = ""
                        website_link = element.find('a', href=re.compile(r'^https?://'))
                        if website_link:
                            website = website_link.get('href')
                        
                        # Extract description
                        description = element.get_text(strip=True)[:300]
                        
                        if self._is_new_company(website):
                            company = HealthcareCompany(
                                name=name,
                                website=website,
                                description=description,
                                location="Germany",
                                source_directory=url,
                                category="Optics/Medical Technology",
                                tags=["SPECTARIS", "Medical Technology", "German"]
                            )
                            companies.append(company)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting company from SPECTARIS: {e}")
                        continue
            
            logger.info(f"Extracted {len(companies)} companies from SPECTARIS")
            
        except Exception as e:
            logger.error(f"Error scraping SPECTARIS: {str(e)}")
        
        return companies
    
    def extract_from_digital_health_hub(self) -> List[HealthcareCompany]:
        """Extract from Digital Health Hub Berlin"""
        companies = []
        
        try:
            logger.info("Scraping Digital Health Hub...")
            url = "https://digitalhealthhub.de/startups/"
            
            if self.use_selenium and self.driver:
                self.driver.get(url)
                time.sleep(3)
                
                # Look for startup cards
                startup_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "div.startup-card, div.company-card, div.member-card")
                
                for element in startup_elements:
                    try:
                        # Extract company name
                        name_element = element.find_element(By.CSS_SELECTOR, 
                            "h3, h4, .startup-name, .company-name")
                        name = name_element.text.strip()
                        
                        if not self._is_valid_company_name(name):
                            continue
                        
                        # Extract website
                        website = ""
                        try:
                            website_element = element.find_element(By.CSS_SELECTOR, 
                                "a[href^='http'], .website a")
                            website = website_element.get_attribute('href')
                        except NoSuchElementException:
                            pass
                        
                        # Extract description
                        description = ""
                        try:
                            desc_element = element.find_element(By.CSS_SELECTOR, 
                                ".description, .summary, p")
                            description = desc_element.text.strip()[:300]
                        except NoSuchElementException:
                            pass
                        
                        if self._is_new_company(website):
                            company = HealthcareCompany(
                                name=name,
                                website=website,
                                description=description,
                                location="Berlin",
                                source_directory=url,
                                category="Digital Health",
                                tags=["Digital Health Hub", "Startup", "Berlin"]
                            )
                            companies.append(company)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting startup from Digital Health Hub: {e}")
                        continue
            
            logger.info(f"Extracted {len(companies)} companies from Digital Health Hub")
            
        except Exception as e:
            logger.error(f"Error scraping Digital Health Hub: {str(e)}")
        
        return companies
    
    def extract_from_biom_cluster(self) -> List[HealthcareCompany]:
        """Extract from BioM - Bavaria Biotech Cluster"""
        companies = []
        
        try:
            logger.info("Scraping BioM cluster directory...")
            url = "https://www.bio-m.org/de/unternehmen/"
            
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for company listings
                company_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'company|unternehmen|member', re.I))
                
                for element in company_elements:
                    try:
                        # Extract company name
                        name_element = element.find(['h3', 'h4', 'td', 'strong', 'a'])
                        if not name_element:
                            continue
                        
                        name = name_element.get_text(strip=True)
                        if not self._is_valid_company_name(name):
                            continue
                        
                        # Extract website
                        website = ""
                        website_link = element.find('a', href=re.compile(r'^https?://'))
                        if website_link:
                            website = website_link.get('href')
                        
                        # Extract description
                        description = element.get_text(strip=True)[:300]
                        
                        if self._is_new_company(website):
                            company = HealthcareCompany(
                                name=name,
                                website=website,
                                description=description,
                                location="Bavaria",
                                source_directory=url,
                                category="Biotechnology",
                                tags=["BioM", "Biotech", "Bavaria"]
                            )
                            companies.append(company)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting company from BioM: {e}")
                        continue
            
            logger.info(f"Extracted {len(companies)} companies from BioM")
            
        except Exception as e:
            logger.error(f"Error scraping BioM: {str(e)}")
        
        return companies
    
    def extract_from_ehealth_initiative(self) -> List[HealthcareCompany]:
        """Extract from eHealth Initiative Germany"""
        companies = []
        
        try:
            logger.info("Scraping eHealth Initiative...")
            url = "https://www.ehealth-initiative.de/mitglieder/"
            
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for member listings
                member_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'member|mitglied|company', re.I))
                
                for element in member_elements:
                    try:
                        # Extract company name
                        name_element = element.find(['h3', 'h4', 'td', 'strong', 'a'])
                        if not name_element:
                            continue
                        
                        name = name_element.get_text(strip=True)
                        if not self._is_valid_company_name(name):
                            continue
                        
                        # Extract website
                        website = ""
                        website_link = element.find('a', href=re.compile(r'^https?://'))
                        if website_link:
                            website = website_link.get('href')
                        
                        # Extract description
                        description = element.get_text(strip=True)[:300]
                        
                        if self._is_new_company(website):
                            company = HealthcareCompany(
                                name=name,
                                website=website,
                                description=description,
                                location="Germany",
                                source_directory=url,
                                category="eHealth",
                                tags=["eHealth Initiative", "Digital Health", "German"]
                            )
                            companies.append(company)
                            
                    except Exception as e:
                        logger.debug(f"Error extracting company from eHealth Initiative: {e}")
                        continue
            
            logger.info(f"Extracted {len(companies)} companies from eHealth Initiative")
            
        except Exception as e:
            logger.error(f"Error scraping eHealth Initiative: {str(e)}")
        
        return companies
    
    def extract_from_startup_blogs(self) -> List[HealthcareCompany]:
        """Extract from healthcare startup blogs and articles"""
        companies = []
        
        blog_urls = [
            "https://www.healthtech.de/startups/",
            "https://www.e-health-com.de/details-news/digital-health-startups-in-deutschland/",
            "https://www.digitale-gesundheit.de/startups/",
            "https://www.medtech-zwo.de/nachrichten/maerkte-und-trends/startup-landscape-deutschland.html"
        ]
        
        for url in blog_urls:
            try:
                logger.info(f"Scraping healthcare blog: {urlparse(url).netloc}")
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for company mentions
                    company_mentions = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
                    
                    for mention in company_mentions:
                        text = mention.get_text(strip=True)
                        
                        if self._is_valid_company_name(text):
                            # Look for nearby links
                            parent = mention.parent
                            website = ""
                            description = ""
                            
                            if parent:
                                # Look for links
                                links = parent.find_all('a', href=True)
                                for link in links:
                                    href = link.get('href')
                                    if self._is_company_website(href):
                                        website = href
                                        break
                                
                                # Get description
                                desc_text = parent.get_text(strip=True)
                                if len(desc_text) > len(text):
                                    description = desc_text[:300]
                            
                            if self._is_new_company(website):
                                company = HealthcareCompany(
                                    name=text,
                                    website=website,
                                    description=description,
                                    location="Germany",
                                    source_directory=url,
                                    category="Healthcare Startup",
                                    tags=["Blog Mention", "Startup", "German"]
                                )
                                companies.append(company)
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error scraping {urlparse(url).netloc}: {str(e)}")
        
        return companies
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Check if text looks like a valid company name"""
        if not name or len(name) < 3 or len(name) > 100:
            return False
        
        # Skip common non-company words
        skip_words = [
            'read more', 'click here', 'learn more', 'contact', 'about',
            'home', 'news', 'blog', 'search', 'menu', 'login', 'register',
            'privacy', 'terms', 'imprint', 'impressum', 'datenschutz',
            'mitglied', 'member', 'directory', 'verzeichnis'
        ]
        
        name_lower = name.lower()
        for skip in skip_words:
            if skip in name_lower:
                return False
        
        # Look for company indicators
        company_indicators = [
            'gmbh', 'ag', 'inc', 'ltd', 'corp', 'llc', 'group', 'systems',
            'solutions', 'technologies', 'health', 'medical', 'care',
            'tech', 'bio', 'pharma', 'therapeutics', 'diagnostics',
            'medizin', 'gesundheit', 'technologie'
        ]
        
        has_indicator = any(indicator in name_lower for indicator in company_indicators)
        
        # Or looks like a proper name
        looks_proper = name[0].isupper() and not name.isupper()
        
        # Should have letters
        has_letters = any(c.isalpha() for c in name)
        
        # Not too many numbers
        num_count = sum(1 for c in name if c.isdigit())
        mostly_letters = num_count < len(name) / 2
        
        return has_letters and mostly_letters and (has_indicator or looks_proper)
    
    def _is_company_website(self, url: str) -> bool:
        """Check if URL is a company website"""
        if not url or len(url) < 8:
            return False
        
        # Skip non-company domains
        skip_domains = [
            'google.', 'facebook.', 'twitter.', 'linkedin.', 'youtube.',
            'github.', 'crunchbase.', 'xing.', 'wikipedia.', 'blog.',
            'medium.', 'news.', 'instagram.', 'pinterest.'
        ]
        
        url_lower = url.lower()
        for skip in skip_domains:
            if skip in url_lower:
                return False
        
        # Must have company TLD
        company_tlds = ['.com', '.de', '.org', '.net', '.eu', '.co.uk', '.co', '.io', '.ai', '.health']
        has_tld = any(tld in url_lower for tld in company_tlds)
        
        return has_tld
    
    def _is_new_company(self, website: str) -> bool:
        """Check if company is new (not in known list)"""
        if not website:
            return True
        
        domain = self._extract_domain(website)
        return domain not in self.known_companies
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def enhance_companies_with_details(self, companies: List[HealthcareCompany]) -> List[HealthcareCompany]:
        """Enhance companies with additional details"""
        enhanced = []
        
        logger.info(f"Enhancing {len(companies)} companies with additional details...")
        
        for i, company in enumerate(companies):
            if i % 25 == 0:
                logger.info(f"Enhanced {i}/{len(companies)} companies...")
            
            enhanced_company = company
            
            # Try to find website if missing
            if not company.website:
                website = self._find_company_website(company.name)
                if website:
                    enhanced_company.website = website
            
            # Clean up name
            enhanced_company.name = self._clean_company_name(company.name)
            
            # Extract city from location
            if company.location and not company.city:
                enhanced_company.city = self._extract_city(company.location)
            
            enhanced.append(enhanced_company)
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(0.5)
        
        return enhanced
    
    def _find_company_website(self, company_name: str) -> str:
        """Try to find company website"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        
        potential_urls = [
            f"https://www.{clean_name}.de",
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.de",
            f"https://{clean_name}.com"
        ]
        
        for url in potential_urls:
            try:
                response = self.session.head(url, timeout=3)
                if response.status_code in [200, 301, 302]:
                    return url
            except:
                continue
        
        return ""
    
    def _clean_company_name(self, name: str) -> str:
        """Clean up company name"""
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove common prefixes
        prefixes = ['unternehmen:', 'company:', 'startup:', 'member:']
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name
    
    def _extract_city(self, location: str) -> str:
        """Extract city from location string"""
        if not location:
            return ""
        
        # Common German cities
        cities = [
            'Berlin', 'Hamburg', 'München', 'Munich', 'Köln', 'Cologne',
            'Frankfurt', 'Stuttgart', 'Düsseldorf', 'Dortmund', 'Essen',
            'Leipzig', 'Bremen', 'Dresden', 'Hannover', 'Nürnberg'
        ]
        
        for city in cities:
            if city.lower() in location.lower():
                return city
        
        return location
    
    def run_extraction(self) -> List[HealthcareCompany]:
        """Run the complete extraction process"""
        logger.info("🚀 STARTING ENHANCED HEALTHCARE DIRECTORY EXTRACTION")
        logger.info("=" * 80)
        
        all_companies = []
        
        # Define extraction methods
        extraction_methods = [
            ("BVMed - Medical Technology Association", self.extract_from_bvmed),
            ("SPECTARIS - Industry Association", self.extract_from_spectaris),
            ("Digital Health Hub Berlin", self.extract_from_digital_health_hub),
            ("BioM - Bavaria Biotech Cluster", self.extract_from_biom_cluster),
            ("eHealth Initiative Germany", self.extract_from_ehealth_initiative),
            ("Healthcare Startup Blogs", self.extract_from_startup_blogs)
        ]
        
        # Execute extractions
        for phase_name, method in extraction_methods:
            logger.info(f"🔍 Phase: {phase_name}")
            try:
                companies = method()
                all_companies.extend(companies)
                logger.info(f"✅ Extracted {len(companies)} companies from {phase_name}")
            except Exception as e:
                logger.error(f"❌ Error in {phase_name}: {str(e)}")
            
            time.sleep(5)  # Rate limiting between phases
        
        # Remove duplicates
        unique_companies = self._remove_duplicates(all_companies)
        logger.info(f"📊 Total unique companies: {len(unique_companies)}")
        
        # Enhance companies
        logger.info("🔍 Enhancing companies with additional details...")
        enhanced_companies = self.enhance_companies_with_details(unique_companies)
        
        return enhanced_companies
    
    def _remove_duplicates(self, companies: List[HealthcareCompany]) -> List[HealthcareCompany]:
        """Remove duplicate companies"""
        seen = set()
        unique = []
        
        for company in companies:
            # Create key for deduplication
            key = (
                company.name.lower().strip(),
                self._extract_domain(company.website)
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(company)
        
        return unique
    
    def save_results(self, companies: List[HealthcareCompany], output_dir: str = "output"):
        """Save extraction results"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Convert to dict format
        company_dicts = []
        for company in companies:
            company_dict = asdict(company)
            company_dict['domain'] = self._extract_domain(company.website)
            company_dicts.append(company_dict)
        
        # Save to CSV
        csv_file = output_path / "enhanced_healthcare_companies.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON
        json_file = output_path / "enhanced_healthcare_companies.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Results saved to {csv_file} and {json_file}")
        
        return company_dicts
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main execution"""
    scraper = EnhancedHealthcareScraper(use_selenium=True)
    
    start_time = time.time()
    companies = scraper.run_extraction()
    runtime = time.time() - start_time
    
    if companies:
        # Save results
        company_dicts = scraper.save_results(companies)
        
        # Statistics
        with_websites = sum(1 for c in company_dicts if c['website'])
        german_companies = sum(1 for c in company_dicts if 'germany' in c['location'].lower())
        
        # Count by source
        sources = {}
        for c in company_dicts:
            source = urlparse(c['source_directory']).netloc
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("🎉 ENHANCED EXTRACTION COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"📊 FINAL RESULTS:")
        logger.info(f"   Total companies: {len(companies)}")
        logger.info(f"   With websites: {with_websites} ({with_websites/len(companies)*100:.1f}%)")
        logger.info(f"   German companies: {german_companies}")
        logger.info(f"   Runtime: {runtime:.1f} seconds")
        
        logger.info("📈 BREAKDOWN BY SOURCE:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"   {source}: {count} companies")
        
        # Show sample companies
        logger.info("\n🏢 SAMPLE COMPANIES:")
        for i, company in enumerate(companies[:10], 1):
            logger.info(f"   {i}. {company.name}")
            if company.website:
                logger.info(f"      🌐 {company.website}")
            if company.description:
                logger.info(f"      📝 {company.description[:60]}...")
            logger.info(f"      📍 {company.location}")
            logger.info(f"      🏷️  {', '.join(company.tags)}")
    else:
        logger.error("❌ No companies extracted")

if __name__ == "__main__":
    main()