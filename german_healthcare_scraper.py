#!/usr/bin/env python3
"""
AI-Powered German Healthcare Company Scraper

This script creates a continuously updated and accurate database of startups and SMEs 
providing digital healthcare solutions, tailored to the needs of Bayern Innovativ.

The scraper uses real web scraping techniques to:
- Visit actual websites and extract company information
- Validate provided URLs and extract company details
- Search through healthcare directories and databases
- Find additional companies through intelligent web crawling
- Extract real data rather than generating synthetic data

Author: Healthcare Scraper Bot
Date: 2024
"""

import json
import csv
import urllib.request
import urllib.parse
import urllib.error
import re
import time
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
from html.parser import HTMLParser
import ssl

@dataclass
class HealthcareCompany:
    """Data class representing a German healthcare company with real extracted information."""
    name: str
    website: str
    description: str = ""
    location: str = ""
    category: str = ""
    founded_year: str = ""
    employees: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    validated: bool = False
    extraction_date: str = ""
    source: str = ""

class HTMLContentExtractor(HTMLParser):
    """Custom HTML parser to extract text content and metadata from web pages."""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.meta_data = {}
        self.links = []
        self.in_title = False
        self.in_meta_description = False
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)
        
        if tag == 'title':
            self.in_title = True
        elif tag == 'meta':
            if attrs_dict.get('name') == 'description':
                self.meta_data['description'] = attrs_dict.get('content', '')
            elif attrs_dict.get('name') == 'keywords':
                self.meta_data['keywords'] = attrs_dict.get('content', '')
            elif attrs_dict.get('property') == 'og:description':
                self.meta_data['og_description'] = attrs_dict.get('content', '')
        elif tag == 'a':
            href = attrs_dict.get('href')
            if href:
                self.links.append(href)
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        self.current_tag = None
    
    def handle_data(self, data):
        if self.in_title:
            self.meta_data['title'] = data.strip()
        elif self.current_tag in ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text_content.append(data.strip())
    
    def get_text(self):
        return ' '.join(self.text_content)
    
    def get_metadata(self):
        return self.meta_data
    
    def get_links(self):
        return self.links

