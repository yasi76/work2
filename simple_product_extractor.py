#!/usr/bin/env python3
"""
🔍 Simple Product Extractor and US Filter
==========================================
Filter out US companies and extract product/service names using built-in libraries only.
"""

import csv
import json
import re
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import time
from datetime import datetime
import ssl

class SimpleProductExtractor:
    """Extract product and service names from healthcare websites using built-in libraries only."""
    
    def __init__(self):
        """Initialize product extractor."""
        # Manual product mappings (from your examples)
        self.manual_products = {
            'acalta': 'Acalta Health Platform, Patienta App, Acalta Clinics',
            'actimi': 'Actimi Herzinsuffizienz Set, Actimi Notaufnahme-Set',
            'advanova': 'Elektronische Patientenkurve vMobil',
            'ahorn': 'Emmora',
            'alfa-ai': 'ALFA AI Coach',
            'alfa_ai': 'ALFA AI Coach',
            'allm': 'Join',
            'apheris': 'apheris',
            'aporize': 'Aporize',
            'artificy': 'Lena',
            'assistme': 'alea App',
            'aura': 'Aura',
            'aurora': 'aurora nutrio, Nutrio App',
            'auta': 'Auta Health',
            'avayl': 'AVAL',
            'avi': 'avi Impact',
            'avimedical': 'avi Impact',
            'aycan': 'aycan smartvisit Portal',
            'baxter': 'Arzneimitteltherapiesicherheit (AMTS)',
            'becure': 'BECURE',
            'cogthera': 'Cogthera App - Kognitives Training',
            'curecurve': 'Elina App',
            'deepeye': 'DeepEye AI',
            'denton': 'Denton Systems',
            'elixion': 'Elixion Medical',
            'fyzo': 'Fyzo Assistant',
            'gleea': 'Gleea',
            'incontalert': 'Incont Alert',
            'getnutrio': 'Nutrio App',
            'visioncheckout': 'Vision Checkout',
            'dianovi': 'Dianovi',
            'dpv': 'DPV Analytics',
            'floy': 'Floy',
            'heynanny': 'HeyNanny'
        }
        
        # Product name patterns
        self.product_patterns = [
            r'<title[^>]*>([^<]+)</title>',
            r'<h1[^>]*>([^<]+)</h1>',
            r'<h2[^>]*>([^<]+)</h2>',
            r'(\w+\s+App)',
            r'(\w+\s+Platform)',
            r'(\w+\s+Set)',
            r'(\w+\s+Portal)',
            r'(\w+\s+System)',
            r'(\w+\s+Software)',
            r'(\w+\s+Solution)',
            r'(\w+\s+Coach)',
            r'(\w+\s+AI)',
        ]
    
    def is_us_company(self, row):
        """Check if a company is US-based."""
        us_indicators = [
            'Alabama', 'Delaware', 'United States', 'USA', 'US'
        ]
        
        location_fields = [
            row.get('state', ''),
            row.get('city', ''),
            row.get('location_summary', ''),
            row.get('country', '')
        ]
        
        for field in location_fields:
            if field:
                for indicator in us_indicators:
                    if indicator in str(field):
                        return True
        return False
    
    def extract_products_from_website(self, url, company_name):
        """Extract product names from website content."""
        try:
            # Check manual mappings first
            company_key = company_name.lower().replace(' ', '').replace('-', '_')
            for key in self.manual_products:
                if key in company_key or company_key in key:
                    return self.manual_products[key]
            
            # Also check URL domain
            domain = urlparse(url).netloc.lower().replace('www.', '').replace('.com', '').replace('.de', '').replace('.eu', '')
            domain_key = domain.replace('.', '').replace('-', '_')
            
            for key in self.manual_products:
                if key in domain_key or domain_key.startswith(key):
                    return self.manual_products[key]
            
            # Try to extract from website
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=8) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    return self.parse_products_from_html(content, company_name)
                    
        except Exception as e:
            print(f"  ⚠️  Error extracting from {url}: {str(e)[:80]}")
            
        # Fallback to company name
        return f"{company_name} (Product details not available)"
    
    def parse_products_from_html(self, html_content, company_name):
        """Parse product names from HTML content using regex."""
        try:
            # Extract title
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                if title and company_name.lower() not in title.lower():
                    # Clean title
                    title = re.sub(r'\s+', ' ', title)
                    if len(title) < 100:  # Reasonable length
                        return title
            
            # Look for headers with product info
            products = []
            for pattern in self.product_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    clean_match = re.sub(r'\s+', ' ', match).strip()
                    if len(clean_match) > 3 and len(clean_match) < 100:
                        products.append(clean_match)
            
            if products:
                # Return first few unique products
                unique_products = []
                for product in products[:5]:
                    if product not in unique_products:
                        unique_products.append(product)
                
                return ', '.join(unique_products)
            
            # Fallback
            return f"{company_name} (Product details not available)"
                    
        except Exception as e:
            print(f"  ⚠️  Error parsing HTML: {str(e)[:50]}")
        
        return f"{company_name} (Product details not available)"

