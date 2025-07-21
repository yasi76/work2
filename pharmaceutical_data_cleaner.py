#!/usr/bin/env python3
"""
Pharmaceutical Company Dataset Cleaner
Identifies and corrects issues in pharmaceutical company data
"""

import pandas as pd
import re
import requests
from urllib.parse import urlparse
import time
from typing import Dict, List, Tuple, Optional

class PharmaceuticalDataCleaner:
    def __init__(self):
        self.verified_companies = {
            # Format: domain -> (correct_name, correct_country, correct_website, wikipedia_url)
            'ferring.ch': ('Ferring Pharmaceuticals', 'Switzerland', 'https://ferring.ch', 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals'),
            'ferring.co.uk': ('Ferring Pharmaceuticals UK', 'United Kingdom', 'https://ferring.co.uk', 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals'),
            'jazzpharma.com': ('Jazz Pharmaceuticals', 'United States', 'https://www.jazzpharma.com', 'https://en.wikipedia.org/wiki/Jazz_Pharmaceuticals'),
            'siegfried.ch': ('Siegfried Holding AG', 'Switzerland', 'https://www.siegfried.ch', 'https://en.wikipedia.org/wiki/Siegfried_Holding'),
            'bene-arzneimittel.de': ('bene-Arzneimittel GmbH', 'Germany', 'https://www.bene-arzneimittel.de', None),
            'crescentpharma.com': ('Crescent Pharma', 'United Kingdom', 'https://www.crescentpharma.com', None),
        }
        
        self.fake_patterns = [
            'medicinechestidiom',
            'pharmaceuticalcompaniesbycountry',
            'drugsin',
            'healthcarecompaniesof',
            'pharmaceuticalcompaniesof',
            'listofpharmaceuticalmanufacturers',
            'pharmaceuticalindustryinthe',
            'biotechnologycompaniesbycountry',
            'medicaltechnologycompaniesbycountry',
            'healthcarecompaniesbycountry',
            'medicalandhealthorganisations',
            'privatemedicinein',
            'healthclubsin',
            'biotechnologyin',
            'medicaltechnologyin'
        ]
        
        self.wikipedia_categories = [
            'Category:Pharmaceutical_companies',
            'Category:Biotechnology_companies',
            'Category:Medical_technology_companies',
            'Category:Health_care_companies',
            'Category:Drugs_in_',
            'Medicine_chest_(idiom)',
            'Biotechnology',
            'Health_Valley',
            'Health_Navigator',
            'Healthera'
        ]

    def load_data(self, file_path: str = None, data_string: str = None) -> pd.DataFrame:
        """Load data from file or string"""
        if data_string:
            lines = data_string.strip().split('\n')
            data = []
            for line in lines:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 5:
                        data.append(parts)
            df = pd.DataFrame(data, columns=['url', 'source', 'category', 'country', 'wikipedia_page'])
        elif file_path:
            df = pd.read_csv(file_path, names=['url', 'source', 'category', 'country', 'wikipedia_page'])
        else:
            raise ValueError("Either file_path or data_string must be provided")
        
        return df

    def is_fake_company(self, url: str, wikipedia_url: str) -> bool:
        """Check if the entry is a fake company based on patterns"""
        domain = urlparse(url).netloc.lower().replace('www.', '')
        
        # Check against fake patterns
        for pattern in self.fake_patterns:
            if pattern in domain:
                return True
        
        # Check if Wikipedia URL points to categories or non-company pages
        if wikipedia_url:
            for category in self.wikipedia_categories:
                if category in wikipedia_url:
                    return True
        
        return False

    def extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except:
            return ""

    def check_url_accessibility(self, url: str, timeout: int = 5) -> bool:
        """Check if URL is accessible (basic check)"""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code < 400
        except:
            return False

    def clean_dataset(self, df: pd.DataFrame, check_urls: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Clean the dataset and return clean and rejected data"""
        clean_data = []
        rejected_data = []
        
        print(f"Processing {len(df)} entries...")
        
        for idx, row in df.iterrows():
            url = str(row['url']).strip()
            wikipedia_url = str(row['wikipedia_page']).strip()
            
            # Skip empty rows
            if not url or url == 'nan':
                continue
            
            domain = self.extract_domain(url)
            
            # Check if it's a fake company
            if self.is_fake_company(url, wikipedia_url):
                rejected_data.append({
                    'original_url': url,
                    'reason': 'Fake company / Wikipedia category',
                    'domain': domain,
                    'source': row.get('source', ''),
                    'category': row.get('category', ''),
                    'country': row.get('country', ''),
                    'wikipedia_page': wikipedia_url
                })
                continue
            
            # Check if it's a verified company
            if domain in self.verified_companies:
                verified_info = self.verified_companies[domain]
                clean_entry = {
                    'url': verified_info[2],  # correct website
                    'source': 'Verified Official Website',
                    'category': 'Pharmaceutical company',
                    'country': verified_info[1],  # correct country
                    'wikipedia_page': verified_info[3] or wikipedia_url,
                    'company_name': verified_info[0],
                    'verification_status': 'Verified'
                }
                clean_data.append(clean_entry)
                continue
            
            # Check URL accessibility if requested
            url_accessible = True
            if check_urls:
                url_accessible = self.check_url_accessibility(url)
                time.sleep(0.1)  # Be respectful
            
            if not url_accessible:
                rejected_data.append({
                    'original_url': url,
                    'reason': 'URL not accessible',
                    'domain': domain,
                    'source': row.get('source', ''),
                    'category': row.get('category', ''),
                    'country': row.get('country', ''),
                    'wikipedia_page': wikipedia_url
                })
                continue
            
            # If we get here, it might be legitimate but unverified
            potential_entry = {
                'url': url,
                'source': row.get('source', ''),
                'category': row.get('category', ''),
                'country': row.get('country', ''),
                'wikipedia_page': wikipedia_url,
                'company_name': domain.replace('.com', '').replace('.de', '').replace('.uk', '').title(),
                'verification_status': 'Needs manual verification'
            }
            clean_data.append(potential_entry)
        
        clean_df = pd.DataFrame(clean_data)
        rejected_df = pd.DataFrame(rejected_data)
        
        return clean_df, rejected_df

    def generate_report(self, original_count: int, clean_df: pd.DataFrame, rejected_df: pd.DataFrame):
        """Generate cleaning report"""
        print("\n" + "="*60)
        print("PHARMACEUTICAL DATA CLEANING REPORT")
        print("="*60)
        print(f"Original entries: {original_count}")
        print(f"Clean entries: {len(clean_df)}")
        print(f"Rejected entries: {len(rejected_df)}")
        print(f"Data quality: {len(clean_df)/original_count*100:.1f}% usable")
        
        print(f"\nVerified companies found: {len(clean_df[clean_df['verification_status'] == 'Verified'])}")
        print(f"Entries needing verification: {len(clean_df[clean_df['verification_status'] == 'Needs manual verification'])}")
        
        print("\n📊 REJECTION REASONS:")
        if len(rejected_df) > 0:
            rejection_counts = rejected_df['reason'].value_counts()
            for reason, count in rejection_counts.items():
                print(f"  • {reason}: {count} entries")
        
        print("\n✅ VERIFIED COMPANIES:")
        verified_entries = clean_df[clean_df['verification_status'] == 'Verified']
        for _, entry in verified_entries.iterrows():
            print(f"  • {entry['company_name']} ({entry['country']}) - {entry['url']}")
        
        print("\n⚠️  TOP FAKE PATTERNS DETECTED:")
        fake_domains = rejected_df[rejected_df['reason'] == 'Fake company / Wikipedia category']['domain'].value_counts().head(10)
        for domain, count in fake_domains.items():
            print(f"  • {domain}: {count} variations")

def main():
    """Main function to demonstrate usage"""
    
    # Your original data as a string (sample)
    sample_data = """https://www.knollpharmaceuticals.com,Wikipedia,Category:Pharmaceutical_companies_of_Germany,Germany,https://en.wikipedia.org/wiki/Knoll_Pharmaceuticals
https://www.medicinechestidiom.com,Wikipedia,Category:Pharmaceutical_companies_of_Germany,Germany,https://en.wikipedia.org/wiki/Medicine_chest_(idiom)
https://www.pharmaceuticalcompaniesbycountry.com,Wikipedia,Category:Pharmaceutical_companies_of_Germany,Germany,https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_by_country
https://ferring.ch,Official Website,Pharmaceutical company,Switzerland,https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals
https://www.jazzpharma.com,Official Website,Pharmaceutical company,United States,https://en.wikipedia.org/wiki/Jazz_Pharmaceuticals
https://www.gwpharmaceuticals.com,Wikipedia,Category:Pharmaceutical_companies_of_the_United_Kingdom,United Kingdom,https://en.wikipedia.org/wiki/GW_Pharmaceuticals"""
    
    # Initialize cleaner
    cleaner = PharmaceuticalDataCleaner()
    
    # Load data
    df = cleaner.load_data(data_string=sample_data)
    original_count = len(df)
    
    # Clean data
    clean_df, rejected_df = cleaner.clean_dataset(df, check_urls=False)  # Set to True to check URL accessibility
    
    # Generate report
    cleaner.generate_report(original_count, clean_df, rejected_df)
    
    # Save results
    clean_df.to_csv('cleaned_pharmaceutical_companies.csv', index=False)
    rejected_df.to_csv('rejected_entries.csv', index=False)
    
    print(f"\n💾 Files saved:")
    print(f"  • cleaned_pharmaceutical_companies.csv ({len(clean_df)} entries)")
    print(f"  • rejected_entries.csv ({len(rejected_df)} entries)")
    
    return clean_df, rejected_df

if __name__ == "__main__":
    clean_data, rejected_data = main()