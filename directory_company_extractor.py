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
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

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

class DirectoryCompanyExtractor:
    """
    Extracts individual companies from healthcare directory pages
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.extracted_companies = []
        
    def extract_from_medicalstartups_org(self) -> List[ExtractedCompany]:
        """Extract companies from medicalstartups.org Germany page"""
        companies = []
        
        try:
            print("   🔍 Scraping medicalstartups.org (82 medical startups)...")
            url = "https://www.medicalstartups.org/country/Germany/"
            
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for startup cards/listings
                startup_cards = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'startup|company|card|listing', re.I))
                
                # Also look for links that might be companies
                company_links = soup.find_all('a', href=True)
                
                for link in company_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Skip internal navigation
                    if any(skip in href.lower() for skip in ['#', 'javascript:', 'mailto:', '/country/', '/category/', '/about']):
                        continue
                    
                    # Look for external company websites
                    if href.startswith('http') and 'medicalstartups.org' not in href:
                        if self._is_company_link(href, text):
                            # Get context from parent element
                            parent = link.parent
                            description = ""
                            if parent:
                                desc_text = parent.get_text(strip=True)
                                if len(desc_text) > len(text):
                                    description = desc_text[:300]
                            
                            company = ExtractedCompany(
                                name=text,
                                website=href,
                                description=description,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                
                # Also look for company names in text
                company_names = self._extract_company_names_from_text(soup.get_text())
                for name in company_names:
                    if len(name) > 3 and name not in [c.name for c in companies]:
                        company = ExtractedCompany(
                            name=name,
                            source_directory=url,
                            location="Germany"
                        )
                        companies.append(company)
                
                print(f"      ✅ Found {len(companies)} companies")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:100]}")
        
        return companies
    
    def extract_from_inven_ai(self) -> List[ExtractedCompany]:
        """Extract companies from inven.ai top healthcare companies list"""
        companies = []
        
        try:
            print("   🔍 Scraping inven.ai (top 22 healthcare companies)...")
            url = "https://www.inven.ai/company-lists/top-22-healthcare-companies-in-germany"
            
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for company listings - inven.ai likely has structured data
                company_elements = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'company|item|card|list', re.I))
                
                for element in company_elements:
                    # Look for company name
                    name_element = element.find(['h1', 'h2', 'h3', 'h4', 'strong', 'b'])
                    if name_element:
                        name = name_element.get_text(strip=True)
                        
                        if self._is_valid_company_name(name):
                            # Look for website link
                            website_link = element.find('a', href=re.compile(r'^https?://(?!.*inven\.ai)'))
                            website = ""
                            if website_link:
                                website = website_link.get('href')
                            
                            # Get description
                            description = element.get_text(strip=True)[:300]
                            
                            company = ExtractedCompany(
                                name=name,
                                website=website,
                                description=description,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                
                # Also look for any direct company links
                external_links = soup.find_all('a', href=re.compile(r'^https?://(?!.*inven\.ai)'))
                for link in external_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if self._is_company_link(href, text):
                        if text not in [c.name for c in companies]:
                            company = ExtractedCompany(
                                name=text,
                                website=href,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                
                print(f"      ✅ Found {len(companies)} companies")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:100]}")
        
        return companies
    
    def extract_from_f6s_directories(self) -> List[ExtractedCompany]:
        """Extract companies from F6S directory pages"""
        companies = []
        
        f6s_urls = [
            "https://www.f6s.com/companies/health-medical/germany/co",
            "https://www.f6s.com/companies/health/germany/co",
            "https://www.f6s.com/companies/digital-health/germany/co"
        ]
        
        for url in f6s_urls:
            try:
                print(f"   🔍 Scraping F6S: {url.split('/')[-2]}...")
                
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # F6S has company cards
                    company_cards = soup.find_all(['div', 'article'], class_=re.compile(r'company|startup|profile', re.I))
                    
                    for card in company_cards:
                        # Get company name
                        name_link = card.find('a', href=True)
                        if name_link:
                            name = name_link.get_text(strip=True)
                            
                            if self._is_valid_company_name(name):
                                # Look for website link (not F6S profile link)
                                website_links = card.find_all('a', href=re.compile(r'^https?://(?!.*f6s\.com)'))
                                website = ""
                                if website_links:
                                    website = website_links[0].get('href')
                                
                                # Get description
                                description = card.get_text(strip=True)[:200]
                                
                                company = ExtractedCompany(
                                    name=name,
                                    website=website,
                                    description=description,
                                    source_directory=url,
                                    location="Germany"
                                )
                                companies.append(company)
                    
                    print(f"      ✅ Found {len([c for c in companies if c.source_directory == url])} companies")
                    
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"      ❌ Error with {url}: {str(e)[:100]}")
        
        return companies
    
    def extract_from_startup_blogs(self) -> List[ExtractedCompany]:
        """Extract companies from startup blog articles"""
        companies = []
        
        blog_urls = [
            "https://www.spinlab.co/blog/10-promising-ehealth-startups-from-germany",
            "https://startuprise.co.uk/top-10-healthtech-startups-in-germany/",
            "https://eustartup.news/15-innovative-health-care-startups-in-germany-driving-change-in-the-industry/"
        ]
        
        for url in blog_urls:
            try:
                print(f"   🔍 Scraping startup blog: {urlparse(url).netloc}...")
                
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for structured company mentions
                    # Often in blog posts, companies are mentioned with strong/bold tags
                    company_mentions = soup.find_all(['strong', 'b', 'h3', 'h4'])
                    
                    for mention in company_mentions:
                        text = mention.get_text(strip=True)
                        
                        if self._is_valid_company_name(text):
                            # Look for nearby links
                            parent = mention.parent
                            website = ""
                            description = ""
                            
                            if parent:
                                # Look for links in the same paragraph
                                links = parent.find_all('a', href=True)
                                for link in links:
                                    href = link.get('href')
                                    if self._is_company_link(href, text):
                                        website = href
                                        break
                                
                                # Get description from paragraph
                                description = parent.get_text(strip=True)[:250]
                            
                            company = ExtractedCompany(
                                name=text,
                                website=website,
                                description=description,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                    
                    # Also look for explicit company links
                    external_links = soup.find_all('a', href=re.compile(r'^https?://(?!.*(' + '|'.join([
                        'spinlab.co', 'startuprise.co.uk', 'eustartup.news', 'linkedin.com', 'twitter.com'
                    ]) + '))'))
                    
                    for link in external_links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if self._is_company_link(href, text):
                            # Get context
                            parent = link.parent
                            description = ""
                            if parent:
                                description = parent.get_text(strip=True)[:200]
                            
                            company = ExtractedCompany(
                                name=text,
                                website=href,
                                description=description,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                    
                    print(f"      ✅ Found {len([c for c in companies if c.source_directory == url])} companies")
                    
                time.sleep(3)  # Rate limiting
                
            except Exception as e:
                print(f"      ❌ Error with {urlparse(url).netloc}: {str(e)[:100]}")
        
        return companies
    
    def extract_from_crunchbase_directory(self) -> List[ExtractedCompany]:
        """Extract companies from Crunchbase Germany healthcare directory"""
        companies = []
        
        try:
            print("   🔍 Scraping Crunchbase Germany healthcare directory...")
            url = "https://www.crunchbase.com/hub/germany-health-care-companies"
            
            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Crunchbase has company cards/listings
                company_elements = soup.find_all(['div', 'article'], attrs={
                    'class': re.compile(r'card|item|company|organization', re.I)
                })
                
                for element in company_elements:
                    # Look for company name link
                    name_links = element.find_all('a', href=re.compile(r'/organization/'))
                    
                    for link in name_links:
                        name = link.get_text(strip=True)
                        
                        if self._is_valid_company_name(name):
                            # Get description from the card
                            description = element.get_text(strip=True)[:200]
                            
                            company = ExtractedCompany(
                                name=name,
                                description=description,
                                source_directory=url,
                                location="Germany"
                            )
                            companies.append(company)
                
                print(f"      ✅ Found {len(companies)} companies")
                
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:100]}")
        
        return companies
    
    def _is_company_link(self, url: str, text: str) -> bool:
        """Check if URL and text represent a company"""
        if not url or len(url) < 8:
            return False
        
        # Skip non-company domains
        skip_domains = [
            'google.', 'facebook.', 'twitter.', 'linkedin.', 'youtube.',
            'github.', 'crunchbase.', 'f6s.', 'angellist.',
            'wikipedia.', 'blog.', 'medium.', 'news.'
        ]
        
        for skip in skip_domains:
            if skip in url.lower():
                return False
        
        # Must have company indicators
        company_indicators = ['.com', '.de', '.org', '.net', '.eu', '.co.uk']
        has_tld = any(tld in url.lower() for tld in company_indicators)
        
        # Text should look like a company name
        text_valid = len(text) > 2 and text.lower() not in ['website', 'visit', 'more', 'link', 'here']
        
        return has_tld and text_valid
    
    def _is_valid_company_name(self, name: str) -> bool:
        """Check if text looks like a valid company name"""
        if not name or len(name) < 3 or len(name) > 100:
            return False
        
        # Skip common non-company words
        skip_words = [
            'read more', 'click here', 'learn more', 'contact', 'about',
            'home', 'news', 'blog', 'search', 'menu', 'login', 'register'
        ]
        
        name_lower = name.lower()
        for skip in skip_words:
            if skip in name_lower:
                return False
        
        # Look for company indicators
        company_words = ['gmbh', 'ag', 'inc', 'ltd', 'corp', 'llc', 'group', 'systems', 'solutions', 'technologies']
        has_company_word = any(word in name_lower for word in company_words)
        
        # Or looks like a proper name (capitalized)
        looks_proper = name[0].isupper() and not name.isupper()
        
        # Should have at least some letters
        has_letters = any(c.isalpha() for c in name)
        
        return has_letters and (has_company_word or looks_proper)
    
    def _extract_company_names_from_text(self, text: str) -> List[str]:
        """Extract potential company names from free text"""
        names = []
        
        # Look for patterns like "Company Name GmbH" or "Tech Solutions Inc"
        patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:GmbH|AG|Inc|Ltd|Corp|LLC)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Systems|Solutions|Technologies|Group)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*Health|Medical|Care|Tech|Bio)\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._is_valid_company_name(match):
                    names.append(match)
        
        return names[:20]  # Limit to avoid noise
    
    def enhance_companies_with_websites(self, companies: List[ExtractedCompany]) -> List[ExtractedCompany]:
        """Try to find websites for companies that don't have them"""
        enhanced = []
        
        print(f"   🔍 Enhancing {len(companies)} companies with missing websites...")
        
        for i, company in enumerate(companies):
            if i % 25 == 0:
                print(f"      📊 Enhanced {i}/{len(companies)}...")
            
            enhanced_company = company
            
            # If no website, try to find one
            if not company.website:
                potential_urls = [
                    f"https://www.{company.name.lower().replace(' ', '')}.com",
                    f"https://www.{company.name.lower().replace(' ', '')}.de",
                    f"https://{company.name.lower().replace(' ', '')}.com",
                    f"https://{company.name.lower().replace(' ', '')}.de"
                ]
                
                for url in potential_urls:
                    try:
                        response = self.session.head(url, timeout=3)
                        if response.status_code in [200, 301, 302]:
                            enhanced_company.website = url
                            break
                    except:
                        continue
            
            enhanced.append(enhanced_company)
            
            # Rate limiting
            if i % 10 == 0:
                time.sleep(0.5)
        
        return enhanced
    
    def run_directory_extraction(self) -> List[ExtractedCompany]:
        """Run the complete directory extraction process"""
        print("🚀 DIRECTORY COMPANY EXTRACTION")
        print("=" * 80)
        print("🎯 Extracting individual companies from discovered directories")
        print("📂 Processing multiple healthcare directory sources")
        print()
        
        all_companies = []
        
        # Extract from each directory type
        print("🔍 Phase 1: Medical Startups Directory")
        medical_startups = self.extract_from_medicalstartups_org()
        all_companies.extend(medical_startups)
        print()
        
        print("🔍 Phase 2: Inven.ai Healthcare Companies")
        inven_companies = self.extract_from_inven_ai()
        all_companies.extend(inven_companies)
        print()
        
        print("🔍 Phase 3: F6S Startup Directories")
        f6s_companies = self.extract_from_f6s_directories()
        all_companies.extend(f6s_companies)
        print()
        
        print("🔍 Phase 4: Startup Blog Articles")
        blog_companies = self.extract_from_startup_blogs()
        all_companies.extend(blog_companies)
        print()
        
        print("🔍 Phase 5: Crunchbase Directory")
        crunchbase_companies = self.extract_from_crunchbase_directory()
        all_companies.extend(crunchbase_companies)
        print()
        
        # Remove duplicates
        unique_companies = []
        seen_names = set()
        
        for company in all_companies:
            name_key = company.name.lower().strip()
            if name_key not in seen_names and len(name_key) > 2:
                seen_names.add(name_key)
                unique_companies.append(company)
        
        print(f"📊 Total unique companies extracted: {len(unique_companies)}")
        print()
        
        # Enhance with websites
        print("🔍 Phase 6: Website Enhancement")
        enhanced_companies = self.enhance_companies_with_websites(unique_companies)
        print()
        
        return enhanced_companies

