#!/usr/bin/env python3
"""
Deep Pharmaceutical Data Investigator
Comprehensive analysis and cleaning of pharmaceutical company datasets
"""

import json
import re
import socket
import ssl
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
import csv
import os

class DeepPharmaInvestigator:
    def __init__(self):
        self.verified_companies = self._load_verified_companies()
        self.fake_patterns = self._load_fake_patterns()
        self.tld_analysis = {}
        self.domain_analysis = {}
        self.investigation_log = []
        
    def _load_verified_companies(self) -> Dict:
        """Load comprehensive verified pharmaceutical companies database"""
        return {
            # Verified active companies with real websites
            'ferring.ch': {
                'name': 'Ferring Pharmaceuticals',
                'country': 'Switzerland',
                'website': 'https://ferring.ch',
                'wikipedia': 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals',
                'founded': 1950,
                'status': 'active',
                'headquarters': 'Saint-Prex, Switzerland',
                'verified_domains': ['ferring.ch', 'ferring.co.uk', 'ferring.com']
            },
            'ferring.co.uk': {
                'name': 'Ferring Pharmaceuticals UK',
                'country': 'United Kingdom',
                'website': 'https://ferring.co.uk',
                'wikipedia': 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals',
                'parent_company': 'Ferring Pharmaceuticals',
                'status': 'active'
            },
            'jazzpharma.com': {
                'name': 'Jazz Pharmaceuticals',
                'country': 'United States',
                'website': 'https://www.jazzpharma.com',
                'wikipedia': 'https://en.wikipedia.org/wiki/Jazz_Pharmaceuticals',
                'acquired_companies': ['GW Pharmaceuticals'],
                'status': 'active',
                'founded': 2003
            },
            'siegfried.ch': {
                'name': 'Siegfried Holding AG',
                'country': 'Switzerland',
                'website': 'https://www.siegfried.ch',
                'wikipedia': 'https://en.wikipedia.org/wiki/Siegfried_Holding',
                'acquired_operations': ['Knoll Pharmaceuticals operations'],
                'status': 'active'
            },
            'bene-arzneimittel.de': {
                'name': 'bene-Arzneimittel GmbH',
                'country': 'Germany',
                'website': 'https://www.bene-arzneimittel.de',
                'status': 'active',
                'founded': 1950
            },
            'crescentpharma.com': {
                'name': 'Crescent Pharma',
                'country': 'United Kingdom',
                'website': 'https://www.crescentpharma.com',
                'status': 'active'
            }
        }
    
    def _load_fake_patterns(self) -> List[str]:
        """Load patterns that indicate fake/generated domains"""
        return [
            # Wikipedia category-based fakes
            'medicinechestidiom',
            'pharmaceuticalcompaniesbycountry',
            'pharmaceuticalcompaniesof',
            'healthcarecompaniesof',
            'biotechnologycompaniesof',
            'medicaltechnologycompaniesof',
            'healthcarecompaniesby',
            
            # Generic topic-based fakes
            'drugsin',
            'pharmaceuticalindustryinthe',
            'biotechnologyinthe',
            'medicaltechnologyinthe',
            'healthcareindustryinthe',
            
            # List-based fakes
            'listofpharmaceuticalmanufacturers',
            'listofbiotechnologycompanies',
            'listofhealthcarecompanies',
            
            # Category-based fakes
            'medicalandhealthorganisations',
            'privatemedicinein',
            'healthclubsin',
            'pharmaceuticalindustry',
            'biotechnology',
            'medicaltechnology',
            
            # Geographic variations
            'companiesofgermany',
            'companiesoftheunitedkingdom',
            'companiesoffrance',
            'companiesofswitzerland',
            'companiesofsweden',
            'companiesofthenetherlands'
        ]
    
    def deep_url_analysis(self, url: str) -> Dict:
        """Perform comprehensive URL analysis"""
        analysis = {
            'original_url': url,
            'parsed_components': {},
            'domain_info': {},
            'tld_analysis': {},
            'pattern_analysis': {},
            'accessibility': {},
            'security_analysis': {},
            'content_hints': {},
            'fabrication_score': 0,
            'legitimacy_indicators': []
        }
        
        try:
            # Parse URL components
            parsed = urllib.parse.urlparse(url)
            analysis['parsed_components'] = {
                'scheme': parsed.scheme,
                'netloc': parsed.netloc,
                'path': parsed.path,
                'params': parsed.params,
                'query': parsed.query,
                'fragment': parsed.fragment
            }
            
            # Extract and analyze domain
            domain = parsed.netloc.lower().replace('www.', '')
            analysis['domain_info'] = self._analyze_domain(domain)
            
            # TLD analysis
            analysis['tld_analysis'] = self._analyze_tld(domain)
            
            # Pattern matching
            analysis['pattern_analysis'] = self._analyze_patterns(domain, url)
            
            # DNS and accessibility check
            analysis['accessibility'] = self._check_accessibility(url, domain)
            
            # Security analysis
            analysis['security_analysis'] = self._analyze_security(url)
            
            # Content analysis from URL structure
            analysis['content_hints'] = self._analyze_content_hints(url, domain)
            
            # Calculate fabrication score
            analysis['fabrication_score'] = self._calculate_fabrication_score(analysis)
            
            # Determine legitimacy indicators
            analysis['legitimacy_indicators'] = self._find_legitimacy_indicators(analysis)
            
        except Exception as e:
            analysis['error'] = str(e)
            analysis['fabrication_score'] = 100  # Assume fake if can't parse
        
        return analysis
    
    def _analyze_domain(self, domain: str) -> Dict:
        """Deep domain analysis"""
        parts = domain.split('.')
        
        return {
            'full_domain': domain,
            'subdomain': '.'.join(parts[:-2]) if len(parts) > 2 else '',
            'domain_name': parts[-2] if len(parts) >= 2 else domain,
            'tld': parts[-1] if len(parts) >= 2 else '',
            'length': len(domain),
            'part_count': len(parts),
            'has_numbers': bool(re.search(r'\d', domain)),
            'has_hyphens': '-' in domain,
            'suspicious_length': len(domain) > 50,  # Very long domains are suspicious
            'all_parts': parts
        }
    
    def _analyze_tld(self, domain: str) -> Dict:
        """Analyze top-level domain"""
        tld = domain.split('.')[-1] if '.' in domain else ''
        
        # Common legitimate pharmaceutical company TLDs
        legitimate_tlds = {
            'com': 'Commercial - most common for companies',
            'ch': 'Switzerland - legitimate for Swiss companies',
            'de': 'Germany - legitimate for German companies',
            'co.uk': 'United Kingdom - legitimate for UK companies',
            'uk': 'United Kingdom - legitimate for UK companies',
            'fr': 'France - legitimate for French companies',
            'nl': 'Netherlands - legitimate for Dutch companies',
            'se': 'Sweden - legitimate for Swedish companies',
            'org': 'Organization - less common for pharma companies',
            'eu': 'European Union - less common for individual companies'
        }
        
        # Suspicious TLD patterns for pharmaceutical companies
        suspicious_indicators = []
        if tld not in legitimate_tlds:
            suspicious_indicators.append(f"Unusual TLD: {tld}")
        
        return {
            'tld': tld,
            'is_legitimate': tld in legitimate_tlds,
            'description': legitimate_tlds.get(tld, 'Unknown or uncommon TLD'),
            'suspicious_indicators': suspicious_indicators
        }
    
    def _analyze_patterns(self, domain: str, url: str) -> Dict:
        """Analyze domain patterns for fake indicators"""
        fake_indicators = []
        legitimacy_indicators = []
        
        # Check against known fake patterns
        for pattern in self.fake_patterns:
            if pattern in domain.lower():
                fake_indicators.append(f"Contains fake pattern: {pattern}")
        
        # Check for Wikipedia category indicators in URL
        wikipedia_categories = [
            'Category:', 'category:', 'Medicine_chest_(idiom)',
            'List_of_', 'Drugs_in_', 'Companies_of_', 'Industry_in_'
        ]
        
        for category in wikipedia_categories:
            if category in url:
                fake_indicators.append(f"Wikipedia category reference: {category}")
        
        # Check for legitimate pharmaceutical patterns
        pharma_terms = ['pharma', 'pharmaceutical', 'medicine', 'health', 'bio']
        found_pharma_terms = [term for term in pharma_terms if term in domain.lower()]
        
        if found_pharma_terms:
            legitimacy_indicators.append(f"Contains pharma-related terms: {', '.join(found_pharma_terms)}")
        
        # Check for country-specific patterns that suggest fabrication
        country_fabrication_patterns = [
            'companiesof', 'pharmaceuticalcompaniesof', 'drugsin',
            'healthcareof', 'industryinthe'
        ]
        
        for pattern in country_fabrication_patterns:
            if pattern in domain.lower().replace('-', '').replace('_', ''):
                fake_indicators.append(f"Country-based fabrication pattern: {pattern}")
        
        return {
            'fake_indicators': fake_indicators,
            'legitimacy_indicators': legitimacy_indicators,
            'fake_score': len(fake_indicators),
            'legitimacy_score': len(legitimacy_indicators)
        }
    
    def _check_accessibility(self, url: str, domain: str) -> Dict:
        """Check domain accessibility and DNS resolution"""
        accessibility = {
            'dns_resolvable': False,
            'http_accessible': False,
            'https_accessible': False,
            'response_code': None,
            'dns_error': None,
            'connection_error': None,
            'ssl_valid': False
        }
        
        try:
            # DNS resolution check
            socket.gethostbyname(domain)
            accessibility['dns_resolvable'] = True
        except socket.gaierror as e:
            accessibility['dns_error'] = str(e)
        
        # HTTP accessibility check (basic)
        if accessibility['dns_resolvable']:
            for scheme in ['https', 'http']:
                test_url = f"{scheme}://{domain}"
                try:
                    # Simple HEAD request with timeout
                    req = urllib.request.Request(test_url, method='HEAD')
                    req.add_header('User-Agent', 'Mozilla/5.0 (compatible; DataValidator/1.0)')
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        accessibility['response_code'] = response.getcode()
                        if scheme == 'https':
                            accessibility['https_accessible'] = True
                            accessibility['ssl_valid'] = True
                        else:
                            accessibility['http_accessible'] = True
                        break
                        
                except Exception as e:
                    accessibility['connection_error'] = str(e)
        
        return accessibility
    
    def _analyze_security(self, url: str) -> Dict:
        """Analyze security aspects of the URL"""
        parsed = urllib.parse.urlparse(url)
        
        return {
            'uses_https': parsed.scheme == 'https',
            'has_suspicious_path': len(parsed.path) > 100,
            'has_query_params': bool(parsed.query),
            'security_score': 1 if parsed.scheme == 'https' else 0
        }
    
    def _analyze_content_hints(self, url: str, domain: str) -> Dict:
        """Analyze URL for content hints"""
        hints = {
            'likely_company_site': False,
            'likely_wikipedia': False,
            'likely_category_page': False,
            'content_indicators': []
        }
        
        # Check for Wikipedia indicators
        if 'wikipedia.org' in url or 'wiki' in domain:
            hints['likely_wikipedia'] = True
            hints['content_indicators'].append('Wikipedia reference')
        
        # Check for category page indicators
        if 'Category:' in url or 'category' in url.lower():
            hints['likely_category_page'] = True
            hints['content_indicators'].append('Category page reference')
        
        # Check for company site indicators
        company_indicators = ['.com', '.co.', 'pharma', 'healthcare', 'medical']
        if any(indicator in domain.lower() for indicator in company_indicators):
            hints['likely_company_site'] = True
            hints['content_indicators'].append('Company site indicators')
        
        return hints
    
    def _calculate_fabrication_score(self, analysis: Dict) -> int:
        """Calculate overall fabrication likelihood score (0-100)"""
        score = 0
        
        # Pattern analysis weight (40 points max)
        pattern_data = analysis.get('pattern_analysis', {})
        fake_score = pattern_data.get('fake_score', 0)
        score += min(fake_score * 15, 40)
        
        # Content hints weight (20 points max)
        content_hints = analysis.get('content_hints', {})
        if content_hints.get('likely_category_page'):
            score += 20
        elif content_hints.get('likely_wikipedia'):
            score += 15
        
        # Accessibility weight (20 points max)
        accessibility = analysis.get('accessibility', {})
        if not accessibility.get('dns_resolvable'):
            score += 20
        elif not accessibility.get('https_accessible') and not accessibility.get('http_accessible'):
            score += 15
        
        # Domain analysis weight (20 points max)
        domain_info = analysis.get('domain_info', {})
        if domain_info.get('suspicious_length'):
            score += 10
        if domain_info.get('length', 0) > 60:
            score += 10
        
        return min(score, 100)
    
    def _find_legitimacy_indicators(self, analysis: Dict) -> List[str]:
        """Find indicators that suggest legitimacy"""
        indicators = []
        
        domain = analysis.get('domain_info', {}).get('full_domain', '')
        
        # Check against verified companies
        if domain in self.verified_companies:
            indicators.append(f"Verified company: {self.verified_companies[domain]['name']}")
        
        # Check accessibility
        accessibility = analysis.get('accessibility', {})
        if accessibility.get('https_accessible'):
            indicators.append("HTTPS accessible")
        if accessibility.get('dns_resolvable'):
            indicators.append("DNS resolvable")
        
        # Check TLD legitimacy
        tld_analysis = analysis.get('tld_analysis', {})
        if tld_analysis.get('is_legitimate'):
            indicators.append(f"Legitimate TLD: {tld_analysis.get('tld')}")
        
        # Check for pharmaceutical terms
        pattern_analysis = analysis.get('pattern_analysis', {})
        legitimacy_score = pattern_analysis.get('legitimacy_score', 0)
        if legitimacy_score > 0:
            indicators.append(f"Contains pharmaceutical terms")
        
        return indicators
    
    def investigate_wikipedia_reference(self, wikipedia_url: str) -> Dict:
        """Deep investigation of Wikipedia references"""
        investigation = {
            'url': wikipedia_url,
            'type': 'unknown',
            'legitimacy': 'unknown',
            'indicators': [],
            'analysis': {}
        }
        
        if not wikipedia_url or 'wikipedia.org' not in wikipedia_url:
            investigation['type'] = 'not_wikipedia'
            investigation['legitimacy'] = 'suspicious'
            investigation['indicators'].append('Not a valid Wikipedia URL')
            return investigation
        
        # Analyze Wikipedia URL structure
        if 'Category:' in wikipedia_url:
            investigation['type'] = 'category_page'
            investigation['legitimacy'] = 'fake_company_reference'
            investigation['indicators'].append('Wikipedia category page, not a company article')
        
        elif 'Medicine_chest_(idiom)' in wikipedia_url:
            investigation['type'] = 'idiom_page'
            investigation['legitimacy'] = 'fake_company_reference'
            investigation['indicators'].append('English idiom page, not a pharmaceutical company')
        
        elif any(term in wikipedia_url for term in ['List_of_', 'Drugs_in_', 'Industry_in_']):
            investigation['type'] = 'list_page'
            investigation['legitimacy'] = 'fake_company_reference'
            investigation['indicators'].append('Wikipedia list page, not a specific company')
        
        else:
            # Could be a legitimate company page
            investigation['type'] = 'potential_company_page'
            investigation['legitimacy'] = 'needs_verification'
            investigation['indicators'].append('Potential legitimate company Wikipedia page')
        
        return investigation
    
    def comprehensive_analysis(self, dataset: List[Dict]) -> Dict:
        """Perform comprehensive analysis of entire dataset"""
        results = {
            'total_entries': len(dataset),
            'verified_companies': [],
            'fabricated_entries': [],
            'suspicious_entries': [],
            'legitimate_candidates': [],
            'analysis_summary': {},
            'patterns_detected': {},
            'recommendations': []
        }
        
        print(f"\n🔍 DEEP INVESTIGATION: Analyzing {len(dataset)} entries...")
        print("=" * 70)
        
        for i, entry in enumerate(dataset, 1):
            url = entry.get('url', '').strip()
            wikipedia_url = entry.get('wikipedia_page', '').strip()
            
            if not url:
                continue
            
            print(f"\n[{i}/{len(dataset)}] Investigating: {url}")
            
            # Deep URL analysis
            url_analysis = self.deep_url_analysis(url)
            
            # Wikipedia reference investigation
            wiki_investigation = self.investigate_wikipedia_reference(wikipedia_url)
            
            # Combined analysis
            fabrication_score = url_analysis.get('fabrication_score', 0)
            
            entry_result = {
                'original_entry': entry,
                'url_analysis': url_analysis,
                'wikipedia_investigation': wiki_investigation,
                'fabrication_score': fabrication_score,
                'classification': self._classify_entry(fabrication_score, url_analysis, wiki_investigation)
            }
            
            # Categorize based on analysis
            if fabrication_score >= 80:
                results['fabricated_entries'].append(entry_result)
                print(f"  ❌ FABRICATED (Score: {fabrication_score})")
            elif fabrication_score >= 50:
                results['suspicious_entries'].append(entry_result)
                print(f"  ⚠️  SUSPICIOUS (Score: {fabrication_score})")
            elif url_analysis.get('domain_info', {}).get('full_domain') in self.verified_companies:
                results['verified_companies'].append(entry_result)
                print(f"  ✅ VERIFIED COMPANY")
            else:
                results['legitimate_candidates'].append(entry_result)
                print(f"  🔍 NEEDS VERIFICATION (Score: {fabrication_score})")
        
        # Generate analysis summary
        results['analysis_summary'] = self._generate_analysis_summary(results)
        
        # Detect patterns
        results['patterns_detected'] = self._detect_patterns(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _classify_entry(self, fabrication_score: int, url_analysis: Dict, wiki_investigation: Dict) -> str:
        """Classify entry based on all analysis"""
        if fabrication_score >= 80:
            return 'FABRICATED'
        elif wiki_investigation.get('legitimacy') == 'fake_company_reference':
            return 'FAKE_REFERENCE'
        elif url_analysis.get('domain_info', {}).get('full_domain') in self.verified_companies:
            return 'VERIFIED'
        elif fabrication_score >= 50:
            return 'SUSPICIOUS'
        else:
            return 'NEEDS_VERIFICATION'
    
    def _generate_analysis_summary(self, results: Dict) -> Dict:
        """Generate comprehensive analysis summary"""
        total = results['total_entries']
        
        return {
            'total_analyzed': total,
            'verified_count': len(results['verified_companies']),
            'fabricated_count': len(results['fabricated_entries']),
            'suspicious_count': len(results['suspicious_entries']),
            'candidates_count': len(results['legitimate_candidates']),
            'data_quality_percentage': (len(results['verified_companies']) / total * 100) if total > 0 else 0,
            'fabrication_percentage': (len(results['fabricated_entries']) / total * 100) if total > 0 else 0
        }
    
    def _detect_patterns(self, results: Dict) -> Dict:
        """Detect patterns in fabricated entries"""
        patterns = {
            'fake_domain_patterns': {},
            'wikipedia_abuse_patterns': {},
            'tld_abuse_patterns': {},
            'common_fabrication_methods': []
        }
        
        # Analyze fabricated entries for patterns
        for entry in results['fabricated_entries']:
            domain = entry['url_analysis'].get('domain_info', {}).get('full_domain', '')
            
            # Count fake patterns
            for pattern in self.fake_patterns:
                if pattern in domain:
                    patterns['fake_domain_patterns'][pattern] = patterns['fake_domain_patterns'].get(pattern, 0) + 1
            
            # Wikipedia abuse patterns
            wiki_type = entry['wikipedia_investigation'].get('type', '')
            if wiki_type != 'unknown':
                patterns['wikipedia_abuse_patterns'][wiki_type] = patterns['wikipedia_abuse_patterns'].get(wiki_type, 0) + 1
        
        return patterns
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        summary = results['analysis_summary']
        
        if summary['fabrication_percentage'] > 80:
            recommendations.append("🚨 CRITICAL: Over 80% of entries are fabricated. Complete dataset review required.")
        elif summary['fabrication_percentage'] > 50:
            recommendations.append("⚠️  WARNING: Over 50% of entries are fabricated. Significant cleanup needed.")
        
        if summary['data_quality_percentage'] < 10:
            recommendations.append("📊 DATA QUALITY: Less than 10% verified companies. Consider rebuilding dataset from official sources.")
        
        if len(results['verified_companies']) > 0:
            recommendations.append(f"✅ SALVAGEABLE: {len(results['verified_companies'])} verified companies can be retained.")
        
        recommendations.append("🔍 VERIFICATION: All 'NEEDS_VERIFICATION' entries should be manually checked against official business registries.")
        recommendations.append("🗑️  CLEANUP: Remove all entries classified as 'FABRICATED' or 'FAKE_REFERENCE'.")
        
        return recommendations
    
    def generate_detailed_report(self, results: Dict) -> str:
        """Generate comprehensive investigation report"""
        report_lines = []
        
        report_lines.append("=" * 80)
        report_lines.append("DEEP PHARMACEUTICAL DATA INVESTIGATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Executive Summary
        summary = results['analysis_summary']
        report_lines.append("📊 EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(f"Total entries analyzed: {summary['total_analyzed']}")
        report_lines.append(f"Verified companies: {summary['verified_count']} ({summary['data_quality_percentage']:.1f}%)")
        report_lines.append(f"Fabricated entries: {summary['fabricated_count']} ({summary['fabrication_percentage']:.1f}%)")
        report_lines.append(f"Suspicious entries: {summary['suspicious_count']}")
        report_lines.append(f"Needs verification: {summary['candidates_count']}")
        report_lines.append("")
        
        # Verified Companies
        if results['verified_companies']:
            report_lines.append("✅ VERIFIED PHARMACEUTICAL COMPANIES")
            report_lines.append("-" * 40)
            for entry in results['verified_companies']:
                domain = entry['url_analysis']['domain_info']['full_domain']
                company_info = self.verified_companies.get(domain, {})
                name = company_info.get('name', 'Unknown')
                country = company_info.get('country', 'Unknown')
                report_lines.append(f"  • {name} ({country}) - {domain}")
            report_lines.append("")
        
        # Top Fabrication Patterns
        patterns = results['patterns_detected']
        if patterns['fake_domain_patterns']:
            report_lines.append("🚫 TOP FABRICATION PATTERNS DETECTED")
            report_lines.append("-" * 40)
            sorted_patterns = sorted(patterns['fake_domain_patterns'].items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:10]:
                report_lines.append(f"  • {pattern}: {count} variations")
            report_lines.append("")
        
        # Wikipedia Abuse Analysis
        if patterns['wikipedia_abuse_patterns']:
            report_lines.append("📚 WIKIPEDIA REFERENCE ABUSE")
            report_lines.append("-" * 40)
            for abuse_type, count in patterns['wikipedia_abuse_patterns'].items():
                report_lines.append(f"  • {abuse_type}: {count} instances")
            report_lines.append("")
        
        # Recommendations
        report_lines.append("💡 RECOMMENDATIONS")
        report_lines.append("-" * 40)
        for recommendation in results['recommendations']:
            report_lines.append(f"  {recommendation}")
        report_lines.append("")
        
        # Sample Fabricated Entries
        if results['fabricated_entries']:
            report_lines.append("🔍 SAMPLE FABRICATED ENTRIES")
            report_lines.append("-" * 40)
            for entry in results['fabricated_entries'][:5]:
                url = entry['original_entry']['url']
                score = entry['fabrication_score']
                classification = entry['classification']
                report_lines.append(f"  • {url} (Score: {score}, {classification})")
            if len(results['fabricated_entries']) > 5:
                report_lines.append(f"  ... and {len(results['fabricated_entries']) - 5} more fabricated entries")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_investigation_results(self, results: Dict, base_filename: str = "pharma_investigation"):
        """Save comprehensive investigation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed report
        report_filename = f"{base_filename}_report_{timestamp}.txt"
        report = self.generate_detailed_report(results)
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save verified companies CSV
        if results['verified_companies']:
            verified_filename = f"{base_filename}_verified_{timestamp}.csv"
            with open(verified_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['company_name', 'country', 'website', 'verification_status', 'wikipedia_page'])
                
                for entry in results['verified_companies']:
                    domain = entry['url_analysis']['domain_info']['full_domain']
                    company_info = self.verified_companies.get(domain, {})
                    writer.writerow([
                        company_info.get('name', 'Unknown'),
                        company_info.get('country', 'Unknown'),
                        company_info.get('website', entry['original_entry']['url']),
                        'Verified Active',
                        company_info.get('wikipedia', entry['original_entry'].get('wikipedia_page', ''))
                    ])
        
        # Save fabricated entries analysis
        fabricated_filename = f"{base_filename}_fabricated_{timestamp}.csv"
        with open(fabricated_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['original_url', 'fabrication_score', 'classification', 'fake_patterns', 'wikipedia_abuse'])
            
            for entry in results['fabricated_entries']:
                url = entry['original_entry']['url']
                score = entry['fabrication_score']
                classification = entry['classification']
                
                # Extract fake indicators
                fake_indicators = entry['url_analysis'].get('pattern_analysis', {}).get('fake_indicators', [])
                wiki_type = entry['wikipedia_investigation'].get('type', '')
                
                writer.writerow([url, score, classification, '; '.join(fake_indicators), wiki_type])
        
        print(f"\n💾 INVESTIGATION RESULTS SAVED:")
        print(f"  📋 Detailed Report: {report_filename}")
        if results['verified_companies']:
            print(f"  ✅ Verified Companies: {verified_filename}")
        print(f"  ❌ Fabricated Analysis: {fabricated_filename}")

def main():
    """Main investigation function"""
    # Sample dataset from your original data
    dataset = [
        {'url': 'https://www.knollpharmaceuticals.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Germany', 'country': 'Germany', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Knoll_Pharmaceuticals'},
        {'url': 'https://www.medicinechestidiom.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Germany', 'country': 'Germany', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Medicine_chest_(idiom)'},
        {'url': 'https://www.pharmaceuticalcompaniesbycountry.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Germany', 'country': 'Germany', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_by_country'},
        {'url': 'https://www.ferringpharmaceuticals.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Switzerland', 'country': 'Switzerland', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals'},
        {'url': 'https://ferring.ch', 'source': 'Official Website', 'category': 'Pharmaceutical company', 'country': 'Switzerland', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Ferring_Pharmaceuticals'},
        {'url': 'https://www.gwpharmaceuticals.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_the_United_Kingdom', 'country': 'United Kingdom', 'wikipedia_page': 'https://en.wikipedia.org/wiki/GW_Pharmaceuticals'},
        {'url': 'https://www.drugsingermany.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Germany', 'country': 'Germany', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Category:Drugs_in_Germany'},
        {'url': 'https://www.healthcarecompaniesofgermany.com', 'source': 'Wikipedia', 'category': 'Category:Pharmaceutical_companies_of_Germany', 'country': 'Germany', 'wikipedia_page': 'https://en.wikipedia.org/wiki/Category:Health_care_companies_of_Germany'}
    ]
    
    # Initialize investigator
    investigator = DeepPharmaInvestigator()
    
    # Perform comprehensive analysis
    results = investigator.comprehensive_analysis(dataset)
    
    # Generate and display report
    print(investigator.generate_detailed_report(results))
    
    # Save results
    investigator.save_investigation_results(results)
    
    return results

if __name__ == "__main__":
    results = main()