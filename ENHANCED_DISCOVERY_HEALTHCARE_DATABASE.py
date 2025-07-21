#!/usr/bin/env python3
"""
Enhanced European Healthcare Database Builder with Automatic Discovery
Automatically discovers new healthcare startups from multiple European directories
"""

import urllib.request
import urllib.parse
import urllib.error
import csv
import json
import time
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
import ssl

# Your original manually curated URLs
MANUAL_URLS = [
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

# European healthcare startup directories to scrape
DISCOVERY_SOURCES = [
    # Main European startup directories
    'https://www.eu-startups.com/category/healthtech/',
    'https://www.eu-startups.com/category/medtech/',
    'https://www.eu-startups.com/category/biotech/',
    
    # German specific directories
    'https://startup-map.de/startup-ecosystem/healthcare/',
    'https://german-startups.com/category/health/',
    'https://www.deutsche-startups.de/category/health/',
    
    # UK directories
    'https://www.uktech.news/category/healthtech/',
    'https://techround.co.uk/category/health-tech/',
    
    # French directories
    'https://www.frenchweb.fr/tag/sante/',
    'https://www.maddyness.com/tag/sante/',
    
    # Netherlands
    'https://startupamsterdam.com/sector/health/',
    'https://www.startupjuncture.com/category/healthtech/',
    
    # Nordic
    'https://arcticstartup.com/category/health/',
    'https://nordic.vc/category/health/',
    
    # Spain
    'https://www.novobrief.com/category/health/',
    'https://startup.info/es/category/salud/',
    
    # Italy
    'https://www.startupitalia.eu/category/health/',
    'https://www.economyup.it/category/startup/salute/',
    
    # General European tech sites
    'https://tech.eu/category/health/',
    'https://sifted.eu/category/healthcare/',
    'https://www.techinformed.com/category/health-tech/',
    
    # Crunchbase searches (free tier)
    'https://www.crunchbase.com/discover/organization.companies/cb_rank/organizations',
    
    # AngelList equivalent searches
    'https://angel.co/companies?markets[]=health-care&locations[]=europe',
    
    # Additional European directories
    'https://startup-europe.eu/directory/?category=health',
    'https://ecosystem.europa.eu/search?category=health',
    'https://www.startupblink.com/ecosystem/healthcare',
]

# Health-related keywords for filtering
HEALTH_KEYWORDS = [
    'health', 'med', 'care', 'clinic', 'hospital', 'pharma', 'bio', 'therapy',
    'diagnostic', 'treatment', 'patient', 'doctor', 'telemedicine', 'wellness',
    'fitness', 'nutrition', 'mental', 'dental', 'vision', 'hearing', 'rehab',
    'surgery', 'radiology', 'cardio', 'neuro', 'oncology', 'diabetes', 'pain',
    'drug', 'vaccine', 'genome', 'dna', 'ai-health', 'digital-health', 'e-health',
    'gesundheit', 'medizin', 'arzt', 'klinik', 'sante', 'medico', 'salud', 'saude'
]

# European country domains
EUROPEAN_DOMAINS = [
    '.de', '.uk', '.fr', '.nl', '.se', '.ch', '.es', '.it', '.at', '.be', '.dk',
    '.fi', '.no', '.pl', '.cz', '.ie', '.pt', '.gr', '.hu', '.ro', '.bg', '.hr',
    '.si', '.sk', '.lt', '.lv', '.ee', '.lu', '.mt', '.cy', '.eu'
]

def create_safe_request(url, timeout=10):
    """Create a safe HTTP request with proper headers and SSL context"""
    try:
        # Create SSL context that doesn't verify certificates (for scraping)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create request with realistic headers
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        return urllib.request.urlopen(req, timeout=timeout, context=ssl_context)
    except Exception as e:
        print(f"  ❌ Error creating request for {url}: {str(e)[:100]}")
        return None

def extract_urls_from_content(content, base_url):
    """Extract all URLs from HTML content"""
    urls = set()
    
    try:
        # Find all href attributes
        href_pattern = r'href=["\']([^"\']+)["\']'
        href_matches = re.findall(href_pattern, content, re.IGNORECASE)
        
        # Find all direct URLs in text
        url_pattern = r'https?://[^\s<>"\']+(?:[^\s<>"\'.,;:])'
        url_matches = re.findall(url_pattern, content)
        
        all_matches = href_matches + url_matches
        
        for url in all_matches:
            try:
                # Convert relative URLs to absolute
                if url.startswith('/'):
                    url = urljoin(base_url, url)
                elif url.startswith('http'):
                    pass  # Already absolute
                else:
                    continue  # Skip other relative URLs
                
                # Basic URL validation
                parsed = urlparse(url)
                if parsed.scheme in ['http', 'https'] and parsed.netloc:
                    # Clean up URL
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if clean_url.endswith('/'):
                        clean_url = clean_url[:-1]
                    urls.add(clean_url)
                    
            except Exception:
                continue
                
    except Exception as e:
        print(f"  ⚠️ Error extracting URLs: {str(e)[:50]}")
    
    return urls

def is_health_related_url(url):
    """Check if URL is health-related based on domain and keywords"""
    try:
        domain = urlparse(url).netloc.lower()
        path = urlparse(url).path.lower()
        
        # Check if domain contains health keywords
        for keyword in HEALTH_KEYWORDS:
            if keyword in domain or keyword in path:
                return True
                
        return False
    except:
        return False

def is_european_domain(url):
    """Check if URL belongs to a European domain"""
    try:
        domain = urlparse(url).netloc.lower()
        
        # Check for European country domains
        for eu_domain in EUROPEAN_DOMAINS:
            if domain.endswith(eu_domain):
                return True
                
        # Check for .com domains that might be European companies
        if domain.endswith('.com'):
            # This could be enhanced with more sophisticated checking
            # For now, we'll include .com domains if they're health-related
            return True
            
        return False
    except:
        return False

def discover_healthcare_startups():
    """
    Discover healthcare startup URLs from multiple European directories
    
    Returns:
        set: Deduplicated set of healthcare startup URLs
    """
    print("🔍 Starting Healthcare Startup Discovery Phase...")
    print("=" * 60)
    
    discovered_urls = set()
    
    for i, source_url in enumerate(DISCOVERY_SOURCES, 1):
        print(f"[{i}/{len(DISCOVERY_SOURCES)}] Scraping: {source_url}")
        
        try:
            response = create_safe_request(source_url, timeout=15)
            if not response:
                continue
                
            content = response.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='ignore')
            
            # Extract URLs from content
            page_urls = extract_urls_from_content(content, source_url)
            
            # Filter for health-related and European URLs
            health_urls = set()
            for url in page_urls:
                if is_european_domain(url) and is_health_related_url(url):
                    health_urls.add(url)
            
            discovered_urls.update(health_urls)
            print(f"  ✅ Found {len(health_urls)} health-related URLs from this source")
            
        except Exception as e:
            print(f"  ❌ Error scraping {source_url}: {str(e)[:100]}")
            continue
        
        # Be respectful with delays
        time.sleep(2)
    
    print(f"\n🎯 Discovery Complete!")
    print(f"📊 Total unique healthcare URLs discovered: {len(discovered_urls)}")
    
    return discovered_urls

