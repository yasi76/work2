#!/usr/bin/env python3
"""
QUICK Healthcare Discovery (Government Sources Skipped)
Focuses on reliable industry directories and startup databases
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import ultimate_config as uconfig
import url_validator
import utils

class QuickHealthcareDiscoverer:
    """Quick healthcare discovery focusing on reliable sources"""
    
    def __init__(self):
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=10)  # Shorter timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.discovered_urls = set()
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=10,  # Reduced concurrent connections
            limit_per_host=2,
            ssl=False  # Skip SSL verification
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def discover_from_source(self, url: str) -> set:
        """Discover URLs from a single source with timeout"""
        discovered = set()
        try:
            print(f"   ✅ Processing: {url}")
            
            # Add timeout for the entire operation
            async with asyncio.timeout(30):  # 30 second timeout per source
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract URLs
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('/'):
                                full_url = urljoin(url, href)
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            # Quick healthcare check
                            if self._quick_healthcare_check(full_url, link.get_text()):
                                discovered.add(full_url)
                                if len(discovered) >= 50:  # Limit per source
                                    break
                        
                        print(f"   ✅ Found {len(discovered)} URLs from {url}")
                    else:
                        print(f"   ❌ Status {response.status} for {url}")
                        
        except asyncio.TimeoutError:
            print(f"   ⏰ Timeout: {url}")
        except Exception as e:
            print(f"   ❌ Error: {url} - {str(e)[:100]}")
        
        return discovered
    
    def _quick_healthcare_check(self, url: str, text: str = "") -> bool:
        """Quick healthcare relevance check"""
        combined = f"{url} {text}".lower()
        healthcare_keywords = [
            'health', 'medical', 'medicine', 'healthcare', 'medtech', 
            'biotech', 'pharma', 'clinic', 'hospital', 'therapy'
        ]
        
        # Must contain at least 1 healthcare keyword and not be excluded
        has_healthcare = any(keyword in combined for keyword in healthcare_keywords)
        is_excluded = any(exclude in url.lower() for exclude in [
            'facebook.com', 'linkedin.com', 'twitter.com', 'google.com',
            'login', 'signup', 'privacy', 'terms'
        ])
        
        return has_healthcare and not is_excluded

    async def quick_discovery(self) -> List[Dict]:
        """Run quick discovery focusing on reliable sources"""
        print("🚀 QUICK Healthcare Discovery (Government Sources Skipped)")
        print("=" * 60)
        print("🎯 Target: 1000-3000 healthcare companies")
        print("⚡ Focus: Reliable industry sources only")
        print("⏰ Estimated time: 5-10 minutes")
        print()
        
        all_urls = set()
        
        # Use only reliable sources (skip government)
        reliable_sources = [
            # Industry directories (most reliable)
            'https://www.startupblink.com/startups/healthtech',
            'https://angel.co/companies?markets[]=health-care',
            'https://www.crunchbase.com/hub/european-health-care-companies',
            'https://www.f6s.com/companies/health/europe',
            'https://healtheuropa.eu/category/digital-health/',
            'https://www.digitalhealth.net/companies/',
            'https://innovationorigins.com/en/category/health/',
            
            # Startup databases
            'https://www.eu-startups.com/tag/health/',
            'https://startup-map.eu/health',
            'https://www.dealroom.co/companies/health-technology',
            
            # Healthcare directories
            'https://www.healthtech-event.com/directory/',
            'https://www.himss.org/membership/corporate-members',
            'https://www.mobihealthnews.com/directory/',
            
            # Tech directories with health sections
            'https://techcrunch.com/category/health/',
            'https://venturebeat.com/health/',
        ]
        
        print(f"🔍 Processing {len(reliable_sources)} reliable sources...")
        
        # Process sources with limited concurrency
        semaphore = asyncio.Semaphore(3)  # Only 3 concurrent requests
        
        async def process_source(source_url):
            async with semaphore:
                return await self.discover_from_source(source_url)
        
        # Run discovery
        tasks = [process_source(url) for url in reliable_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in results:
            if isinstance(result, set):
                all_urls.update(result)
        
        print(f"\n📊 Discovery Summary:")
        print(f"   Total URLs discovered: {len(all_urls)}")
        
        # Convert to result format
        final_results = []
        for url in all_urls:
            final_results.append({
                'url': url,
                'source': 'Quick Discovery',
                'healthcare_score': 5,  # Default score
                'is_live': None,
                'is_healthcare': True,  # Pre-filtered
                'status_code': None,
                'title': '',
                'description': '',
                'error': None,
                'response_time': None
            })
        
        print(f"   URLs for validation: {len(final_results)}")
        print(f"\n✅ Quick discovery complete!")
        
        return final_results


async def run_quick_discovery():
    """Run quick healthcare discovery"""
    async with QuickHealthcareDiscoverer() as discoverer:
        return await discoverer.quick_discovery()


if __name__ == "__main__":
    print("🚀 Quick Healthcare Discovery")
    
    async def main():
        # Step 1: Quick discovery
        discovered = await run_quick_discovery()
        
        if discovered:
            # Step 2: Validate discovered URLs
            print(f"\n🔬 Validating {len(discovered)} discovered URLs...")
            urls_to_validate = [r['url'] for r in discovered]
            validated = url_validator.clean_and_validate_urls(urls_to_validate)
            
            # Step 3: Save results
            healthcare_only = [r for r in validated if r.get('is_live') and r.get('is_healthcare')]
            
            if healthcare_only:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Save CSV
                import pandas as pd
                df_data = []
                for result in healthcare_only:
                    df_data.append({
                        'url': result['url'],
                        'domain': utils.extract_domain(result['url']),
                        'title': result.get('title', ''),
                        'country': utils.get_ultimate_country_estimate(result['url'], result.get('title', '')),
                        'sector': utils.classify_healthcare_sector(result['url'], result.get('title', '')),
                        'source': 'Quick Discovery'
                    })
                
                df = pd.DataFrame(df_data)
                csv_file = f"quick_healthcare_companies_{timestamp}.csv"
                df.to_csv(csv_file, index=False)
                
                print(f"\n🎉 QUICK DISCOVERY COMPLETE!")
                print(f"📊 Found {len(healthcare_only)} verified healthcare companies")
                print(f"💾 Saved to: {csv_file}")
                print(f"🌍 Countries: {len(df['country'].unique())}")
                print(f"🏥 Sectors: {len(df['sector'].unique())}")
            else:
                print("⚠️ No healthcare companies found after validation")
        else:
            print("❌ No URLs discovered")
    
    asyncio.run(main())