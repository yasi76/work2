#!/usr/bin/env python3
"""
MASTER SCRIPT: RUN ALL 3 PARTS
Complete 3-part URL discovery, evaluation, and company name extraction
Uses only FREE tools and includes user's hardcoded URLs
"""

import sys
import os
import time
from datetime import datetime

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)

def print_summary(part_num: int, title: str, stats: dict):
    """Print part summary"""
    print(f"\n✅ PART {part_num} COMPLETED: {title}")
    print("-" * 40)
    for key, value in stats.items():
        print(f"  • {key}: {value}")

def main():
    """Run all 3 parts sequentially"""
    start_time = time.time()
    
    print_header("FREE 3-PART URL DISCOVERY SYSTEM")
    print("🎯 OBJECTIVE: Find URLs → Evaluate URLs → Extract Company Names")
    print("🆓 METHOD: Using only FREE tools (no paid APIs)")
    print("👤 INCLUDES: User's hardcoded URLs as priority source")
    print("")
    
    # Track overall statistics
    overall_stats = {
        'start_time': datetime.now().isoformat(),
        'parts_completed': 0,
        'total_urls_discovered': 0,
        'working_urls_found': 0,
        'company_names_extracted': 0,
        'files_created': []
    }
    
    try:
        # PART 1: URL Discovery
        print_header("PART 1: URL DISCOVERY")
        print("🔍 Finding European health tech startup URLs...")
        
        # Import and run Part 1
        sys.path.append('.')
        from part1_url_finder import FreeURLFinder
        
        finder = FreeURLFinder()
        part1_results = finder.find_all_urls()
        csv_file, json_file = finder.save_discovered_urls(part1_results)
        
        overall_stats['parts_completed'] = 1
        overall_stats['total_urls_discovered'] = part1_results['total_urls_found']
        overall_stats['files_created'].extend([csv_file, json_file])
        
        print_summary(1, "URL Discovery", {
            "URLs discovered": part1_results['total_urls_found'],
            "User hardcoded URLs": part1_results['sources']['user_hardcoded'],
            "Additional sources": len(part1_results['sources']) - 1,
            "Files created": f"{csv_file}, {json_file}"
        })
        
        time.sleep(2)  # Brief pause between parts
        
        # PART 2: URL Evaluation
        print_header("PART 2: URL EVALUATION")
        print("🧪 Testing discovered URLs for accessibility and quality...")
        
        # Import and run Part 2
        from part2_url_evaluator import FreeURLEvaluator, load_urls_from_part1
        
        # Load URLs from Part 1
        urls_to_evaluate = load_urls_from_part1(csv_file)
        
        evaluator = FreeURLEvaluator()
        part2_results = evaluator.evaluate_urls(urls_to_evaluate)
        part2_summary = evaluator.generate_summary(part2_results)
        
        json_file2, working_csv, problematic_csv = evaluator.save_results(part2_results, part2_summary)
        
        overall_stats['parts_completed'] = 2
        overall_stats['working_urls_found'] = part2_summary['working_urls_count']
        overall_stats['files_created'].extend([json_file2, working_csv, problematic_csv])
        
        print_summary(2, "URL Evaluation", {
            "URLs evaluated": part2_summary['total_urls_evaluated'],
            "Working URLs": part2_summary['working_urls_count'],
            "Success rate": f"{part2_summary['success_rate']}%",
            "Avg response time": f"{part2_summary['average_response_time']}s",
            "Files created": f"{working_csv}, {problematic_csv}"
        })
        
        time.sleep(2)  # Brief pause between parts
        
        # PART 3: Company Name Extraction
        print_header("PART 3: COMPANY NAME EXTRACTION")
        print("🏢 Extracting company names from working URLs...")
        
        # Import and run Part 3
        from part3_company_name_extractor import FreeCompanyNameExtractor, load_urls_from_part2
        
        # Load working URLs from Part 2
        working_urls = load_urls_from_part2(working_csv)
        
        extractor = FreeCompanyNameExtractor()
        part3_results = extractor.extract_company_names(working_urls)
        part3_summary = extractor.generate_summary(part3_results)
        
        json_file3, companies_csv, successful_csv = extractor.save_results(part3_results, part3_summary)
        
        overall_stats['parts_completed'] = 3
        overall_stats['company_names_extracted'] = part3_summary['successful_extractions']
        overall_stats['files_created'].extend([json_file3, companies_csv, successful_csv])
        
        print_summary(3, "Company Name Extraction", {
            "URLs processed": part3_summary['total_urls_processed'],
            "Company names extracted": part3_summary['successful_extractions'],
            "Success rate": f"{part3_summary['success_rate']}%",
            "Avg confidence": f"{part3_summary['average_confidence_score']}/10",
            "Files created": f"{companies_csv}, {successful_csv}"
        })
        
        # FINAL SUMMARY
        end_time = time.time()
        total_time = end_time - start_time
        overall_stats['end_time'] = datetime.now().isoformat()
        overall_stats['total_execution_time'] = f"{total_time:.1f} seconds"
        
        print_header("🎉 COMPLETE SUCCESS!")
        print("🏆 ALL 3 PARTS COMPLETED SUCCESSFULLY")
        print("")
        print("📊 FINAL STATISTICS:")
        print(f"  🔍 URLs discovered: {overall_stats['total_urls_discovered']}")
        print(f"  ✅ Working URLs found: {overall_stats['working_urls_found']}")
        print(f"  🏢 Company names extracted: {overall_stats['company_names_extracted']}")
        print(f"  ⏱️  Total execution time: {overall_stats['total_execution_time']}")
        print(f"  📁 Files created: {len(overall_stats['files_created'])}")
        
        print("\n📁 OUTPUT FILES:")
        for i, file in enumerate(overall_stats['files_created'], 1):
            print(f"  {i:2d}. {file}")
        
        print("\n🎯 KEY ACHIEVEMENTS:")
        print("  ✅ Used only FREE tools - no paid APIs required")
        print("  ✅ Included all user hardcoded URLs as priority")
        print("  ✅ Found and validated working health tech URLs")
        print("  ✅ Extracted company names with confidence scores")
        print("  ✅ Created comprehensive company directory")
        
        success_rate = (overall_stats['company_names_extracted'] / overall_stats['total_urls_discovered']) * 100
        print(f"\n🏆 OVERALL SUCCESS RATE: {success_rate:.1f}% (companies extracted from discovered URLs)")
        
        # Show top companies
        if part3_summary['extracted_companies']:
            print(f"\n🌟 TOP 10 EXTRACTED COMPANIES:")
            sorted_companies = sorted(part3_summary['extracted_companies'], 
                                    key=lambda x: x['confidence_score'], reverse=True)
            for i, company in enumerate(sorted_companies[:10], 1):
                print(f"  {i:2d}. {company['company_name']} ({company['confidence_score']:.1f}) - {company['url']}")
        
        print("\n" + "=" * 80)
        print("🎊 MISSION ACCOMPLISHED! Your European health tech company directory is ready!")
        print("=" * 80)
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Error occurred: {str(e)}")
        print("📊 Partial results may be available in created files")
        return False

if __name__ == "__main__":
    print("🚀 Starting 3-part URL discovery system...")
    print("📋 This will take several minutes to complete")
    print("⏸️  You can press Ctrl+C to stop at any time")
    print("")
    
    # Ask for confirmation
    try:
        response = input("🤔 Ready to start? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            success = main()
            if success:
                print("\n✨ Process completed successfully!")
                sys.exit(0)
            else:
                print("\n⚠️  Process completed with issues")
                sys.exit(1)
        else:
            print("👋 Process cancelled by user")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n👋 Process cancelled by user")
        sys.exit(0)