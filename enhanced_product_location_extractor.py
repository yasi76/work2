#!/usr/bin/env python3
"""
🔍 Enhanced Product and Location Extractor
===========================================
Extract exact product names from websites and precise location data from URLs.
Focus on European companies only with accurate product extraction.
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

class EnhancedProductLocationExtractor:
    """Enhanced extractor for exact product names and precise locations."""
    
    def __init__(self):
        """Initialize enhanced extractor."""
        # European countries and regions
        self.european_countries = {
            'germany', 'france', 'italy', 'spain', 'netherlands', 'belgium', 
            'austria', 'switzerland', 'poland', 'czech', 'hungary', 'slovakia',
            'slovenia', 'croatia', 'romania', 'bulgaria', 'greece', 'portugal',
            'sweden', 'norway', 'denmark', 'finland', 'ireland', 'uk', 'britain',
            'england', 'scotland', 'wales', 'lithuania', 'latvia', 'estonia',
            'luxembourg', 'malta', 'cyprus', 'europe', 'eu'
        }
        
        # German states and cities
        self.german_locations = {
            'berlin': {'state': 'Berlin', 'type': 'city-state'},
            'hamburg': {'state': 'Hamburg', 'type': 'city-state'},
            'bremen': {'state': 'Bremen', 'type': 'city-state'},
            'munich': {'state': 'Bavaria', 'type': 'city'},
            'münchen': {'state': 'Bavaria', 'type': 'city'},
            'cologne': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'köln': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'frankfurt': {'state': 'Hesse', 'type': 'city'},
            'stuttgart': {'state': 'Baden-Württemberg', 'type': 'city'},
            'düsseldorf': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'dusseldorf': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'dortmund': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'essen': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'leipzig': {'state': 'Saxony', 'type': 'city'},
            'dresden': {'state': 'Saxony', 'type': 'city'},
            'hannover': {'state': 'Lower Saxony', 'type': 'city'},
            'nuremberg': {'state': 'Bavaria', 'type': 'city'},
            'nürnberg': {'state': 'Bavaria', 'type': 'city'},
            'duisburg': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'bochum': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'wuppertal': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'bielefeld': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'bonn': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'mannheim': {'state': 'Baden-Württemberg', 'type': 'city'},
            'karlsruhe': {'state': 'Baden-Württemberg', 'type': 'city'},
            'wiesbaden': {'state': 'Hesse', 'type': 'city'},
            'augsburg': {'state': 'Bavaria', 'type': 'city'},
            'mainz': {'state': 'Rhineland-Palatinate', 'type': 'city'},
            'kiel': {'state': 'Schleswig-Holstein', 'type': 'city'},
            'erfurt': {'state': 'Thuringia', 'type': 'city'},
            'kassel': {'state': 'Hesse', 'type': 'city'},
            'rostock': {'state': 'Mecklenburg-Vorpommern', 'type': 'city'},
            'magdeburg': {'state': 'Saxony-Anhalt', 'type': 'city'},
            'freiburg': {'state': 'Baden-Württemberg', 'type': 'city'},
            'krefeld': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'lübeck': {'state': 'Schleswig-Holstein', 'type': 'city'},
            'oberhausen': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'ulm': {'state': 'Baden-Württemberg', 'type': 'city'},
            'offenbach': {'state': 'Hesse', 'type': 'city'},
            'pforzheim': {'state': 'Baden-Württemberg', 'type': 'city'},
            'ingolstadt': {'state': 'Bavaria', 'type': 'city'},
            'würzburg': {'state': 'Bavaria', 'type': 'city'},
            'regensburg': {'state': 'Bavaria', 'type': 'city'},
            'heidelberg': {'state': 'Baden-Württemberg', 'type': 'city'},
            'darmstadt': {'state': 'Hesse', 'type': 'city'},
            'potsdam': {'state': 'Brandenburg', 'type': 'city'},
            'recklinghausen': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'göttingen': {'state': 'Lower Saxony', 'type': 'city'},
            'bottrop': {'state': 'North Rhine-Westphalia', 'type': 'city'},
            'trier': {'state': 'Rhineland-Palatinate', 'type': 'city'},
            'jena': {'state': 'Thuringia', 'type': 'city'},
            'erlangen': {'state': 'Bavaria', 'type': 'city'}
        }
        
        # European cities for other countries
        self.european_cities = {
            'london': {'country': 'United Kingdom', 'state': 'England'},
            'paris': {'country': 'France', 'state': 'Île-de-France'},
            'rome': {'country': 'Italy', 'state': 'Lazio'},
            'madrid': {'country': 'Spain', 'state': 'Community of Madrid'},
            'amsterdam': {'country': 'Netherlands', 'state': 'North Holland'},
            'vienna': {'country': 'Austria', 'state': 'Vienna'},
            'zurich': {'country': 'Switzerland', 'state': 'Zurich'},
            'brussels': {'country': 'Belgium', 'state': 'Brussels-Capital'},
            'prague': {'country': 'Czech Republic', 'state': 'Prague'},
            'budapest': {'country': 'Hungary', 'state': 'Budapest'},
            'warsaw': {'country': 'Poland', 'state': 'Masovian'},
            'stockholm': {'country': 'Sweden', 'state': 'Stockholm'},
            'copenhagen': {'country': 'Denmark', 'state': 'Capital Region'},
            'oslo': {'country': 'Norway', 'state': 'Oslo'},
            'helsinki': {'country': 'Finland', 'state': 'Uusimaa'},
            'dublin': {'country': 'Ireland', 'state': 'Leinster'},
            'barcelona': {'country': 'Spain', 'state': 'Catalonia'},
            'milan': {'country': 'Italy', 'state': 'Lombardy'},
            'lisbon': {'country': 'Portugal', 'state': 'Lisbon'},
            'athens': {'country': 'Greece', 'state': 'Attica'}
        }
        
        # Enhanced product patterns for exact extraction
        self.product_patterns = [
            # Exact product names with specific keywords
            r'(?i)(?:produkt|product)[\s:]*([^<>\n,]{5,50})',
            r'(?i)(?:software|app|platform|system|lösung|solution)[\s:]*([\w\s-]{3,40})',
            r'(?i)(?:anwendung|application)[\s:]*([^<>\n,]{5,50})',
            r'(?i)(?:tool|werkzeug)[\s:]*([^<>\n,]{5,50})',
            r'(?i)(?:service|dienst)[\s:]*([^<>\n,]{5,50})',
            r'(?i)(?:therapeut|therapy|therapie)[\s:]*([^<>\n,]{5,50})',
            
            # HTML title and header patterns
            r'<title[^>]*>([^<]{10,100})</title>',
            r'<h1[^>]*>([^<]{5,80})</h1>',
            r'<h2[^>]*>([^<]{5,80})</h2>',
            
            # Product description patterns
            r'(?i)description["\']?\s*content=["\']([^"\']{10,100})["\']',
            r'(?i)og:title["\']?\s*content=["\']([^"\']{10,100})["\']',
            r'(?i)twitter:title["\']?\s*content=["\']([^"\']{10,100})["\']',
            
            # German specific product terms
            r'(?i)(?:gesundheits|health)[\s-]*(app|software|platform|system|lösung)',
            r'(?i)(?:medizin|medical)[\s-]*(app|software|platform|system|lösung)',
            r'(?i)(?:patienten|patient)[\s-]*(app|software|platform|system|lösung)',
            r'(?i)(?:digital|ai|ki)[\s-]*(health|gesundheit|medizin|lösung)',
            
            # Specific medical/healthcare product names
            r'(?i)([\w\s-]{3,30}(?:app|software|platform|system|lösung|portal|coach|analytics|ai))',
            r'(?i)([A-Z][\w\s-]{2,30}(?:App|Software|Platform|System|Portal|Coach|Analytics|AI))',
        ]
    
    def is_european_company(self, row):
        """Check if a company is European-based."""
        # Check for explicit non-European indicators
        non_european_indicators = [
            'united states', 'usa', 'us', 'america', 'california', 'new york',
            'texas', 'florida', 'illinois', 'pennsylvania', 'ohio', 'georgia',
            'north carolina', 'michigan', 'virginia', 'washington', 'arizona',
            'massachusetts', 'tennessee', 'indiana', 'missouri', 'maryland',
            'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama',
            'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut',
            'utah', 'iowa', 'nevada', 'arkansas', 'mississippi', 'kansas',
            'new mexico', 'nebraska', 'west virginia', 'idaho', 'hawaii',
            'new hampshire', 'maine', 'montana', 'rhode island', 'delaware',
            'south dakota', 'north dakota', 'alaska', 'vermont', 'wyoming'
        ]
        
        location_fields = [
            row.get('state', '').lower(),
            row.get('city', '').lower(),
            row.get('location_summary', '').lower(),
            row.get('country', '').lower()
        ]
        
        # Check if any field contains non-European indicators
        for field in location_fields:
            if field:
                for indicator in non_european_indicators:
                    if indicator in field:
                        return False
        
        return True  # Default to European if no US indicators found
    
    def extract_location_from_url(self, url, company_name):
        """Extract precise location information from URL and website content."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            # Remove common prefixes
            domain = domain.replace('www.', '').replace('shop.', '').replace('de.', '')
            
            location_info = {
                'city': '',
                'state': '',
                'country': 'Europe',
                'method': 'url_analysis'
            }
            
            # Check for .de domain (Germany)
            if domain.endswith('.de'):
                location_info['country'] = 'Germany'
                
                # Check for German cities in domain or path
                for city, info in self.german_locations.items():
                    if city in domain or city in path:
                        location_info['city'] = city.title()
                        location_info['state'] = info['state']
                        location_info['method'] = 'domain_analysis'
                        break
            
            # Check for other European domains
            elif domain.endswith(('.eu', '.at', '.ch', '.fr', '.it', '.es', '.nl', '.be')):
                country_map = {
                    '.eu': 'Europe',
                    '.at': 'Austria',
                    '.ch': 'Switzerland', 
                    '.fr': 'France',
                    '.it': 'Italy',
                    '.es': 'Spain',
                    '.nl': 'Netherlands',
                    '.be': 'Belgium'
                }
                location_info['country'] = country_map.get('.' + domain.split('.')[-1], 'Europe')
            
            # Check for European cities in URL
            for city, info in self.european_cities.items():
                if city in domain or city in path:
                    location_info['city'] = city.title()
                    location_info['state'] = info['state']
                    location_info['country'] = info['country']
                    location_info['method'] = 'city_detection'
                    break
            
            # Try to extract from website content
            website_location = self.extract_location_from_content(url)
            if website_location and not location_info['city']:
                location_info.update(website_location)
            
            return location_info
            
        except Exception as e:
            print(f"  ⚠️  Error extracting location: {str(e)[:50]}")
            return {'city': '', 'state': '', 'country': 'Europe', 'method': 'error'}
    
    def extract_location_from_content(self, url):
        """Extract location from website content."""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    
                    # Look for address information
                    address_patterns = [
                        r'(?i)address["\']?\s*[:|>]\s*([^<>\n]{10,100})',
                        r'(?i)adresse["\']?\s*[:|>]\s*([^<>\n]{10,100})',
                        r'(?i)kontakt["\']?\s*[:|>]\s*([^<>\n]{10,100})',
                        r'(?i)standort["\']?\s*[:|>]\s*([^<>\n]{10,100})',
                        r'(?i)location["\']?\s*[:|>]\s*([^<>\n]{10,100})'
                    ]
                    
                    for pattern in address_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            # Check if contains German cities
                            for city, info in self.german_locations.items():
                                if city.lower() in match.lower():
                                    return {
                                        'city': city.title(),
                                        'state': info['state'],
                                        'country': 'Germany',
                                        'method': 'content_analysis'
                                    }
                    
        except Exception:
            pass
        
        return None
    
    def extract_exact_products_from_website(self, url, company_name):
        """Extract exact product names from website with enhanced accuracy."""
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5,de;q=0.3',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
                if response.getcode() == 200:
                    content = response.read().decode('utf-8', errors='ignore')
                    return self.parse_exact_products_from_content(content, company_name, url)
                    
        except Exception as e:
            print(f"  ⚠️  Error extracting from {url}: {str(e)[:80]}")
            
        return f"{company_name} (Product details not available)"
    
    def parse_exact_products_from_content(self, content, company_name, url):
        """Parse exact product names from website content with enhanced accuracy."""
        try:
            # Clean content
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            products = []
            
            # Extract page title (highest priority)
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                # Clean and validate title
                title = re.sub(r'\s+', ' ', title)
                title = title.replace('&quot;', '"').replace('&amp;', '&')
                if len(title) > 5 and len(title) < 150 and company_name.lower() not in title.lower():
                    products.append(title)
            
            # Extract from meta descriptions
            meta_patterns = [
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']{20,200})["\']',
                r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']{10,100})["\']',
                r'<meta[^>]*name=["\']twitter:title["\'][^>]*content=["\']([^"\']{10,100})["\']'
            ]
            
            for pattern in meta_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    clean_match = re.sub(r'\s+', ' ', match.strip())
                    if len(clean_match) > 5 and len(clean_match) < 150:
                        products.append(clean_match)
            
            # Extract from headers (H1, H2)
            header_patterns = [
                r'<h1[^>]*>([^<]{5,100})</h1>',
                r'<h2[^>]*>([^<]{5,80})</h2>'
            ]
            
            for pattern in header_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    clean_match = re.sub(r'\s+', ' ', match.strip())
                    clean_match = re.sub(r'<[^>]+>', '', clean_match)  # Remove any remaining HTML
                    if len(clean_match) > 3 and len(clean_match) < 100:
                        products.append(clean_match)
            
            # Look for specific product mentions
            for pattern in self.product_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1] if len(match) > 1 else ''
                    clean_match = re.sub(r'\s+', ' ', str(match).strip())
                    clean_match = re.sub(r'<[^>]+>', '', clean_match)  # Remove HTML tags
                    if len(clean_match) > 3 and len(clean_match) < 100:
                        products.append(clean_match)
            
            # Clean and deduplicate products
            final_products = []
            seen = set()
            
            for product in products:
                # Clean the product name
                clean_product = re.sub(r'\s+', ' ', product).strip()
                clean_product = clean_product.replace('&nbsp;', ' ')
                clean_product = clean_product.replace('&amp;', '&')
                clean_product = clean_product.replace('&quot;', '"')
                clean_product = clean_product.replace('&lt;', '<')
                clean_product = clean_product.replace('&gt;', '>')
                
                # Validate product name
                if (len(clean_product) > 3 and 
                    len(clean_product) < 150 and
                    clean_product.lower() not in seen and
                    not re.match(r'^[0-9\s\-_.]+$', clean_product) and  # Not just numbers/symbols
                    'cookie' not in clean_product.lower() and
                    'privacy' not in clean_product.lower() and
                    'datenschutz' not in clean_product.lower() and
                    'impressum' not in clean_product.lower()):
                    
                    final_products.append(clean_product)
                    seen.add(clean_product.lower())
                
                # Limit to top 5 products
                if len(final_products) >= 5:
                    break
            
            # Return best products
            if final_products:
                return ', '.join(final_products[:3])  # Top 3 most relevant
            else:
                # Fallback: use cleaned page title if available
                if title_match:
                    title = title_match.group(1).strip()
                    title = re.sub(r'\s+', ' ', title)
                    if len(title) > 5 and len(title) < 150:
                        return title
                
                return f"{company_name} (Product details not available)"
                    
        except Exception as e:
            print(f"  ⚠️  Error parsing content: {str(e)[:50]}")
        
        return f"{company_name} (Product details not available)"

def process_european_database():
    """Process database to keep only European companies and extract exact products."""
    extractor = EnhancedProductLocationExtractor()
    
    # Read the enhanced database
    input_file = "ENHANCED_HEALTHCARE_DATABASE_WITH_LOCATIONS_20250721_125857.csv"
    
    print("🔍 ENHANCED EUROPEAN HEALTHCARE DATABASE PROCESSING")
    print("=" * 70)
    print("1. Filtering to keep ONLY European companies")
    print("2. Extracting EXACT product names from websites")
    print("3. Finding precise state and city information")
    print("=" * 70)
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
        
        # Filter to keep only European companies
        european_rows = []
        non_european_filtered = 0
        
        for row in rows:
            if extractor.is_european_company(row):
                european_rows.append(row)
            else:
                non_european_filtered += 1
                print(f"  🚫 Filtered non-European company: {row['name']}")
        
        print(f"\n📊 Filtered out {non_european_filtered} non-European companies")
        print(f"📊 Processing {len(european_rows)} European companies")
        print("\n🔍 Extracting exact product information and locations...")
        
        # Enhanced processing for remaining companies
        enhanced_rows = []
        for i, row in enumerate(european_rows, 1):
            print(f"\n  [{i}/{len(european_rows)}] Processing: {row['name']}")
            
            # Extract exact products
            products = extractor.extract_exact_products_from_website(row['website'], row['name'])
            
            # Extract precise location
            location_info = extractor.extract_location_from_url(row['website'], row['name'])
            
            # Update row with enhanced information
            row['exact_products'] = products
            row['precise_city'] = location_info['city']
            row['precise_state'] = location_info['state']
            row['precise_country'] = location_info['country']
            row['location_extraction_method'] = location_info['method']
            
            enhanced_rows.append(row)
            
            print(f"    ✅ Products: {products[:100]}...")
            print(f"    📍 Location: {location_info['city']}, {location_info['state']}, {location_info['country']}")
            
            # Respectful delay
            time.sleep(0.5)
        
        # Create enhanced output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"EUROPEAN_HEALTHCARE_EXACT_PRODUCTS_{timestamp}.csv"
        
        # Write enhanced data with new columns
        if enhanced_rows:
            fieldnames = list(enhanced_rows[0].keys())
            
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enhanced_rows)
        
        # Create summary
        summary = {
            "processing_date": datetime.now().isoformat(),
            "original_companies": len(rows),
            "non_european_filtered": non_european_filtered,
            "final_european_companies": len(enhanced_rows),
            "output_file": output_file,
            "enhancements": [
                "exact_products - Precisely extracted product names",
                "precise_city - Accurate city information",
                "precise_state - Accurate state/region information", 
                "precise_country - Accurate country information",
                "location_extraction_method - Method used for location extraction"
            ]
        }
        
        with open(f"ENHANCED_PROCESSING_SUMMARY_{timestamp}.json", 'w') as file:
            json.dump(summary, file, indent=2)
        
        print("\n" + "=" * 70)
        print("✅ ENHANCED PROCESSING COMPLETE!")
        print("=" * 70)
        print(f"📁 Output file: {output_file}")
        print(f"📊 Original companies: {len(rows)}")
        print(f"🚫 Non-European companies filtered: {non_european_filtered}")
        print(f"✅ Final European companies: {len(enhanced_rows)}")
        print(f"📈 Success rate: {len(enhanced_rows)}/{len(rows)} ({(len(enhanced_rows)/len(rows)*100):.1f}%)")
        print(f"🔍 Enhanced with exact products and precise locations")
        
        return output_file, enhanced_rows
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {input_file}")
        return None, []
    except Exception as e:
        print(f"❌ Error processing database: {e}")
        return None, []

if __name__ == "__main__":
    output_file, data = process_european_database()
    
    if output_file and data:
        print(f"\n🎯 Sample enhanced results:")
        print("-" * 70)
        for i, row in enumerate(data[:5], 1):
            print(f"{i}. {row['name']}")
            print(f"   Website: {row['website']}")
            print(f"   Exact Products: {row['exact_products']}")
            print(f"   Location: {row['precise_city']}, {row['precise_state']}, {row['precise_country']}")
            print()