def main():
    """Main execution"""
    extractor = DirectoryCompanyExtractor()
    
    start_time = time.time()
    companies = extractor.run_directory_extraction()
    runtime = time.time() - start_time
    
    if companies:
        # Save results
        print("💾 Saving results...")
        
        # Convert to dict format
        company_dicts = []
        for company in companies:
            company_dicts.append({
                'name': company.name,
                'website': company.website,
                'description': company.description,
                'location': company.location,
                'category': company.category,
                'source_directory': company.source_directory,
                'employees': company.employees,
                'funding': company.funding,
                'domain': urlparse(company.website).netloc if company.website else ""
            })
        
        # Save to CSV
        with open('extracted_healthcare_companies.csv', 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON
        with open('extracted_healthcare_companies.json', 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to extracted_healthcare_companies.csv")
        print(f"   ✅ Saved to extracted_healthcare_companies.json")
        print()
        
        # Statistics
        with_websites = sum(1 for c in company_dicts if c['website'])
        german_companies = sum(1 for c in company_dicts if c['location'] == 'Germany')
        
        # Count by source
        sources = {}
        for c in company_dicts:
            source = urlparse(c['source_directory']).netloc
            sources[source] = sources.get(source, 0) + 1
        
        print("🎉 DIRECTORY EXTRACTION COMPLETE!")
        print("=" * 80)
        print(f"📊 EXTRACTION RESULTS:")
        print(f"   Total companies extracted: {len(companies)}")
        print(f"   Companies with websites: {with_websites} ({with_websites/len(companies)*100:.1f}%)")
        print(f"   German companies: {german_companies} ({german_companies/len(companies)*100:.1f}%)")
        print(f"   Runtime: {runtime:.1f} seconds")
        print(f"   Rate: {len(companies)/runtime:.2f} companies/second")
        print()
        print(f"📈 BREAKDOWN BY SOURCE:")
        for source, count in sources.items():
            print(f"   {source}: {count} companies")
        print()
        print("🏆 SUCCESS! Extracted individual companies from directories!")
        
        # Show sample companies
        print()
        print("🏢 SAMPLE EXTRACTED COMPANIES:")
        for i, company in enumerate(companies[:15], 1):
            print(f"   {i}. {company.name}")
            if company.website:
                print(f"      🌐 {company.website}")
            if company.description:
                print(f"      📝 {company.description[:80]}...")
            print(f"      📂 Source: {urlparse(company.source_directory).netloc}")
            print()
    else:
        print("❌ No companies extracted")

if __name__ == "__main__":
    main()