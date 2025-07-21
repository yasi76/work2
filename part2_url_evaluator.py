#!/usr/bin/env python3
"""
PART 2: FREE URL EVALUATOR
Evaluate and separate correct URLs using only free tools
Tests accessibility, SSL, redirects, and basic content analysis
"""

import urllib.request
import urllib.parse
import json
import csv
import re
import time
import socket
import ssl
from datetime import datetime
from typing import List, Dict, Set, Optional
import sys

class FreeURLEvaluator:
    def __init__(self):
        self.results = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.timeout = 10
        self.health_keywords = [
            'health', 'medical', 'doctor', 'patient', 'clinic', 'hospital', 'pharma', 'medicine',
            'therapy', 'treatment', 'diagnosis', 'wellness', 'care', 'healthcare', 'medic',
            'app', 'digital', 'ai', 'analytics', 'platform', 'solution', 'tech', 'system'
        ]
    
    def check_dns_resolution(self, url: str) -> Dict:
        """Check if domain resolves using free DNS lookup"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Simple DNS resolution check
            ip = socket.gethostbyname(domain)
            return {
                'dns_resolves': True,
                'ip_address': ip,
                'domain': domain
            }
        except (socket.gaierror, socket.error) as e:
            return {
                'dns_resolves': False,
                'error': str(e),
                'domain': domain if 'domain' in locals() else 'unknown'
            }
    
    def check_http_accessibility(self, url: str) -> Dict:
        """Check HTTP/HTTPS accessibility using free urllib"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Create request with headers
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            
            start_time = time.time()
            
            # Make request
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_time = time.time() - start_time
                status_code = response.getcode()
                final_url = response.geturl()
                
                # Read content (limit to first 10KB for performance)
                content = response.read(10240).decode('utf-8', errors='ignore')
                
                return {
                    'accessible': True,
                    'status_code': status_code,
                    'response_time': round(response_time, 2),
                    'final_url': final_url,
                    'redirected': final_url != url,
                    'content_preview': content[:500],
                    'content_length': len(content)
                }
                
        except urllib.error.HTTPError as e:
            return {
                'accessible': False,
                'status_code': e.code,
                'error': f'HTTP Error: {e.code} - {e.reason}',
                'response_time': None
            }
        except urllib.error.URLError as e:
            return {
                'accessible': False,
                'status_code': None,
                'error': f'URL Error: {str(e.reason)}',
                'response_time': None
            }
        except Exception as e:
            return {
                'accessible': False,
                'status_code': None,
                'error': f'Exception: {str(e)}',
                'response_time': None
            }
    
    def check_ssl_certificate(self, url: str) -> Dict:
        """Check SSL certificate validity using free methods"""
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme != 'https':
                return {
                    'ssl_valid': False,
                    'reason': 'Not HTTPS',
                    'has_ssl': False
                }
            
            domain = parsed.netloc
            port = 443
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate info
            with socket.create_connection((domain, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'ssl_valid': True,
                        'has_ssl': True,
                        'issuer': dict(x[0] for x in cert['issuer']).get('organizationName', 'Unknown'),
                        'subject': dict(x[0] for x in cert['subject']).get('commonName', 'Unknown'),
                        'version': cert.get('version', 'Unknown')
                    }
                    
        except ssl.SSLError as e:
            return {
                'ssl_valid': False,
                'has_ssl': True,
                'error': f'SSL Error: {str(e)}'
            }
        except Exception as e:
            return {
                'ssl_valid': False,
                'has_ssl': False,
                'error': f'Connection Error: {str(e)}'
            }
    
    def analyze_content(self, content: str, url: str) -> Dict:
        """Analyze webpage content for health-related indicators"""
        if not content:
            return {
                'has_title': False,
                'health_related': False,
                'content_quality': 'poor'
            }
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        
        # Remove HTML tags for text analysis
        text_content = re.sub(r'<[^>]+>', ' ', content).lower()
        
        # Check for health keywords
        health_keyword_count = sum(1 for keyword in self.health_keywords if keyword in text_content)
        
        # Check for common health tech indicators
        health_indicators = [
            'patient', 'doctor', 'medical', 'health', 'clinic', 'hospital',
            'diagnosis', 'treatment', 'therapy', 'wellness', 'healthcare',
            'pharmaceutical', 'medicine', 'drug', 'cure', 'heal'
        ]
        
        indicator_count = sum(1 for indicator in health_indicators if indicator in text_content)
        
        # Determine if health-related
        is_health_related = health_keyword_count >= 2 or indicator_count >= 3
        
        # Content quality assessment
        content_quality = 'excellent' if len(content) > 5000 and title else \
                         'good' if len(content) > 2000 and title else \
                         'fair' if len(content) > 500 else 'poor'
        
        return {
            'has_title': bool(title),
            'title': title[:100] if title else '',
            'health_related': is_health_related,
            'health_keyword_count': health_keyword_count,
            'health_indicator_count': indicator_count,
            'content_quality': content_quality,
            'content_length': len(content)
        }
    
    def categorize_url(self, url: str, analysis_results: Dict) -> str:
        """Categorize URL based on analysis results"""
        # Check if accessible
        if not analysis_results.get('http_check', {}).get('accessible', False):
            return 'Not Accessible'
        
        # Check DNS
        if not analysis_results.get('dns_check', {}).get('dns_resolves', False):
            return 'DNS Failed'
        
        # Check content
        content_analysis = analysis_results.get('content_analysis', {})
        
        if content_analysis.get('health_related', False):
            if content_analysis.get('content_quality') in ['excellent', 'good']:
                return 'Health Tech - Verified'
            else:
                return 'Health Tech - Basic'
        elif content_analysis.get('has_title', False):
            return 'General Website'
        else:
            return 'Low Quality'
    
    def evaluate_single_url(self, url: str) -> Dict:
        """Evaluate a single URL comprehensively"""
        print(f"  🔍 Evaluating: {url}")
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'evaluation_status': 'pending'
        }
        
        try:
            # DNS Check
            dns_result = self.check_dns_resolution(url)
            result['dns_check'] = dns_result
            
            if dns_result['dns_resolves']:
                # HTTP Accessibility Check
                http_result = self.check_http_accessibility(url)
                result['http_check'] = http_result
                
                if http_result['accessible']:
                    # SSL Check (if HTTPS)
                    if url.startswith('https://'):
                        ssl_result = self.check_ssl_certificate(url)
                        result['ssl_check'] = ssl_result
                    
                    # Content Analysis
                    content = http_result.get('content_preview', '')
                    content_analysis = self.analyze_content(content, url)
                    result['content_analysis'] = content_analysis
                    
                    # Categorization
                    category = self.categorize_url(url, result)
                    result['category'] = category
                    result['evaluation_status'] = 'completed'
                    
                    print(f"    ✅ {category} - {http_result['status_code']} ({http_result['response_time']}s)")
                else:
                    result['category'] = 'Not Accessible'
                    result['evaluation_status'] = 'completed'
                    print(f"    ❌ Not accessible - {http_result.get('error', 'Unknown error')}")
            else:
                result['category'] = 'DNS Failed'
                result['evaluation_status'] = 'completed'
                print(f"    ❌ DNS failed - {dns_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            result['evaluation_status'] = 'error'
            result['error'] = str(e)
            result['category'] = 'Error'
            print(f"    ❌ Error: {str(e)}")
        
        return result
    
    def evaluate_urls(self, urls: List[str]) -> List[Dict]:
        """Evaluate a list of URLs"""
        print(f"🚀 PART 2: EVALUATING {len(urls)} URLs")
        print("=" * 60)
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            result = self.evaluate_single_url(url)
            results.append(result)
            
            # Rate limiting
            time.sleep(1)
            
            # Progress update every 10 URLs
            if i % 10 == 0:
                working_count = sum(1 for r in results if r.get('category') not in ['Not Accessible', 'DNS Failed', 'Error'])
                print(f"\n  📊 Progress: {i}/{len(urls)} completed, {working_count} working URLs found")
        
        self.results = results
        return results
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate evaluation summary"""
        total = len(results)
        
        # Count by category
        categories = {}
        working_urls = []
        problematic_urls = []
        
        for result in results:
            category = result.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
            
            if category in ['Health Tech - Verified', 'Health Tech - Basic', 'General Website']:
                working_urls.append(result['url'])
            else:
                problematic_urls.append({
                    'url': result['url'],
                    'issue': category,
                    'error': result.get('error', result.get('dns_check', {}).get('error', 'Unknown'))
                })
        
        # Response time analysis
        response_times = [
            r.get('http_check', {}).get('response_time', 0) 
            for r in results 
            if r.get('http_check', {}).get('response_time') is not None
        ]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        summary = {
            'total_urls_evaluated': total,
            'working_urls_count': len(working_urls),
            'problematic_urls_count': len(problematic_urls),
            'success_rate': round((len(working_urls) / total) * 100, 2) if total > 0 else 0,
            'categories': categories,
            'working_urls': working_urls,
            'problematic_urls': problematic_urls,
            'average_response_time': round(avg_response_time, 2),
            'evaluation_timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def save_results(self, results: List[Dict], summary: Dict, filename: str = "url_evaluation_part2"):
        """Save evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results (JSON)
        json_filename = f"{filename}_detailed_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': summary,
                'detailed_results': results
            }, f, indent=2, ensure_ascii=False)
        
        # Save working URLs (CSV)
        working_csv = f"working_urls_{timestamp}.csv"
        with open(working_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'category', 'status_code', 'response_time', 'title', 'health_related'])
            
            for result in results:
                if result.get('category') in ['Health Tech - Verified', 'Health Tech - Basic', 'General Website']:
                    http_check = result.get('http_check', {})
                    content_analysis = result.get('content_analysis', {})
                    
                    writer.writerow([
                        result['url'],
                        result.get('category', ''),
                        http_check.get('status_code', ''),
                        http_check.get('response_time', ''),
                        content_analysis.get('title', '')[:50],
                        content_analysis.get('health_related', False)
                    ])
        
        # Save problematic URLs (CSV)
        problematic_csv = f"problematic_urls_{timestamp}.csv"
        with open(problematic_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'issue', 'error_details'])
            
            for problem in summary['problematic_urls']:
                writer.writerow([
                    problem['url'],
                    problem['issue'],
                    problem['error'][:100]
                ])
        
        return json_filename, working_csv, problematic_csv

