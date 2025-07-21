#!/usr/bin/env python3
"""
PART 3: FREE COMPANY NAME EXTRACTOR
Extract company names from working URLs using only free tools
Uses webpage content analysis, domain parsing, and pattern matching
"""

import urllib.request
import urllib.parse
import json
import csv
import re
import time
from datetime import datetime
from typing import List, Dict, Set, Optional
import sys

class FreeCompanyNameExtractor:
    def __init__(self):
        self.results = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.timeout = 15
        
        # Common company identifiers
        self.company_suffixes = [
            'GmbH', 'AG', 'Inc', 'Corp', 'Corporation', 'Ltd', 'Limited', 'LLC', 'S.A.', 'B.V.',
            'SAS', 'SARL', 'Oy', 'AB', 'AS', 'ApS', 'Kft', 'Sp. z o.o.', 'S.R.L.', 'S.L.',
            'Technologies', 'Technology', 'Solutions', 'Systems', 'Group', 'Company', 'Co.',
            'Healthcare', 'Health', 'Medical', 'Pharma', 'Pharmaceuticals', 'Biotech', 'Bio'
        ]
        
        # Patterns for company name extraction
        self.extraction_patterns = [
            # Meta tags
            r'<meta\s+(?:name|property)=["\'](?:og:site_name|application-name|author|company)["\']?\s+content=["\']([^"\']+)["\']',
            # Title patterns
            r'<title[^>]*>([^|•·\-]+)(?:\s*[\|•·\-].*)?</title>',
            # Schema.org organization
            r'"@type":\s*"Organization"[^}]*"name":\s*"([^"]+)"',
            # Copyright patterns
            r'©\s*(?:20\d{2}[-\s]?(?:20\d{2})?\s+)?([^,\n\r\.]+?)(?:\s+(?:GmbH|AG|Inc|Corp|Ltd|LLC|All Rights Reserved))',
            # About us patterns
            r'(?:about|company|who we are|our company).*?<h[1-6][^>]*>([^<]+)</h[1-6]>',
            # Navigation brand
            r'<(?:a|span|div)[^>]*class[^>]*(?:brand|logo|company)[^>]*>([^<]+)</(?:a|span|div)>',
        ]
        
        # German company name patterns
        self.german_patterns = [
            r'([A-ZÄÖÜ][a-zäöüß]*(?:\s+[A-ZÄÖÜ][a-zäöüß]*)*)\s+GmbH',
            r'([A-ZÄÖÜ][a-zäöüß]*(?:\s+[A-ZÄÖÜ][a-zäöüß]*)*)\s+AG',
            r'([A-ZÄÖÜ][a-zäöüß]*(?:\s+[A-ZÄÖÜ][a-zäöüß]*)*)\s+UG',
        ]
        
        # Words to exclude from company names
        self.exclude_words = {
            'privacy', 'policy', 'terms', 'conditions', 'cookie', 'legal', 'imprint', 'impressum',
            'contact', 'about', 'home', 'login', 'register', 'sign', 'welcome', 'dashboard',
            'blog', 'news', 'support', 'help', 'faq', 'careers', 'jobs', 'press', 'media'
        }
    
    def extract_page_content(self, url: str) -> str:
        """Extract full page content for analysis"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5,de;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            )
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                # Read more content for company name extraction
                content = response.read(50000).decode('utf-8', errors='ignore')
                return content
                
        except Exception as e:
            print(f"    ❌ Content extraction failed: {str(e)}")
            return ""
    
    def clean_company_name(self, name: str) -> str:
        """Clean and normalize company name"""
        if not name:
            return ""
        
        # Basic cleaning
        name = re.sub(r'<[^>]+>', '', name)  # Remove HTML tags
        name = re.sub(r'\s+', ' ', name)     # Normalize whitespace
        name = name.strip()
        
        # Remove common unwanted prefixes/suffixes
        name = re.sub(r'^(?:Welcome to|Home\s*[-\|]?\s*)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*[-\|•·]\s*.*$', '', name)  # Remove everything after separators
        
        # Remove if it's a common excluded word
        if name.lower() in self.exclude_words:
            return ""
        
        # Length checks
        if len(name) < 2 or len(name) > 100:
            return ""
        
        return name
    
    def extract_from_domain(self, url: str) -> str:
        """Extract company name from domain name"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path
            
            # Remove www and common prefixes
            domain = re.sub(r'^www\.', '', domain)
            domain = re.sub(r'^(?:app|api|portal|shop|store|my)\.', '', domain)
            
            # Get the main domain part
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                main_domain = domain_parts[0]
                
                # Convert to readable format
                # Handle camelCase and kebab-case
                name = re.sub(r'([a-z])([A-Z])', r'\1 \2', main_domain)
                name = re.sub(r'[-_]', ' ', name)
                name = name.title()
                
                return name
            
        except Exception:
            pass
        
        return ""
    
    def extract_from_title(self, content: str) -> List[str]:
        """Extract potential company names from page title"""
        candidates = []
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            
            # Try different title parsing strategies
            # Strategy 1: Before first separator
            parts = re.split(r'\s*[\|\-•·]\s*', title)
            if parts:
                candidates.append(self.clean_company_name(parts[0]))
            
            # Strategy 2: Look for company suffixes
            for suffix in self.company_suffixes:
                pattern = rf'([^|\-•·]*{re.escape(suffix)}[^|\-•·]*)'
                matches = re.finditer(pattern, title, re.IGNORECASE)
                for match in matches:
                    candidates.append(self.clean_company_name(match.group(1)))
        
        return [c for c in candidates if c]
    
    def extract_from_meta_tags(self, content: str) -> List[str]:
        """Extract company names from meta tags"""
        candidates = []
        
        # Common meta tags that contain company names
        meta_patterns = [
            r'<meta\s+name=["\'](?:author|company|application-name)["\']?\s+content=["\']([^"\']+)["\']',
            r'<meta\s+property=["\']og:site_name["\']?\s+content=["\']([^"\']+)["\']',
            r'<meta\s+name=["\']description["\']?\s+content=["\']([^"\']*(?:GmbH|AG|Inc|Corp|Ltd)[^"\']*)["\']',
        ]
        
        for pattern in meta_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                candidates.append(self.clean_company_name(match.group(1)))
        
        return [c for c in candidates if c]
    
    def extract_from_schema_org(self, content: str) -> List[str]:
        """Extract company names from Schema.org structured data"""
        candidates = []
        
        # Look for Organization schema
        org_patterns = [
            r'"@type":\s*"Organization"[^}]*"name":\s*"([^"]+)"',
            r'"@type":\s*"LocalBusiness"[^}]*"name":\s*"([^"]+)"',
            r'"@type":\s*"Corporation"[^}]*"name":\s*"([^"]+)"',
        ]
        
        for pattern in org_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                candidates.append(self.clean_company_name(match.group(1)))
        
        return [c for c in candidates if c]
    
    def extract_from_copyright(self, content: str) -> List[str]:
        """Extract company names from copyright notices"""
        candidates = []
        
        copyright_patterns = [
            r'©\s*(?:20\d{2}[-\s]?(?:20\d{2})?\s+)?([^,\n\r\.]+?)(?:\s+(?:GmbH|AG|Inc|Corp|Ltd|LLC|All Rights Reserved))',
            r'Copyright\s*(?:©|\(c\))?\s*(?:20\d{2}[-\s]?(?:20\d{2})?\s+)?([^,\n\r\.]+)',
            r'©\s*([^,\n\r\.]+?)\s+(?:20\d{2})',
        ]
        
        for pattern in copyright_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                name = self.clean_company_name(match.group(1))
                if name and not re.match(r'^\d+$', name):  # Not just numbers
                    candidates.append(name)
        
        return [c for c in candidates if c]
    
    def extract_from_headers(self, content: str) -> List[str]:
        """Extract company names from page headers"""
        candidates = []
        
        # Look in main headers
        header_patterns = [
            r'<h1[^>]*>([^<]+)</h1>',
            r'<h2[^>]*>([^<]+)</h2>',
            r'<(?:a|span|div)[^>]*class[^>]*(?:brand|logo|company|navbar-brand)[^>]*>([^<]+)</(?:a|span|div)>',
        ]
        
        for pattern in header_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                name = self.clean_company_name(match.group(1))
                # Only consider if it looks like a company name
                if name and len(name.split()) <= 4:  # Not too long
                    candidates.append(name)
        
        return [c for c in candidates if c]
    
    def score_company_name(self, name: str, url: str, content: str) -> float:
        """Score a company name candidate based on various factors"""
        if not name:
            return 0.0
        
        score = 0.0
        
        # Base score
        score += 1.0
        
        # Length preference (2-4 words ideal)
        word_count = len(name.split())
        if word_count == 1:
            score += 0.5
        elif 2 <= word_count <= 3:
            score += 2.0
        elif word_count == 4:
            score += 1.0
        else:
            score -= 1.0
        
        # Company suffix bonus
        for suffix in self.company_suffixes:
            if suffix.lower() in name.lower():
                score += 3.0
                break
        
        # Domain similarity bonus
        domain_name = self.extract_from_domain(url).lower()
        if domain_name and domain_name in name.lower():
            score += 2.0
        
        # Frequency in content
        name_count = content.lower().count(name.lower())
        score += min(name_count * 0.5, 3.0)  # Cap at 3.0
        
        # Capitalization pattern (proper names usually capitalized)
        if name[0].isupper():
            score += 1.0
        
        # Penalty for generic terms
        generic_terms = ['home', 'welcome', 'about', 'contact', 'login']
        if any(term in name.lower() for term in generic_terms):
            score -= 2.0
        
        return max(score, 0.0)
    
    def extract_company_name(self, url: str) -> Dict:
        """Extract company name from a single URL"""
        print(f"  🏢 Extracting company name from: {url}")
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'extraction_status': 'pending'
        }
        
        try:
            # Get page content
            content = self.extract_page_content(url)
            
            if not content:
                result['extraction_status'] = 'failed'
                result['company_name'] = ''
                result['method'] = 'content_unavailable'
                print(f"    ❌ No content available")
                return result
            
            # Collect all candidates
            all_candidates = []
            
            # Extract from different sources
            all_candidates.extend(self.extract_from_title(content))
            all_candidates.extend(self.extract_from_meta_tags(content))
            all_candidates.extend(self.extract_from_schema_org(content))
            all_candidates.extend(self.extract_from_copyright(content))
            all_candidates.extend(self.extract_from_headers(content))
            
            # Add domain-based name as fallback
            domain_name = self.extract_from_domain(url)
            if domain_name:
                all_candidates.append(domain_name)
            
            # Remove duplicates and empty names
            candidates = list(set([c for c in all_candidates if c]))
            
            if not candidates:
                result['extraction_status'] = 'no_candidates'
                result['company_name'] = domain_name or ''
                result['method'] = 'domain_fallback'
                print(f"    ⚠️  No candidates found, using domain: {domain_name}")
                return result
            
            # Score all candidates
            scored_candidates = []
            for candidate in candidates:
                score = self.score_company_name(candidate, url, content)
                scored_candidates.append((candidate, score))
            
            # Sort by score and pick the best
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_candidate, best_score = scored_candidates[0]
            
            result['extraction_status'] = 'success'
            result['company_name'] = best_candidate
            result['confidence_score'] = round(best_score, 2)
            result['all_candidates'] = [c for c, s in scored_candidates[:5]]  # Top 5
            result['method'] = 'content_analysis'
            
            print(f"    ✅ {best_candidate} (score: {best_score:.1f})")
            
        except Exception as e:
            result['extraction_status'] = 'error'
            result['error'] = str(e)
            result['company_name'] = self.extract_from_domain(url) or ''
            result['method'] = 'error_fallback'
            print(f"    ❌ Error: {str(e)}")
        
        return result
    
    def extract_company_names(self, urls: List[str]) -> List[Dict]:
        """Extract company names from a list of URLs"""
        print(f"🚀 PART 3: EXTRACTING COMPANY NAMES FROM {len(urls)} URLs")
        print("=" * 60)
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            result = self.extract_company_name(url)
            results.append(result)
            
            # Rate limiting to be respectful
            time.sleep(2)
            
            # Progress update every 10 URLs
            if i % 10 == 0:
                success_count = sum(1 for r in results if r.get('extraction_status') == 'success')
                print(f"\n  📊 Progress: {i}/{len(urls)} completed, {success_count} company names extracted")
        
        self.results = results
        return results
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate extraction summary"""
        total = len(results)
        
        # Count by status
        status_counts = {}
        successful_extractions = []
        failed_extractions = []
        
        for result in results:
            status = result.get('extraction_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status == 'success':
                successful_extractions.append({
                    'url': result['url'],
                    'company_name': result['company_name'],
                    'confidence_score': result.get('confidence_score', 0),
                    'method': result.get('method', 'unknown')
                })
            else:
                failed_extractions.append({
                    'url': result['url'],
                    'status': status,
                    'error': result.get('error', 'Unknown error')
                })
        
        # Confidence score analysis
        confidence_scores = [
            r.get('confidence_score', 0) 
            for r in results 
            if r.get('extraction_status') == 'success'
        ]
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        summary = {
            'total_urls_processed': total,
            'successful_extractions': len(successful_extractions),
            'failed_extractions': len(failed_extractions),
            'success_rate': round((len(successful_extractions) / total) * 100, 2) if total > 0 else 0,
            'status_counts': status_counts,
            'average_confidence_score': round(avg_confidence, 2),
            'extracted_companies': successful_extractions,
            'failed_urls': failed_extractions,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def save_results(self, results: List[Dict], summary: Dict, filename: str = "company_extraction_part3"):
        """Save extraction results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results (JSON)
        json_filename = f"{filename}_detailed_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': summary,
                'detailed_results': results
            }, f, indent=2, ensure_ascii=False)
        
        # Save company directory (CSV)
        companies_csv = f"company_directory_{timestamp}.csv"
        with open(companies_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['company_name', 'website_url', 'confidence_score', 'extraction_method', 'status'])
            
            for result in results:
                writer.writerow([
                    result.get('company_name', ''),
                    result['url'],
                    result.get('confidence_score', ''),
                    result.get('method', ''),
                    result.get('extraction_status', '')
                ])
        
        # Save successful extractions only (CSV)
        successful_csv = f"successful_companies_{timestamp}.csv"
        with open(successful_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['company_name', 'website_url', 'confidence_score'])
            
            for company in summary['extracted_companies']:
                writer.writerow([
                    company['company_name'],
                    company['url'],
                    company['confidence_score']
                ])
        
        return json_filename, companies_csv, successful_csv

