#!/usr/bin/env python3
"""
Healthcare Startup Discovery System - Demo

This demo script shows the key functionality of the system
without requiring all dependencies to be installed.
"""

import re
import json
from typing import List, Dict, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse


class SimpleHealthcareFilter:
    """Simplified healthcare keyword filter for demo purposes"""
    
    def __init__(self):
        self.healthcare_keywords = {
            # English terms
            'healthcare', 'health tech', 'healthtech', 'digital health',
            'medical technology', 'medtech', 'biotech', 'biotechnology',
            'telemedicine', 'telehealth', 'mhealth', 'ehealth',
            'pharmaceutical', 'pharma', 'clinical', 'medical device',
            'diagnostics', 'therapeutics', 'patient care', 'wellness',
            'fitness', 'nutrition', 'mental health', 'therapy',
            'hospital', 'clinic', 'doctor', 'physician',
            
            # German terms
            'gesundheitswesen', 'gesundheit', 'medizin', 'medizinisch',
            'gesundheitstechnik', 'medizintechnik', 'biotechnik',
            'telemedizin', 'digitale gesundheit', 'e-health',
            'pharmazie', 'pharmazeutisch', 'klinik', 'krankenhaus',
            'arzt', 'ärztin', 'patient', 'therapie', 'behandlung'
        }
        
        self.country_keywords = {
            'germany', 'deutschland', 'german', 'deutsch',
            'austria', 'österreich', 'switzerland', 'schweiz',
            'netherlands', 'niederlande', 'belgium', 'belgien',
            'france', 'frankreich', 'italy', 'italien'
        }
    
    def analyze_text(self, text: str, url: str = "") -> Tuple[float, Set[str], List[str]]:
        """
        Analyze text for healthcare relevance
        
        Returns:
            Tuple of (confidence_score, matched_keywords, detected_countries)
        """
        text_lower = text.lower()
        matched_keywords = set()
        detected_countries = []
        
        # Find healthcare keywords
        for keyword in self.healthcare_keywords:
            if keyword in text_lower:
                matched_keywords.add(keyword)
        
        # Find country mentions
        for country in self.country_keywords:
            if country in text_lower:
                detected_countries.append(country)
        
        # Calculate confidence score
        keyword_score = len(matched_keywords) / 10  # Normalize
        url_bonus = 0.1 if any(k in url.lower() for k in ['health', 'med', 'bio']) else 0
        country_bonus = 0.1 if detected_countries else 0
        
        confidence = min(1.0, keyword_score + url_bonus + country_bonus)
        
        return confidence, matched_keywords, detected_countries


class SimpleURLValidator:
    """Simplified URL validator for demo purposes"""
    
    def __init__(self):
        self.excluded_domains = {
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
            'youtube.com', 'pinterest.com', 'wikipedia.org', 'google.com'
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not excluded"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check against excluded domains
            for excluded in self.excluded_domains:
                if excluded in domain:
                    return False
            
            return True
        except:
            return False
    
    def clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        if url.endswith('/'):
            url = url[:-1]
        
        return url


class MockCompany:
    """Mock company data for demonstration"""
    
    def __init__(self, name: str, url: str, description: str):
        self.name = name
        self.url = url
        self.description = description
        self.discovered_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'discovered_at': self.discovered_at.isoformat()
        }


def demo_healthcare_filtering():
    """Demonstrate healthcare keyword filtering"""
    print("\n" + "="*60)
    print("HEALTHCARE KEYWORD FILTERING DEMO")
    print("="*60)
    
    filter_engine = SimpleHealthcareFilter()
    
    test_companies = [
        {
            'name': 'HealthTech Solutions',
            'description': 'We develop digital health platforms for hospitals and clinics.',
            'url': 'https://healthtech-solutions.com'
        },
        {
            'name': 'German MedTech GmbH',
            'description': 'Medizintechnik Unternehmen für Diagnostik und Therapie.',
            'url': 'https://german-medtech.de'
        },
        {
            'name': 'TechCorp Inc',
            'description': 'Software development company focusing on enterprise solutions.',
            'url': 'https://techcorp.com'
        },
        {
            'name': 'BioInnovate',
            'description': 'Biotechnology startup developing precision medicine solutions.',
            'url': 'https://bioinnovate.eu'
        },
        {
            'name': 'Digital Wellness',
            'description': 'Mental health app connecting patients with therapists.',
            'url': 'https://digital-wellness.com'
        }
    ]
    
    print("\nAnalyzing companies for healthcare relevance:\n")
    
    healthcare_companies = []
    
    for company in test_companies:
        text = f"{company['name']} {company['description']}"
        confidence, keywords, countries = filter_engine.analyze_text(text, company['url'])
        
        print(f"Company: {company['name']}")
        print(f"Confidence: {confidence:.3f}")
        print(f"Keywords: {', '.join(sorted(keywords)) if keywords else 'None'}")
        print(f"Countries: {', '.join(countries) if countries else 'None'}")
        print(f"Healthcare relevant: {'✓' if confidence >= 0.3 else '✗'}")
        print("-" * 40)
        
        if confidence >= 0.3:
            healthcare_companies.append({
                **company,
                'confidence': confidence,
                'keywords': list(keywords),
                'countries': countries
            })
    
    print(f"\nSummary: {len(healthcare_companies)}/{len(test_companies)} companies identified as healthcare-related")
    return healthcare_companies


