#!/usr/bin/env python3
"""
Test Apheris specifically to show tagline filtering improvements
"""

import requests
from bs4 import BeautifulSoup
import re

# Test both old and new filtering approaches
def test_old_approach(url):
    """Simulate the old extraction approach that picks up taglines"""
    print("\n" + "="*60)
    print("OLD APPROACH (picks up taglines)")
    print("="*60)
    
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    candidates = []
    
    # Old approach: grab all headings
    for tag in ['h1', 'h2', 'h3']:
        for heading in soup.find_all(tag):
            text = heading.get_text(strip=True)
            if text and len(text) > 3 and len(text) < 50:
                candidates.append({
                    'text': text,
                    'tag': tag,
                    'parent': heading.parent.name if heading.parent else 'none'
                })
    
    print(f"\nFound {len(candidates)} candidates:")
    for c in candidates[:10]:  # Show first 10
        print(f"  [{c['tag']}] {c['text']}")
    
    return candidates

def test_new_approach(url):
    """Demonstrate the V4 filtering that removes taglines"""
    print("\n" + "="*60)
    print("NEW APPROACH V4 (filters taglines)")
    print("="*60)
    
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Slogan patterns from V4
    SLOGAN_PATTERNS = [
        r'^(how|why|when|where|what|who)\s+.*',
        r'^(a|an|the)\s+[a-z]+.*',
        r'^(get|build|create|make|start|join|discover|explore|learn|find|connect|transform|unlock).*',
        r'.*\s+(your|our|the)\s+(way|solution|choice|future|journey)$',
        r'^(introducing|announcing|welcome|experience|discover).*',
        r'^(powered by|built with|designed for|made for|created by).*',
        r'^(fast|easy|simple|secure|safe|reliable|powerful|smart).*',
        r'fits\s*right\s*in',
        r'auditability\s*built\s*in',
        r'preprocess.*your\s*way',
        r'proprietary\s*data.*',
        r'a\s*blind\s*man.*view',
    ]
    
    # Required product keywords
    PRODUCT_INDICATORS = [
        'platform', 'app', 'application', 'software', 'solution', 'tool', 
        'system', 'device', 'monitor', 'tracker', 'assistant', 'coach'
    ]
    
    slogan_regex = [re.compile(p, re.IGNORECASE) for p in SLOGAN_PATTERNS]
    
    candidates = []
    filtered_out = []
    
    # Look only in product-related sections
    product_sections = soup.find_all(['section', 'div', 'article'], 
        class_=re.compile(r'product|solution|offering|software', re.I))
    
    # If no product sections found, check main content
    if not product_sections:
        product_sections = soup.find_all(['main', 'div'], class_=re.compile(r'content|container', re.I))
    
    for section in product_sections:
        for tag in ['h2', 'h3', 'h4']:
            for heading in section.find_all(tag):
                text = heading.get_text(strip=True)
                text_lower = text.lower()
                
                # Get context
                parent = heading.parent
                context = parent.get_text(strip=True)[:200] if parent else ""
                context_lower = context.lower()
                
                # Apply filters
                reasons = []
                
                # Check length
                if len(text) < 5:
                    reasons.append("too short")
                    
                # Check for slogans
                for pattern in slogan_regex:
                    if pattern.match(text_lower):
                        reasons.append(f"matches slogan pattern")
                        break
                
                # Check for capital letters
                if not any(c.isupper() for c in text):
                    reasons.append("no capitals")
                
                # Check for product keywords
                combined = f"{text_lower} {context_lower}"
                has_product_keyword = any(kw in combined for kw in PRODUCT_INDICATORS)
                
                # Require 2+ words or product indicator
                words = [w for w in text.split() if len(w) > 1]
                if len(words) < 2 and not has_product_keyword:
                    reasons.append("single word without product indicator")
                
                if reasons:
                    filtered_out.append({
                        'text': text,
                        'reasons': reasons,
                        'tag': tag
                    })
                else:
                    candidates.append({
                        'text': text,
                        'tag': tag,
                        'has_keyword': has_product_keyword,
                        'context_preview': context[:50] + "..."
                    })
    
    print(f"\nFiltered out {len(filtered_out)} taglines/slogans:")
    for f in filtered_out[:10]:
        print(f"  ❌ '{f['text']}' - Reasons: {', '.join(f['reasons'])}")
    
    print(f"\nKept {len(candidates)} valid candidates:")
    for c in candidates:
        keyword_marker = "✓" if c['has_keyword'] else "?"
        print(f"  {keyword_marker} [{c['tag']}] {c['text']}")
        print(f"     Context: {c['context_preview']}")
    
    return candidates, filtered_out

def main():
    url = "https://www.apheris.com"
    print(f"Testing: {url}")
    
    # Test old approach
    old_candidates = test_old_approach(url)
    
    # Test new approach
    new_candidates, filtered = test_new_approach(url)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Old approach found: {len(old_candidates)} candidates (includes many taglines)")
    print(f"New approach found: {len(new_candidates)} valid products")
    print(f"New approach filtered: {len(filtered)} taglines/slogans")
    
    # Show what would be extracted as final products
    print("\nFinal products (high confidence only):")
    for c in new_candidates:
        if c['has_keyword']:
            print(f"  ✅ {c['text']}")

if __name__ == "__main__":
    main()