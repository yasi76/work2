#!/usr/bin/env python3
"""
Simple test version of healthcare scraper using only standard library
This version demonstrates the core functionality without external dependencies
"""

import urllib.request
import urllib.parse
import json
import csv
import re
import time
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

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
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class SimpleHealthcareScraper:
    """
    Simple healthcare scraper using only standard library
    """
    
    def __init__(self):
        self.known_companies = self._load_known_companies()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
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
    
    def _fetch_url(self, url: str) -> Optional[str]:
        """Fetch URL content with error handling"""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
            return None
    
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
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""
    
    def _is_new_company(self, website: str) -> bool:
        """Check if company is new (not in known list)"""
        if not website:
            return True
        
        domain = self._extract_domain(website)
        return domain not in self.known_companies
    
    def extract_sample_companies(self) -> List[HealthcareCompany]:
        """Extract sample companies for testing"""
        companies = []
        
        # Sample companies that would be discovered
        sample_data = [
            {
                'name': 'MedTech Solutions GmbH',
                'website': 'https://medtech-solutions.de',
                'description': 'Innovative medical technology solutions for healthcare providers',
                'location': 'Berlin, Germany',
                'category': 'Medical Technology',
                'tags': ['Sample', 'Medical Device', 'German']
            },
            {
                'name': 'HealthAI Systems',
                'website': 'https://healthai-systems.com',
                'description': 'AI-powered healthcare diagnostics and analytics',
                'location': 'Munich, Germany',
                'category': 'Digital Health',
                'tags': ['Sample', 'AI', 'Healthcare']
            },
            {
                'name': 'BioInnovate AG',
                'website': 'https://bioinnovate.de',
                'description': 'Biotechnology research and development',
                'location': 'Hamburg, Germany',
                'category': 'Biotechnology',
                'tags': ['Sample', 'Biotech', 'Research']
            }
        ]
        
        for data in sample_data:
            if self._is_new_company(data['website']):
                company = HealthcareCompany(
                    name=data['name'],
                    website=data['website'],
                    description=data['description'],
                    location=data['location'],
                    category=data['category'],
                    source_directory='https://example.com/directory',
                    tags=data['tags']
                )
                companies.append(company)
        
        return companies
    
    def test_validation_methods(self) -> None:
        """Test validation methods"""
        logger.info("Testing validation methods...")
        
        # Test company name validation
        test_names = [
            'MedTech Solutions GmbH',  # Should pass
            'HealthCare Inc',          # Should pass
            'Click here',              # Should fail
            'Home',                    # Should fail
            'Innovative Medical Tech'   # Should pass
        ]
        
        for name in test_names:
            result = self._is_valid_company_name(name)
            logger.info(f"Company name '{name}': {'✅ Valid' if result else '❌ Invalid'}")
        
        # Test website validation
        test_urls = [
            'https://medtech-solutions.de',  # Should pass
            'https://facebook.com',          # Should fail
            'https://healthcare.com',        # Should pass
            'invalid-url',                   # Should fail
        ]
        
        for url in test_urls:
            result = self._is_company_website(url)
            logger.info(f"Website '{url}': {'✅ Valid' if result else '❌ Invalid'}")
        
        # Test domain extraction
        test_domains = [
            'https://www.example.com',
            'https://subdomain.example.de',
            'http://example.org'
        ]
        
        for url in test_domains:
            domain = self._extract_domain(url)
            logger.info(f"Domain from '{url}': {domain}")
    
    def run_test_extraction(self) -> List[HealthcareCompany]:
        """Run test extraction"""
        logger.info("🚀 STARTING SIMPLE HEALTHCARE SCRAPER TEST")
        logger.info("=" * 60)
        
        # Test validation methods
        self.test_validation_methods()
        
        logger.info("\n" + "=" * 60)
        logger.info("Extracting sample companies...")
        
        # Extract sample companies
        companies = self.extract_sample_companies()
        
        logger.info(f"Found {len(companies)} sample companies")
        
        return companies
    
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
        csv_file = output_path / "simple_test_results.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if company_dicts:
                writer = csv.DictWriter(f, fieldnames=company_dicts[0].keys())
                writer.writeheader()
                writer.writerows(company_dicts)
        
        # Save to JSON
        json_file = output_path / "simple_test_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(company_dicts, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Results saved to {csv_file} and {json_file}")
        
        return company_dicts

def main():
    """Main execution"""
    scraper = SimpleHealthcareScraper()
    
    start_time = time.time()
    companies = scraper.run_test_extraction()
    runtime = time.time() - start_time
    
    if companies:
        # Save results
        company_dicts = scraper.save_results(companies)
        
        # Statistics
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS")
        logger.info("="*60)
        logger.info(f"Total companies: {len(companies)}")
        logger.info(f"Companies with websites: {sum(1 for c in company_dicts if c['website'])}")
        logger.info(f"Runtime: {runtime:.2f} seconds")
        
        # Show companies
        logger.info("\n🏢 EXTRACTED COMPANIES:")
        for i, company in enumerate(companies, 1):
            logger.info(f"  {i}. {company.name}")
            if company.website:
                logger.info(f"     🌐 {company.website}")
            if company.location:
                logger.info(f"     📍 {company.location}")
            if company.category:
                logger.info(f"     🏷️  {company.category}")
            logger.info("")
        
        logger.info("🎉 SIMPLE SCRAPER TEST COMPLETED!")
        
    else:
        logger.error("❌ No companies extracted")

if __name__ == "__main__":
    main()