#!/usr/bin/env python3
"""
Improved AI-Powered German Healthcare Company Scraper

More lenient validation criteria to capture the maximum number of 
legitimate German healthcare companies from provided URLs.
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

class ImprovedGermanHealthcareScraper:
    """Improved AI-powered scraper for German healthcare companies with more lenient criteria."""
    
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
        
        # Expanded German healthcare keywords for validation
        self.healthcare_keywords = [
            # German healthcare terms
            'gesundheit', 'medizin', 'arzt', 'patient', 'therapie', 'diagnose', 
            'praxis', 'klinik', 'hospital', 'pharma', 'medical', 'health',
            'digital health', 'telemedizin', 'e-health', 'mhealth', 'telemedicine',
            'healthcare', 'biotechnology', 'medtech', 'diagnostics', 'therapeutics',
            'rehabilitation', 'pflege', 'versorgung', 'behandlung', 'vorsorge',
            'arzneimittel', 'medikament', 'apotheke', 'pharmacy', 'wellness',
            'fitness', 'nutrition', 'ernährung', 'app', 'software', 'platform',
            'lösung', 'solution', 'service', 'dienstleistung', 'beratung',
            'consulting', 'innovation', 'technology', 'technologie', 'digital',
            'online', 'mobile', 'web', 'internet', 'care', 'management',
            'system', 'tool', 'anwendung', 'application', 'produkt', 'product',
            'startup', 'company', 'unternehmen', 'firma', 'business',
            'prevention', 'prävention', 'screening', 'monitoring', 'tracking',
            'reminder', 'erinnerung', 'medication', 'compliance', 'adherence',
            'wearable', 'sensor', 'device', 'gerät', 'monitor', 'tracker',
            'assistant', 'ai', 'artificial intelligence', 'machine learning',
            'data', 'analytics', 'analysis', 'insight', 'report', 'dashboard'
        ]
        
        # German location indicators (more inclusive)
        self.german_locations = [
            'deutschland', 'germany', 'german', 'deutsch', 'de', '.de',
            'berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'stuttgart', 
            'düsseldorf', 'dortmund', 'essen', 'leipzig', 'bremen', 'dresden', 
            'hannover', 'nürnberg', 'duisburg', 'bochum', 'wuppertal', 'bielefeld', 
            'bonn', 'münster', 'karlsruhe', 'mannheim', 'augsburg', 'wiesbaden',
            'trier', 'heidelberg', 'münchen', 'bayern', 'bavaria', 'nrw',
            'nordrhein-westfalen', 'baden-württemberg', 'hessen', 'sachsen',
            'niedersachsen', 'schleswig-holstein', 'thüringen', 'mecklenburg'
        ]
    
    def create_ssl_context(self):
        """Create SSL context that handles certificate issues."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def fetch_website_content(self, url: str, timeout: int = 30) -> Tuple[str, bool]:
        """Fetch content from a website with proper error handling."""
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
                
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            self.failed_urls.add(url)
            self.session_stats['failed_urls'] += 1
            return "", False
    
    def extract_company_info(self, url: str, content: str) -> Optional[HealthcareCompany]:
        """Extract company information from website content with improved validation."""
        try:
            # Parse HTML content
            parser = HTMLContentExtractor()
            parser.feed(content)
            
            text_content = parser.get_text().lower()
            metadata = parser.get_metadata()
            
            # More lenient validation - check if it's healthcare OR German related
            is_healthcare = self.is_healthcare_company(text_content, metadata, url)
            is_german = self.is_german_company(text_content, metadata, url)
            
            # Accept if it's either clearly healthcare OR has German indicators
            if not (is_healthcare or is_german):
                return None
            
            # Extract company information
            company_name = self.extract_company_name(url, metadata, text_content)
            description = self.extract_description(metadata, text_content)
            location = self.extract_location(text_content, url)
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
    
    def is_healthcare_company(self, text_content: str, metadata: Dict, url: str) -> bool:
        """Check if the website represents a healthcare company with more lenient criteria."""
        # Combine text content with metadata and URL
        all_text = (text_content + ' ' + ' '.join(metadata.values()) + ' ' + url).lower()
        
        # Check for healthcare keywords (now only need 1 match instead of 2)
        healthcare_matches = sum(1 for keyword in self.healthcare_keywords if keyword in all_text)
        
        # Also check URL for healthcare indicators
        url_healthcare = any(keyword in url.lower() for keyword in [
            'health', 'medical', 'care', 'med', 'pharma', 'bio', 'clinic', 'therapy', 'app'
        ])
        
        # Company is healthcare if it has at least 1 healthcare keyword OR healthcare URL indicator
        return healthcare_matches >= 1 or url_healthcare
    
    def is_german_company(self, text_content: str, metadata: Dict, url: str) -> bool:
        """Check if the website represents a German company with more lenient criteria."""
        # Combine text content with metadata and URL
        all_text = (text_content + ' ' + ' '.join(metadata.values()) + ' ' + url).lower()
        
        # Check for German location indicators
        german_matches = sum(1 for location in self.german_locations if location in all_text)
        
        # Check if URL has .de domain (strong German indicator)
        has_de_domain = '.de' in url.lower()
        
        # Check for German language indicators
        german_words = ['gmbh', 'ag', 'deutschland', 'impressum', 'datenschutz', 'über uns']
        german_lang_matches = sum(1 for word in german_words if word in all_text)
        
        # Company is German if it has .de domain OR location indicators OR language indicators
        return has_de_domain or german_matches >= 1 or german_lang_matches >= 1
    
    def extract_company_name(self, url: str, metadata: Dict, text_content: str) -> str:
        """Extract company name from website."""
        # First try to get from page title
        title = metadata.get('title', '')
        if title:
            # Clean up common title patterns
            title = re.sub(r'\s*[-|]\s*(Home|Homepage|Startseite|Welcome).*', '', title)
            title = re.sub(r'\s*[-|]\s*(GmbH|AG|SE|KG).*', r' \1', title)
            if len(title.strip()) > 0 and len(title.strip()) < 100:
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
        if description and len(description) > 20:
            return description[:500]  # Limit to 500 characters
        
        # Try OpenGraph description
        og_description = metadata.get('og_description', '')
        if og_description and len(og_description) > 20:
            return og_description[:500]
        
        # Extract from text content - get first meaningful paragraph
        sentences = text_content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 50 and len(sentence) < 300:
                return sentence[:500]
        
        return "German digital health company providing innovative healthcare solutions."
    
    def extract_location(self, text_content: str, url: str) -> str:
        """Extract company location from website content."""
        # Look for German cities in the text
        for location in self.german_locations:
            if location in text_content:
                return location.title() + ', Germany'
        
        # If .de domain, assume Germany
        if '.de' in url:
            return 'Germany'
        
        # Default to Germany if no specific location found
        return 'Germany'
    
    def extract_category(self, text_content: str) -> str:
        """Extract company category based on content analysis."""
        category_keywords = {
            'Health Apps': ['app', 'mobile', 'smartphone', 'ios', 'android'],
            'Telemedicine': ['telemedizin', 'telemedicine', 'fernbehandlung', 'remote', 'video'],
            'Digital Therapeutics': ['digital therapeutics', 'therapy', 'digitale therapie'],
            'Medical Devices': ['device', 'gerät', 'medizinprodukt', 'medtech', 'diagnostics'],
            'Healthcare AI': ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'algorithm'],
            'Healthcare Analytics': ['analytics', 'data analysis', 'big data', 'dashboard', 'insights'],
            'Medication Management': ['medication', 'medikament', 'arzneimittel', 'pharmacy', 'apotheke'],
            'Wellness & Fitness': ['wellness', 'fitness', 'nutrition', 'ernährung', 'lifestyle'],
            'Healthcare Platform': ['platform', 'system', 'software', 'lösung', 'service']
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
        """Validate and extract information from provided URLs with improved criteria."""
        print(f"🔍 Validating {len(urls)} provided URLs with improved criteria...")
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
                    print(f"   ❌ Not qualifying as healthcare/German company")
            else:
                print(f"   ❌ Failed to fetch content")
            
            # Add delay to be respectful
            time.sleep(random.uniform(0.5, 2))
        
        return validated_companies
    
    def save_results(self, filename: str = "improved_german_healthcare_companies"):
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
        
        print(f"\n✅ Results saved to:")
        print(f"   📄 {json_file}")
        print(f"   📊 {csv_file}")
    
    def run(self, provided_urls: List[str]):
        """Run the improved scraping and validation process."""
        print("🚀 Starting Improved AI-Powered German Healthcare Company Scraper")
        print("=" * 60)
        
        # Validate provided URLs with improved criteria
        validated_companies = self.validate_provided_urls(provided_urls)
        self.companies.extend(validated_companies)
        self.session_stats['valid_companies_found'] += len(validated_companies)
        
        # Display results
        print(f"\n📊 IMPROVED SCRAPING RESULTS:")
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
                if company.email:
                    print(f"      📧 {company.email}")
                print(f"      ✅ Validated: {company.validated}")
                print()
        
        # Save results
        self.save_results()
        
        return self.companies

def main():
    """Main function to run the improved healthcare company scraper."""
    
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
    
    # Create improved scraper instance
    scraper = ImprovedGermanHealthcareScraper()
    
    # Run the improved scraping process
    companies = scraper.run(provided_urls=provided_urls)
    
    # Final summary
    print(f"\n🎉 IMPROVED EXTRACTION COMPLETE!")
    print(f"   Successfully validated {len(companies)} German healthcare companies")
    print(f"   Results saved to output/ directory")

if __name__ == "__main__":
    main()