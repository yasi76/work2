#!/usr/bin/env python3
"""
Enhanced German Healthcare Company Scraper
Extracts real healthcare companies from German directories
Uses only Python standard library for maximum compatibility
"""

import urllib.request
import urllib.parse
import json
import csv
import re
import time
import ssl
from dataclasses import dataclass, asdict
from typing import List, Dict, Set
from pathlib import Path

@dataclass
class HealthcareCompany:
    name: str
    website: str = ""
    description: str = ""
    location: str = "Germany"
    category: str = ""
    source_directory: str = ""
    founded_year: str = ""
    employee_count: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class HealthcareScraper:
    def __init__(self, existing_companies_file: str = None):
        self.existing_companies = set()
        self.scraped_companies = []
        
        # Load existing companies to avoid duplicates
        if existing_companies_file and Path(existing_companies_file).exists():
            self.load_existing_companies(existing_companies_file)
        
        # Create SSL context that's more permissive
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def load_existing_companies(self, filename: str):
        """Load existing companies to avoid duplicates"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    companies = json.load(f)
                    for company in companies:
                        if 'website' in company and company['website']:
                            self.existing_companies.add(company['website'].lower())
                        if 'name' in company:
                            self.existing_companies.add(company['name'].lower())
                else:  # CSV
                    import csv
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'website' in row and row['website']:
                            self.existing_companies.add(row['website'].lower())
                        if 'name' in row:
                            self.existing_companies.add(row['name'].lower())
            print(f"Loaded {len(self.existing_companies)} existing companies to avoid duplicates")
        except Exception as e:
            print(f"Warning: Could not load existing companies: {e}")
    
    def fetch_url(self, url: str) -> str:
        """Fetch URL with proper headers and SSL handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            # Use custom SSL context for HTTPS URLs
            if url.startswith('https://'):
                with urllib.request.urlopen(req, timeout=30, context=self.ssl_context) as response:
                    content = response.read()
            else:
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
            
            # Try to decode with UTF-8, fallback to other encodings
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return content.decode('latin-1')
                except UnicodeDecodeError:
                    return content.decode('utf-8', errors='ignore')
                    
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def is_new_company(self, name: str, website: str) -> bool:
        """Check if company is new (not in existing list)"""
        if name.lower() in self.existing_companies:
            return False
        if website and website.lower() in self.existing_companies:
            return False
        return True
    
    def extract_companies_from_html(self, html: str, source_url: str, category: str) -> List[HealthcareCompany]:
        """Extract companies from HTML using regex patterns"""
        companies = []
        
        if not html:
            return companies
        
        # Pattern 1: Company links with names
        link_patterns = [
            r'<a[^>]*href=["\']([^"\']*(?:\.com|\.de|\.org|\.net|\.eu|\.health|\.io)[^"\']*)["\'][^>]*>([^<]{4,80})</a>',
            r'href=["\']([^"\']*(?:\.com|\.de|\.org|\.net|\.eu|\.health|\.io)[^"\']*)["\'][^>]*title=["\']([^"\']{4,80})["\']',
            r'<td[^>]*>([^<]{4,80})</td>[^<]*<td[^>]*><a[^>]*href=["\']([^"\']*(?:\.com|\.de|\.org|\.net|\.eu|\.health|\.io)[^"\']*)["\']'
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) == 2:
                    url, name = match
                    name = self.clean_company_name(name)
                    
                    if self.is_valid_healthcare_company(name, url) and self.is_new_company(name, url):
                        companies.append(HealthcareCompany(
                            name=name,
                            website=url,
                            source_directory=source_url,
                            category=category,
                            location="Germany"
                        ))
        
        # Pattern 2: Company names with German business suffixes
        company_name_patterns = [
            r'\b([A-Z][a-zA-Z\s&.-]{3,50}(?:GmbH|AG|KG|OHG|mbH))\b',
            r'\b([A-Z][a-zA-Z\s&.-]{4,50}(?:Systems|Technologies|Solutions|Medical|Health|Care|Tech|Bio|Pharma|Diagnostics|Therapeutics))\b'
        ]
        
        for pattern in company_name_patterns:
            matches = re.findall(pattern, html)
            for name in matches:
                name = self.clean_company_name(name)
                if self.is_valid_healthcare_company(name, "") and self.is_new_company(name, ""):
                    # Try to find associated website
                    website = self.find_nearby_website(html, name)
                    companies.append(HealthcareCompany(
                        name=name,
                        website=website,
                        source_directory=source_url,
                        category=category,
                        location="Germany"
                    ))
        
        return companies
    
    def clean_company_name(self, name: str) -> str:
        """Clean and normalize company name"""
        # Remove HTML tags
        name = re.sub(r'<[^>]+>', '', name)
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Remove quotes
        name = name.strip('"\'')
        return name.strip()
    
    def is_valid_healthcare_company(self, name: str, url: str) -> bool:
        """Check if this is a valid healthcare company"""
        if not name or len(name) < 3:
            return False
        
        # Skip obvious non-companies
        skip_words = [
            'cookie', 'datenschutz', 'impressum', 'kontakt', 'about', 'news',
            'domain', 'marktplatz', 'verkaufen', 'elite', 'mehr', 'weiter',
            'startseite', 'home', 'login', 'register', 'search', 'zurück'
        ]
        
        if any(skip in name.lower() for skip in skip_words):
            return False
        
        # Look for healthcare indicators
        healthcare_keywords = [
            'health', 'medical', 'medtech', 'biotech', 'pharma', 'care',
            'clinic', 'hospital', 'diagnostics', 'therapeutics', 'surgical',
            'dental', 'orthopedic', 'cardio', 'neuro', 'onco', 'radio',
            'gmbh', 'ag', 'systems', 'solutions', 'technologies', 'instruments',
            'devices', 'equipment', 'software', 'digital', 'innovation'
        ]
        
        # More lenient matching for German companies
        if any(keyword in name.lower() for keyword in healthcare_keywords):
            return True
        
        # German business suffixes are good indicators
        if any(suffix in name for suffix in ['GmbH', 'AG', 'KG', 'OHG']):
            return True
        
        return False
    
    def find_nearby_website(self, html: str, company_name: str) -> str:
        """Find website URL near company name in HTML"""
        try:
            # Find position of company name
            name_pos = html.find(company_name)
            if name_pos == -1:
                return ""
            
            # Look in 2000 character window around the name
            start = max(0, name_pos - 1000)
            end = min(len(html), name_pos + 1000)
            window = html[start:end]
            
            # Find URLs in this window
            url_pattern = r'https?://[a-zA-Z0-9.-]+\.(?:com|de|org|net|eu|health|io)(?:[^\s<>"\']*)?'
            urls = re.findall(url_pattern, window)
            
            for url in urls:
                if self.is_valid_company_website(url):
                    return url
        except Exception:
            pass
        
        return ""
    
    def is_valid_company_website(self, url: str) -> bool:
        """Check if URL looks like a company website"""
        if not url:
            return False
        
        # Skip common non-company URLs
        skip_domains = [
            'google.com', 'facebook.com', 'twitter.com', 'linkedin.com',
            'youtube.com', 'instagram.com', 'xing.com', 'kununu.com'
        ]
        
        return not any(domain in url.lower() for domain in skip_domains)
    
    def scrape_healthcare_directories(self) -> List[HealthcareCompany]:
        """Scrape multiple German healthcare directories"""
        
        # Curated list of working German healthcare directories
        directories = [
            {
                'name': 'BVMed Medical Technology',
                'url': 'https://www.bvmed.de/de/unternehmen/mitgliedsunternehmen',
                'category': 'Medical Technology'
            },
            {
                'name': 'SPECTARIS Industry Association',
                'url': 'https://www.spectaris.de/mitglieder/',
                'category': 'Medical Technology'
            },
            {
                'name': 'Berlin Health Startups',
                'url': 'https://berlin.startup-directory.de/startups/health',
                'category': 'Digital Health'
            },
            {
                'name': 'German Biotech Directory',
                'url': 'https://biotechnologie.de/branche/biotech-branche/biotech-unternehmen',
                'category': 'Biotechnology'
            },
            {
                'name': 'Medical Valley Directory',
                'url': 'https://www.medical-valley-emn.de/unternehmen/',
                'category': 'Medical Technology'
            },
            {
                'name': 'Health Innovation Hub',
                'url': 'https://hih-2025.de/portfolio/',
                'category': 'Health Innovation'
            }
        ]
        
        all_companies = []
        
        for directory in directories:
            print(f"Scraping {directory['name']}...")
            
            html = self.fetch_url(directory['url'])
            if html:
                companies = self.extract_companies_from_html(
                    html, directory['url'], directory['category']
                )
                all_companies.extend(companies)
                print(f"✅ Found {len(companies)} companies from {directory['name']}")
            else:
                print(f"❌ Failed to fetch {directory['name']}")
            
            # Rate limiting
            time.sleep(2)
        
        return all_companies
    
    def save_results(self, companies: List[HealthcareCompany], output_dir: str = "output"):
        """Save results to CSV and JSON files"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save as JSON
        json_file = Path(output_dir) / "healthcare_companies.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(company) for company in companies], f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = Path(output_dir) / "healthcare_companies.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if companies:
                writer = csv.DictWriter(f, fieldnames=asdict(companies[0]).keys())
                writer.writeheader()
                for company in companies:
                    writer.writerow(asdict(company))
        
        print(f"✅ Results saved to {json_file} and {csv_file}")
    
    def run(self) -> List[HealthcareCompany]:
        """Run the complete scraping process"""
        print("🚀 Starting German Healthcare Company Scraper")
        print("=" * 60)
        
        # Scrape all directories
        companies = self.scrape_healthcare_directories()
        
        # Remove duplicates
        unique_companies = []
        seen = set()
        
        for company in companies:
            key = (company.name.lower(), company.website.lower())
            if key not in seen:
                seen.add(key)
                unique_companies.append(company)
        
        print(f"\n📊 RESULTS:")
        print(f"   Total companies found: {len(unique_companies)}")
        print(f"   Companies with websites: {sum(1 for c in unique_companies if c.website)}")
        
        # Show breakdown by category
        categories = {}
        for company in unique_companies:
            categories[company.category] = categories.get(company.category, 0) + 1
        
        print(f"\n📈 BREAKDOWN BY CATEGORY:")
        for category, count in categories.items():
            print(f"   {category}: {count} companies")
        
        # Show sample companies
        print(f"\n🏢 SAMPLE COMPANIES:")
        for i, company in enumerate(unique_companies[:10]):
            print(f"   {i+1}. {company.name}")
            if company.website:
                print(f"      🌐 {company.website}")
            print(f"      📍 {company.location}")
            print(f"      🏷️  {company.category}")
            print()
        
        # Save results
        self.save_results(unique_companies)
        
        return unique_companies

def main():
    """Main function"""
    scraper = HealthcareScraper("existing_companies.json")
    companies = scraper.run()
    
    print(f"\n🎉 SCRAPING COMPLETE!")
    print(f"   Extracted {len(companies)} unique German healthcare companies")
    print(f"   Results saved to output/ directory")

if __name__ == "__main__":
    main()