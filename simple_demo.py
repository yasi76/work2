#!/usr/bin/env python3
"""
Healthcare Startup Discovery System - Simple Demo
Works without any external dependencies for immediate testing.
"""

import re
import json
from typing import List, Dict, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse


def simple_healthcare_check(text: str) -> Tuple[float, List[str]]:
    """Simple healthcare keyword checker without dependencies"""
    
    healthcare_keywords = [
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
    ]
    
    text_lower = text.lower()
    matched_keywords = []
    
    for keyword in healthcare_keywords:
        if keyword in text_lower:
            matched_keywords.append(keyword)
    
    confidence = min(1.0, len(matched_keywords) / 5.0)  # Normalize to 0-1
    return confidence, matched_keywords


def simple_url_check(url: str) -> bool:
    """Simple URL validation without dependencies"""
    if not url:
        return False
    
    # Basic URL format check
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
    except Exception:
        return False
    
    # Check for excluded domains
    excluded_domains = [
        'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
        'youtube.com', 'pinterest.com', 'wikipedia.org', 'google.com'
    ]
    
    for domain in excluded_domains:
        if domain in url.lower():
            return False
    
    return True


def demo_healthcare_detection():
    """Demonstrate healthcare detection functionality"""
    print("=" * 60)
    print("HEALTHCARE STARTUP DETECTION DEMO")
    print("=" * 60)
    
    test_companies = [
        {
            'name': 'HealthTech Solutions GmbH',
            'description': 'We develop digital health platforms for hospitals and clinics in Germany.',
            'url': 'https://healthtech-solutions.de'
        },
        {
            'name': 'MedTech Innovations',
            'description': 'Medizintechnik Unternehmen für Diagnostik und Therapie in Deutschland.',
            'url': 'https://medtech-innovations.com'
        },
        {
            'name': 'TechCorp Software',
            'description': 'Enterprise software development company for business solutions.',
            'url': 'https://techcorp-software.com'
        },
        {
            'name': 'BioInnovate Europe',
            'description': 'Biotechnology startup developing precision medicine solutions.',
            'url': 'https://bioinnovate.eu'
        },
        {
            'name': 'Digital Wellness App',
            'description': 'Mental health platform connecting patients with therapists.',
            'url': 'https://digital-wellness.de'
        },
        {
            'name': 'CareTech Solutions',
            'description': 'Telemedicine and eHealth solutions for European healthcare providers.',
            'url': 'https://caretech-solutions.eu'
        }
    ]
    
    print("\nAnalyzing companies for healthcare relevance:\n")
    
    healthcare_companies = []
    
    for company in test_companies:
        combined_text = f"{company['name']} {company['description']}"
        confidence, keywords = simple_healthcare_check(combined_text)
        is_valid_url = simple_url_check(company['url'])
        
        print(f"Company: {company['name']}")
        print(f"URL: {company['url']}")
        print(f"Description: {company['description'][:60]}...")
        print(f"Healthcare Confidence: {confidence:.3f}")
        print(f"Keywords Found: {', '.join(keywords[:3]) + ('...' if len(keywords) > 3 else '')}")
        print(f"Valid URL: {'✓' if is_valid_url else '✗'}")
        print(f"Healthcare Relevant: {'✓' if confidence >= 0.2 else '✗'}")
        print("-" * 50)
        
        if confidence >= 0.2 and is_valid_url:
            healthcare_companies.append({
                **company,
                'confidence': confidence,
                'keywords': keywords
            })
    
    print(f"\nSUMMARY:")
    print(f"Total companies analyzed: {len(test_companies)}")
    print(f"Healthcare companies found: {len(healthcare_companies)}")
    print(f"Success rate: {len(healthcare_companies)/len(test_companies)*100:.1f}%")
    
    return healthcare_companies


def demo_output_generation(companies: List[Dict]):
    """Demonstrate output file generation"""
    print("\n" + "=" * 60)
    print("OUTPUT GENERATION DEMO")
    print("=" * 60)
    
    # Generate CSV-style output
    print("\nGenerated CSV format output:")
    print("-" * 40)
    print("Company Name,Website URL,Confidence,Keywords")
    
    for company in companies:
        keywords_str = '; '.join(company['keywords'][:3])
        print(f'"{company["name"]}","{company["url"]}",{company["confidence"]:.3f},"{keywords_str}"')
    
    # Generate JSON-style output
    json_output = {
        'session_info': {
            'generated_at': datetime.now().isoformat(),
            'total_companies': len(companies),
            'demo_mode': True
        },
        'companies': companies
    }
    
    print(f"\nGenerated JSON format output (sample):")
    print("-" * 40)
    print(json.dumps(json_output, indent=2)[:400] + "...")
    
    print(f"\nOutput would be saved to files:")
    print(f"- healthcare_startups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    print(f"- healthcare_startups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")


def demo_search_queries():
    """Show example search queries"""
    print("\n" + "=" * 60)
    print("SEARCH QUERY EXAMPLES")
    print("=" * 60)
    
    search_queries = [
        "deutsche healthcare startups",
        "medizintechnik unternehmen deutschland", 
        "digital health companies germany",
        "biotech startups europe",
        "telemedicine platforms german",
        '"medical device" company deutschland',
        "gesundheitstechnik startup österreich",
        "healthcare AI companies schweiz"
    ]
    
    print("\nExample search queries that would be used:")
    print("-" * 50)
    
    for i, query in enumerate(search_queries, 1):
        print(f"{i:2d}. {query}")
    
    print(f"\nThese queries would be executed across multiple search engines")
    print(f"(Google, Bing, DuckDuckGo) to discover healthcare startup URLs.")


def main():
    """Main demo function"""
    print("Healthcare Startup Discovery System - Simple Demo")
    print("No external dependencies required!")
    print("\nThis demonstrates core functionality:")
    print("1. Healthcare keyword detection (English + German)")
    print("2. Company relevance scoring")
    print("3. URL validation and filtering")
    print("4. Output generation examples")
    
    try:
        # Run demonstration
        healthcare_companies = demo_healthcare_detection()
        demo_output_generation(healthcare_companies)
        demo_search_queries()
        
        # Final summary
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"✓ Found {len(healthcare_companies)} healthcare companies")
        print("✓ Demonstrated URL validation")
        print("✓ Showed output formats (CSV/JSON)")
        print("✓ Listed search query examples")
        
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print("To use the full system with all features:")
        print("\n1. Install dependencies:")
        print("   Windows: install-windows.bat")
        print("   Linux/Mac: chmod +x install.sh && ./install.sh")
        print("\n2. Run full system:")
        print("   python main.py")
        print("\n3. Or try the enhanced demo:")
        print("   python demo.py")
        
        print(f"\nThe full system includes:")
        print("• Asynchronous web scraping")
        print("• Advanced NLP with machine learning") 
        print("• Multiple data sources (directories, search engines)")
        print("• Rate limiting and ethical scraping")
        print("• Comprehensive error handling")
        print("• Professional output with statistics")
        
    except Exception as e:
        print(f"Demo error: {e}")
        print("This shouldn't happen with the simple demo!")


if __name__ == "__main__":
    main()