def process_database():
    """Process the database to filter US companies and extract products."""
    extractor = SimpleProductExtractor()
    
    # Read the enhanced database
    input_file = "ENHANCED_HEALTHCARE_DATABASE_WITH_LOCATIONS_20250721_125857.csv"
    
    print("🔍 PROCESSING HEALTHCARE DATABASE")
    print("=" * 60)
    print("1. Filtering out US companies")
    print("2. Extracting product/service names")
    print("=" * 60)
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        # Filter out US companies
        non_us_rows = []
        us_companies_filtered = 0
        
        for row in rows:
            if extractor.is_us_company(row):
                us_companies_filtered += 1
                print(f"  🚫 Filtered US company: {row['name']}")
            else:
                non_us_rows.append(row)
        
        print(f"\n📊 Filtered out {us_companies_filtered} US companies")
        print(f"📊 Processing {len(non_us_rows)} non-US companies")
        print("\n🔍 Extracting product information...")
        
        # Extract products for remaining companies
        enhanced_rows = []
        for i, row in enumerate(non_us_rows, 1):
            print(f"\n  [{i}/{len(non_us_rows)}] Processing: {row['name']}")
            
            # Extract products
            products = extractor.extract_products_from_website(row['website'], row['name'])
            
            # Add product information to row
            row['products'] = products
            enhanced_rows.append(row)
            
            print(f"    ✅ Products: {products[:80]}...")
            
            # Small delay to be respectful
            time.sleep(0.3)
        
        # Create output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"GERMAN_HEALTHCARE_WITH_PRODUCTS_{timestamp}.csv"
        
        # Write enhanced data
        fieldnames = list(enhanced_rows[0].keys()) if enhanced_rows else []
        
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(enhanced_rows)
        
        # Create summary
        summary = {
            "processing_date": datetime.now().isoformat(),
            "original_companies": len(rows),
            "us_companies_filtered": us_companies_filtered,
            "final_companies": len(enhanced_rows),
            "output_file": output_file
        }
        
        with open(f"PROCESSING_SUMMARY_{timestamp}.json", 'w') as file:
            json.dump(summary, file, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ PROCESSING COMPLETE!")
        print("=" * 60)
        print(f"📁 Output file: {output_file}")
        print(f"📊 Original companies: {len(rows)}")
        print(f"🚫 US companies filtered: {us_companies_filtered}")
        print(f"✅ Final companies: {len(enhanced_rows)}")
        print(f"📈 Success rate: {len(enhanced_rows)}/{len(rows)} ({(len(enhanced_rows)/len(rows)*100):.1f}%)")
        
        return output_file, enhanced_rows
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {input_file}")
        return None, []
    except Exception as e:
        print(f"❌ Error processing database: {e}")
        return None, []

if __name__ == "__main__":
    output_file, data = process_database()
    
    if output_file and data:
        print(f"\n🎯 Sample results:")
        print("-" * 50)
        for i, row in enumerate(data[:5], 1):
            print(f"{i}. {row['name']}")
            print(f"   Website: {row['website']}")
            print(f"   Products: {row['products']}")
            print()