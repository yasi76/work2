#!/usr/bin/env python3
"""
Analyze Full Pharmaceutical Dataset
Process the complete 563-entry dataset to find legitimate URLs
"""

import csv
from simple_pharma_cleaner import SimplePharmaDataCleaner

def load_full_dataset():
    """Load the complete discovered URLs dataset"""
    dataset = []
    
    try:
        with open('DISCOVERED_URLS_20250721_144405.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset.append(row)
    except FileNotFoundError:
        print("❌ Full dataset file not found")
        return []
    
    return dataset

def enhance_verified_companies():
    """Add more verified pharmaceutical companies based on research"""
    enhanced_companies = {
        # Existing verified companies
        'ferring.ch': 'Ferring Pharmaceuticals (Switzerland)',
        'ferring.co.uk': 'Ferring Pharmaceuticals UK',
        'jazzpharma.com': 'Jazz Pharmaceuticals (US) - acquired GW Pharmaceuticals',
        'siegfried.ch': 'Siegfried Holding AG (Switzerland) - acquired Knoll operations',
        'bene-arzneimittel.de': 'bene-Arzneimittel GmbH (Germany)',
        'crescentpharma.com': 'Crescent Pharma (UK)',
        
        # Additional research-verified companies (add more as discovered)
        'roche.com': 'F. Hoffmann-La Roche AG (Switzerland)',
        'novartis.com': 'Novartis AG (Switzerland) ', 
        'bayer.com': 'Bayer AG (Germany)',
        'sanofi.com': 'Sanofi S.A. (France)',
        'pfizer.com': 'Pfizer Inc. (US)',
        'gsk.com': 'GlaxoSmithKline plc (UK)',
        'merck.com': 'Merck & Co. (US)',
        'astrazeneca.com': 'AstraZeneca plc (UK/Sweden)',
        'boehringer-ingelheim.com': 'Boehringer Ingelheim (Germany)',
        'takeda.com': 'Takeda Pharmaceutical Company (Japan)',
        'abbvie.com': 'AbbVie Inc. (US)',
        'amgen.com': 'Amgen Inc. (US)',
        'gilead.com': 'Gilead Sciences (US)',
        'biogen.com': 'Biogen Inc. (US)',
        'regeneron.com': 'Regeneron Pharmaceuticals (US)',
        'vertex.com': 'Vertex Pharmaceuticals (US)',
        'alexion.com': 'Alexion Pharmaceuticals (US)',
        'incyte.com': 'Incyte Corporation (US)',
        'biomarin.com': 'BioMarin Pharmaceutical (US)',
        'illumina.com': 'Illumina Inc. (US)',
        'genmab.com': 'Genmab A/S (Denmark)',
        'lundbeck.com': 'H. Lundbeck A/S (Denmark)',
        'novo-nordisk.com': 'Novo Nordisk A/S (Denmark)',
        'orion.fi': 'Orion Corporation (Finland)',
        'gedeon-richter.com': 'Gedeon Richter Plc. (Hungary)',
        'servier.com': 'Servier (France)',
        'ipsen.com': 'Ipsen S.A. (France)',
        'pierre-fabre.com': 'Pierre Fabre (France)',
        'recordati.com': 'Recordati S.p.A. (Italy)',
        'chiesi.com': 'Chiesi Farmaceutici S.p.A. (Italy)',
        'almirall.com': 'Almirall S.A. (Spain)',
        'grifols.com': 'Grifols S.A. (Spain)',
        'teva.com': 'Teva Pharmaceutical Industries (Israel)',
        'dr-reddy.com': 'Dr. Reddy\'s Laboratories (India)',
        'sunpharma.com': 'Sun Pharmaceutical Industries (India)',
        'lupin.com': 'Lupin Limited (India)',
        'cipla.com': 'Cipla Limited (India)',
    }
    
    return enhanced_companies

def main():
    """Analyze the full dataset"""
    print("🔍 FULL PHARMACEUTICAL DATASET ANALYSIS")
    print("=" * 70)
    
    # Load full dataset
    dataset = load_full_dataset()
    print(f"📊 Loaded {len(dataset)} URLs from complete dataset")
    
    if not dataset:
        return
    
    # Create enhanced cleaner
    cleaner = SimplePharmaDataCleaner()
    
    # Enhance with more verified companies
    enhanced_companies = enhance_verified_companies()
    cleaner.verified_companies = enhanced_companies
    
    print(f"🏢 Using database of {len(enhanced_companies)} verified pharmaceutical companies")
    
    # Clean the full dataset
    print(f"\n🧹 Starting comprehensive analysis...")
    results = cleaner.clean_dataset(dataset)
    
    # Display comprehensive results
    print("\n" + "=" * 70)
    print("📋 FULL DATASET ANALYSIS RESULTS")
    print("=" * 70)
    
    summary = results['summary']
    print(f"\n📊 COMPLETE STATISTICS:")
    print(f"  • Total URLs analyzed: {summary['total']:,}")
    print(f"  • ✅ Verified legitimate URLs: {summary['verified']:,} ({summary['data_quality_percent']:.1f}%)")
    print(f"  • ❌ Fabricated URLs: {summary['fabricated']:,} ({summary['fabrication_percent']:.1f}%)")
    print(f"  • 🔍 Need verification: {summary['needs_verification']:,}")
    
    # Show all verified companies found
    if results['verified']:
        print(f"\n✅ ALL VERIFIED PHARMACEUTICAL COMPANIES FOUND ({len(results['verified'])}):")
        unique_domains = set()
        for item in results['verified']:
            domain = item['analysis']['domain']
            if domain not in unique_domains:
                info = item['analysis']['verified_info']
                print(f"  • {info} - {domain}")
                unique_domains.add(domain)
        
        print(f"\n📈 UNIQUE VERIFIED DOMAINS: {len(unique_domains)}")
    
    # Show top fabrication patterns
    if results['fabricated']:
        print(f"\n❌ TOP FABRICATION PATTERNS:")
        pattern_counts = {}
        for item in results['fabricated']:
            reason = item['analysis']['fake_domain_reason'] or item['analysis']['fake_wikipedia_reason']
            if reason:
                pattern_counts[reason] = pattern_counts.get(reason, 0) + 1
        
        # Show top 10 patterns
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns[:10]:
            print(f"  • {pattern}: {count:,} instances")
    
    # Save comprehensive results
    cleaner.save_results(results, "full_dataset_analysis")
    
    # Create final count summary
    print(f"\n🎯 FINAL URL COUNT SUMMARY:")
    print(f"  📥 Original dataset: {len(dataset):,} URLs")
    print(f"  ✅ Legitimate companies: {len(set(item['analysis']['domain'] for item in results['verified'])):,} unique domains")
    print(f"  ❌ Fabricated entries: {len(results['fabricated']):,} URLs")
    print(f"  🔍 Requiring verification: {len(results['needs_verification']):,} URLs")
    print(f"  📊 Data quality: {summary['data_quality_percent']:.1f}% verified")
    
    return results

if __name__ == "__main__":
    results = main()