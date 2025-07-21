#!/usr/bin/env python3
"""
ULTIMATE STARTUP DISCOVERY SYSTEM
Combines multiple discovery methods to find digital health startups
Uses only free tools and prioritizes real startup websites
"""

import json
import csv
import time
from datetime import datetime
from typing import List, Dict, Set
import sys
import os

# Import discovery methods
try:
    from enhanced_startup_discovery import EnhancedStartupDiscovery
    from google_search_scraper import GoogleSearchStartupFinder
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Make sure all discovery modules are in the same directory")
    sys.exit(1)

class UltimateStartupDiscovery:
    def __init__(self):
        self.all_discovered_urls = set()
        self.final_results = []
        
    def get_user_hardcoded_urls(self) -> List[Dict]:
        """User's verified hardcoded URLs - Always included with highest priority"""
        print("🔍 Loading user's verified hardcoded URLs...")
        
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
        
        results = []
        for url in user_urls:
            results.append({
                'url': url,
                'source': 'User Verified',
                'confidence': 10,
                'category': 'Verified Health Tech',
                'country': 'Germany/Europe',
                'method': 'Hardcoded'
            })
            self.all_discovered_urls.add(url)
            
        print(f"✅ Loaded {len(results)} verified user URLs")
        return results

    def run_enhanced_discovery(self) -> List[Dict]:
        """Run the enhanced startup discovery method"""
        print("\n🚀 Running Enhanced Startup Discovery...")
        print("-" * 50)
        
        try:
            discoverer = EnhancedStartupDiscovery()
            results = discoverer.discover_all_startups()
            
            enhanced_results = []
            for url_data in results['urls']:
                if url_data['url'] not in self.all_discovered_urls:
                    self.all_discovered_urls.add(url_data['url'])
                    url_data['method'] = 'Enhanced Discovery'
                    enhanced_results.append(url_data)
            
            print(f"✅ Enhanced discovery found {len(enhanced_results)} new URLs")
            return enhanced_results
            
        except Exception as e:
            print(f"⚠️ Enhanced discovery error: {str(e)}")
            return []

    def run_google_search_discovery(self) -> List[Dict]:
        """Run the Google search-based discovery method"""
        print("\n🔍 Running Google Search Discovery...")
        print("-" * 50)
        
        try:
            finder = GoogleSearchStartupFinder()
            results = finder.discover_all_startups()
            
            google_results = []
            for url_data in results['urls']:
                if url_data['url'] not in self.all_discovered_urls:
                    self.all_discovered_urls.add(url_data['url'])
                    url_data['method'] = 'Google Search'
                    google_results.append(url_data)
            
            print(f"✅ Google search found {len(google_results)} new URLs")
            return google_results
            
        except Exception as e:
            print(f"⚠️ Google search discovery error: {str(e)}")
            return []

    def add_curated_startup_urls(self) -> List[Dict]:
        """Add manually curated startup URLs from known sources"""
        print("\n📋 Adding curated startup URLs...")
        print("-" * 50)
        
        # Additional curated startups from various sources
        curated_startups = [
            # German Digital Health Leaders
            'https://www.ada.com',
            'https://www.doctolib.de',
            'https://www.kaia-health.com',
            'https://www.teleclinic.com',
            'https://www.zavamed.com',
            'https://www.medwing.com',
            'https://www.felmo.de',
            'https://www.viomedo.de',
            'https://www.caresyntax.com',
            'https://www.merantix.com',
            'https://www.contextflow.com',
            'https://www.heartkinetics.com',
            'https://www.samedi.de',
            'https://www.medigene.com',
            'https://www.smartpatient.eu',
            
            # European Digital Health
            'https://www.doctolib.fr',
            'https://www.livi.co.uk',
            'https://www.babylon.com',
            'https://www.echo.co.uk',
            'https://www.accurx.com',
            'https://www.zava.com',
            'https://www.medgate.ch',
            'https://www.kry.se',
            'https://www.medadom.com',
            'https://www.qare.fr',
            'https://www.1177.se',
            'https://www.netdoktor.dk',
            'https://www.opensafely.org',
            
            # AI & Analytics
            'https://www.owkin.com',
            'https://www.benevolent.ai',
            'https://www.exscientia.ai',
            'https://www.healx.io',
            'https://www.deepmind.com/about/health',
            'https://www.insilico.com',
            
            # MedTech & Devices
            'https://www.siemens-healthineers.com',
            'https://www.philips.com/healthcare',
            'https://www.getinge.com',
            'https://www.elekta.com',
            'https://www.fresenius.com',
            'https://www.braun.com',
            
            # Pharma & Biotech
            'https://www.bayer.com',
            'https://www.boehringer-ingelheim.com',
            'https://www.merckgroup.com',
            'https://www.qiagen.com',
            'https://www.roche.com',
            'https://www.novartis.com',
            'https://www.sanofi.com',
            'https://www.gsk.com',
            'https://www.astrazeneca.com',
            
            # Emerging Startups
            'https://www.mindmaze.com',
            'https://www.sophia-genetics.com',
            'https://www.iqvia.com',
            'https://www.veracyte.com',
            'https://www.tempus.com',
            'https://www.flatiron.com',
            'https://www.paige.ai',
            'https://www.path.ai',
            'https://www.viz.ai',
            'https://www.arterys.com'
        ]
        
        results = []
        for url in curated_startups:
            if url not in self.all_discovered_urls:
                self.all_discovered_urls.add(url)
                results.append({
                    'url': url,
                    'source': 'Curated List',
                    'confidence': 8,
                    'category': 'Curated Health Tech',
                    'country': 'Europe/International',
                    'method': 'Manual Curation'
                })
        
        print(f"✅ Added {len(results)} curated startup URLs")
        return results

    def consolidate_and_rank_results(self, all_results: List[Dict]) -> List[Dict]:
        """Consolidate results and rank by confidence and relevance"""
        print("\n🔄 Consolidating and ranking results...")
        print("-" * 50)
        
        # Remove any remaining duplicates
        unique_results = []
        seen_urls = set()
        
        # Sort by confidence (highest first), then by method priority
        method_priority = {
            'Hardcoded': 5,
            'Manual Curation': 4,
            'Google Search': 3,
            'Enhanced Discovery': 2,
            'Generated': 1
        }
        
        sorted_results = sorted(all_results, key=lambda x: (
            x['confidence'], 
            method_priority.get(x.get('method', 'Unknown'), 0)
        ), reverse=True)
        
        for result in sorted_results:
            url = result['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        print(f"✅ Consolidated to {len(unique_results)} unique URLs")
        return unique_results

    def analyze_discovery_results(self, results: List[Dict]) -> Dict:
        """Analyze the discovery results and provide statistics"""
        print("\n📊 Analyzing discovery results...")
        print("-" * 50)
        
        # Count by method
        method_counts = {}
        confidence_distribution = {}
        category_counts = {}
        country_counts = {}
        
        for result in results:
            method = result.get('method', 'Unknown')
            confidence = result.get('confidence', 0)
            category = result.get('category', 'Unknown')
            country = result.get('country', 'Unknown')
            
            method_counts[method] = method_counts.get(method, 0) + 1
            confidence_distribution[confidence] = confidence_distribution.get(confidence, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            country_counts[country] = country_counts.get(country, 0) + 1
        
        # Calculate quality metrics
        high_confidence = len([r for r in results if r.get('confidence', 0) >= 8])
        medium_confidence = len([r for r in results if 5 <= r.get('confidence', 0) < 8])
        low_confidence = len([r for r in results if r.get('confidence', 0) < 5])
        
        analysis = {
            'total_urls': len(results),
            'method_counts': method_counts,
            'confidence_distribution': confidence_distribution,
            'category_counts': category_counts,
            'country_counts': country_counts,
            'quality_metrics': {
                'high_confidence': high_confidence,
                'medium_confidence': medium_confidence,
                'low_confidence': low_confidence,
                'quality_score': (high_confidence * 3 + medium_confidence * 2 + low_confidence) / len(results) if results else 0
            }
        }
        
        return analysis

    def save_comprehensive_results(self, results: List[Dict], analysis: Dict) -> tuple:
        """Save comprehensive results with analysis"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV file
        csv_filename = f"ultimate_startup_discovery_{timestamp}.csv"
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'source', 'confidence', 'category', 'country', 'method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'url': result['url'],
                    'source': result.get('source', ''),
                    'confidence': result.get('confidence', 0),
                    'category': result.get('category', ''),
                    'country': result.get('country', ''),
                    'method': result.get('method', '')
                })
        
        # JSON file with analysis
        json_filename = f"ultimate_startup_discovery_{timestamp}.json"
        comprehensive_data = {
            'discovery_timestamp': timestamp,
            'total_urls_discovered': len(results),
            'analysis': analysis,
            'urls': results
        }
        
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(comprehensive_data, jsonfile, indent=2, ensure_ascii=False)
        
        # Summary report
        report_filename = f"discovery_report_{timestamp}.txt"
        with open(report_filename, 'w', encoding='utf-8') as report:
            report.write("🚀 ULTIMATE STARTUP DISCOVERY REPORT\n")
            report.write("=" * 60 + "\n\n")
            report.write(f"Discovery Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            report.write(f"Total URLs Discovered: {len(results)}\n\n")
            
            report.write("📊 DISCOVERY METHODS:\n")
            for method, count in analysis['method_counts'].items():
                report.write(f"  • {method}: {count} URLs\n")
            
            report.write(f"\n🎯 QUALITY METRICS:\n")
            report.write(f"  • High Confidence (8-10): {analysis['quality_metrics']['high_confidence']} URLs\n")
            report.write(f"  • Medium Confidence (5-7): {analysis['quality_metrics']['medium_confidence']} URLs\n")
            report.write(f"  • Low Confidence (1-4): {analysis['quality_metrics']['low_confidence']} URLs\n")
            report.write(f"  • Overall Quality Score: {analysis['quality_metrics']['quality_score']:.2f}/3.0\n")
            
            report.write(f"\n🏷️ CATEGORIES:\n")
            for category, count in analysis['category_counts'].items():
                report.write(f"  • {category}: {count} URLs\n")
            
            report.write(f"\n🌍 GEOGRAPHIC DISTRIBUTION:\n")
            for country, count in analysis['country_counts'].items():
                report.write(f"  • {country}: {count} URLs\n")
            
            report.write(f"\n🔝 TOP 20 HIGHEST CONFIDENCE URLs:\n")
            top_urls = sorted(results, key=lambda x: x.get('confidence', 0), reverse=True)[:20]
            for i, url_data in enumerate(top_urls, 1):
                report.write(f"  {i:2d}. {url_data['url']} (confidence: {url_data.get('confidence', 0)})\n")
        
        return csv_filename, json_filename, report_filename

    def run_ultimate_discovery(self) -> Dict:
        """Run the complete ultimate discovery process"""
        print("🚀 ULTIMATE STARTUP DISCOVERY SYSTEM")
        print("=" * 60)
        print("🎯 Comprehensive discovery of digital health startups")
        print("🌍 Focus: Germany and Europe")
        print("🆓 Using only free tools and methods")
        print("")
        
        start_time = time.time()
        all_results = []
        
        # 1. User hardcoded URLs (highest priority)
        print("1️⃣ USER VERIFIED URLs")
        user_results = self.get_user_hardcoded_urls()
        all_results.extend(user_results)
        
        # 2. Enhanced discovery
        print("\n2️⃣ ENHANCED DISCOVERY")
        enhanced_results = self.run_enhanced_discovery()
        all_results.extend(enhanced_results)
        
        # 3. Google search discovery
        print("\n3️⃣ GOOGLE SEARCH DISCOVERY")
        google_results = self.run_google_search_discovery()
        all_results.extend(google_results)
        
        # 4. Curated startup URLs
        print("\n4️⃣ CURATED STARTUP URLs")
        curated_results = self.add_curated_startup_urls()
        all_results.extend(curated_results)
        
        # 5. Consolidate and rank
        print("\n5️⃣ CONSOLIDATION & RANKING")
        final_results = self.consolidate_and_rank_results(all_results)
        
        # 6. Analyze results
        print("\n6️⃣ ANALYSIS")
        analysis = self.analyze_discovery_results(final_results)
        
        # 7. Save results
        print("\n7️⃣ SAVING RESULTS")
        csv_file, json_file, report_file = self.save_comprehensive_results(final_results, analysis)
        
        end_time = time.time()
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 ULTIMATE DISCOVERY COMPLETED!")
        print("=" * 60)
        print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
        print(f"📊 Total URLs discovered: {len(final_results)}")
        print(f"🎯 Quality score: {analysis['quality_metrics']['quality_score']:.2f}/3.0")
        print(f"📁 Files created:")
        print(f"  • CSV: {csv_file}")
        print(f"  • JSON: {json_file}")
        print(f"  • Report: {report_file}")
        
        print(f"\n🔝 Top 10 Discovered URLs:")
        for i, url_data in enumerate(final_results[:10], 1):
            print(f"  {i:2d}. {url_data['url']} ({url_data.get('method', 'Unknown')}, confidence: {url_data.get('confidence', 0)})")
        
        print(f"\n📊 Discovery Summary:")
        for method, count in analysis['method_counts'].items():
            print(f"  • {method}: {count} URLs")
        
        return {
            'total_urls': len(final_results),
            'results': final_results,
            'analysis': analysis,
            'files': {
                'csv': csv_file,
                'json': json_file,
                'report': report_file
            }
        }

def main():
    """Main function"""
    print("🚀 ULTIMATE STARTUP DISCOVERY SYSTEM")
    print("=" * 60)
    print("This system combines multiple discovery methods to find")
    print("digital health startup URLs across Germany and Europe.")
    print("")
    print("⏱️  Estimated time: 5-10 minutes")
    print("🆓 Uses only free tools and methods")
    print("")
    
    try:
        # Initialize and run discovery
        discovery = UltimateStartupDiscovery()
        results = discovery.run_ultimate_discovery()
        
        print(f"\n✨ SUCCESS! Discovered {results['total_urls']} startup URLs")
        print(f"📋 Next steps:")
        print(f"  1. Review the discovery report: {results['files']['report']}")
        print(f"  2. Use existing part2_url_evaluator.py to test URLs")
        print(f"  3. Use existing part3_company_name_extractor.py to extract company names")
        print(f"  4. Build final startup directory")
        
        return results
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Discovery interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Error during discovery: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()
    if results:
        print(f"\n🎊 Ultimate discovery completed successfully!")
    else:
        print(f"\n⚠️ Discovery completed with issues")