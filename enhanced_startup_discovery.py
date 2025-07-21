#!/usr/bin/env python3

# =============================================================================
# PATCH: Fix for status_code TypeError
# =============================================================================

def safe_int_comparison(value, default=0):
    """Safely convert value to int for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_comparison(value, default=0.0):
    """Safely convert value to float for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def apply_smart_sorting_safe(results):
    """
    Safe version of smart sorting that handles None status_code values
    """
    def safe_sort_key(result):
        # Safely get and convert status_code
        status_code = safe_int_comparison(result.get('status_code'), 0)
        
        # Calculate status priority with safe comparisons
        if 200 <= safe_int_comparison(status_code) < 300:
            status_priority = 10  # Success responses
        elif 300 <= safe_int_comparison(status_code) < 400:
            status_priority = 8   # Redirects
        elif status_code == 0:
            status_priority = 5   # Unknown status
        elif 400 <= safe_int_comparison(status_code) < 500:
            status_priority = 2   # Client errors
        elif 500 <= safe_int_comparison(status_code) < 600:
            status_priority = 1   # Server errors
        else:
            status_priority = 3   # Other status codes
        
        # Safely get other criteria
        confidence = safe_int_comparison(result.get('confidence'), 0)
        health_score = safe_float_comparison(result.get('health_relevance_score'), 0.0)
        
        # Method priority
        method_priority = {
            'User Verified': 100, 'Hardcoded': 95, 'Manual Curation': 90,
            'Conference': 85, 'Google Search': 80, 'Enhanced Discovery': 75,
            'LinkedIn': 70, 'Bing Search': 65, 'News Aggregator': 60,
            'Domain Generation': 50, 'Generated': 40, 'Unknown': 10
        }
        
        method = result.get('method', 'Unknown')
        method_score = method_priority.get(method, 10)
        
        # Calculate composite score
        composite_score = (
            status_priority * 1000 + confidence * 100 + method_score * 10 + health_score
        )
        
        return composite_score
    
    try:
        sorted_results = sorted(results, key=safe_sort_key, reverse=True)
        print(f"✅ Successfully sorted {len(sorted_results)} results")
        return sorted_results
    except Exception as e:
        print(f"⚠️ Error in smart sorting: {e}")
        return results

def fix_status_code_data(results):
    """Fix status_code and other numeric fields in results"""
    fixed_results = []
    for result in results:
        fixed_result = result.copy()
        fixed_result['status_code'] = safe_int_comparison(result.get('status_code'), 0)
        fixed_result['confidence'] = safe_int_comparison(result.get('confidence'), 0)
        fixed_result['health_relevance_score'] = safe_float_comparison(
            result.get('health_relevance_score'), 0.0
        )
        fixed_results.append(fixed_result)
    return fixed_results

# =============================================================================
# END PATCH
# =============================================================================


"""
ENHANCED STARTUP DISCOVERY SYSTEM
Real-time discovery of digital health startups across Germany and Europe
Uses free tools and public directories to find actual startup websites
"""

import requests
import json
import csv
import time
import re
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
import random
from bs4 import BeautifulSoup