def search_specific_platforms():
    """
    Search specific platforms for healthcare startups using their search/API endpoints
    """
    print("\n🔍 Searching Specific Platforms...")
    
    platform_urls = set()
    
    # Search queries for different platforms
    search_queries = [
        # Google search for European health startups
        'https://www.google.com/search?q=site:eu+healthcare+startup+2024',
        'https://www.google.com/search?q=site:de+digital+health+startup',
        'https://www.google.com/search?q=european+medtech+companies+2024',
        
        # LinkedIn company search (if accessible)
        'https://www.linkedin.com/search/results/companies/?keywords=healthcare%20startup&origin=SWITCH_SEARCH_VERTICAL',
        
        # Startup database searches
        'https://www.startupranking.com/countries/europe/healthcare',
        'https://www.tracxn.com/explore/Healthcare-Startups-in-Europe',
    ]
    
    # Note: This is a simplified version. In practice, you might want to use APIs
    # or more sophisticated scraping for these platforms
    
    return platform_urls

def clean_and_deduplicate_urls(discovered_urls, manual_urls):
    """
    Clean and deduplicate the discovered URLs
    
    Args:
        discovered_urls (set): URLs discovered from scraping
        manual_urls (list): Manually curated URLs
    
    Returns:
        list: Combined and deduplicated list of URLs
    """
    print("\n🧹 Cleaning and Deduplicating URLs...")
    
    # Convert manual URLs to set and normalize
    manual_set = set()
    for url in manual_urls:
        try:
            parsed = urlparse(url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url.endswith('/'):
                clean_url = clean_url[:-1]
            manual_set.add(clean_url)
        except:
            continue
    
    # Clean discovered URLs
    clean_discovered = set()
    for url in discovered_urls:
        try:
            parsed = urlparse(url)
            # Skip if no scheme or netloc
            if not parsed.scheme or not parsed.netloc:
                continue
            
            # Skip social media, directories, and non-company URLs
            skip_domains = [
                'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                'youtube.com', 'crunchbase.com', 'angel.co', 'google.com',
                'bloomberg.com', 'reuters.com', 'techcrunch.com', 'venturebeat.com'
            ]
            
            if any(skip_domain in parsed.netloc.lower() for skip_domain in skip_domains):
                continue
            
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url.endswith('/'):
                clean_url = clean_url[:-1]
            clean_discovered.add(clean_url)
            
        except:
            continue
    
    # Combine and deduplicate
    all_urls = manual_set.union(clean_discovered)
    
    print(f"📊 Manual URLs: {len(manual_set)}")
    print(f"📊 Discovered URLs: {len(clean_discovered)}")
    print(f"📊 Total unique URLs: {len(all_urls)}")
    print(f"📊 New discoveries: {len(clean_discovered - manual_set)}")
    
    return list(all_urls)

def validate_url(url):
    """Validate URL and extract company information"""
    try:
        response = create_safe_request(url, timeout=10)
        if not response:
            return create_error_record(url, "Network error")
        
        content = response.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        # Extract title
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Healthcare Company"
        title = clean_text(title)
        
        # Extract description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else "European healthcare company"
        description = clean_text(description)
        
        # Determine healthcare type
        healthcare_type = determine_healthcare_type(url, content, title)
        
        # Extract country
        country = extract_country(url)
        
        return {
            'name': title,
            'website': url,
            'description': description,
            'country': country,
            'healthcare_type': healthcare_type,
            'status': 'Active',
            'status_code': response.getcode(),
            'source': 'Discovered' if url not in MANUAL_URLS else 'Manual',
            'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        return create_error_record(url, str(e))

def create_error_record(url, error_msg):
    """Create error record for failed validations"""
    return {
        'name': 'Healthcare Company',
        'website': url,
        'description': 'European healthcare company',
        'country': extract_country(url),
        'healthcare_type': 'Healthcare Services',
        'status': f'Error: {error_msg[:50]}',
        'status_code': 0,
        'source': 'Discovered' if url not in MANUAL_URLS else 'Manual',
        'validated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def clean_text(text):
    """Clean text from HTML/CSS garbage"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove CSS
    text = re.sub(r'{[^}]*}', '', text)
    # Remove excess whitespace
    text = ' '.join(text.split())
    # Limit length
    return text[:200] if len(text) > 200 else text

def determine_healthcare_type(url, content, title):
    """Determine healthcare type from URL and content"""
    text = f"{url} {content} {title}".lower()
    
    if any(keyword in text for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning']):
        return 'AI/ML Healthcare'
    elif any(keyword in text for keyword in ['telemedicine', 'telehealth', 'digital health', 'remote', 'virtual']):
        return 'Digital Health'
    elif any(keyword in text for keyword in ['biotech', 'biotechnology', 'drug', 'pharmaceutical', 'therapy']):
        return 'Biotechnology'
    elif any(keyword in text for keyword in ['medical device', 'diagnostic', 'monitoring', 'equipment']):
        return 'Medical Devices'
    elif any(keyword in text for keyword in ['mental health', 'psychology', 'therapy', 'wellness']):
        return 'Mental Health'
    else:
        return 'Healthcare Services'

def extract_country(url):
    """Extract country from domain"""
    domain = urlparse(url).netloc.lower()
    
    country_codes = {
        '.de': 'Germany', '.uk': 'United Kingdom', '.fr': 'France', '.nl': 'Netherlands',
        '.se': 'Sweden', '.ch': 'Switzerland', '.es': 'Spain', '.it': 'Italy',
        '.at': 'Austria', '.be': 'Belgium', '.dk': 'Denmark', '.fi': 'Finland',
        '.no': 'Norway', '.pl': 'Poland', '.cz': 'Czech Republic', '.ie': 'Ireland',
        '.pt': 'Portugal', '.gr': 'Greece', '.hu': 'Hungary', '.ro': 'Romania'
    }
    
    for code, country in country_codes.items():
        if domain.endswith(code):
            return country
    
    return 'Europe'

def save_to_files(companies, base_filename):
    """Save to both CSV and JSON"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"{base_filename}_{timestamp}.csv"
    json_filename = f"{base_filename}_{timestamp}.json"
    
    # Save CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'website', 'description', 'country', 'healthcare_type', 'status', 'status_code', 'source', 'validated_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for company in companies:
            writer.writerow(company)
    
    # Save JSON
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(companies, jsonfile, indent=2, ensure_ascii=False)
    
    return csv_filename, json_filename

def main():
    """Main function with discovery and validation"""
    print("🏥 Enhanced European Healthcare Database Builder")
    print("🔍 With Automatic Discovery from Multiple Sources")
    print("=" * 70)
    
    # Phase 1: Discovery
    discovered_urls = discover_healthcare_startups()
    
    # Phase 2: Search specific platforms (optional)
    # platform_urls = search_specific_platforms()
    # discovered_urls.update(platform_urls)
    
    # Phase 3: Clean and combine URLs
    all_urls = clean_and_deduplicate_urls(discovered_urls, MANUAL_URLS)
    
    # Phase 4: Validation
    print(f"\n🔍 Starting Validation Phase...")
    print(f"📊 Total URLs to validate: {len(all_urls)}")
    print("=" * 70)
    
    validated_companies = []
    
    for i, url in enumerate(all_urls, 1):
        print(f"[{i}/{len(all_urls)}] Validating: {url}")
        
        company_data = validate_url(url)
        validated_companies.append(company_data)
        
        status_emoji = "✅" if company_data['status'] == 'Active' else "❌"
        source_emoji = "🔍" if company_data['source'] == 'Discovered' else "📝"
        print(f"  {status_emoji}{source_emoji} {company_data['status']} - {company_data['healthcare_type']} ({company_data['country']})")
        
        # Respectful delay
        time.sleep(1)
    
    # Phase 5: Save results
    csv_file, json_file = save_to_files(validated_companies, "ENHANCED_EUROPEAN_HEALTHCARE_DATABASE")
    
    # Phase 6: Generate comprehensive report
    print("\n" + "=" * 70)
    print("📈 COMPREHENSIVE FINAL REPORT")
    print("=" * 70)
    
    active_count = sum(1 for c in validated_companies if c['status'] == 'Active')
    manual_count = sum(1 for c in validated_companies if c['source'] == 'Manual')
    discovered_count = sum(1 for c in validated_companies if c['source'] == 'Discovered')
    
    print(f"📊 OVERVIEW:")
    print(f"  • Total companies processed: {len(validated_companies)}")
    print(f"  • Active websites: {active_count}")
    print(f"  • Manual URLs: {manual_count}")
    print(f"  • Discovered URLs: {discovered_count}")
    print(f"  • Success rate: {(active_count/len(validated_companies)*100):.1f}%")
    
    # Healthcare type breakdown
    healthcare_types = {}
    countries = {}
    sources = {}
    
    for company in validated_companies:
        if company['status'] == 'Active':
            htype = company['healthcare_type']
            country = company['country']
            source = company['source']
            
            healthcare_types[htype] = healthcare_types.get(htype, 0) + 1
            countries[country] = countries.get(country, 0) + 1
            sources[source] = sources.get(source, 0) + 1
    
    print(f"\n🏥 HEALTHCARE CATEGORIES:")
    for htype, count in sorted(healthcare_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {htype}: {count} companies")
    
    print(f"\n🌍 COUNTRIES:")
    for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {country}: {count} companies")
    
    print(f"\n📈 SOURCES:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {source}: {count} companies")
    
    print(f"\n💾 FILES SAVED:")
    print(f"  • {csv_file}")
    print(f"  • {json_file}")
    
    print(f"\n🎉 ENHANCED European Healthcare Database completed!")
    print(f"📊 {len(validated_companies)} companies total with automatic discovery!")

if __name__ == "__main__":
    main()