def demo_url_validation():
    """Demonstrate URL validation and cleaning"""
    print("\n" + "="*60)
    print("URL VALIDATION DEMO")
    print("="*60)
    
    validator = SimpleURLValidator()
    
    test_urls = [
        'healthtech-startup.com',
        'https://medical-devices.de',
        'http://facebook.com/some-company',
        'https://biotech-innovations.eu/about',
        'linkedin.com/company/medtech',
        'https://digital-health-solutions.com',
        'invalid-url',
        'https://german-healthcare.de/products'
    ]
    
    print("\nValidating and cleaning URLs:\n")
    
    valid_urls = []
    
    for url in test_urls:
        cleaned_url = validator.clean_url(url)
        is_valid = validator.is_valid_url(cleaned_url)
        
        print(f"Original: {url}")
        print(f"Cleaned:  {cleaned_url}")
        print(f"Valid:    {'✓' if is_valid else '✗'}")
        print("-" * 40)
        
        if is_valid:
            valid_urls.append(cleaned_url)
    
    print(f"\nSummary: {len(valid_urls)}/{len(test_urls)} URLs are valid")
    return valid_urls


def demo_output_generation(companies: List[Dict]):
    """Demonstrate output file generation"""
    print("\n" + "="*60)
    print("OUTPUT GENERATION DEMO")
    print("="*60)
    
    # Generate CSV content
    csv_content = "Company Name,Website URL,Description,Confidence Score,Keywords Matched\n"
    
    for company in companies:
        keywords_str = '; '.join(company.get('keywords', []))
        csv_content += f'"{company["name"]}","{company["url"]}","{company["description"]}",{company["confidence"]:.3f},"{keywords_str}"\n'
    
    # Generate JSON content
    json_content = {
        'session_info': {
            'generated_at': datetime.now().isoformat(),
            'total_companies': len(companies),
            'demo_mode': True
        },
        'companies': companies
    }
    
    print("Sample CSV output:")
    print("-" * 20)
    print(csv_content[:500] + "..." if len(csv_content) > 500 else csv_content)
    
    print("\nSample JSON output:")
    print("-" * 20)
    print(json.dumps(json_content, indent=2)[:500] + "..." if len(json.dumps(json_content, indent=2)) > 500 else json.dumps(json_content, indent=2))
    
    # Write actual files (commented out for demo)
    # with open('demo_output.csv', 'w') as f:
    #     f.write(csv_content)
    # 
    # with open('demo_output.json', 'w') as f:
    #     json.dump(json_content, f, indent=2)
    
    print(f"\nOutput would contain {len(companies)} healthcare companies")


def demo_search_queries():
    """Demonstrate search query examples"""
    print("\n" + "="*60)
    print("SEARCH QUERY EXAMPLES")
    print("="*60)
    
    search_queries = [
        "deutsche healthcare startups",
        "medizintechnik startups deutschland",
        "digital health companies europe",
        "biotech startups germany austria",
        "telemedicine platforms european",
        '"medical device" startup germany',
        '"digital health" company founded 2020..2024',
        "healthcare AI startups europe"
    ]
    
    print("\nExample search queries for discovering healthcare companies:\n")
    
    for i, query in enumerate(search_queries, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\nThese queries would be used across multiple search engines")
    print("to discover healthcare startup URLs systematically.")


def main():
    """Main demo function"""
    print("Healthcare Startup Discovery System - Demo")
    print("=" * 50)
    print("\nThis demo shows the key functionality of the system:")
    print("1. Healthcare keyword filtering and relevance scoring")
    print("2. URL validation and cleaning")
    print("3. Output generation in CSV and JSON formats")
    print("4. Search query examples")
    
    try:
        # Run demos
        healthcare_companies = demo_healthcare_filtering()
        valid_urls = demo_url_validation()
        demo_output_generation(healthcare_companies)
        demo_search_queries()
        
        # Summary
        print("\n" + "="*60)
        print("DEMO SUMMARY")
        print("="*60)
        print(f"✓ Healthcare filtering: {len(healthcare_companies)} relevant companies identified")
        print(f"✓ URL validation: {len(valid_urls)} valid URLs processed")
        print("✓ Output generation: CSV and JSON formats demonstrated")
        print("✓ Search queries: 8 example queries shown")
        
        print("\n" + "="*60)
        print("FULL SYSTEM CAPABILITIES")
        print("="*60)
        print("The complete system includes:")
        print("• Asynchronous scraping with aiohttp")
        print("• Advanced NLP processing with NLTK and scikit-learn")
        print("• Multiple data sources (directories, search engines, news)")
        print("• Comprehensive URL validation and deduplication")
        print("• Rate limiting and robots.txt compliance")
        print("• Error handling and retry logic")
        print("• Detailed logging and progress tracking")
        print("• Configurable filtering and output options")
        
        print(f"\nTo use the full system:")
        print("1. Run: chmod +x install.sh && ./install.sh")
        print("2. Activate virtual environment: source venv/bin/activate")
        print("3. Run discovery: python main.py")
        
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    main()