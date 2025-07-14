#!/usr/bin/env python3
"""
Enterprise Healthcare Company Discovery System
AI-Powered Data Collection for European Healthcare Companies

This system automatically discovers healthcare companies from multiple sources:
- Company websites and directories
- Crunchbase, AngelList, and industry databases
- News articles and press releases
- LinkedIn and professional networks
- Government startup databases
- Healthcare industry platforms

Author: Healthcare Discovery AI
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
from typing import List, Dict, Set, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import ssl
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

@dataclass
class HealthcareCompany:
    """Comprehensive data class for European healthcare companies."""
    
    # Core Information
    name: str
    website: str
    description: str = ""
    location: str = ""
    country: str = ""
    city: str = ""
    
    # Business Details
    category: str = ""
    subcategory: str = ""
    industry_tags: List[str] = None
    business_model: str = ""
    target_market: str = ""
    
    # Financial Information
    founded_year: str = ""
    employees: str = ""
    funding_amount: str = ""
    funding_stage: str = ""
    revenue: str = ""
    valuation: str = ""
    
    # Contact and Social
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    twitter: str = ""
    crunchbase: str = ""
    
    # Discovery Metadata
    source: str = ""
    discovery_method: str = ""
    confidence_score: float = 0.0
    last_updated: str = ""
    
    def __post_init__(self):
        if self.industry_tags is None:
            self.industry_tags = []

class EnterpriseHealthcareDiscovery:
    """AI-Powered Healthcare Company Discovery System for Europe and Germany."""
    
    def __init__(self):
        self.companies = []
        self.discovered_urls = set()
        self.processed_sources = set()
        self.discovery_sources = []
        self.lock = threading.Lock()
        
        # SSL context for HTTPS requests
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        self.setup_discovery_sources()
    
    def setup_discovery_sources(self):
        """Setup comprehensive discovery sources for European healthcare companies."""
        
        # German Healthcare Directories
        german_sources = [
            "https://www.healthcapital.de/companies",
            "https://www.berlinhealthinnovation.com/companies",
            "https://www.health-innovation.org/directory",
            "https://www.medicalvalues.com/companies",
            "https://www.health-tech.de/companies",
            "https://www.biopharma-germany.com/directory",
            "https://www.germanstartupmonitor.de/healthcare",
            "https://www.gtai.de/gtai-en/invest/industries/healthcare",
            "https://www.digital-health.de/companies",
            "https://www.bvds.de/mitglieder",
        ]
        
        # European Healthcare Platforms
        european_sources = [
            "https://www.healthtech-europe.com/directory",
            "https://www.medtech-europe.org/members",
            "https://www.eucomed.org/members",
            "https://www.efpia.eu/about-medicines/development-of-medicines/",
            "https://www.ema.europa.eu/en/partners-networks",
            "https://www.ehealth-impact.org/companies",
            "https://www.healtheuropa.eu/companies",
            "https://www.ehealthnews.eu/companies",
            "https://www.healthcare-innovations.org/directory",
            "https://www.health20-paris.com/companies",
        ]
        
        # Global Startup Directories
        startup_directories = [
            "https://www.crunchbase.com/discover/organization.companies/field/categories/slug/health-care",
            "https://angel.co/companies?markets=Healthcare",
            "https://www.f6s.com/companies/healthcare",
            "https://www.startupranking.com/categories/healthcare",
            "https://tracxn.com/explore/Healthcare-Startups",
            "https://www.cbinsights.com/companies/healthcare",
            "https://pitchbook.com/industries/healthcare",
            "https://wellfound.com/companies?markets=Healthcare",
            "https://www.indiehackers.com/companies?category=healthcare",
            "https://www.producthunt.com/topics/health-and-fitness",
        ]
        
        # Industry-Specific Platforms
        healthcare_platforms = [
            "https://www.healthcarestartups.com/directory",
            "https://www.digitalhealthcompanies.com",
            "https://www.healthtechcompanies.com",
            "https://www.medstartups.com",
            "https://www.healthtechfinder.com",
            "https://www.medtech.directory",
            "https://www.healthcareinnovation.com/companies",
            "https://www.healthnewsreview.org/companies",
            "https://www.himss.org/healthcare-it-companies",
            "https://www.healthcareitnews.com/companies",
        ]
        
        # Government and Institution Sources
        government_sources = [
            "https://www.bmwi.de/Redaktion/DE/Dossier/digitale-gesundheitswirtschaft.html",
            "https://www.bmbf.de/foerderungen/bekanntmachung-2951.html",
            "https://www.exist.de/EXIST/Navigation/DE/Gruendungsfoerderung/EXIST-Forschungstransfer/exist-forschungstransfer.html",
            "https://ec.europa.eu/health/ehealth/policy_en",
            "https://ec.europa.eu/programmes/horizon2020/en/area/health-demographic-change-and-wellbeing",
            "https://www.eit.europa.eu/our-communities/eit-health",
            "https://www.eib.org/en/products/advisory-services/innovfin/life-sciences",
            "https://www.eif.org/what_we_do/equity/news/2019/index.htm",
        ]
        
        # News and Media Sources
        media_sources = [
            "https://www.mobihealthnews.com/companies",
            "https://www.healthtechnews.com/companies",
            "https://www.fiercehealthcare.com/companies",
            "https://www.medcitynews.com/companies",
            "https://www.healthcarefinancenews.com/companies",
            "https://www.digitalhealth.net/companies",
            "https://www.healthcare-it-news.com/companies",
            "https://www.healthdatamanagement.com/companies",
            "https://www.healthleadersmedia.com/companies",
            "https://www.modernhealthcare.com/companies",
        ]
        
        # LinkedIn and Professional Networks
        professional_sources = [
            "https://www.linkedin.com/company/search/results/?keywords=healthcare%20startup",
            "https://www.linkedin.com/company/search/results/?keywords=digital%20health",
            "https://www.linkedin.com/company/search/results/?keywords=medtech",
            "https://www.linkedin.com/company/search/results/?keywords=healthtech",
            "https://www.xing.com/companies/healthcare",
        ]
        
        self.discovery_sources = {
            'german': german_sources,
            'european': european_sources,
            'startups': startup_directories,
            'healthcare': healthcare_platforms,
            'government': government_sources,
            'media': media_sources,
            'professional': professional_sources
        }
    
    def get_headers(self) -> Dict[str, str]:
        """Get rotating headers for requests."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def fetch_url(self, url: str, timeout: int = 30) -> str:
        """Fetch URL content with error handling using urllib."""
        try:
            headers = self.get_headers()
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=timeout, context=self.ssl_context) as response:
                content = response.read()
                # Try to decode with utf-8, fallback to latin-1
                try:
                    return content.decode('utf-8')
                except UnicodeDecodeError:
                    return content.decode('latin-1', errors='ignore')
                    
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""
    
    def extract_companies_from_directory(self, html: str, source_url: str) -> List[str]:
        """Extract company URLs from directory pages."""
        company_urls = []
        
        # Healthcare company URL patterns
        patterns = [
            r'https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:com|de|eu|org|net|io|co|health|care|med))["\s<>]',
            r'href=["\']https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:com|de|eu|org|net|io|co|health|care|med))["\']',
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?(?:healthcare|health|medical|med|clinic|hospital|pharma|biotech|digital health|telehealth|telemedicine)',
        ]
        
        # Healthcare-related keywords for filtering
        healthcare_keywords = [
            'healthcare', 'health', 'medical', 'med', 'clinic', 'hospital', 'pharma', 'pharmaceutical',
            'biotech', 'biotechnology', 'digital health', 'ehealth', 'e-health', 'telehealth',
            'telemedicine', 'medtech', 'healthtech', 'wellness', 'fitness', 'therapy', 'diagnostic',
            'therapeutics', 'device', 'surgery', 'patient', 'doctor', 'nurse', 'care'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match.group(1) if match.groups() else match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url.lstrip('/')
                
                # Filter for healthcare relevance
                if any(keyword in url.lower() or keyword in html[max(0, match.start()-100):match.end()+100].lower() 
                       for keyword in healthcare_keywords):
                    company_urls.append(url)
        
        return list(set(company_urls))
    
    def discover_from_crunchbase_api(self) -> List[str]:
        """Discover companies from Crunchbase-style data."""
        crunchbase_urls = []
        
        search_terms = [
            "healthcare startup europe",
            "digital health germany", 
            "medtech europe",
            "healthtech startup",
            "medical device europe",
            "pharmaceutical startup",
            "biotech europe",
            "telemedicine startup"
        ]
        
        for term in search_terms:
            search_url = f"https://www.crunchbase.com/discover/organization.companies?q={urllib.parse.quote(term)}"
            try:
                html = self.fetch_url(search_url)
                urls = self.extract_companies_from_directory(html, search_url)
                crunchbase_urls.extend(urls)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Error searching Crunchbase for '{term}': {e}")
        
        return crunchbase_urls
    
    def discover_from_angellist(self) -> List[str]:
        """Discover companies from AngelList/Wellfound."""
        angellist_urls = []
        
        healthcare_markets = [
            "Healthcare", "Digital Health", "Medical Devices", "Biotechnology",
            "Pharmaceuticals", "Healthcare IT", "Telemedicine", "Medical"
        ]
        
        for market in healthcare_markets:
            search_url = f"https://wellfound.com/companies?markets={urllib.parse.quote(market)}&locations=Europe"
            try:
                html = self.fetch_url(search_url)
                urls = self.extract_companies_from_directory(html, search_url)
                angellist_urls.extend(urls)
                time.sleep(2)
            except Exception as e:
                print(f"Error searching AngelList for '{market}': {e}")
        
        return angellist_urls
    
    def discover_from_government_sources(self) -> List[str]:
        """Discover companies from government and institutional sources."""
        government_urls = []
        
        for source in self.discovery_sources['government']:
            try:
                html = self.fetch_url(source)
                urls = self.extract_companies_from_directory(html, source)
                government_urls.extend(urls)
                time.sleep(2)
            except Exception as e:
                print(f"Error processing government source {source}: {e}")
        
        return government_urls
    
    def discover_from_news_sources(self) -> List[str]:
        """Discover companies from healthcare news and media."""
        news_urls = []
        
        for source in self.discovery_sources['media']:
            try:
                html = self.fetch_url(source)
                urls = self.extract_companies_from_directory(html, source)
                news_urls.extend(urls)
                time.sleep(2)
            except Exception as e:
                print(f"Error processing news source {source}: {e}")
        
        return news_urls
    
    def discover_from_linkedin(self) -> List[str]:
        """Discover companies from LinkedIn searches."""
        # Note: LinkedIn requires authentication for full access
        # This is a simplified version for demonstration
        linkedin_urls = []
        
        search_terms = [
            "healthcare startup", "digital health", "medtech", "healthtech",
            "medical device", "pharmaceutical", "biotech", "telemedicine"
        ]
        
        for term in search_terms:
            # This would require LinkedIn API access or specialized scraping
            print(f"LinkedIn discovery for '{term}' would require API integration")
        
        return linkedin_urls
    
    def extract_company_info(self, html: str, url: str) -> HealthcareCompany:
        """Extract detailed company information from website."""
        
        # Extract company name
        name_patterns = [
            r'<title>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'<meta property="og:title" content="([^"]+)"',
            r'<meta name="title" content="([^"]+)"'
        ]
        
        name = ""
        for pattern in name_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name
                name = re.sub(r'\s*\|\s*.*$', '', name)  # Remove everything after |
                name = re.sub(r'\s*-\s*.*$', '', name)   # Remove everything after -
                break
        
        if not name:
            name = url.split('//')[1].split('/')[0].replace('www.', '').split('.')[0].title()
        
        # Extract description
        desc_patterns = [
            r'<meta name="description" content="([^"]+)"',
            r'<meta property="og:description" content="([^"]+)"',
            r'<p[^>]*class="[^"]*(?:description|about|intro)[^"]*"[^>]*>([^<]+)</p>'
        ]
        
        description = ""
        for pattern in desc_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                description = match.group(1).strip()
                break
        
        # Extract location
        location_patterns = [
            r'(?:location|address|based in|headquarters)[:\s]*([A-Za-z\s,]+?)(?:\s*[<\n]|$)',
            r'([A-Za-z]+,\s*(?:Germany|Deutschland|Berlin|Munich|Hamburg|Frankfurt))',
            r'(Berlin|Munich|Hamburg|Frankfurt|Cologne|Stuttgart|Germany|Deutschland)'
        ]
        
        location = ""
        for pattern in location_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
        
        # Determine country
        country = ""
        if any(term in (location + html).lower() for term in ['germany', 'deutschland', 'berlin', 'munich', 'hamburg']):
            country = "Germany"
        elif any(term in (location + html).lower() for term in ['france', 'paris', 'lyon']):
            country = "France"
        elif any(term in (location + html).lower() for term in ['uk', 'london', 'manchester', 'edinburgh']):
            country = "UK"
        elif '.de' in url:
            country = "Germany"
        elif '.fr' in url:
            country = "France"
        elif '.co.uk' in url:
            country = "UK"
        
        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, html)
        email = email_match.group(0) if email_match else ""
        
        # Extract LinkedIn
        linkedin_pattern = r'(?:linkedin\.com/company/)([\w-]+)'
        linkedin_match = re.search(linkedin_pattern, html, re.IGNORECASE)
        linkedin = f"https://linkedin.com/company/{linkedin_match.group(1)}" if linkedin_match else ""
        
        # Categorize company
        category = self.categorize_company(html)
        
        return HealthcareCompany(
            name=name,
            website=url,
            description=description,
            location=location,
            country=country,
            email=email,
            linkedin=linkedin,
            category=category,
            source=url,
            discovery_method="web_scraping",
            confidence_score=0.8,
            last_updated=datetime.now().isoformat()
        )
    
    def categorize_company(self, html: str) -> str:
        """Categorize company based on content analysis."""
        content_lower = html.lower()
        
        if any(term in content_lower for term in ['telemedicine', 'telehealth', 'remote consultation']):
            return "Telemedicine"
        elif any(term in content_lower for term in ['medical device', 'diagnostic', 'imaging']):
            return "Medical Devices"
        elif any(term in content_lower for term in ['pharmaceutical', 'drug', 'medicine']):
            return "Pharmaceuticals"
        elif any(term in content_lower for term in ['biotech', 'biotechnology', 'genetics']):
            return "Biotechnology"
        elif any(term in content_lower for term in ['digital health', 'health app', 'mobile health']):
            return "Digital Health"
        elif any(term in content_lower for term in ['hospital', 'clinic', 'healthcare provider']):
            return "Healthcare Services"
        elif any(term in content_lower for term in ['health insurance', 'insurance']):
            return "Health Insurance"
        else:
            return "Healthcare IT"
    
    def process_discovery_batch(self, urls: List[str], batch_name: str) -> None:
        """Process a batch of URLs for company discovery."""
        print(f"🔍 Processing {len(urls)} URLs from {batch_name}...")
        
        for i, url in enumerate(urls):
            try:
                print(f"  [{i+1}/{len(urls)}] Processing: {url}")
                self.process_single_url(url)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"  ❌ Error with {url}: {e}")
    
    def process_single_url(self, url: str) -> None:
        """Process a single URL to extract company information."""
        if url in self.processed_sources:
            return
        
        try:
            html = self.fetch_url(url)
            if not html:
                return
            
            # Extract companies from directory page
            discovered_urls = self.extract_companies_from_directory(html, url)
            
            # Process each discovered company
            for company_url in discovered_urls[:5]:  # Limit to 5 companies per source for demonstration
                if company_url not in self.discovered_urls:
                    self.discovered_urls.add(company_url)
                    company_html = self.fetch_url(company_url)
                    if company_html:
                        company = self.extract_company_info(company_html, company_url)
                        if company.name and len(company.name) > 2:  # Basic validation
                            with self.lock:
                                self.companies.append(company)
                            print(f"    ✅ Discovered: {company.name} ({company.country}) - {company.category}")
                    
                    time.sleep(0.5)  # Rate limiting
            
            self.processed_sources.add(url)
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    def run_comprehensive_discovery(self) -> None:
        """Run comprehensive AI-powered discovery across all sources."""
        print("🚀 ENTERPRISE HEALTHCARE COMPANY DISCOVERY SYSTEM")
        print("=" * 60)
        print("📊 Target: Comprehensive European & German Healthcare Companies")
        print("🎯 AI-Powered Data Collection from Multiple Sources")
        print("=" * 60)
        
        start_time = time.time()
        
        # Phase 1: German Healthcare Sources
        print("\n🇩🇪 PHASE 1: GERMAN HEALTHCARE DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['german'][:3], "German Healthcare")
        
        # Phase 2: European Healthcare Sources  
        print(f"\n🇪🇺 PHASE 2: EUROPEAN HEALTHCARE DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['european'][:3], "European Healthcare")
        
        # Phase 3: Startup Directories
        print(f"\n🚀 PHASE 3: STARTUP DIRECTORY DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['startups'][:3], "Startup Directories")
        
        # Phase 4: Healthcare Platforms
        print(f"\n🏥 PHASE 4: HEALTHCARE PLATFORM DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['healthcare'][:3], "Healthcare Platforms")
        
        # Phase 5: Government Sources
        print(f"\n🏛️ PHASE 5: GOVERNMENT SOURCE DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['government'][:2], "Government Sources")
        
        # Phase 6: News and Media
        print(f"\n📰 PHASE 6: NEWS AND MEDIA DISCOVERY")
        print("-" * 50)
        self.process_discovery_batch(self.discovery_sources['media'][:3], "News and Media")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("✅ ENTERPRISE DISCOVERY COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🏢 Companies Discovered: {len(self.companies)}")
        print(f"🌐 Sources Processed: {len(self.processed_sources)}")
        print(f"🔗 URLs Discovered: {len(self.discovered_urls)}")
        print(f"📈 Discovery Rate: {len(self.companies)/max(1, len(self.processed_sources)):.2f} companies per source")
        
        # Show geographic breakdown
        countries = Counter(company.country for company in self.companies if company.country)
        categories = Counter(company.category for company in self.companies if company.category)
        
        print(f"\n🌍 GEOGRAPHIC DISTRIBUTION:")
        for country, count in countries.most_common():
            print(f"  {country}: {count} companies")
        
        print(f"\n� CATEGORY DISTRIBUTION:")
        for category, count in categories.most_common():
            print(f"  {category}: {count} companies")
        
        self.save_results()
    
    def save_results(self) -> None:
        """Save discovery results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_file = f"output/enterprise_healthcare_companies_{timestamp}.csv"
        Path("output").mkdir(exist_ok=True)
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            if self.companies:
                fieldnames = asdict(self.companies[0]).keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for company in self.companies:
                    writer.writerow(asdict(company))
        
        # Save to JSON
        json_file = f"output/enterprise_healthcare_companies_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as jsonfile:
            json.dump([asdict(company) for company in self.companies], jsonfile, indent=2, ensure_ascii=False)
        
        # Generate summary report
        self.generate_discovery_report(timestamp)
        
        print(f"\n💾 RESULTS SAVED:")
        print(f"📊 CSV: {csv_file}")
        print(f"📋 JSON: {json_file}")
        print(f"📈 Report: output/discovery_report_{timestamp}.md")
    
    def generate_discovery_report(self, timestamp: str) -> None:
        """Generate comprehensive discovery report."""
        report_file = f"output/discovery_report_{timestamp}.md"
        
        # Analytics
        total_companies = len(self.companies)
        countries = Counter(company.country for company in self.companies if company.country)
        categories = Counter(company.category for company in self.companies if company.category)
        
        report = f"""# Enterprise Healthcare Company Discovery Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Discovery Summary
- **Total Companies Discovered:** {total_companies}
- **Sources Processed:** {len(self.processed_sources)}
- **Unique Company URLs:** {len(self.discovered_urls)}
- **Discovery Success Rate:** {(total_companies/max(1, len(self.processed_sources)))*100:.1f}%

## 🌍 Geographic Distribution
"""
        
        for country, count in countries.most_common():
            percentage = (count / total_companies) * 100
            report += f"- **{country}:** {count} companies ({percentage:.1f}%)\n"
        
        report += "\n## 🏥 Category Distribution\n"
        for category, count in categories.most_common():
            percentage = (count / total_companies) * 100
            report += f"- **{category}:** {count} companies ({percentage:.1f}%)\n"
        
        report += f"""
## 🎯 Discovery Sources Performance
- **German Healthcare Sources:** {len(self.discovery_sources['german'])} sources available
- **European Healthcare Sources:** {len(self.discovery_sources['european'])} sources available
- **Startup Directories:** {len(self.discovery_sources['startups'])} sources available
- **Healthcare Platforms:** {len(self.discovery_sources['healthcare'])} sources available
- **Government Sources:** {len(self.discovery_sources['government'])} sources available
- **News and Media:** {len(self.discovery_sources['media'])} sources available

## 🚀 Top Discovered Companies

### German Companies
"""
        
        german_companies = [c for c in self.companies if c.country == "Germany"][:20]
        for i, company in enumerate(german_companies, 1):
            report += f"{i}. **{company.name}** - {company.category} - {company.website}\n"
        
        report += "\n### Other European Countries\n"
        non_german_companies = [c for c in self.companies if c.country != "Germany"][:20]
        for i, company in enumerate(non_german_companies, 1):
            report += f"{i}. **{company.name}** ({company.country}) - {company.category} - {company.website}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    """Main function to run enterprise healthcare discovery."""
    discovery = EnterpriseHealthcareDiscovery()
    discovery.run_comprehensive_discovery()

if __name__ == "__main__":
    main()