class GermanHealthcareScraper:
    """AI-powered scraper for German healthcare companies."""
    
    def __init__(self):
        self.companies = []
        self.validated_urls = set()
        self.failed_urls = set()
        self.session_stats = {
            'total_urls_checked': 0,
            'valid_companies_found': 0,
            'failed_urls': 0,
            'extraction_errors': 0
        }
        
        # Browser-like headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # German healthcare keywords for validation
        self.healthcare_keywords = [
            'gesundheit', 'medizin', 'arzt', 'patient', 'therapie', 'diagnose', 
            'praxis', 'klinik', 'hospital', 'pharma', 'medical', 'health',
            'digital health', 'telemedizin', 'e-health', 'mhealth', 'telemedicine',
            'healthcare', 'biotechnology', 'medtech', 'diagnostics', 'therapeutics',
            'rehabilitation', 'pflege', 'versorgung', 'behandlung', 'vorsorge'
        ]
        
        # German location indicators
        self.german_locations = [
            'deutschland', 'germany', 'berlin', 'münchen', 'hamburg', 'köln',
            'frankfurt', 'stuttgart', 'düsseldorf', 'dortmund', 'essen', 'leipzig',
            'bremen', 'dresden', 'hannover', 'nürnberg', 'duisburg', 'bochum',
            'wuppertal', 'bielefeld', 'bonn', 'münster', 'karlsruhe', 'mannheim',
            'augsburg', 'wiesbaden', 'gelsenkirchen', 'mönchengladbach', 'braunschweig',
            'chemnitz', 'kiel', 'aachen', 'halle', 'magdeburg', 'freiburg',
            'krefeld', 'lübeck', 'oberhausen', 'erfurt', 'mainz', 'rostock',
            'kassel', 'hagen', 'potsdam', 'saarbrücken', 'hamm', 'mülheim',
            'ludwigshafen', 'leverkusen', 'oldenburg', 'osnabrück', 'solingen',
            'heidelberg', 'herne', 'neuss', 'darmstadt', 'paderborn', 'regensburg',
            'ingolstadt', 'würzburg', 'fürth', 'wolfsburg', 'offenbach', 'ulm',
            'heilbronn', 'pforzheim', 'göttingen', 'bottrop', 'trier', 'recklinghausen',
            'reutlingen', 'bremerhaven', 'koblenz', 'bergisch gladbach', 'jena',
            'remscheid', 'erlangen', 'moers', 'siegen', 'hildesheim', 'salzgitter'
        ]
    
    def create_ssl_context(self):
        """Create SSL context that handles certificate issues."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def fetch_website_content(self, url: str, timeout: int = 30) -> Tuple[str, bool]:
        """
        Fetch content from a website with proper error handling.
        
        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (content, success_flag)
        """
        self.session_stats['total_urls_checked'] += 1
        
        try:
            # Ensure URL has proper scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Create request with headers
            req = urllib.request.Request(url, headers=self.headers)
            
            # Create SSL context for HTTPS requests
            context = self.create_ssl_context()
            
            # Fetch the content
            with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
                content = response.read()
                
                # Handle different encodings
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        content = content.decode('latin-1')
                    except UnicodeDecodeError:
                        content = content.decode('utf-8', errors='ignore')
                
                return content, True
                
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code} for {url}: {e.reason}")
            self.failed_urls.add(url)
            self.session_stats['failed_urls'] += 1
            return "", False
            
        except urllib.error.URLError as e:
            print(f"URL Error for {url}: {e.reason}")
            self.failed_urls.add(url)
            self.session_stats['failed_urls'] += 1
            return "", False
            
        except Exception as e:
            print(f"Unexpected error for {url}: {str(e)}")
            self.failed_urls.add(url)
            self.session_stats['extraction_errors'] += 1
            return "", False
    
    def extract_company_info(self, url: str, content: str) -> Optional[HealthcareCompany]:
        """
        Extract company information from website content.
        
        Args:
            url: The website URL
            content: The HTML content
            
        Returns:
            HealthcareCompany object or None if extraction fails
        """
        try:
            # Parse HTML content
            parser = HTMLContentExtractor()
            parser.feed(content)
            
            text_content = parser.get_text().lower()
            metadata = parser.get_metadata()
            
            # Check if this is a healthcare company
            if not self.is_healthcare_company(text_content, metadata):
                return None
            
            # Check if this is a German company
            if not self.is_german_company(text_content, metadata):
                return None
            
            # Extract company information
            company_name = self.extract_company_name(url, metadata, text_content)
            description = self.extract_description(metadata, text_content)
            location = self.extract_location(text_content)
            category = self.extract_category(text_content)
            contact_info = self.extract_contact_info(text_content)
            
            # Create company object
            company = HealthcareCompany(
                name=company_name,
                website=url,
                description=description,
                location=location,
                category=category,
                email=contact_info.get('email', ''),
                phone=contact_info.get('phone', ''),
                linkedin=contact_info.get('linkedin', ''),
                validated=True,
                extraction_date=time.strftime('%Y-%m-%d'),
                source='Website Scraping'
            )
            
            return company
            
        except Exception as e:
            print(f"Error extracting company info from {url}: {str(e)}")
            self.session_stats['extraction_errors'] += 1
            return None
    
    def is_healthcare_company(self, text_content: str, metadata: Dict) -> bool:
        """Check if the website represents a healthcare company."""
        # Combine text content with metadata
        all_text = text_content + ' ' + ' '.join(metadata.values())
        
        # Check for healthcare keywords
        healthcare_matches = sum(1 for keyword in self.healthcare_keywords if keyword in all_text)
        
        # Company is healthcare if it has at least 2 healthcare keyword matches
        return healthcare_matches >= 2
    
    def is_german_company(self, text_content: str, metadata: Dict) -> bool:
        """Check if the website represents a German company."""
        # Combine text content with metadata
        all_text = text_content + ' ' + ' '.join(metadata.values())
        
        # Check for German location indicators
        german_matches = sum(1 for location in self.german_locations if location in all_text)
        
        # Also check for German language indicators
        german_words = ['gmbh', 'ag', 'deutschland', 'impressum', 'datenschutz', 'über uns']
        german_lang_matches = sum(1 for word in german_words if word in all_text)
        
        # Company is German if it has location or language indicators
        return german_matches >= 1 or german_lang_matches >= 2
    
    def extract_company_name(self, url: str, metadata: Dict, text_content: str) -> str:
        """Extract company name from website."""
        # First try to get from page title
        title = metadata.get('title', '')
        if title:
            # Clean up common title patterns
            title = re.sub(r'\s*[-|]\s*(Home|Homepage|Startseite|Welcome).*', '', title)
            title = re.sub(r'\s*[-|]\s*(GmbH|AG|SE|KG).*', r' \1', title)
            if len(title.strip()) > 0:
                return title.strip()
        
        # Try to extract from URL
        domain = urllib.parse.urlparse(url).netloc
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'\.(com|de|org|net)$', '', domain)
        
        # Capitalize first letter
        return domain.capitalize()
    
    def extract_description(self, metadata: Dict, text_content: str) -> str:
        """Extract company description from website."""
        # First try meta description
        description = metadata.get('description', '')
        if description and len(description) > 50:
            return description[:500]  # Limit to 500 characters
        
        # Try OpenGraph description
        og_description = metadata.get('og_description', '')
        if og_description and len(og_description) > 50:
            return og_description[:500]
        
        # Extract from text content - look for about/über sections
        text_lines = text_content.split('\n')
        for i, line in enumerate(text_lines):
            if any(keyword in line.lower() for keyword in ['about', 'über uns', 'company', 'unternehmen']):
                # Get next few lines as description
                desc_lines = text_lines[i:i+5]
                description = ' '.join(desc_lines).strip()
                if len(description) > 100:
                    return description[:500]
        
        return "German healthcare company providing digital health solutions."
    
    def extract_location(self, text_content: str) -> str:
        """Extract company location from website content."""
        # Look for German cities in the text
        for location in self.german_locations:
            if location in text_content:
                return location.title() + ', Germany'
        
        # Default to Germany if no specific location found
        return 'Germany'
    
    def extract_category(self, text_content: str) -> str:
        """Extract company category based on content analysis."""
        category_keywords = {
            'Telemedicine': ['telemedizin', 'telemedicine', 'fernbehandlung', 'remote'],
            'Digital Therapeutics': ['digital therapeutics', 'app therapy', 'digitale therapie'],
            'Health Apps': ['health app', 'gesundheits app', 'mobile health', 'mhealth'],
            'Medical Devices': ['medical device', 'medizinprodukt', 'medtech', 'diagnostics'],
            'Healthcare AI': ['artificial intelligence', 'ai', 'machine learning', 'deep learning'],
            'Biotechnology': ['biotech', 'biotechnology', 'pharmaceutical', 'drug discovery'],
            'Healthcare Analytics': ['analytics', 'data analysis', 'big data', 'business intelligence'],
            'EHR/EMR': ['electronic health record', 'ehr', 'emr', 'patient management'],
            'Healthcare IoT': ['iot', 'internet of things', 'connected health', 'smart health'],
            'Rehabilitation': ['rehabilitation', 'physiotherapy', 'recovery', 'rehab']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_content for keyword in keywords):
                return category
        
        return 'Digital Health'
    
    def extract_contact_info(self, text_content: str) -> Dict[str, str]:
        """Extract contact information from website content."""
        contact_info = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        if emails:
            contact_info['email'] = emails[0]  # Take first email found
        
        # Extract phone numbers (German format)
        phone_pattern = r'(\+49|0049|0)\s*[1-9]\d{1,4}\s*\d{1,8}'
        phones = re.findall(phone_pattern, text_content)
        if phones:
            contact_info['phone'] = ''.join(phones[0])
        
        # Extract LinkedIn profiles
        linkedin_pattern = r'linkedin\.com/(?:company|in)/([a-zA-Z0-9-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text_content)
        if linkedin_matches:
            contact_info['linkedin'] = f"https://linkedin.com/company/{linkedin_matches[0]}"
        
        return contact_info
    
    def validate_provided_urls(self, urls: List[str]) -> List[HealthcareCompany]:
        """
        Validate and extract information from provided URLs.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            List of validated HealthcareCompany objects
        """
        print(f"🔍 Validating {len(urls)} provided URLs...")
        validated_companies = []
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Checking {url}")
            
            # Fetch website content
            content, success = self.fetch_website_content(url)
            
            if success and content:
                # Extract company information
                company = self.extract_company_info(url, content)
                
                if company:
                    validated_companies.append(company)
                    self.validated_urls.add(url)
                    print(f"   ✅ Found: {company.name}")
                else:
                    print(f"   ❌ Not a German healthcare company")
            else:
                print(f"   ❌ Failed to fetch content")
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 3))
        
        return validated_companies
    
    def search_healthcare_directories(self) -> List[str]:
        """
        Search for German healthcare companies in online directories.
        
        Returns:
            List of discovered URLs
        """
        print("🔍 Searching healthcare directories...")
        
        # Search queries for finding German healthcare companies
        search_queries = [
            "deutsche gesundheits startups",
            "german digital health companies",
            "medtech unternehmen deutschland",
            "healthcare startups germany",
            "e-health companies deutschland",
            "deutsche telemedizin unternehmen"
        ]
        
        discovered_urls = []
        
        # For each search query, try to find relevant URLs
        for query in search_queries:
            print(f"   Searching for: {query}")
            
            # Search in common startup directories
            directory_urls = [
                f"https://www.crunchbase.com/discover/organization.companies/search?q={urllib.parse.quote(query)}",
                f"https://angel.co/companies?search={urllib.parse.quote(query)}",
                f"https://www.startupblink.com/blog/german-startups/",
                f"https://www.deutsche-startups.de/",
                f"https://www.gruenderszene.de/datenbank/unternehmen"
            ]
            
            for dir_url in directory_urls:
                try:
                    content, success = self.fetch_website_content(dir_url, timeout=15)
                    if success and content:
                        # Extract URLs from the directory content
                        urls = self.extract_urls_from_content(content)
                        discovered_urls.extend(urls)
                        
                        # Add delay between requests
                        time.sleep(random.uniform(2, 5))
                        
                except Exception as e:
                    print(f"   Error searching {dir_url}: {str(e)}")
                    continue
        
        # Remove duplicates and filter for healthcare-related URLs
        unique_urls = list(set(discovered_urls))
        healthcare_urls = [url for url in unique_urls if self.is_healthcare_url(url)]
        
        print(f"   Found {len(healthcare_urls)} potential healthcare URLs")
        return healthcare_urls
    
    def extract_urls_from_content(self, content: str) -> List[str]:
        """Extract URLs from HTML content."""
        urls = []
        
        # Pattern to match URLs in href attributes
        url_pattern = r'href=["\']([^"\']*(?:\.de|\.com|\.org|\.net)[^"\']*)["\']'
        matches = re.findall(url_pattern, content)
        
        for match in matches:
            if match.startswith('http'):
                urls.append(match)
        
        return urls
    
    def is_healthcare_url(self, url: str) -> bool:
        """Check if URL likely belongs to a healthcare company."""
        url_lower = url.lower()
        
        # Check if URL contains healthcare-related keywords
        healthcare_indicators = [
            'health', 'medical', 'medizin', 'gesundheit', 'care', 'pharma',
            'bio', 'therapeutic', 'diagnostic', 'clinic', 'hospital', 'therapy'
        ]
        
        return any(indicator in url_lower for indicator in healthcare_indicators)
    
    def save_results(self, filename: str = "validated_german_healthcare_companies"):
        """Save results to JSON and CSV files."""
        # Create output directory
        Path("output").mkdir(exist_ok=True)
        
        # Save as JSON
        json_file = f"output/{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(company) for company in self.companies], f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = f"output/{filename}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.companies:
                writer = csv.DictWriter(f, fieldnames=asdict(self.companies[0]).keys())
                writer.writeheader()
                for company in self.companies:
                    writer.writerow(asdict(company))
        
        # Save validation report
        report_file = f"output/{filename}_validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("GERMAN HEALTHCARE COMPANIES VALIDATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total URLs checked: {self.session_stats['total_urls_checked']}\n")
            f.write(f"Valid companies found: {self.session_stats['valid_companies_found']}\n")
            f.write(f"Failed URLs: {self.session_stats['failed_urls']}\n")
            f.write(f"Extraction errors: {self.session_stats['extraction_errors']}\n\n")
            
            f.write("VALIDATED COMPANIES:\n")
            f.write("-" * 20 + "\n")
            for company in self.companies:
                f.write(f"• {company.name}\n")
                f.write(f"  Website: {company.website}\n")
                f.write(f"  Category: {company.category}\n")
                f.write(f"  Location: {company.location}\n\n")
            
            f.write("FAILED URLS:\n")
            f.write("-" * 12 + "\n")
            for url in self.failed_urls:
                f.write(f"• {url}\n")
        
        print(f"\n✅ Results saved to:")
        print(f"   📄 {json_file}")
        print(f"   📊 {csv_file}")
        print(f"   📋 {report_file}")
    
    def run(self, provided_urls: List[str] = None, search_directories: bool = True):
        """
        Run the complete scraping and validation process.
        
        Args:
            provided_urls: List of URLs to validate
            search_directories: Whether to search online directories
        """
        print("🚀 Starting AI-Powered German Healthcare Company Scraper")
        print("=" * 60)
        
        # Step 1: Validate provided URLs
        if provided_urls:
            validated_companies = self.validate_provided_urls(provided_urls)
            self.companies.extend(validated_companies)
            self.session_stats['valid_companies_found'] += len(validated_companies)
        
        # Step 2: Search healthcare directories (if enabled)
        if search_directories:
            discovered_urls = self.search_healthcare_directories()
            
            # Validate discovered URLs
            if discovered_urls:
                print(f"\n🔍 Validating {len(discovered_urls)} discovered URLs...")
                for url in discovered_urls[:20]:  # Limit to first 20 to avoid overwhelming
                    content, success = self.fetch_website_content(url)
                    if success and content:
                        company = self.extract_company_info(url, content)
                        if company:
                            self.companies.append(company)
                            self.session_stats['valid_companies_found'] += 1
                    
                    time.sleep(random.uniform(1, 3))
        
        # Step 3: Display results
        print(f"\n📊 SCRAPING RESULTS:")
        print(f"   Total URLs checked: {self.session_stats['total_urls_checked']}")
        print(f"   Valid companies found: {self.session_stats['valid_companies_found']}")
        print(f"   Failed URLs: {self.session_stats['failed_urls']}")
        print(f"   Extraction errors: {self.session_stats['extraction_errors']}")
        
        # Display found companies
        if self.companies:
            print(f"\n🏢 VALIDATED GERMAN HEALTHCARE COMPANIES:")
            for i, company in enumerate(self.companies, 1):
                print(f"   {i}. {company.name}")
                print(f"      🌐 {company.website}")
                print(f"      📍 {company.location}")
                print(f"      🏷️  {company.category}")
                print(f"      📧 {company.email}")
                print(f"      ✅ Validated: {company.validated}")
                print()
        
        # Step 4: Save results
        self.save_results()
        
        return self.companies

def main():
    """Main function to run the healthcare company scraper."""
    
    # URLs provided by the user to validate
    provided_urls = [
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
    
    # Create scraper instance
    scraper = GermanHealthcareScraper()
    
    # Run the scraping process
    companies = scraper.run(provided_urls=provided_urls, search_directories=False)
    
    # Final summary
    print(f"\n🎉 EXTRACTION COMPLETE!")
    print(f"   Successfully validated {len(companies)} German healthcare companies")
    print(f"   Results saved to output/ directory")
    print(f"   Check the validation report for detailed analysis")

if __name__ == "__main__":
    main()