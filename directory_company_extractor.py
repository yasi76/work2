#!/usr/bin/env python3
"""
Directory Company Extractor
Scrapes discovered directory URLs to extract individual healthcare companies
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExtractedCompany:
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
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class DirectoryCompanyExtractor:
    """
    Extracts individual companies from healthcare directory pages
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.extracted_companies = []
        self.known_companies = self._load_known_companies()
        
    def _load_known_companies(self) -> Set[str]:
        """Load known companies to avoid duplicates"""
        known_websites = {
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
        }
        return {self._normalize_domain(url) for url in known_websites}
    
    def _normalize_domain(self, url: str) -> str:
        """Normalize domain for comparison"""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            return f"{parsed.netloc.lower()}"
        except:
            return ""
    
    def extract_from_medicalstartups_org(self) -> List[ExtractedCompany]:
        """Extract companies from medicalstartups.org Germany page"""
        companies = []
        
        try:
            logger.info("Scraping medicalstartups.org...")
            url = "https://www.medicalstartups.org/country/Germany/"
            
            response = self.session.get(url, timeout=20)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for company listings in different structures
                company_selectors = [
                    'div.company-card',
                    'div.startup-card',
                    'div.listing-item',
                    'article.company',
                    'div.company-profile',
                    '[class*="company"]',
                    '[class*="startup"]'
                ]
                
                for selector in company_selectors:
                    elements = soup.select(selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        for element in elements:
                            company = self._extract_company_from_element(element, url)
                            if company:
                                companies.append(company)
                        break
                
                # Fallback: look for external links
                if not companies:
                    external_links = soup.find_all('a', href=True)
                    for link in external_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        if self._is_company_link(href, text):
                            company = ExtractedCompany(
                                name=text,
                                website=href,
                                source_directory=url,
                                location="Germany",
                                category="Healthcare/Medical"
                            )
                            companies.append(company)
                
                logger.info(f"Found {len(companies)} companies from medicalstartups.org")
                
        except Exception as e:
            logger.error(f"Error scraping medicalstartups.org: {str(e)}")
        
        return companies
    
    def extract_from_startup_directories(self) -> List[ExtractedCompany]:
        """Extract from multiple startup directories"""
        companies = []
        
        directories = [
            {
                'url': 'https://www.rocket-internet.com/our-companies/',
                'name': 'Rocket Internet',
                'selectors': ['div.company-card', 'div.portfolio-item']
            },
            {
                'url': 'https://www.gtec.at/portfolio/',
                'name': 'GTEC',
                'selectors': ['div.portfolio-item', 'div.company-card']
            },
            {
                'url': 'https://www.berlin-startup-jobs.com/companies?industries=health',
                'name': 'Berlin Startup Jobs',
                'selectors': ['div.company-card', 'div.job-company']
            },
            {
                'url': 'https://www.startup-map.de/health',
                'name': 'Startup Map',
                'selectors': ['div.startup-card', 'div.company-item']
            }
        ]
        
        for directory in directories:
            try:
                logger.info(f"Scraping {directory['name']}...")
                response = self.session.get(directory['url'], timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for selector in directory['selectors']:
                        elements = soup.select(selector)
                        if elements:
                            for element in elements:
                                company = self._extract_company_from_element(element, directory['url'])
                                if company:
                                    companies.append(company)
                            break
                
                time.sleep(3)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping {directory['name']}: {str(e)}")
        
        return companies
    
    def extract_from_healthtech_blogs(self) -> List[ExtractedCompany]:
        """Extract from healthtech blog articles and lists"""
        companies = []
        
        blog_urls = [
            "https://www.healthtech.de/startups/",
            "https://www.e-health-com.de/details-news/digital-health-startups-in-deutschland/",
            "https://www.digitale-gesundheit.de/startups/",
            "https://www.heise.de/news/Die-vielversprechendsten-Health-Tech-Startups-in-Deutschland-6085734.html",
            "https://www.manager-magazin.de/unternehmen/artikel/health-tech-startups-diese-unternehmen-revolutionieren-die-gesundheitsbranche-a-1289756.html",
            "https://www.gruenderszene.de/health-tech-startups-deutschland",
            "https://www.digital-health-startups.de/",
            "https://www.medtech-zwo.de/nachrichten/maerkte-und-trends/startup-landscape-deutschland.html"
        ]
        
        for url in blog_urls:
            try:
                logger.info(f"Scraping healthtech blog: {urlparse(url).netloc}")
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for company mentions in various formats
                    company_elements = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
                    
                    for element in company_elements:
                        text = element.get_text(strip=True)
                        
                        if self._is_valid_company_name(text):
                            # Look for nearby links or website info
                            parent = element.parent
                            website = ""
                            description = ""
                            
                            if parent:
                                # Look for links in the same section
                                links = parent.find_all('a', href=True)
                                for link in links:
                                    href = link.get('href')
                                    if self._is_company_link(href, text):
                                        website = href
                                        break
                                
                                # Get description
                                desc_text = parent.get_text(strip=True)
                                if len(desc_text) > len(text):
                                    description = desc_text[:300]
                            
                            company = ExtractedCompany(
                                name=text,
                                website=website,
                                description=description,
                                source_directory=url,
                                location="Germany",
                                category="HealthTech"
                            )
                            companies.append(company)
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error scraping {urlparse(url).netloc}: {str(e)}")
        
        return companies
    
    def extract_from_accelerator_portfolios(self) -> List[ExtractedCompany]:
        """Extract from accelerator and incubator portfolios"""
        companies = []
        
        accelerators = [
            {
                'url': 'https://www.rocket-internet.com/companies/',
                'name': 'Rocket Internet',
                'location': 'Berlin'
            },
            {
                'url': 'https://www.berlinstartupjobs.com/companies?industries=health',
                'name': 'Berlin Startup Jobs',
                'location': 'Berlin'
            },
            {
                'url': 'https://www.high-tech-gruenderfonds.de/portfolio/',
                'name': 'High-Tech Gründerfonds',
                'location': 'Germany'
            },
            {
                'url': 'https://www.techstars.com/portfolio?location=Berlin',
                'name': 'Techstars Berlin',
                'location': 'Berlin'
            }
        ]
        
        for accelerator in accelerators:
            try:
                logger.info(f"Scraping {accelerator['name']}...")
                response = self.session.get(accelerator['url'], timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for portfolio companies
                    portfolio_elements = soup.find_all(['div', 'article'], class_=re.compile(r'portfolio|company|startup', re.I))
                    
                    for element in portfolio_elements:
                        company = self._extract_company_from_element(element, accelerator['url'])
                        if company:
                            company.location = accelerator['location']
                            companies.append(company)
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error scraping {accelerator['name']}: {str(e)}")
        
        return companies
    
    def extract_from_funding_databases(self) -> List[ExtractedCompany]:
        """Extract from funding and investment databases"""
        companies = []
        
        funding_sources = [
            "https://www.crunchbase.com/hub/germany-health-care-companies",
            "https://www.dealroom.co/companies/f/company_type/anyof_startup_scaleup/locations/anyof_Germany/tags/anyof_health",
            "https://www.pitchbook.com/profiles/company/",
            "https://www.cbinsights.com/company/",
            "https://www.eu-startups.com/directory/country/germany/industry/health/"
        ]
        
        for url in funding_sources:
            try:
                logger.info(f"Scraping funding database: {urlparse(url).netloc}")
                response = self.session.get(url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for company listings
                    company_elements = soup.find_all(['div', 'article'], class_=re.compile(r'company|organization|startup', re.I))
                    
                    for element in company_elements:
                        company = self._extract_company_from_element(element, url)
                        if company:
                            companies.append(company)
                
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error scraping {urlparse(url).netloc}: {str(e)}")
        
        return companies
    
    def _extract_company_from_element(self, element, source_url: str) -> Optional[ExtractedCompany]:
        """Extract company information from a DOM element"""
        try:
            # Try to find company name
            name_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5',
                '.company-name', '.startup-name', '.name',
                'strong', 'b', 'a[href]'
            ]
            
            name = ""
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    if self._is_valid_company_name(name):
                        break
            
            if not name or not self._is_valid_company_name(name):
                return None
            
            # Try to find website
            website = ""
            website_selectors = [
                'a[href^="http"]',
                'a[href^="https"]',
                '.website a',
                '.url a'
            ]
            
            for selector in website_selectors:
                link_element = element.select_one(selector)
                if link_element:
                    href = link_element.get('href')
                    if self._is_company_link(href, name):
                        website = href
                        break
            
            # Get description
            description = ""
            desc_selectors = [
                '.description', '.summary', '.about',
                'p', '.content', '.text'
            ]
            
            for selector in desc_selectors:
                desc_element = element.select_one(selector)
                if desc_element:
                    desc_text = desc_element.get_text(strip=True)
                    if len(desc_text) > 20:
                        description = desc_text[:300]
                        break
            
            # Get location
            location = "Germany"  # Default
            location_selectors = [
                '.location', '.city', '.address',
                '[class*="location"]', '[class*="city"]'
            ]
            
            for selector in location_selectors:
                loc_element = element.select_one(selector)
                if loc_element:
                    loc_text = loc_element.get_text(strip=True)
                    if loc_text and len(loc_text) < 50:
                        location = loc_text
                        break
            
            # Check if we already have this company
            if website and self._normalize_domain(website) in self.known_companies:
                return None
            
            company = ExtractedCompany(
                name=name,
                website=website,
                description=description,
                location=location,
                source_directory=source_url,
                category="Healthcare/Medical"
            )
            
            return company
            
        except Exception as e:
            logger.error(f"Error extracting company from element: {str(e)}")
            return None
    
    def _is_company_link(self, url: str, text: str) -> bool:
        """Check if URL and text represent a company"""
        if not url or len(url) < 8:
            return False
        
        # Skip non-company domains
        skip_domains = [
            'google.', 'facebook.', 'twitter.', 'linkedin.', 'youtube.',
            'github.', 'crunchbase.', 'f6s.', 'angellist.', 'xing.',
            'wikipedia.', 'blog.', 'medium.', 'news.', 'reddit.',
            'instagram.', 'pinterest.', 'tiktok.', 'snapchat.'
        ]
        
        url_lower = url.lower()
        for skip in skip_domains:
            if skip in url_lower:
                return False
        
        # Must have company TLD
        company_tlds = ['.com', '.de', '.org', '.net', '.eu', '.co.uk', '.co', '.io', '.ai', '.health']
        has_tld = any(tld in url_lower for tld in company_tlds)
        
        # Text should look like a company name
        text_valid = len(text) > 2 and text.lower() not in [
            'website', 'visit', 'more', 'link', 'here', 'click', 'read',
            'learn', 'see', 'view', 'go', 'check', 'find'
        ]
        
        return has_tld and text_valid
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Check if text looks like a valid company name"""
        if not name or len(name) < 3 or len(name) > 100:
            return False
        
        # Skip common non-company words
        skip_words = [
            'read more', 'click here', 'learn more', 'contact', 'about',
            'home', 'news', 'blog', 'search', 'menu', 'login', 'register',
            'privacy', 'terms', 'imprint', 'impressum', 'datenschutz',
            'cookie', 'newsletter', 'subscribe', 'follow', 'share'
        ]
        
        name_lower = name.lower()
        for skip in skip_words:
            if skip in name_lower:
                return False
        
        # Look for company indicators
        company_indicators = [
            'gmbh', 'ag', 'inc', 'ltd', 'corp', 'llc', 'group', 'systems',
            'solutions', 'technologies', 'health', 'medical', 'care',
            'tech', 'bio', 'pharma', 'therapeutics', 'diagnostics'
        ]
        
        has_indicator = any(indicator in name_lower for indicator in company_indicators)
        
        # Or looks like a proper name (starts with capital)
        looks_proper = name[0].isupper() and not name.isupper()
        
        # Should have at least some letters
        has_letters = any(c.isalpha() for c in name)
        
        # Not too many numbers
        num_count = sum(1 for c in name if c.isdigit())
        mostly_letters = num_count < len(name) / 2
        
        return has_letters and mostly_letters and (has_indicator or looks_proper)
    
    def enhance_companies_with_validation(self, companies: List[ExtractedCompany]) -> List[ExtractedCompany]:
        """Validate and enhance company information"""
        enhanced = []
        
        logger.info(f"Enhancing {len(companies)} companies...")
        
        for i, company in enumerate(companies):
            if i % 50 == 0:
                logger.info(f"Enhanced {i}/{len(companies)} companies...")
            
            enhanced_company = company
            
            # Validate website if present
            if company.website:
                if not self._validate_website(company.website):
                    enhanced_company.website = ""
            
            # Try to find website if missing
            if not enhanced_company.website:
                found_website = self._find_company_website(company.name)
                if found_website:
                    enhanced_company.website = found_website
            
            # Clean up name
            enhanced_company.name = self._clean_company_name(company.name)
            
            # Add to enhanced list if valid
            if enhanced_company.name and len(enhanced_company.name) > 2:
                enhanced.append(enhanced_company)
            
            # Rate limiting
            if i % 20 == 0:
                time.sleep(1)
        
        return enhanced
    
    def _validate_website(self, url: str) -> bool:
        """Validate if website is accessible"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code in [200, 301, 302, 403]  # 403 might be blocking bots
        except:
            return False
    
    def _find_company_website(self, company_name: str) -> str:
        """Try to find company website"""
        # Generate potential URLs
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        
        potential_urls = [
            f"https://www.{clean_name}.com",
            f"https://www.{clean_name}.de",
            f"https://{clean_name}.com",
            f"https://{clean_name}.de",
            f"https://www.{clean_name}.health",
            f"https://www.{clean_name}.io"
        ]
        
        for url in potential_urls:
            if self._validate_website(url):
                return url
        
        return ""
    
    def _clean_company_name(self, name: str) -> str:
        """Clean up company name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name.strip())
        
        # Remove common prefixes/suffixes that aren't part of company name
        prefixes = ['startup:', 'company:', 'founded:', 'website:']
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name
    
    def run_directory_extraction(self) -> List[ExtractedCompany]:
        """Run the complete directory extraction process"""
        logger.info("🚀 STARTING DIRECTORY COMPANY EXTRACTION")
        logger.info("=" * 80)
        
        all_companies = []
        
        # Extract from different sources
        extraction_methods = [
            ("Medical Startups Directory", self.extract_from_medicalstartups_org),
            ("Startup Directories", self.extract_from_startup_directories),
            ("HealthTech Blogs", self.extract_from_healthtech_blogs),
            ("Accelerator Portfolios", self.extract_from_accelerator_portfolios),
            ("Funding Databases", self.extract_from_funding_databases)
        ]
        
        for phase_name, method in extraction_methods:
            logger.info(f"🔍 Phase: {phase_name}")
            try:
                companies = method()
                all_companies.extend(companies)
                logger.info(f"✅ Extracted {len(companies)} companies from {phase_name}")
            except Exception as e:
                logger.error(f"❌ Error in {phase_name}: {str(e)}")
            
            time.sleep(2)  # Rate limiting between phases
        
        # Remove duplicates
        unique_companies = self._remove_duplicates(all_companies)
        logger.info(f"📊 Total unique companies: {len(unique_companies)}")
        
        # Enhance companies
        logger.info("🔍 Enhancing companies with validation...")
        enhanced_companies = self.enhance_companies_with_validation(unique_companies)
        
        return enhanced_companies
    
    def _remove_duplicates(self, companies: List[ExtractedCompany]) -> List[ExtractedCompany]:
        """Remove duplicate companies"""
        seen = set()
        unique = []
        
        for company in companies:
            # Create a key for deduplication
            key = (
                company.name.lower().strip(),
                self._normalize_domain(company.website)
            )
            
            if key not in seen:
                seen.add(key)
                unique.append(company)
        
        return unique

def main():
    """Main execution"""
    extractor = DirectoryCompanyExtractor()
    
    start_time = time.time()
    companies = extractor.run_directory_extraction()
    runtime = time.time() - start_time
    
    if companies:
        # Save results
        logger.info("💾 Saving results...")
        
        # Convert to dict format
        company_dicts = []
        for company in companies:
            company_dict = asdict(company)
            company_dict['domain'] = extractor._normalize_domain(company.website)
            company_dicts.append(company_dict)
        
        # Save to files
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        csv_file = output_dir / "extracted_healthcare_companies.csv"
        json_file = output_dir / "extracted_healthcare_companies.json"
        
        # Save to CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved to {csv_file}")
        logger.info(f"✅ Saved to {json_file}")
        
        # Statistics
        with_websites = sum(1 for c in company_dicts if c['website'])
        german_companies = sum(1 for c in company_dicts if 'germany' in c['location'].lower())
        
        # Count by source
        sources = {}
        for c in company_dicts:
            source = urlparse(c['source_directory']).netloc
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("🎉 DIRECTORY EXTRACTION COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"📊 RESULTS:")
        logger.info(f"   Total companies: {len(companies)}")
        logger.info(f"   With websites: {with_websites} ({with_websites/len(companies)*100:.1f}%)")
        logger.info(f"   German companies: {german_companies}")
        logger.info(f"   Runtime: {runtime:.1f} seconds")
        logger.info(f"   Rate: {len(companies)/runtime:.2f} companies/second")
        
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
                logger.info(f"      📝 {company.description[:80]}...")
            logger.info(f"      📍 {company.location}")
    else:
        logger.error("❌ No companies extracted")

if __name__ == "__main__":
    main()