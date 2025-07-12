#!/usr/bin/env python3
"""
European Healthcare Company Scraper

Very inclusive scraper to capture healthcare companies from all over Europe
with minimal validation requirements to maximize capture rate.
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
    """Data class representing a European healthcare company."""
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
    validated: bool = True
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

class EuropeanHealthcareScraper:
    """Very inclusive scraper for European healthcare companies."""
    
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
        
        # Very broad healthcare and tech keywords
        self.broad_keywords = [
            'health', 'medical', 'care', 'app', 'tech', 'digital', 'platform',
            'solution', 'service', 'company', 'startup', 'business', 'software',
            'system', 'tool', 'product', 'innovation', 'technology', 'data',
            'analytics', 'ai', 'intelligence', 'management', 'consulting',
            'wellness', 'fitness', 'therapy', 'treatment', 'patient', 'doctor',
            'clinic', 'hospital', 'pharmacy', 'medication', 'drug', 'device',
            'monitoring', 'tracking', 'screening', 'diagnosis', 'prevention',
            'rehabilitation', 'telemedicine', 'telehealth', 'mhealth',
            'gesundheit', 'medizin', 'pflege', 'therapie', 'patient', 'arzt'
        ]
        
        # European countries and domains
        self.european_indicators = [
            '.de', '.com', '.eu', '.org', '.net', '.co', '.app', '.ai', '.tech',
            'germany', 'deutschland', 'berlin', 'munich', 'hamburg', 'cologne',
            'europe', 'european', 'uk', 'france', 'spain', 'italy', 'netherlands',
            'belgium', 'austria', 'switzerland', 'poland', 'sweden', 'norway',
            'denmark', 'finland', 'ireland', 'portugal', 'czech', 'slovakia'
        ]
    
    def create_ssl_context(self):
        """Create SSL context that handles certificate issues."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def fetch_website_content(self, url: str, timeout: int = 15) -> Tuple[str, bool]:
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
            print(f"   ❌ Error: {str(e)[:100]}")
            self.failed_urls.add(url)
            self.session_stats['failed_urls'] += 1
            return "", False
    
    def extract_company_info(self, url: str, content: str) -> HealthcareCompany:
        """Extract company information from website content - very inclusive."""
        try:
            # Parse HTML content
            parser = HTMLContentExtractor()
            parser.feed(content)
            
            text_content = parser.get_text()
            metadata = parser.get_metadata()
            
            # Extract company information
            company_name = self.extract_company_name(url, metadata, text_content)
            description = self.extract_description(metadata, text_content)
            location = self.extract_location(text_content, url)
            category = self.extract_category(text_content, url)
            contact_info = self.extract_contact_info(text_content)
            
            # Create company object - always create one for valid URLs
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
            print(f"   ❌ Extraction error: {str(e)[:50]}")
            self.session_stats['extraction_errors'] += 1
            return None
    
    def extract_company_name(self, url: str, metadata: Dict, text_content: str) -> str:
        """Extract company name from website."""
        # First try to get from page title
        title = metadata.get('title', '')
        if title and len(title.strip()) > 0:
            # Clean up common title patterns
            title = re.sub(r'\s*[-|]\s*(Home|Homepage|Startseite|Welcome).*', '', title)
            title = re.sub(r'\s*[-|]\s*(GmbH|AG|SE|KG|Inc|Ltd|LLC).*', r' \1', title)
            if len(title.strip()) > 0 and len(title.strip()) < 150:
                return title.strip()
        
        # Try to extract from URL
        domain = urllib.parse.urlparse(url).netloc
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'\.(com|de|org|net|eu|co|app|ai|tech)$', '', domain)
        
        # Make it more readable
        domain = domain.replace('-', ' ').replace('_', ' ')
        return domain.title()
    
    def extract_description(self, metadata: Dict, text_content: str) -> str:
        """Extract company description from website."""
        # First try meta description
        description = metadata.get('description', '')
        if description and len(description) > 10:
            return description[:500]
        
        # Try OpenGraph description
        og_description = metadata.get('og_description', '')
        if og_description and len(og_description) > 10:
            return og_description[:500]
        
        # Extract from text content - get first meaningful sentences
        sentences = re.split(r'[.!?]', text_content)
        meaningful_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:
                meaningful_sentences.append(sentence)
                if len(meaningful_sentences) >= 2:
                    break
        
        if meaningful_sentences:
            return '. '.join(meaningful_sentences)[:500]
        
        return "European healthcare technology company providing digital health solutions."
    
    def extract_location(self, text_content: str, url: str) -> str:
        """Extract company location from website content."""
        text_lower = text_content.lower()
        
        # European cities and countries
        locations = [
            'berlin', 'munich', 'hamburg', 'cologne', 'frankfurt', 'stuttgart',
            'london', 'manchester', 'birmingham', 'edinburgh', 'dublin',
            'paris', 'lyon', 'marseille', 'toulouse', 'madrid', 'barcelona',
            'milan', 'rome', 'naples', 'amsterdam', 'rotterdam', 'brussels',
            'antwerp', 'vienna', 'zurich', 'geneva', 'warsaw', 'krakow',
            'stockholm', 'gothenburg', 'oslo', 'copenhagen', 'helsinki',
            'prague', 'bratislava', 'budapest', 'bucharest', 'sofia',
            'athens', 'lisbon', 'porto', 'helsinki', 'tallinn', 'riga', 'vilnius'
        ]
        
        for city in locations:
            if city in text_lower:
                country = self.get_country_from_city(city)
                return f"{city.title()}, {country}"
        
        # Check domain for country indication
        if '.de' in url:
            return 'Germany'
        elif '.co.uk' in url or '.uk' in url:
            return 'United Kingdom'
        elif '.fr' in url:
            return 'France'
        elif '.es' in url:
            return 'Spain'
        elif '.it' in url:
            return 'Italy'
        elif '.nl' in url:
            return 'Netherlands'
        elif '.be' in url:
            return 'Belgium'
        elif '.at' in url:
            return 'Austria'
        elif '.ch' in url:
            return 'Switzerland'
        elif '.pl' in url:
            return 'Poland'
        elif '.se' in url:
            return 'Sweden'
        elif '.no' in url:
            return 'Norway'
        elif '.dk' in url:
            return 'Denmark'
        elif '.fi' in url:
            return 'Finland'
        elif '.ie' in url:
            return 'Ireland'
        
        return 'Europe'
    
    def get_country_from_city(self, city: str) -> str:
        """Get country from city name."""
        city_country_map = {
            'berlin': 'Germany', 'munich': 'Germany', 'hamburg': 'Germany', 'cologne': 'Germany',
            'frankfurt': 'Germany', 'stuttgart': 'Germany',
            'london': 'United Kingdom', 'manchester': 'United Kingdom', 'birmingham': 'United Kingdom',
            'edinburgh': 'United Kingdom', 'dublin': 'Ireland',
            'paris': 'France', 'lyon': 'France', 'marseille': 'France', 'toulouse': 'France',
            'madrid': 'Spain', 'barcelona': 'Spain',
            'milan': 'Italy', 'rome': 'Italy', 'naples': 'Italy',
            'amsterdam': 'Netherlands', 'rotterdam': 'Netherlands',
            'brussels': 'Belgium', 'antwerp': 'Belgium',
            'vienna': 'Austria', 'zurich': 'Switzerland', 'geneva': 'Switzerland',
            'warsaw': 'Poland', 'krakow': 'Poland',
            'stockholm': 'Sweden', 'gothenburg': 'Sweden',
            'oslo': 'Norway', 'copenhagen': 'Denmark', 'helsinki': 'Finland',
            'prague': 'Czech Republic', 'bratislava': 'Slovakia', 'budapest': 'Hungary'
        }
        return city_country_map.get(city.lower(), 'Europe')
    
    def extract_category(self, text_content: str, url: str) -> str:
        """Extract company category based on content analysis."""
        text_lower = text_content.lower()
        url_lower = url.lower()
        
        # Category keywords with broader matches
        if any(word in text_lower or word in url_lower for word in ['app', 'mobile', 'smartphone']):
            return 'Health Apps'
        elif any(word in text_lower for word in ['telemedicine', 'telemedizin', 'remote', 'video', 'consultation']):
            return 'Telemedicine'
        elif any(word in text_lower for word in ['ai', 'artificial', 'intelligence', 'machine learning', 'algorithm']):
            return 'Healthcare AI'
        elif any(word in text_lower for word in ['analytics', 'data', 'insights', 'dashboard', 'reporting']):
            return 'Healthcare Analytics'
        elif any(word in text_lower for word in ['medication', 'pharmacy', 'drug', 'prescription', 'adherence']):
            return 'Medication Management'
        elif any(word in text_lower for word in ['device', 'hardware', 'sensor', 'monitor', 'wearable']):
            return 'Medical Devices'
        elif any(word in text_lower for word in ['therapy', 'treatment', 'rehabilitation', 'recovery']):
            return 'Digital Therapeutics'
        elif any(word in text_lower for word in ['wellness', 'fitness', 'nutrition', 'lifestyle']):
            return 'Wellness & Fitness'
        elif any(word in text_lower for word in ['platform', 'system', 'software', 'solution', 'service']):
            return 'Healthcare Platform'
        elif any(word in text_lower for word in ['diagnostic', 'screening', 'test', 'analysis']):
            return 'Diagnostics'
        
        return 'Digital Health'
    
    def extract_contact_info(self, text_content: str) -> Dict[str, str]:
        """Extract contact information from website content."""
        contact_info = {}
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text_content)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone numbers (European formats)
        phone_patterns = [
            r'\+\d{1,3}\s*\d{1,4}\s*\d{1,8}',  # International format
            r'\d{3,4}[-\s]\d{3,8}',  # Local format
            r'\(\d{2,4}\)\s*\d{3,8}'  # Area code format
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text_content)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # Extract LinkedIn profiles
        linkedin_pattern = r'linkedin\.com/(?:company|in)/([a-zA-Z0-9-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text_content)
        if linkedin_matches:
            contact_info['linkedin'] = f"https://linkedin.com/company/{linkedin_matches[0]}"
        
        return contact_info
    
    def validate_provided_urls(self, urls: List[str]) -> List[HealthcareCompany]:
        """Validate and extract information from provided URLs - very inclusive."""
        print(f"🔍 Processing {len(urls)} URLs with maximum inclusivity...")
        validated_companies = []
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Processing {url}")
            
            # Fetch website content
            content, success = self.fetch_website_content(url)
            
            if success and content:
                # Extract company information - always try to create a company
                company = self.extract_company_info(url, content)
                
                if company:
                    validated_companies.append(company)
                    self.validated_urls.add(url)
                    print(f"   ✅ Extracted: {company.name}")
                else:
                    print(f"   ⚠️  Failed to extract info")
            else:
                print(f"   ❌ Failed to fetch")
            
            # Small delay to be respectful
            time.sleep(random.uniform(0.2, 1))
        
        return validated_companies
    
    def save_results(self, filename: str = "european_healthcare_companies"):
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
        """Run the very inclusive scraping process."""
        print("🚀 Starting European Healthcare Company Scraper")
        print("   Maximum inclusivity - capturing all possible companies")
        print("=" * 60)
        
        # Process all provided URLs
        validated_companies = self.validate_provided_urls(provided_urls)
        self.companies.extend(validated_companies)
        self.session_stats['valid_companies_found'] = len(validated_companies)
        
        # Display results
        print(f"\n📊 SCRAPING RESULTS:")
        print(f"   📋 Total URLs processed: {self.session_stats['total_urls_checked']}")
        print(f"   ✅ Companies extracted: {self.session_stats['valid_companies_found']}")
        print(f"   ❌ Failed URLs: {self.session_stats['failed_urls']}")
        print(f"   ⚠️  Extraction errors: {self.session_stats['extraction_errors']}")
        
        # Display category breakdown
        if self.companies:
            categories = {}
            countries = {}
            for company in self.companies:
                categories[company.category] = categories.get(company.category, 0) + 1
                countries[company.location] = countries.get(company.location, 0) + 1
            
            print(f"\n📈 BREAKDOWN BY CATEGORY:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count} companies")
            
            print(f"\n🌍 BREAKDOWN BY LOCATION:")
            for location, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {location}: {count} companies")
        
        # Display sample companies
        if self.companies:
            print(f"\n🏢 EXTRACTED EUROPEAN HEALTHCARE COMPANIES:")
            for i, company in enumerate(self.companies[:10], 1):  # Show first 10
                print(f"   {i}. {company.name}")
                print(f"      🌐 {company.website}")
                print(f"      📍 {company.location}")
                print(f"      🏷️  {company.category}")
                if company.email:
                    print(f"      📧 {company.email}")
                print()
            
            if len(self.companies) > 10:
                print(f"   ... and {len(self.companies) - 10} more companies")
        
        # Save results
        self.save_results()
        
        return self.companies

def main():
    """Main function to run the European healthcare company scraper."""
    
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
    
    # Create very inclusive scraper
    scraper = EuropeanHealthcareScraper()
    
    # Run the scraping process
    companies = scraper.run(provided_urls=provided_urls)
    
    # Final summary
    print(f"\n🎉 SCRAPING COMPLETE!")
    print(f"   Successfully extracted {len(companies)} European healthcare companies")
    print(f"   Results saved to output/ directory")
    print(f"   Coverage: {len(companies)}/{len(provided_urls)} URLs ({len(companies)/len(provided_urls)*100:.1f}%)")

if __name__ == "__main__":
    main()