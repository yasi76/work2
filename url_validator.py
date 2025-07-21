#!/usr/bin/env python3
"""
Comprehensive URL Validator
Test and evaluate specific URLs for accessibility, content, and legitimacy
"""

import urllib.request
import urllib.parse
import urllib.error
import socket
import ssl
import json
import csv
from datetime import datetime
from typing import Dict, List, Tuple
import time
import re

class URLValidator:
    def __init__(self):
        self.results = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
    def validate_url(self, url: str) -> Dict:
        """Comprehensive URL validation"""
        print(f"🔍 Testing: {url}")
        
        result = {
            'url': url,
            'status': 'UNKNOWN',
            'http_status': None,
            'accessible': False,
            'dns_resolvable': False,
            'ssl_valid': False,
            'content_type': None,
            'title': None,
            'response_time': None,
            'redirect_url': None,
            'error_message': None,
            'domain_info': {},
            'analysis': {}
        }
        
        try:
            # Parse URL
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            result['domain_info'] = {
                'domain': domain,
                'scheme': parsed.scheme,
                'path': parsed.path,
                'query': parsed.query
            }
            
            # DNS Resolution Test
            try:
                start_time = time.time()
                socket.gethostbyname(domain)
                result['dns_resolvable'] = True
                print(f"  ✅ DNS resolved for {domain}")
            except socket.gaierror as e:
                result['error_message'] = f"DNS resolution failed: {str(e)}"
                print(f"  ❌ DNS failed: {domain}")
                result['status'] = 'DNS_FAILED'
                return result
            
            # HTTP/HTTPS Accessibility Test
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', self.user_agent)
                req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
                req.add_header('Accept-Language', 'en-US,en;q=0.5')
                req.add_header('Accept-Encoding', 'gzip, deflate')
                req.add_header('DNT', '1')
                req.add_header('Connection', 'keep-alive')
                
                start_time = time.time()
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    response_time = time.time() - start_time
                    result['response_time'] = round(response_time, 2)
                    result['http_status'] = response.getcode()
                    result['accessible'] = True
                    
                    # Check for redirects
                    if response.url != url:
                        result['redirect_url'] = response.url
                        print(f"  🔄 Redirected to: {response.url}")
                    
                    # Get content type
                    content_type = response.headers.get('Content-Type', '')
                    result['content_type'] = content_type
                    
                    # SSL validation for HTTPS
                    if parsed.scheme == 'https':
                        result['ssl_valid'] = True
                    
                    # Read and analyze content
                    try:
                        content = response.read().decode('utf-8', errors='ignore')
                        result = self._analyze_content(content, result)
                    except Exception as e:
                        print(f"  ⚠️  Content reading failed: {str(e)}")
                    
                    print(f"  ✅ Accessible: HTTP {result['http_status']} ({result['response_time']}s)")
                    result['status'] = 'ACCESSIBLE'
                    
            except urllib.error.HTTPError as e:
                result['http_status'] = e.code
                result['error_message'] = f"HTTP Error {e.code}: {e.reason}"
                print(f"  ❌ HTTP Error: {e.code} {e.reason}")
                result['status'] = 'HTTP_ERROR'
                
            except urllib.error.URLError as e:
                result['error_message'] = f"URL Error: {str(e.reason)}"
                print(f"  ❌ URL Error: {str(e.reason)}")
                result['status'] = 'URL_ERROR'
                
            except socket.timeout:
                result['error_message'] = "Connection timeout"
                print(f"  ⏰ Timeout")
                result['status'] = 'TIMEOUT'
                
            except Exception as e:
                result['error_message'] = f"Unexpected error: {str(e)}"
                print(f"  ❌ Error: {str(e)}")
                result['status'] = 'ERROR'
        
        except Exception as e:
            result['error_message'] = f"Validation failed: {str(e)}"
            result['status'] = 'FAILED'
            print(f"  ❌ Validation failed: {str(e)}")
        
        # Analyze domain for health/medical content
        result['analysis'] = self._analyze_domain_purpose(result)
        
        return result
    
    def _analyze_content(self, content: str, result: Dict) -> Dict:
        """Analyze webpage content"""
        try:
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                result['title'] = title_match.group(1).strip()[:200]  # Limit title length
                print(f"  📄 Title: {result['title'][:80]}...")
            
            # Check for health/medical keywords
            health_keywords = [
                'health', 'medical', 'healthcare', 'medicine', 'pharma', 'pharmaceutical',
                'therapy', 'treatment', 'diagnosis', 'patient', 'doctor', 'clinic',
                'hospital', 'wellness', 'app', 'digital health', 'telemedicine',
                'gesundheit', 'medizin', 'therapie', 'patient', 'arzt', 'klinik'
            ]
            
            content_lower = content.lower()
            found_keywords = [kw for kw in health_keywords if kw in content_lower]
            
            if found_keywords:
                result['health_keywords'] = found_keywords[:10]  # Limit to first 10
                print(f"  🏥 Health keywords found: {', '.join(found_keywords[:5])}")
        
        except Exception as e:
            print(f"  ⚠️  Content analysis failed: {str(e)}")
        
        return result
    
    def _analyze_domain_purpose(self, result: Dict) -> Dict:
        """Analyze domain to determine purpose and legitimacy"""
        analysis = {
            'likely_purpose': 'unknown',
            'health_related': False,
            'app_related': False,
            'commercial': False,
            'indicators': []
        }
        
        url = result['url'].lower()
        domain = result['domain_info']['domain'].lower()
        title = (result.get('title', '') or '').lower()
        
        # Health/Medical indicators
        health_indicators = [
            'health', 'med', 'care', 'pharma', 'clinic', 'doctor', 'patient',
            'therapy', 'treatment', 'wellness', 'gesundheit', 'arzt', 'medizin'
        ]
        
        # App/Digital indicators
        app_indicators = ['app', 'digital', 'ai', 'tech', 'platform', 'software']
        
        # Check domain and title for indicators
        for indicator in health_indicators:
            if indicator in domain or indicator in title:
                analysis['health_related'] = True
                analysis['indicators'].append(f"Health-related: {indicator}")
        
        for indicator in app_indicators:
            if indicator in domain or indicator in title:
                analysis['app_related'] = True
                analysis['indicators'].append(f"App/Tech-related: {indicator}")
        
        # Determine likely purpose
        if analysis['health_related'] and analysis['app_related']:
            analysis['likely_purpose'] = 'digital_health_app'
        elif analysis['health_related']:
            analysis['likely_purpose'] = 'healthcare_service'
        elif analysis['app_related']:
            analysis['likely_purpose'] = 'technology_platform'
        elif 'shop' in url or 'store' in url:
            analysis['likely_purpose'] = 'e_commerce'
            analysis['commercial'] = True
        
        # German TLD analysis
        if domain.endswith('.de'):
            analysis['indicators'].append("German domain (.de)")
        
        return analysis
    
    def validate_urls(self, urls: List[str]) -> List[Dict]:
        """Validate multiple URLs"""
        print(f"🚀 VALIDATING {len(urls)} URLS")
        print("=" * 70)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i:2d}/{len(urls)}] ", end="")
            result = self.validate_url(url)
            self.results.append(result)
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        return self.results
    
    def generate_summary(self) -> Dict:
        """Generate validation summary"""
        total = len(self.results)
        accessible = len([r for r in self.results if r['accessible']])
        dns_ok = len([r for r in self.results if r['dns_resolvable']])
        ssl_valid = len([r for r in self.results if r['ssl_valid']])
        health_related = len([r for r in self.results if r['analysis'].get('health_related', False)])
        
        # Status breakdown
        status_counts = {}
        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Response time analysis
        response_times = [r['response_time'] for r in self.results if r['response_time']]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_urls': total,
            'accessible': accessible,
            'dns_resolvable': dns_ok,
            'ssl_valid': ssl_valid,
            'health_related': health_related,
            'accessibility_rate': (accessible / total * 100) if total > 0 else 0,
            'avg_response_time': round(avg_response_time, 2),
            'status_breakdown': status_counts,
            'fastest_site': min(response_times) if response_times else None,
            'slowest_site': max(response_times) if response_times else None
        }
    
    def save_results(self, filename_base: str = "url_validation"):
        """Save validation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed CSV
        csv_filename = f"{filename_base}_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            if self.results:
                fieldnames = [
                    'url', 'status', 'accessible', 'http_status', 'response_time',
                    'dns_resolvable', 'ssl_valid', 'content_type', 'title',
                    'redirect_url', 'error_message', 'likely_purpose', 
                    'health_related', 'app_related'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.results:
                    row = {
                        'url': result['url'],
                        'status': result['status'],
                        'accessible': result['accessible'],
                        'http_status': result['http_status'],
                        'response_time': result['response_time'],
                        'dns_resolvable': result['dns_resolvable'],
                        'ssl_valid': result['ssl_valid'],
                        'content_type': result['content_type'],
                        'title': result.get('title', ''),
                        'redirect_url': result.get('redirect_url', ''),
                        'error_message': result.get('error_message', ''),
                        'likely_purpose': result['analysis'].get('likely_purpose', ''),
                        'health_related': result['analysis'].get('health_related', False),
                        'app_related': result['analysis'].get('app_related', False)
                    }
                    writer.writerow(row)
        
        # Save JSON with full details
        json_filename = f"{filename_base}_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'validation_timestamp': datetime.now().isoformat(),
                'summary': self.generate_summary(),
                'results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        return csv_filename, json_filename
    
    def print_summary_report(self):
        """Print comprehensive summary report"""
        summary = self.generate_summary()
        
        print("\n" + "=" * 70)
        print("📊 URL VALIDATION SUMMARY REPORT")
        print("=" * 70)
        
        print(f"📈 OVERALL STATISTICS:")
        print(f"  • Total URLs tested: {summary['total_urls']}")
        print(f"  • ✅ Accessible: {summary['accessible']} ({summary['accessibility_rate']:.1f}%)")
        print(f"  • 🌐 DNS resolvable: {summary['dns_resolvable']}")
        print(f"  • 🔒 SSL valid: {summary['ssl_valid']}")
        print(f"  • 🏥 Health-related: {summary['health_related']}")
        
        if summary['avg_response_time'] > 0:
            print(f"  • ⏱️  Average response time: {summary['avg_response_time']}s")
            if summary['fastest_site']:
                print(f"  • ⚡ Fastest response: {summary['fastest_site']}s")
            if summary['slowest_site']:
                print(f"  • 🐌 Slowest response: {summary['slowest_site']}s")
        
        print(f"\n📊 STATUS BREAKDOWN:")
        for status, count in sorted(summary['status_breakdown'].items()):
            percentage = (count / summary['total_urls'] * 100)
            print(f"  • {status}: {count} ({percentage:.1f}%)")
        
        # Show accessible URLs
        accessible_urls = [r for r in self.results if r['accessible']]
        if accessible_urls:
            print(f"\n✅ ACCESSIBLE URLS ({len(accessible_urls)}):")
            for result in accessible_urls:
                status_icon = "🏥" if result['analysis'].get('health_related') else "🌐"
                response_info = f"({result['response_time']}s)" if result['response_time'] else ""
                print(f"  {status_icon} {result['url']} {response_info}")
                if result.get('title'):
                    print(f"    📄 {result['title'][:80]}...")
        
        # Show problematic URLs
        problematic_urls = [r for r in self.results if not r['accessible']]
        if problematic_urls:
            print(f"\n❌ PROBLEMATIC URLS ({len(problematic_urls)}):")
            for result in problematic_urls[:10]:  # Show first 10
                print(f"  ❌ {result['url']}")
                print(f"    Error: {result.get('error_message', 'Unknown error')}")
            
            if len(problematic_urls) > 10:
                print(f"  ... and {len(problematic_urls) - 10} more problematic URLs")

def main():
    """Main validation function"""
    
    # Your URLs to test
    urls_to_test = [
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
    
    print(f"🔍 COMPREHENSIVE URL VALIDATION")
    print(f"Testing {len(urls_to_test)} user-provided URLs")
    print("=" * 70)
    
    # Initialize validator
    validator = URLValidator()
    
    # Validate all URLs
    results = validator.validate_urls(urls_to_test)
    
    # Generate and display summary
    validator.print_summary_report()
    
    # Save results
    csv_file, json_file = validator.save_results("user_url_validation")
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"  📊 Detailed CSV: {csv_file}")
    print(f"  💾 Full JSON: {json_file}")
    
    # Return summary for further analysis
    return validator.generate_summary()

if __name__ == "__main__":
    summary = main()