def load_urls_from_part1(filename: str = None) -> List[str]:
    """Load URLs from Part 1 results"""
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row['url'] for row in reader]
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return []
    else:
        # Return a sample if no file provided
        print("⚠️  No Part 1 file provided, using sample URLs for demonstration")
        return [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://ada.com',
            'https://doctolib.fr',
            'https://medgate.ch'
        ]

def main():
    """Main function for Part 2: URL Evaluation"""
    print("🔍 PART 2: FREE URL EVALUATION")
    print("=" * 60)
    print("Evaluating URLs using only FREE tools")
    print("Testing: DNS resolution, HTTP accessibility, SSL, content analysis")
    print("")
    
    # Load URLs from Part 1 or use sample
    import sys
    if len(sys.argv) > 1:
        urls = load_urls_from_part1(sys.argv[1])
    else:
        # Try to find the most recent Part 1 file
        import glob
        part1_files = glob.glob("discovered_urls_part1_*.csv")
        if part1_files:
            latest_file = max(part1_files)
            print(f"📂 Found Part 1 file: {latest_file}")
            urls = load_urls_from_part1(latest_file)
        else:
            print("📂 No Part 1 file found, loading sample URLs...")
            urls = load_urls_from_part1()
    
    if not urls:
        print("❌ No URLs to evaluate!")
        return
    
    print(f"📊 Loaded {len(urls)} URLs for evaluation")
    
    # Initialize evaluator
    evaluator = FreeURLEvaluator()
    
    # Evaluate URLs
    results = evaluator.evaluate_urls(urls)
    
    # Generate summary
    summary = evaluator.generate_summary(results)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    print(f"🎯 Total URLs evaluated: {summary['total_urls_evaluated']}")
    print(f"✅ Working URLs: {summary['working_urls_count']}")
    print(f"❌ Problematic URLs: {summary['problematic_urls_count']}")
    print(f"📈 Success rate: {summary['success_rate']}%")
    print(f"⏱️  Average response time: {summary['average_response_time']}s")
    
    print(f"\n📋 Categories breakdown:")
    for category, count in summary['categories'].items():
        print(f"  • {category}: {count} URLs")
    
    # Save results
    json_file, working_csv, problematic_csv = evaluator.save_results(results, summary)
    
    print(f"\n💾 FILES SAVED:")
    print(f"  📊 Detailed results: {json_file}")
    print(f"  ✅ Working URLs: {working_csv}")
    print(f"  ❌ Problematic URLs: {problematic_csv}")
    
    print(f"\n🎯 SUMMARY:")
    print(f"  ✅ Successfully evaluated {summary['total_urls_evaluated']} URLs")
    print(f"  ✅ Found {summary['working_urls_count']} working URLs")
    print(f"  🆓 Used only free tools - no paid services required")
    print(f"  ➡️  Ready for Part 3: Company Name Extraction")
    
    return summary

if __name__ == "__main__":
    summary = main()