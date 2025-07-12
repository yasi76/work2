#!/usr/bin/env python3
"""
Simple runner script for the Enhanced Healthcare Scraper
This script provides an easy way to run the scraper with different configurations
"""

import os
import sys
import argparse
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(str(Path(__file__).parent))

try:
    from enhanced_healthcare_scraper import EnhancedHealthcareScraper, logger
except ImportError as e:
    print(f"❌ Error importing scraper: {e}")
    print("Please make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Enhanced Healthcare Company Scraper')
    parser.add_argument('--no-selenium', action='store_true', 
                       help='Run without Selenium (faster but may miss some data)')
    parser.add_argument('--output-dir', default='output', 
                       help='Output directory for results (default: output)')
    parser.add_argument('--sources', nargs='*', 
                       choices=['bvmed', 'spectaris', 'digital_health_hub', 'biom', 'ehealth', 'blogs'],
                       help='Specific sources to scrape (default: all)')
    parser.add_argument('--max-companies', type=int, default=1000,
                       help='Maximum number of companies to extract (default: 1000)')
    
    args = parser.parse_args()
    
    # Create scraper instance
    use_selenium = not args.no_selenium
    scraper = EnhancedHealthcareScraper(use_selenium=use_selenium)
    
    logger.info("🚀 STARTING ENHANCED HEALTHCARE SCRAPER")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  - Selenium: {'Enabled' if use_selenium else 'Disabled'}")
    logger.info(f"  - Output directory: {args.output_dir}")
    logger.info(f"  - Max companies: {args.max_companies}")
    logger.info(f"  - Sources: {args.sources or 'All'}")
    logger.info("=" * 60)
    
    # Run extraction
    try:
        if args.sources:
            # Run specific sources
            all_companies = []
            
            source_mapping = {
                'bvmed': ('BVMed', scraper.extract_from_bvmed),
                'spectaris': ('SPECTARIS', scraper.extract_from_spectaris),
                'digital_health_hub': ('Digital Health Hub', scraper.extract_from_digital_health_hub),
                'biom': ('BioM', scraper.extract_from_biom_cluster),
                'ehealth': ('eHealth Initiative', scraper.extract_from_ehealth_initiative),
                'blogs': ('Healthcare Blogs', scraper.extract_from_startup_blogs)
            }
            
            for source in args.sources:
                if source in source_mapping:
                    source_name, method = source_mapping[source]
                    logger.info(f"🔍 Extracting from {source_name}...")
                    companies = method()
                    all_companies.extend(companies)
                    logger.info(f"✅ Found {len(companies)} companies from {source_name}")
                    
                    # Check if we've reached the limit
                    if len(all_companies) >= args.max_companies:
                        all_companies = all_companies[:args.max_companies]
                        logger.info(f"⚠️  Reached maximum limit of {args.max_companies} companies")
                        break
            
            # Process companies
            unique_companies = scraper._remove_duplicates(all_companies)
            enhanced_companies = scraper.enhance_companies_with_details(unique_companies)
            
        else:
            # Run all sources
            enhanced_companies = scraper.run_extraction()
            
            # Limit results if specified
            if len(enhanced_companies) > args.max_companies:
                enhanced_companies = enhanced_companies[:args.max_companies]
                logger.info(f"⚠️  Limited results to {args.max_companies} companies")
        
        # Save results
        if enhanced_companies:
            company_dicts = scraper.save_results(enhanced_companies, args.output_dir)
            
            # Show summary
            logger.info("\n" + "="*60)
            logger.info("📊 EXTRACTION SUMMARY")
            logger.info("="*60)
            logger.info(f"Total companies extracted: {len(enhanced_companies)}")
            logger.info(f"Companies with websites: {sum(1 for c in company_dicts if c['website'])}")
            logger.info(f"Companies with descriptions: {sum(1 for c in company_dicts if c['description'])}")
            logger.info(f"Output saved to: {args.output_dir}/")
            
            # Show breakdown by category
            categories = {}
            for company in enhanced_companies:
                cat = company.category or 'Unknown'
                categories[cat] = categories.get(cat, 0) + 1
            
            logger.info("\n📈 BREAKDOWN BY CATEGORY:")
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {category}: {count} companies")
            
            # Show sample companies
            logger.info("\n🏢 SAMPLE COMPANIES:")
            for i, company in enumerate(enhanced_companies[:5], 1):
                logger.info(f"  {i}. {company.name}")
                if company.website:
                    logger.info(f"     🌐 {company.website}")
                if company.location:
                    logger.info(f"     📍 {company.location}")
                if company.category:
                    logger.info(f"     🏷️  {company.category}")
                logger.info("")
            
            logger.info("🎉 EXTRACTION COMPLETED SUCCESSFULLY!")
            
        else:
            logger.error("❌ No companies were extracted")
            
    except KeyboardInterrupt:
        logger.info("⚠️  Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Extraction failed: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()

if __name__ == "__main__":
    main()