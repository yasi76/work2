#!/usr/bin/env python3
"""
Extract Company Names Script
Inputs: final_startup_urls.json
Outputs: company_name_mapping.json
🧠 Loads URLs and extracts clean company names.
"""

import json
import re
from urllib.parse import urlparse
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
import time


class CompanyNameExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def load_urls(self) -> Dict:
        """Load URLs from discovery output"""
        print("📁 Loading URLs from final_startup_urls.json...")
        try:
            with open('final_startup_urls.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Loaded {data['total_urls']} URLs")
            return data
        except FileNotFoundError:
            print("❌ Error: final_startup_urls.json not found!")
            print("Please run discover_urls.py first")
            return None
            
    def extract_from_domain(self, url: str) -> str:
        """Extract company name from domain"""
        domain = urlparse(url).netloc
        domain = domain.replace('www.', '')
        domain = domain.split('.')[0]
        # Clean up domain
        domain = domain.replace('-', ' ')
        domain = domain.replace('_', ' ')
        return domain.title()
        
    def extract_from_webpage(self, url: str) -> Optional[str]:
        """Extract company name from webpage"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different methods
            # 1. Look for og:site_name
            og_site = soup.find('meta', property='og:site_name')
            if og_site and og_site.get('content'):
                return og_site['content'].strip()
                
            # 2. Look for title tag
            title = soup.find('title')
            if title and title.text:
                # Clean title - usually format is "Company Name | Tagline"
                title_text = title.text.strip()
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
                elif '-' in title_text:
                    return title_text.split('-')[0].strip()
                    
            # 3. Look for h1 on homepage
            h1 = soup.find('h1')
            if h1 and len(h1.text.strip()) < 50:
                return h1.text.strip()
                
        except Exception as e:
            print(f"  ⚠️ Error fetching {url}: {str(e)}")
            
        return None
        
    def clean_company_name(self, name: str) -> str:
        """Clean and normalize company name"""
        # Remove common suffixes
        suffixes = ['GmbH', 'AG', 'Inc', 'Ltd', 'Limited', 'Corporation', 'Corp']
        for suffix in suffixes:
            name = re.sub(rf'\s*{suffix}\.?\s*$', '', name, flags=re.IGNORECASE)
            
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Capitalize properly
        return name.strip()
        
    def extract_all_names(self) -> Dict:
        """Extract company names for all URLs"""
        data = self.load_urls()
        if not data:
            return None
            
        print("\n🔍 Extracting company names...")
        print("=" * 50)
        
        results = []
        total = len(data['urls'])
        
        for i, url_data in enumerate(data['urls'], 1):
            url = url_data['url']
            print(f"\n[{i}/{total}] Processing {url}")
            
            # Try webpage extraction first
            web_name = self.extract_from_webpage(url)
            
            # Fall back to domain extraction
            domain_name = self.extract_from_domain(url)
            
            # Choose best name
            if web_name:
                company_name = self.clean_company_name(web_name)
                extraction_method = 'webpage'
            else:
                company_name = domain_name
                extraction_method = 'domain'
                
            print(f"  ✅ Company name: {company_name} (via {extraction_method})")
            
            results.append({
                'url': url,
                'company_name': company_name,
                'extraction_method': extraction_method,
                'confidence': url_data.get('confidence', 0),
                'source': url_data.get('source', 'Unknown')
            })
            
            # Rate limiting
            if i < total:
                time.sleep(0.5)
                
        # Save results
        output = {
            'timestamp': data['timestamp'],
            'total_companies': len(results),
            'extraction_methods': {
                'webpage': len([r for r in results if r['extraction_method'] == 'webpage']),
                'domain': len([r for r in results if r['extraction_method'] == 'domain'])
            },
            'companies': results
        }
        
        with open('company_name_mapping.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Extraction complete!")
        print(f"📊 Total companies: {len(results)}")
        print(f"📁 Output saved to: company_name_mapping.json")
        
        return output


def main():
    """Main function"""
    extractor = CompanyNameExtractor()
    extractor.extract_all_names()


if __name__ == "__main__":
    main()