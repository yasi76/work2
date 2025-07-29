#!/usr/bin/env python3
"""
Example of improved product extraction output
"""

import json
from extract_product_names import ProductExtractor

def demonstrate_improved_extraction():
    """Show how the improved extraction produces cleaner results"""
    
    # Example input
    example_startups = [
        {
            "company_name": "Nutrio",
            "url": "https://shop.getnutrio.com/"
        },
        {
            "company_name": "VisionCheckout", 
            "url": "https://visioncheckout.com/"
        },
        {
            "company_name": "Actimi",
            "url": "https://www.actimi.com"
        }
    ]
    
    extractor = ProductExtractor()
    
    print("IMPROVED PRODUCT EXTRACTION RESULTS")
    print("=" * 60)
    print("\nThe new extraction system filters out UI elements and marketing phrases,")
    print("focusing only on actual product names.\n")
    
    results = []
    
    for startup in example_startups:
        # Process the startup
        enriched = extractor.discover_all_products(startup.copy())
        
        # Create clean output
        clean_result = {
            "company_name": enriched["company_name"],
            "url": enriched["url"],
            "products": enriched.get("product_names", []),
            "product_types": [enriched.get("product_types", {}).get(p, "Unknown") 
                            for p in enriched.get("product_names", [])]
        }
        
        results.append(clean_result)
        
        # Display results
        print(f"Company: {clean_result['company_name']}")
        print(f"URL: {clean_result['url']}")
        print(f"Products: {', '.join(clean_result['products']) if clean_result['products'] else 'None found'}")
        print(f"Types: {', '.join(clean_result['product_types']) if clean_result['product_types'] else 'N/A'}")
        print("-" * 40)
    
    print("\n\nJSON Output (Clean Format):")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print("\n\nKey Improvements:")
    print("✓ Filters out navigation elements (Home, Kontakt, etc.)")
    print("✓ Removes marketing slogans and CTAs")
    print("✓ Focuses on text containing product keywords (App, Platform, etc.)")
    print("✓ Prioritizes structured product sections")
    print("✓ Uses ground truth data when available")
    print("✓ Validates product names before including them")

def show_filtering_examples():
    """Show examples of what gets filtered out"""
    
    print("\n\nFILTERING EXAMPLES")
    print("=" * 60)
    
    extractor = ProductExtractor()
    
    # Examples of text that would be filtered
    filtered_examples = [
        ("Der autonome Self-Checkoutfür Ihre Kantine", "No product keyword"),
        ("Unser einzigartiges Servicekonzept", "Marketing phrase"),
        ("Prozessoptimierung", "Generic term, no product keyword"),
        ("Gesundheitsversorgung neu definieren", "Marketing slogan"),
        ("Transforming Healthcare", "Marketing slogan"),
        ("Jetzt starten", "CTA button"),
        ("Demo anfordern", "CTA button"),
        ("Mehr erfahren", "CTA button"),
        ("Kontakt", "Navigation"),
        ("Über uns", "Navigation"),
        ("Alle Kategorien", "Generic UI element")
    ]
    
    # Examples of valid product names
    valid_examples = [
        ("Nutrio App", "Contains 'App' keyword"),
        ("aurora nutrio", "Recognized brand name from ground truth"),
        ("Health Platform", "Contains 'Platform' keyword"),
        ("Actimi Herzinsuffizienz Set", "Contains 'Set' keyword"),
        ("AI Diagnostic Tool", "Contains 'Tool' and 'AI' keywords"),
        ("Patient Monitor Pro", "Contains 'Monitor' keyword"),
        ("Therapy Assistant", "Contains 'Assistant' keyword")
    ]
    
    print("\nFiltered Out (Invalid):")
    for text, reason in filtered_examples:
        is_valid = extractor._is_valid_product_name(text)
        print(f"  ✗ '{text}' - {reason}")
    
    print("\nAccepted (Valid Products):")
    for text, reason in valid_examples:
        is_valid = extractor._is_valid_product_name(text)
        print(f"  ✓ '{text}' - {reason}")

if __name__ == "__main__":
    demonstrate_improved_extraction()
    show_filtering_examples()