def load_urls_from_part2(filename: str = None) -> List[str]:
    """Load working URLs from Part 2 results"""
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row['url'] for row in reader]
        except FileNotFoundError:
            print(f"❌ File {filename} not found")
            return []
    else:
        # Return sample if no file provided
        print("⚠️  No Part 2 file provided, using sample URLs for demonstration")
        return [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://ada.com',
            'https://doctolib.fr',
            'https://medgate.ch'
        ]

def main():
    """Main function for Part 3: Company Name Extraction"""
    print("🏢 PART 3: FREE COMPANY NAME EXTRACTION")
    print("=" * 60)
    print("Extracting company names using only FREE tools")
    print("Methods: Content analysis, meta tags, schema.org, domain parsing")
    print("")
    
    # Load URLs from Part 2 or use sample
    import sys
    if len(sys.argv) > 1:
        urls = load_urls_from_part2(sys.argv[1])
    else:
        # Try to find the most recent Part 2 working URLs file
        import glob
        part2_files = glob.glob("working_urls_*.csv")
        if part2_files:
            latest_file = max(part2_files)
            print(f"📂 Found Part 2 file: {latest_file}")
            urls = load_urls_from_part2(latest_file)
        else:
            print("📂 No Part 2 file found, loading sample URLs...")
            urls = load_urls_from_part2()
    
    if not urls:
        print("❌ No URLs to process!")
        return
    
    print(f"📊 Loaded {len(urls)} working URLs for company name extraction")
    
    # Initialize extractor
    extractor = FreeCompanyNameExtractor()
    
    # Extract company names
    results = extractor.extract_company_names(urls)
    
    # Generate summary
    summary = extractor.generate_summary(results)
    
    # Display results
    print("\n" + "=" * 60)
    print("🏢 EXTRACTION RESULTS")
    print("=" * 60)
    print(f"🎯 Total URLs processed: {summary['total_urls_processed']}")
    print(f"✅ Successful extractions: {summary['successful_extractions']}")
    print(f"❌ Failed extractions: {summary['failed_extractions']}")
    print(f"📈 Success rate: {summary['success_rate']}%")
    print(f"🎯 Average confidence score: {summary['average_confidence_score']}")
    
    print(f"\n📋 Status breakdown:")
    for status, count in summary['status_counts'].items():
        print(f"  • {status.replace('_', ' ').title()}: {count} URLs")
    
    # Show top companies
    if summary['extracted_companies']:
        print(f"\n🏆 TOP EXTRACTED COMPANIES:")
        sorted_companies = sorted(summary['extracted_companies'], 
                                key=lambda x: x['confidence_score'], reverse=True)
        for i, company in enumerate(sorted_companies[:10], 1):
            print(f"  {i:2d}. {company['company_name']} ({company['confidence_score']:.1f}) - {company['url']}")
    
    # Save results
    json_file, companies_csv, successful_csv = extractor.save_results(results, summary)
    
    print(f"\n💾 FILES SAVED:")
    print(f"  📊 Detailed results: {json_file}")
    print(f"  🏢 Company directory: {companies_csv}")
    print(f"  ✅ Successful companies: {successful_csv}")
    
    print(f"\n🎯 FINAL SUMMARY:")
    print(f"  ✅ Successfully extracted {summary['successful_extractions']} company names")
    print(f"  🏢 Created comprehensive company directory")
    print(f"  🆓 Used only free tools - no paid services required")
    print(f"  🎉 3-part process completed successfully!")
    
    return summary

if __name__ == "__main__":
    summary = main()