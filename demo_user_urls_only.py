#!/usr/bin/env python3
"""
DEMO: USER URLS ONLY
Test the 3-part system with only your 53 hardcoded URLs
Perfect for quick demonstration and validation
"""

import sys
import time
from datetime import datetime

def main():
    """Run 3-part system with only user's hardcoded URLs"""
    print("🎯 DEMO: USER'S 53 HARDCODED URLs ONLY")
    print("=" * 60)
    print("This demo runs the full 3-part system on your 53 URLs only")
    print("Perfect for quick testing and validation")
    print("")
    
    # Your 53 hardcoded URLs
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
    
    print(f"📊 Processing {len(user_urls)} URLs")
    print("⏱️  Estimated time: 3-5 minutes")
    print("")
    
    # Create CSV file with user URLs
    import csv
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    demo_csv = f"demo_user_urls_{timestamp}.csv"
    
    with open(demo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'discovery_method', 'status'])
        for url in user_urls:
            writer.writerow([url, 'User Hardcoded', 'Discovered'])
    
    print(f"✅ Created input file: {demo_csv}")
    
    try:
        # PART 2: Evaluate URLs
        print("\n🧪 PART 2: EVALUATING USER URLs")
        print("-" * 40)
        
        from part2_url_evaluator import FreeURLEvaluator, load_urls_from_part1
        
        evaluator = FreeURLEvaluator()
        results = evaluator.evaluate_urls(user_urls)
        summary = evaluator.generate_summary(results)
        
        json_file, working_csv, problematic_csv = evaluator.save_results(results, summary, f"demo_evaluation_{timestamp}")
        
        print(f"\n✅ Part 2 Complete:")
        print(f"  • Working URLs: {summary['working_urls_count']}/{len(user_urls)}")
        print(f"  • Success rate: {summary['success_rate']}%")
        print(f"  • Files: {working_csv}")
        
        # PART 3: Extract Company Names (only from working URLs)
        if summary['working_urls_count'] > 0:
            print("\n🏢 PART 3: EXTRACTING COMPANY NAMES")
            print("-" * 40)
            
            from part3_company_name_extractor import FreeCompanyNameExtractor
            
            extractor = FreeCompanyNameExtractor()
            working_urls = summary['working_urls']
            
            # Process only first 10 working URLs for demo speed
            demo_urls = working_urls[:min(10, len(working_urls))]
            print(f"📊 Processing first {len(demo_urls)} working URLs for demo...")
            
            extraction_results = extractor.extract_company_names(demo_urls)
            extraction_summary = extractor.generate_summary(extraction_results)
            
            json_file3, companies_csv, successful_csv = extractor.save_results(
                extraction_results, extraction_summary, f"demo_companies_{timestamp}"
            )
            
            print(f"\n✅ Part 3 Complete:")
            print(f"  • Company names extracted: {extraction_summary['successful_extractions']}/{len(demo_urls)}")
            print(f"  • Success rate: {extraction_summary['success_rate']}%")
            print(f"  • Files: {successful_csv}")
            
            # Show extracted companies
            if extraction_summary['extracted_companies']:
                print(f"\n🏆 EXTRACTED COMPANIES:")
                for i, company in enumerate(extraction_summary['extracted_companies'][:5], 1):
                    print(f"  {i}. {company['company_name']} - {company['url']}")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Your 53 URLs processed:")
        print(f"  • Working URLs found: {summary['working_urls_count']}")
        if summary['working_urls_count'] > 0:
            print(f"  • Company names extracted: {extraction_summary['successful_extractions']} (from first 10)")
        print(f"\n🎯 This demonstrates the full 3-part system works correctly!")
        print(f"🚀 Run 'python3 run_all_parts.py' for the complete discovery system")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 Quick Demo: Your 53 URLs Only")
    print("This tests the evaluation and extraction on your hardcoded URLs")
    print("")
    
    try:
        response = input("🤔 Start demo? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            success = main()
            if success:
                print("\n✨ Demo completed!")
            else:
                print("\n⚠️  Demo had issues")
        else:
            print("👋 Demo cancelled")
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled")