#!/usr/bin/env python3
"""
🔍 Product Extractor and US Filter
==================================
Filter out US companies and extract specific product/service names from healthcare websites.
"""

import csv
import json
import re
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import time
from datetime import datetime
from bs4 import BeautifulSoup
import ssl

class ProductExtractor:
    """Extract specific product and service names from healthcare websites."""
    
    def __init__(self):
        """Initialize product extractor."""
        # Common healthcare product patterns
        self.product_patterns = [
            r'(\w+\s+App)',  # App names
            r'(\w+\s+Platform)',  # Platform names
            r'(\w+\s+Set)',  # Set names
            r'(\w+\s+Portal)',  # Portal names
            r'(\w+\s+System)',  # System names
            r'(\w+\s+Software)',  # Software names
            r'(\w+\s+Solution)',  # Solution names
            r'(\w+\s+Coach)',  # Coach names
            r'(\w+\s+Analytics)',  # Analytics names
            r'(\w+\s+AI)',  # AI product names
        ]
        
        # German product keywords
        self.german_keywords = [
            'Patientenkurve', 'Herzinsuffizienz', 'Notaufnahme', 
            'Arzneimitteltherapiesicherheit', 'AMTS', 'Klinik',
            'Gesundheit', 'Medizin', 'Therapie', 'Diagnose'
        ]
        
        # Manual product mappings (from your examples)
        self.manual_products = {
            'acalta': 'Acalta Health Platform, Patienta App, Acalta Clinics',
            'actimi': 'Actimi Herzinsuffizienz Set, Actimi Notaufnahme-Set',
            'advanova': 'Elektronische Patientenkurve vMobil',
            'ahorn': 'Emmora',
            'alfa-ai': 'ALFA AI Coach',
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
            'aycan': 'aycan smartvisit Portal',
            'baxter': 'Arzneimitteltherapiesicherheit (AMTS)',
            'becure': 'BECURE'
        }
    
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
            company_key = company_name.lower().replace(' ', '').replace('-', '')
            if company_key in self.manual_products:
                return self.manual_products[company_key]
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    return self.parse_products_from_content(content, company_name)
                    
        except Exception as e:
            print(f"  ⚠️  Error extracting from {url}: {str(e)[:100]}")
            
        return "Product information not available"
    
    def parse_products_from_content(self, content, company_name):
        """Parse product names from website content."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            # Look for product patterns
            products = []
            
            # Search for common product patterns
            for pattern in self.product_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                products.extend(matches)
            
            # Look for title and heading content
            titles = []
            for tag in ['title', 'h1', 'h2', 'h3']:
                elements = soup.find_all(tag)
                for elem in elements:
                    if elem.text:
                        titles.append(elem.text.strip())
            
            # Extract meaningful product names from titles
            for title in titles[:5]:  # Limit to first 5 titles
                if any(keyword in title.lower() for keyword in ['platform', 'app', 'software', 'solution', 'system']):
                    products.append(title)
            
            # Look for German healthcare terms
            german_products = []
            for keyword in self.german_keywords:
                if keyword.lower() in text.lower():
                    # Find context around the keyword
                    pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    german_products.extend(matches)
            
            # Combine and clean products
            all_products = products + german_products
            
            if all_products:
                # Clean and deduplicate
                cleaned = []
                for product in all_products[:10]:  # Limit to 10 products
                    clean_product = re.sub(r'\s+', ' ', product).strip()
                    if len(clean_product) > 3 and clean_product not in cleaned:
                        cleaned.append(clean_product)
                
                if cleaned:
                    return ', '.join(cleaned)
            
            # Fallback: use page title or company name
            page_title = soup.find('title')
            if page_title and page_title.text:
                title_text = page_title.text.strip()
                if title_text and title_text != company_name:
                    return title_text
                    
        except Exception as e:
            print(f"  ⚠️  Error parsing content: {str(e)[:100]}")
        
        return "Product information not available"

def process_database():
    """Process the database to filter US companies and extract products."""
    extractor = ProductExtractor()
    
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
            
            print(f"    ✅ Products: {products[:100]}...")
            
            # Small delay to be respectful
            time.sleep(0.5)
        
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
            print(f"   Products: {row['products'][:100]}...")
            print()