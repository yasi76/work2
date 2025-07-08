"""
Healthcare Startup Discovery System - Main Orchestrator

This is the main entry point for the healthcare startup discovery system.
It coordinates all scrapers, manages the discovery process, and outputs results.
"""

import asyncio
import logging
import json
import csv
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd

from models import CompanyInfo, DiscoverySession, SourceType
from scrapers.directory_scraper import DirectoryScraper
from scrapers.search_scraper import SearchScraper
from nlp_processor import HealthcareNLPProcessor
from url_validator import URLValidator
from config import (
    LOG_LEVEL, LOG_FORMAT, LOG_FILE, OUTPUT_FILENAME,
    DEFAULT_OUTPUT_FORMAT, STARTUP_DIRECTORIES, NEWS_SOURCES
)

# Set up logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, filename=LOG_FILE)
logger = logging.getLogger(__name__)


class HealthcareStartupDiscovery:
    """
    Main orchestrator for healthcare startup discovery
    
    This class coordinates multiple scrapers to discover healthcare
    startups and SMEs across Germany and Europe.
    """
    
    def __init__(self):
        """Initialize the discovery system"""
        self.session_id = str(uuid.uuid4())
        self.session = DiscoverySession(session_id=self.session_id)
        self.nlp_processor = HealthcareNLPProcessor()
        self.url_validator = URLValidator()
        
        logger.info(f"Healthcare Startup Discovery System initialized (Session: {self.session_id})")
    
    async def discover_companies(self, 
                                sources: List[str] = None,
                                max_companies: int = 1000,
                                output_format: str = 'csv',
                                output_file: str = None) -> DiscoverySession:
        """
        Main method to discover healthcare companies
        
        Args:
            sources: List of source types to use ('directories', 'search', 'news')
            max_companies: Maximum number of companies to discover
            output_format: Output format ('csv' or 'json')
            output_file: Custom output filename
            
        Returns:
            DiscoverySession with all results
        """
        if sources is None:
            sources = ['directories', 'search']  # Default sources
        
        logger.info(f"Starting healthcare company discovery with sources: {sources}")
        logger.info(f"Target: {max_companies} companies, Output: {output_format}")
        
        try:
            # Step 1: Directory scraping
            if 'directories' in sources:
                logger.info("=== STEP 1: Directory Scraping ===")
                await self._scrape_directories()
            
            # Step 2: Search engine scraping
            if 'search' in sources:
                logger.info("=== STEP 2: Search Engine Scraping ===")
                await self._scrape_search_engines()
            
            # Step 3: News and press release scraping
            if 'news' in sources:
                logger.info("=== STEP 3: News Source Scraping ===")
                await self._scrape_news_sources()
            
            # Step 4: Post-processing and filtering
            logger.info("=== STEP 4: Post-processing ===")
            await self._post_process_results(max_companies)
            
            # Step 5: Output results
            logger.info("=== STEP 5: Generating Output ===")
            await self._generate_output(output_format, output_file)
            
            # Complete session
            self.session.complete_session()
            
            logger.info(f"Discovery completed successfully!")
            logger.info(f"Total companies found: {len(self.session.get_all_companies())}")
            logger.info(f"Sources scraped: {self.session.sources_scraped}")
            
        except Exception as e:
            logger.error(f"Error in discovery process: {e}")
            raise
        
        return self.session
    
    async def _scrape_directories(self):
        """Scrape startup directories"""
        try:
            async with DirectoryScraper(delay=2.0) as scraper:
                result = await scraper.scrape(
                    directories=STARTUP_DIRECTORIES,
                    max_pages=5
                )
                
                self.session.add_result(result)
                logger.info(f"Directory scraping completed: {len(result.companies)} companies found")
                
        except Exception as e:
            logger.error(f"Error in directory scraping: {e}")
            self.session.errors.append(f"Directory scraping error: {str(e)}")
    
    async def _scrape_search_engines(self):
        """Scrape search engines"""
        try:
            async with SearchScraper(delay=3.0) as scraper:
                result = await scraper.scrape(
                    search_engines=['duckduckgo'],  # Start with DuckDuckGo to avoid blocking
                    max_results_per_query=30
                )
                
                self.session.add_result(result)
                logger.info(f"Search engine scraping completed: {len(result.companies)} companies found")
                
        except Exception as e:
            logger.error(f"Error in search engine scraping: {e}")
            self.session.errors.append(f"Search engine scraping error: {str(e)}")
    
    async def _scrape_news_sources(self):
        """Scrape news and press release sources"""
        try:
            # Use base scraper functionality for news sources
            async with DirectoryScraper(delay=2.0) as scraper:
                result = await scraper.scrape(
                    directories=NEWS_SOURCES,
                    max_pages=3
                )
                
                # Update source type for news results
                for company in result.companies:
                    company.source_type = SourceType.NEWS
                
                self.session.add_result(result)
                logger.info(f"News source scraping completed: {len(result.companies)} companies found")
                
        except Exception as e:
            logger.error(f"Error in news source scraping: {e}")
            self.session.errors.append(f"News source scraping error: {str(e)}")
    
    async def _post_process_results(self, max_companies: int):
        """Post-process and filter results"""
        try:
            all_companies = self.session.get_all_companies()
            logger.info(f"Post-processing {len(all_companies)} companies")
            
            # Filter by confidence score
            high_confidence_companies = [
                company for company in all_companies
                if company.confidence_score >= 0.6
            ]
            
            logger.info(f"High confidence companies: {len(high_confidence_companies)}")
            
            # Sort by confidence score (descending)
            sorted_companies = sorted(
                high_confidence_companies,
                key=lambda x: x.confidence_score,
                reverse=True
            )
            
            # Limit to max_companies
            if len(sorted_companies) > max_companies:
                sorted_companies = sorted_companies[:max_companies]
                logger.info(f"Limited to top {max_companies} companies")
            
            # Update session with filtered companies
            # Clear existing results and add filtered ones
            self.session.results.clear()
            
            # Create a new result with filtered companies
            from models import ScrapingResult
            filtered_result = ScrapingResult(
                source_type=SourceType.WEBSITE,
                source_url="Post-processed results",
                success=True
            )
            
            for company in sorted_companies:
                filtered_result.add_company(company)
            
            self.session.add_result(filtered_result)
            
        except Exception as e:
            logger.error(f"Error in post-processing: {e}")
            self.session.errors.append(f"Post-processing error: {str(e)}")
    
    async def _generate_output(self, output_format: str, output_file: str = None):
        """Generate output files"""
        try:
            companies = self.session.get_all_companies()
            
            if not companies:
                logger.warning("No companies to output")
                return
            
            # Determine output filename
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"{OUTPUT_FILENAME}_{timestamp}"
            
            # Generate CSV output
            if output_format in ['csv', 'both']:
                csv_file = f"{output_file}.csv"
                await self._generate_csv_output(companies, csv_file)
                logger.info(f"CSV output generated: {csv_file}")
            
            # Generate JSON output
            if output_format in ['json', 'both']:
                json_file = f"{output_file}.json"
                await self._generate_json_output(companies, json_file)
                logger.info(f"JSON output generated: {json_file}")
            
            # Generate summary report
            summary_file = f"{output_file}_summary.txt"
            await self._generate_summary_report(summary_file)
            logger.info(f"Summary report generated: {summary_file}")
            
        except Exception as e:
            logger.error(f"Error generating output: {e}")
            raise
    
    async def _generate_csv_output(self, companies: List[CompanyInfo], filename: str):
        """Generate CSV output file"""
        try:
            # Prepare data for CSV
            csv_data = []
            for company in companies:
                csv_data.append({
                    'Company Name': company.name,
                    'Website URL': company.url,
                    'Description': company.description,
                    'Country': company.country.value,
                    'Source Type': company.source_type.value,
                    'Source URL': company.source_url,
                    'Confidence Score': f"{company.confidence_score:.3f}",
                    'Keywords Matched': '; '.join(sorted(company.keywords_matched)),
                    'Discovered At': company.discovered_at.isoformat(),
                    'Additional URLs': '; '.join(company.additional_urls)
                })
            
            # Write CSV file
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False, encoding='utf-8')
            
        except Exception as e:
            logger.error(f"Error generating CSV: {e}")
            raise
    
    async def _generate_json_output(self, companies: List[CompanyInfo], filename: str):
        """Generate JSON output file"""
        try:
            # Prepare data for JSON
            json_data = {
                'session_info': {
                    'session_id': self.session.session_id,
                    'generated_at': datetime.now().isoformat(),
                    'total_companies': len(companies),
                    'sources_scraped': self.session.sources_scraped
                },
                'companies': [company.to_dict() for company in companies]
            }
            
            # Write JSON file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error generating JSON: {e}")
            raise
    
    async def _generate_summary_report(self, filename: str):
        """Generate summary report"""
        try:
            companies = self.session.get_all_companies()
            
            # Calculate statistics
            country_stats = {}
            source_stats = {}
            confidence_stats = {
                'high': 0,     # > 0.8
                'medium': 0,   # 0.6 - 0.8
                'low': 0       # < 0.6
            }
            
            for company in companies:
                # Country statistics
                country = company.country.value
                country_stats[country] = country_stats.get(country, 0) + 1
                
                # Source statistics
                source = company.source_type.value
                source_stats[source] = source_stats.get(source, 0) + 1
                
                # Confidence statistics
                if company.confidence_score > 0.8:
                    confidence_stats['high'] += 1
                elif company.confidence_score >= 0.6:
                    confidence_stats['medium'] += 1
                else:
                    confidence_stats['low'] += 1
            
            # Generate report
            report_lines = [
                "Healthcare Startup Discovery Report",
                "=" * 40,
                f"Session ID: {self.session.session_id}",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Processing Time: {(self.session.completed_at - self.session.started_at).total_seconds():.1f} seconds",
                "",
                "SUMMARY",
                "-" * 20,
                f"Total Companies Discovered: {len(companies)}",
                f"Sources Scraped: {self.session.sources_scraped}",
                f"Errors Encountered: {len(self.session.errors)}",
                "",
                "COUNTRY DISTRIBUTION",
                "-" * 20
            ]
            
            for country, count in sorted(country_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(companies)) * 100
                report_lines.append(f"{country.title()}: {count} ({percentage:.1f}%)")
            
            report_lines.extend([
                "",
                "SOURCE DISTRIBUTION",
                "-" * 20
            ])
            
            for source, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(companies)) * 100
                report_lines.append(f"{source.title()}: {count} ({percentage:.1f}%)")
            
            report_lines.extend([
                "",
                "CONFIDENCE DISTRIBUTION",
                "-" * 20,
                f"High Confidence (>0.8): {confidence_stats['high']}",
                f"Medium Confidence (0.6-0.8): {confidence_stats['medium']}",
                f"Low Confidence (<0.6): {confidence_stats['low']}",
                ""
            ])
            
            if self.session.errors:
                report_lines.extend([
                    "ERRORS",
                    "-" * 20
                ])
                for error in self.session.errors:
                    report_lines.append(f"- {error}")
                report_lines.append("")
            
            # Top companies by confidence
            top_companies = sorted(companies, key=lambda x: x.confidence_score, reverse=True)[:10]
            report_lines.extend([
                "TOP 10 COMPANIES BY CONFIDENCE",
                "-" * 30
            ])
            
            for i, company in enumerate(top_companies, 1):
                report_lines.append(f"{i:2d}. {company.name} ({company.confidence_score:.3f}) - {company.url}")
            
            # Write report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
                
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            raise


async def main():
    """Main entry point"""
    try:
        # Create discovery system
        discovery = HealthcareStartupDiscovery()
        
        # Configure discovery parameters
        sources = ['directories', 'search']  # Can be extended with 'news'
        max_companies = 500  # Adjust based on needs
        output_format = 'both'  # 'csv', 'json', or 'both'
        
        # Run discovery
        session = await discovery.discover_companies(
            sources=sources,
            max_companies=max_companies,
            output_format=output_format
        )
        
        print(f"\n{'='*50}")
        print("HEALTHCARE STARTUP DISCOVERY COMPLETED")
        print(f"{'='*50}")
        print(f"Session ID: {session.session_id}")
        print(f"Companies Found: {len(session.get_all_companies())}")
        print(f"Sources Scraped: {session.sources_scraped}")
        print(f"Processing Time: {(session.completed_at - session.started_at).total_seconds():.1f} seconds")
        
        if session.errors:
            print(f"Errors: {len(session.errors)}")
            for error in session.errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
        
        print(f"\nOutput files generated with timestamp.")
        print("Check the generated CSV/JSON files for complete results.")
        
    except KeyboardInterrupt:
        logger.info("Discovery interrupted by user")
        print("\nDiscovery interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the discovery system
    asyncio.run(main())