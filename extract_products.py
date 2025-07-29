#!/usr/bin/env python3
"""
Extract Products Script
Inputs: final_startup_urls.json
Outputs: product_names.json
🧠 Extracts product names from web pages and GT.
"""

import json
import re
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup
import time


class ProductExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Ground truth product data
        self.ground_truth_products = {
            "https://www.acalta.de": ["Acalta"],
            "https://www.actimi.com": ["Actimi Herzinsuffizienz Set", "Actimi Notaufnahme-Set"],
            "https://www.emmora.de": ["Emmora"],
            "https://www.alfa-ai.com": ["ALFA AI"],
            "https://www.apheris.com": ["apheris"],
            "https://www.aporize.com/": ["Aporize"],
            "https://www.arztlena.com/": ["Lena"],
            "https://shop.getnutrio.com/": ["aurora nutrio", "Nutrio App"],
            "https://www.auta.health/": ["Auta Health"],
            "https://visioncheckout.com/": ["auvisus"],
            "https://www.avayl.tech/": ["AVAL"],
            "https://www.avimedical.com/avi-impact": ["avi Impact"],
            "https://de.becureglobal.com/": ["BECURE"],
            "https://bellehealth.co/de/": ["Belle App"],
            "https://www.biotx.ai/": ["biotx.ai"],
            "https://www.brainjo.de/": ["brainjo"]
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
            
    def get_gt_products(self, url: str) -> List[str]:
        """Get ground truth products for URL"""
        # Normalize URL for matching
        url_norm = url.rstrip('/')
        return self.ground_truth_products.get(url_norm, [])
        
    def extract_from_webpage(self, url: str) -> List[str]:
        """Extract product names from webpage"""
        products = []
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for product-related pages
            product_links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                text = link.text.lower()
                if any(term in href or term in text for term in ['product', 'produkt', 'solution', 'lösung', 'app', 'platform']):
                    product_links.append(urljoin(url, link['href']))
                    
            # Extract from main page
            # Look for headings that might be product names
            for tag in ['h1', 'h2', 'h3']:
                for heading in soup.find_all(tag):
                    text = heading.text.strip()
                    if len(text) < 50 and not any(skip in text.lower() for skip in ['cookie', 'privacy', 'impressum']):
                        # Check if it looks like a product name
                        if any(term in text.lower() for term in ['app', 'platform', 'system', 'tool', 'software']):
                            products.append(text)
                            
            # Look for app store badges
            app_store_links = soup.find_all('a', href=re.compile(r'(apple\.com|google\.com|play\.google)'))
            if app_store_links:
                # Try to find app name nearby
                for link in app_store_links:
                    parent = link.parent
                    if parent:
                        text = parent.text.strip()
                        # Extract app name from context
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and len(line) < 30 and line not in ['Download', 'Get it on', 'Available on']:
                                products.append(line)
                                break
                                
        except Exception as e:
            print(f"  ⚠️ Error fetching {url}: {str(e)}")
            
        # Remove duplicates
        return list(set(products))
        
    def categorize_product(self, product_name: str) -> str:
        """Categorize product type"""
        name_lower = product_name.lower()
        
        if 'app' in name_lower:
            return 'Mobile App'
        elif any(term in name_lower for term in ['platform', 'system', 'software']):
            return 'Software Platform'
        elif any(term in name_lower for term in ['device', 'sensor', 'hardware']):
            return 'Medical Device'
        elif any(term in name_lower for term in ['ai', 'algorithm', 'analytics']):
            return 'AI/Analytics'
        elif any(term in name_lower for term in ['service', 'telehealth', 'telemedicine']):
            return 'Digital Service'
        else:
            return 'Digital Health Product'
            
    def extract_all_products(self) -> Dict:
        """Extract products for all URLs"""
        data = self.load_urls()
        if not data:
            return None
            
        print("\n🔍 Extracting product names...")
        print("=" * 50)
        
        results = []
        total = len(data['urls'])
        
        for i, url_data in enumerate(data['urls'], 1):
            url = url_data['url']
            print(f"\n[{i}/{total}] Processing {url}")
            
            # Get ground truth products
            gt_products = self.get_gt_products(url)
            
            # Extract from webpage
            web_products = self.extract_from_webpage(url)
            
            # Combine products
            all_products = list(set(gt_products + web_products))
            
            if all_products:
                print(f"  ✅ Found {len(all_products)} products")
                for product in all_products:
                    print(f"     - {product}")
            else:
                print(f"  ⚠️ No products found")
                
            # Categorize products
            categorized_products = []
            for product in all_products:
                categorized_products.append({
                    'name': product,
                    'category': self.categorize_product(product),
                    'source': 'ground_truth' if product in gt_products else 'webpage'
                })
                
            results.append({
                'url': url,
                'products': categorized_products,
                'product_count': len(all_products),
                'has_gt_data': len(gt_products) > 0,
                'confidence': url_data.get('confidence', 0)
            })
            
            # Rate limiting
            if i < total:
                time.sleep(0.5)
                
        # Calculate statistics
        total_products = sum(r['product_count'] for r in results)
        urls_with_products = len([r for r in results if r['product_count'] > 0])
        
        # Save results
        output = {
            'timestamp': data['timestamp'],
            'total_urls': len(results),
            'urls_with_products': urls_with_products,
            'total_products_found': total_products,
            'extraction_stats': {
                'from_ground_truth': len([r for r in results if r['has_gt_data']]),
                'from_webpage': len([r for r in results if r['product_count'] > 0 and not r['has_gt_data']])
            },
            'products_by_url': results
        }
        
        with open('product_names.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ Extraction complete!")
        print(f"📊 Total products found: {total_products}")
        print(f"📊 URLs with products: {urls_with_products}/{len(results)}")
        print(f"📁 Output saved to: product_names.json")
        
        return output


def main():
    """Main function"""
    extractor = ProductExtractor()
    extractor.extract_all_products()


if __name__ == "__main__":
    main()