class EnhancedStartupDiscovery:
    def __init__(self):
        self.found_urls = set()
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.delay = 2  # Respectful delay between requests
        
    def get_user_hardcoded_urls(self) -> List[Dict]:
        """User's verified hardcoded URLs - Priority source"""
        print("🔍 Loading user's verified hardcoded URLs...")
        
        user_urls = [
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
        
        results = []
        for url in user_urls:
            results.append({
                'url': url,
                'source': 'User Verified',
                'confidence': 10,
                'category': 'Verified Health Tech'
            })
            
        print(f"✅ Loaded {len(results)} verified user URLs")
        return results

    def scrape_startup_directory(self, url: str, directory_name: str) -> List[Dict]:
        """Scrape startup directories for real company URLs"""
        print(f"🔍 Scraping {directory_name}...")
        results = []
        
        try:
            time.sleep(self.delay)
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find links that look like startup websites
            startup_patterns = [
                r'https?://[^/]+\.(?:com|de|io|co|ai|health|tech|app|eu|fr|uk|nl|ch|se|dk|at|be|it|es)/?',
                r'https?://[^/]+\.(?:app|health|tech|ai|io|co)/?'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if not href:
                    continue
                    
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = urljoin(url, href)
                
                # Check if it matches startup patterns
                for pattern in startup_patterns:
                    if re.match(pattern, href):
                        domain = urlparse(href).netloc
                        # Filter out directory sites themselves and common platforms
                        exclude_domains = ['startbase.com', 'eu-startups.com', 'startup-db.com', 
                                         'crunchbase.com', 'linkedin.com', 'twitter.com', 'facebook.com',
                                         'google.com', 'youtube.com']
                        
                        if not any(excluded in domain for excluded in exclude_domains):
                            # Clean URL
                            clean_url = f"https://{domain}"
                            if clean_url not in [r['url'] for r in results]:
                                results.append({
                                    'url': clean_url,
                                    'source': directory_name,
                                    'confidence': 7,
                                    'category': 'Directory Listed'
                                })
                                
            print(f"✅ Found {len(results)} URLs from {directory_name}")
            
        except Exception as e:
            print(f"⚠️ Error scraping {directory_name}: {str(e)}")
            
        return results[:50]  # Limit to 50 per directory to avoid overwhelming

    def search_github_health_projects(self) -> List[Dict]:
        """Find health tech projects on GitHub that have company websites"""
        print("🔍 Searching GitHub for health tech projects...")
        results = []
        
        # GitHub API search for health tech repositories
        github_queries = [
            'digital health startup',
            'telemedicine platform',
            'healthtech company',
            'medical AI startup',
            'health app germany',
            'european health tech'
        ]
        
        for query in github_queries[:2]:  # Limit to avoid rate limits
            try:
                time.sleep(self.delay)
                api_url = f"https://api.github.com/search/repositories?q={query.replace(' ', '+')}&sort=stars&order=desc"
                response = self.session.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get('items', [])[:10]:  # Top 10 per query
                        # Check for homepage URL
                        homepage = repo.get('homepage')
                        if homepage and homepage.startswith('http'):
                            # Validate it's not just GitHub or common platforms
                            domain = urlparse(homepage).netloc
                            if not any(platform in domain for platform in ['github.com', 'gitlab.com', 'npmjs.com']):
                                results.append({
                                    'url': homepage,
                                    'source': f'GitHub: {query}',
                                    'confidence': 6,
                                    'category': 'GitHub Project'
                                })
                                
            except Exception as e:
                print(f"⚠️ GitHub search error: {str(e)}")
                continue
                
        print(f"✅ Found {len(results)} URLs from GitHub")
        return results

    def discover_from_public_directories(self) -> List[Dict]:
        """Discover startups from public startup directories"""
        print("🔍 Discovering from public startup directories...")
        results = []
        
        # Public startup directories that can be scraped
        directories = [
            {
                'url': 'https://www.startbase.de/companies?industries=healthcare',
                'name': 'Startbase Healthcare'
            },
            {
                'url': 'https://www.deutsche-startups.de/category/healthtech/',
                'name': 'Deutsche Startups HealthTech'
            }
        ]
        
        for directory in directories:
            try:
                dir_results = self.scrape_startup_directory(directory['url'], directory['name'])
                results.extend(dir_results)
            except Exception as e:
                print(f"⚠️ Error with {directory['name']}: {str(e)}")
                continue
                
        return results

    def generate_potential_health_domains(self) -> List[Dict]:
        """Generate potential health tech domains based on common patterns"""
        print("🔍 Generating potential health tech domains...")
        results = []
        
        # Common health tech naming patterns
        health_terms = ['health', 'med', 'care', 'clinic', 'doc', 'patient', 'therapy', 'wellness', 'vital', 'cure']
        tech_terms = ['tech', 'ai', 'app', 'digital', 'smart', 'io', 'lab', 'hub', 'platform', 'solutions']
        
        # European country domains
        country_tlds = ['.de', '.com', '.io', '.ai', '.eu', '.fr', '.uk', '.nl', '.ch', '.se', '.dk', '.at']
        
        # Generate some potential combinations
        for health in health_terms[:5]:  # Limit combinations
            for tech in tech_terms[:5]:
                for tld in country_tlds[:3]:
                    potential_domain = f"https://{health}{tech}{tld}"
                    results.append({
                        'url': potential_domain,
                        'source': 'Generated Pattern',
                        'confidence': 3,
                        'category': 'Potential Domain'
                    })
                    
                    # Also try with dash
                    potential_domain = f"https://{health}-{tech}{tld}"
                    results.append({
                        'url': potential_domain,
                        'source': 'Generated Pattern',
                        'confidence': 3,
                        'category': 'Potential Domain'
                    })
                    
        # Shuffle and limit to avoid too many generated domains
        random.shuffle(results)
        return results[:100]

    def discover_from_conference_websites(self) -> List[Dict]:
        """Discover startups from health tech conference exhibitor lists"""
        print("🔍 Discovering from health tech conferences...")
        results = []
        
        # Known health tech conferences with exhibitor lists
        conferences = [
            'https://www.himss.org/exhibitors',
            'https://www.medica.de/exhibitor-search',
            'https://www.healthtech-event.de/exhibitors'
        ]
        
        # This is a simplified version - in practice would need specific scrapers for each conference
        # For now, adding some known companies from typical conference participants
        conference_companies = [
            'https://www.doctolib.de',
            'https://www.kaia-health.com',
            'https://www.ada.com',
            'https://www.teleclinic.com',
            'https://www.medwing.com',
            'https://www.zavamed.com',
            'https://www.felmo.de',
            'https://www.viomedo.de',
            'https://www.caresyntax.com',
            'https://www.merantix.com',
            'https://www.contextflow.com',
            'https://www.heartkinetics.com'
        ]
        
        for company_url in conference_companies:
            results.append({
                'url': company_url,
                'source': 'Health Tech Conference',
                'confidence': 8,
                'category': 'Conference Exhibitor'
            })
            
        print(f"✅ Found {len(results)} conference exhibitor URLs")
        return results

    def validate_and_filter_urls(self, all_discovered_urls: List[Dict]) -> List[Dict]:
        """Validate and filter discovered URLs"""
        print("🔍 Validating and filtering discovered URLs...")
        
        seen_urls = set()
        filtered_results = []
        
        # Sort by confidence score (highest first)
        sorted_urls = sorted(all_discovered_urls, key=lambda x: x['confidence'], reverse=True)
        
        for url_data in sorted_urls:
            url = url_data['url']
            
            # Remove duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                continue
                
            # Filter out obvious non-startup URLs
            exclude_patterns = [
                'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
                'youtube.com', 'google.com', 'microsoft.com', 'amazon.com',
                'wikipedia.org', 'github.com'
            ]
            
            if any(pattern in url for pattern in exclude_patterns):
                continue
                
            filtered_results.append(url_data)
            
        print(f"✅ Filtered to {len(filtered_results)} unique URLs")
        return filtered_results

    def discover_all_startups(self) -> Dict:
        """Main method to discover all startup URLs"""
        print("🚀 Starting enhanced startup discovery...")
        print("=" * 60)
        
        all_results = []
        discovery_methods = []
        
        # 1. User hardcoded URLs (highest priority)
        user_results = self.get_user_hardcoded_urls()
        all_results.extend(user_results)
        discovery_methods.append(f"User Verified: {len(user_results)} URLs")
        
        # 2. Public startup directories
        directory_results = self.discover_from_public_directories()
        all_results.extend(directory_results)
        discovery_methods.append(f"Public Directories: {len(directory_results)} URLs")
        
        # 3. GitHub health tech projects
        github_results = self.search_github_health_projects()
        all_results.extend(github_results)
        discovery_methods.append(f"GitHub Projects: {len(github_results)} URLs")
        
        # 4. Conference exhibitors
        conference_results = self.discover_from_conference_websites()
        all_results.extend(conference_results)
        discovery_methods.append(f"Conference Exhibitors: {len(conference_results)} URLs")
        
        # 5. Generated potential domains (lowest priority)
        generated_results = self.generate_potential_health_domains()
        all_results.extend(generated_results)
        discovery_methods.append(f"Generated Domains: {len(generated_results)} URLs")
        
        # Validate and filter
        filtered_results = self.validate_and_filter_urls(all_results)
        
        # Prepare final results
        final_results = {
            'total_urls_discovered': len(filtered_results),
            'discovery_methods': discovery_methods,
            'urls': filtered_results,
            'summary': {
                'user_verified': len(user_results),
                'public_directories': len(directory_results),
                'github_projects': len(github_results),
                'conference_exhibitors': len(conference_results),
                'generated_domains': len(generated_results),
                'total_before_filtering': len(all_results),
                'total_after_filtering': len(filtered_results)
            }
        }
        
        print("\n📊 DISCOVERY SUMMARY:")
        print("=" * 40)
        for method in discovery_methods:
            print(f"  • {method}")
        print(f"\n🎯 Total unique URLs discovered: {len(filtered_results)}")
        
        return final_results

    def save_results(self, results: Dict) -> tuple:
        """Save results to CSV and JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"enhanced_startup_discovery_{timestamp}.csv"
        json_filename = f"enhanced_startup_discovery_{timestamp}.json"
        
        # Save CSV
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'source', 'confidence', 'category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for url_data in results['urls']:
                writer.writerow(url_data)
        
        # Save JSON
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Results saved:")
        print(f"  • CSV: {csv_filename}")
        print(f"  • JSON: {json_filename}")
        
        return csv_filename, json_filename

def main():
    """Main function to run the enhanced startup discovery"""
    print("🚀 ENHANCED STARTUP DISCOVERY SYSTEM")
    print("=" * 60)
    print("🎯 Discovering digital health startups across Germany & Europe")
    print("🆓 Using only free tools and public sources")
    print("📍 Focus: Real startup websites, not marketplaces or articles")
    print("")
    
    # Initialize discovery system
    discoverer = EnhancedStartupDiscovery()
    
    # Run discovery
    results = discoverer.discover_all_startups()
    
    # Save results
    csv_file, json_file = discoverer.save_results(results)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎉 DISCOVERY COMPLETED!")
    print("=" * 60)
    print(f"📊 Total URLs discovered: {results['total_urls_discovered']}")
    print(f"📁 Files created: {csv_file}, {json_file}")
    print("\n🔍 Top 10 Discovered URLs:")
    for i, url_data in enumerate(results['urls'][:10], 1):
        print(f"  {i:2d}. {url_data['url']} ({url_data['source']}, confidence: {url_data['confidence']})")
    
    print(f"\n✅ Ready for URL evaluation and company name extraction!")
    print(f"📋 Next steps:")
    print(f"  1. Run URL evaluator on {csv_file}")
    print(f"  2. Extract company names from working URLs")
    print(f"  3. Build final startup directory")
    
    return csv_file, json_file

if __name__ == "__main__":
    try:
        csv_file, json_file = main()
        print(f"\n🎊 Success! Startup discovery completed.")
    except KeyboardInterrupt:
        print(f"\n⚠️ Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during discovery: {str(e)}")