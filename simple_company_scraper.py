#!/usr/bin/env python3
"""
Simple European Healthcare Company Scraper
Maximum inclusivity - extracts company information from all provided URLs
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
from typing import List, Dict
from pathlib import Path
import ssl

@dataclass
class HealthcareCompany:
    """Simple data class for healthcare companies."""
    name: str
    website: str
    description: str = ""
    location: str = ""
    category: str = ""
    email: str = ""
    phone: str = ""
    extraction_date: str = ""

class SimpleHealthcareScraper:
    """Simple scraper that extracts company data from URLs."""
    
    def __init__(self):
        self.companies = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def create_ssl_context(self):
        """Create SSL context that handles certificate issues."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    
    def fetch_content(self, url: str) -> tuple[str, bool]:
        """Fetch content from URL."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            req = urllib.request.Request(url, headers=self.headers)
            context = self.create_ssl_context()
            
            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                content = response.read()
                try:
                    content = content.decode('utf-8', errors='ignore')
                except:
                    content = content.decode('latin-1', errors='ignore')
                return content, True
        except Exception as e:
            print(f"   ❌ Error fetching {url}: {str(e)[:50]}")
            return "", False
    
    def extract_title(self, content: str) -> str:
        """Extract title from HTML content."""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            title = title.replace('\n', ' ').replace('\r', '')
            if len(title) > 100:
                title = title[:100] + "..."
            return title
        return ""
    
    def extract_description(self, content: str) -> str:
        """Extract description from meta tags."""
        # Try meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1)[:300]
        
        # Try og:description
        og_match = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
        if og_match:
            return og_match.group(1)[:300]
        
        return "European healthcare technology company"
    
    def extract_location(self, content: str, url: str) -> str:
        """Extract location information."""
        content_lower = content.lower()
        
        # European cities
        cities = ['berlin', 'munich', 'hamburg', 'cologne', 'frankfurt', 'london', 'paris', 'madrid', 'rome', 'amsterdam', 'vienna', 'zurich']
        for city in cities:
            if city in content_lower:
                return city.title() + ", Europe"
        
        # Country from domain
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
        
        return 'Europe'
    
    def determine_category(self, content: str, url: str) -> str:
        """Determine company category."""
        content_lower = content.lower()
        url_lower = url.lower()
        
        if 'app' in url_lower or 'app' in content_lower:
            return 'Health Apps'
        elif 'ai' in url_lower or 'artificial intelligence' in content_lower:
            return 'Healthcare AI'
        elif 'analytics' in content_lower or 'data' in content_lower:
            return 'Healthcare Analytics'
        elif 'therapy' in content_lower or 'treatment' in content_lower:
            return 'Digital Therapeutics'
        elif 'telemedicine' in content_lower or 'telehealth' in content_lower:
            return 'Telemedicine'
        else:
            return 'Digital Health'
    
    def extract_contact_info(self, content: str) -> dict:
        """Extract contact information."""
        contact = {}
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        if email_match:
            contact['email'] = email_match.group(0)
        
        # Extract phone (simple pattern)
        phone_match = re.search(r'\+\d{1,3}[-\s]?\d{1,4}[-\s]?\d{1,8}', content)
        if phone_match:
            contact['phone'] = phone_match.group(0)
        
        return contact
    
    def extract_company_name(self, url: str, title: str) -> str:
        """Extract company name from URL and title."""
        if title:
            # Clean title to get company name
            name = title.split('-')[0].split('|')[0].split(':')[0]
            name = re.sub(r'\s*(home|homepage|startseite|welcome)\s*', '', name, flags=re.IGNORECASE)
            if len(name.strip()) > 3:
                return name.strip()
        
        # Fall back to domain name
        domain = urllib.parse.urlparse(url).netloc
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'\.(com|de|org|net|eu|co|app|ai|tech)$', '', domain)
        return domain.replace('-', ' ').replace('_', ' ').title()
    
    def process_urls(self, urls: List[str]) -> List[HealthcareCompany]:
        """Process all URLs and extract company information."""
        companies = []
        
        print(f"🔍 Processing {len(urls)} URLs with maximum inclusivity...")
        
        for i, url in enumerate(urls, 1):
            print(f"   [{i}/{len(urls)}] Processing {url}")
            
            content, success = self.fetch_content(url)
            
            if success and content:
                # Extract information
                title = self.extract_title(content)
                company_name = self.extract_company_name(url, title)
                description = self.extract_description(content)
                location = self.extract_location(content, url)
                category = self.determine_category(content, url)
                contact = self.extract_contact_info(content)
                
                # Create company object
                company = HealthcareCompany(
                    name=company_name,
                    website=url,
                    description=description,
                    location=location,
                    category=category,
                    email=contact.get('email', ''),
                    phone=contact.get('phone', ''),
                    extraction_date=time.strftime('%Y-%m-%d')
                )
                
                companies.append(company)
                print(f"   ✅ Extracted: {company.name}")
            else:
                print(f"   ❌ Failed to process")
            
            # Small delay
            time.sleep(random.uniform(0.2, 0.8))
        
        return companies
    
    def save_results(self, companies: List[HealthcareCompany], filename: str = "european_healthcare_companies"):
        """Save results to files."""
        Path("output").mkdir(exist_ok=True)
        
        # Save JSON
        json_file = f"output/{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(company) for company in companies], f, indent=2, ensure_ascii=False)
        
        # Save CSV
        csv_file = f"output/{filename}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if companies:
                writer = csv.DictWriter(f, fieldnames=asdict(companies[0]).keys())
                writer.writeheader()
                for company in companies:
                    writer.writerow(asdict(company))
        
        print(f"\n✅ Results saved to:")
        print(f"   📄 {json_file}")
        print(f"   📊 {csv_file}")
    
    def run(self, urls: List[str]):
        """Main scraping function."""
        print("🚀 Starting Simple European Healthcare Company Scraper")
        print("   Maximum inclusivity - extracting from all accessible URLs")
        print("=" * 60)
        
        companies = self.process_urls(urls)
        self.companies = companies
        
        print(f"\n📊 SCRAPING RESULTS:")
        print(f"   📋 Total URLs processed: {len(urls)}")
        print(f"   ✅ Companies extracted: {len(companies)}")
        print(f"   📈 Success rate: {len(companies)/len(urls)*100:.1f}%")
        
        if companies:
            # Show category breakdown
            categories = {}
            locations = {}
            for company in companies:
                categories[company.category] = categories.get(company.category, 0) + 1
                locations[company.location] = locations.get(company.location, 0) + 1
            
            print(f"\n📈 CATEGORY BREAKDOWN:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"   {category}: {count} companies")
            
            print(f"\n🌍 LOCATION BREAKDOWN:")
            for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
                print(f"   {location}: {count} companies")
            
            print(f"\n🏢 SAMPLE COMPANIES:")
            for i, company in enumerate(companies[:10], 1):
                print(f"   {i}. {company.name}")
                print(f"      🌐 {company.website}")
                print(f"      📍 {company.location}")
                print(f"      🏷️  {company.category}")
                if company.email:
                    print(f"      📧 {company.email}")
                print()
            
            if len(companies) > 10:
                print(f"   ... and {len(companies) - 10} more companies")
        
        self.save_results(companies)
        
        return companies

def main():
    """Main function."""
    
    # Your provided URLs
    urls = [
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
    
    scraper = SimpleHealthcareScraper()
    companies = scraper.run(urls)
    
    print(f"\n🎉 SCRAPING COMPLETE!")
    print(f"   Successfully extracted {len(companies)} European healthcare companies")
    print(f"   Coverage: {len(companies)}/{len(urls)} URLs ({len(companies)/len(urls)*100:.1f}%)")

if __name__ == "__main__":
    main()