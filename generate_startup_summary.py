#!/usr/bin/env python3
"""
Generate comprehensive summary and analytics from validated digital health startup data
"""

import json
import csv
from collections import defaultdict, Counter
from datetime import datetime
import argparse
import logging
from typing import Dict, List, Tuple
from urllib.parse import urlparse

# Optional imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import matplotlib
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StartupSummaryGenerator:
    def __init__(self):
        self.stats = defaultdict(int)
        self.lists = defaultdict(list)
        self.counters = defaultdict(Counter)
        
    def analyze_startups(self, startups: List[Dict]) -> Dict:
        """Analyze startup data and generate comprehensive statistics"""
        
        # Basic counts
        self.stats['total_urls'] = len(startups)
        self.stats['live_websites'] = sum(1 for s in startups if s.get('is_live', False))
        self.stats['dead_websites'] = self.stats['total_urls'] - self.stats['live_websites']
        self.stats['health_related'] = sum(1 for s in startups if s.get('is_health_related', False))
        self.stats['non_health_related'] = self.stats['live_websites'] - self.stats['health_related']
        self.stats['suspicious_pages'] = sum(1 for s in startups if s.get('is_suspicious', False))
        
        # Success rate
        self.stats['success_rate'] = (self.stats['live_websites'] / self.stats['total_urls'] * 100) if self.stats['total_urls'] > 0 else 0
        self.stats['health_rate'] = (self.stats['health_related'] / self.stats['live_websites'] * 100) if self.stats['live_websites'] > 0 else 0
        
        # Analyze each startup
        for startup in startups:
            self._analyze_single_startup(startup)
        
        # Generate summary
        summary = {
            'generation_timestamp': datetime.now().isoformat(),
            'overview': {
                'total_urls_analyzed': self.stats['total_urls'],
                'live_websites': self.stats['live_websites'],
                'dead_websites': self.stats['dead_websites'],
                'health_related': self.stats['health_related'],
                'non_health_related': self.stats['non_health_related'],
                'suspicious_pages': self.stats['suspicious_pages'],
                'success_rate_percent': round(self.stats['success_rate'], 2),
                'health_rate_percent': round(self.stats['health_rate'], 2)
            },
            'by_region': dict(self.counters['regions']),
            'by_language': dict(self.counters['languages']),
            'by_error_type': dict(self.counters['errors']),
            'by_extraction_method': dict(self.counters['name_methods']),
            'by_discovery_method': dict(self.counters['discovery_methods']),
            'by_category': dict(self.counters['categories']),
            'health_score_distribution': self._get_score_distribution(),
            'top_keywords': self.counters['keywords'].most_common(20),
            'verified_health_startups': self._get_verified_startups(startups),
            'dead_urls': self._get_dead_urls(startups),
            'suspicious_urls': self._get_suspicious_urls(startups)
        }
        
        return summary
    
    def _analyze_single_startup(self, startup: Dict):
        """Analyze a single startup entry"""
        # Region analysis
        region = startup.get('region', 'Unknown')
        self.counters['regions'][region] += 1
        
        # Language analysis
        language = startup.get('language', 'unknown')
        self.counters['languages'][language] += 1
        
        # Error analysis
        if not startup.get('is_live', False):
            error = startup.get('error', 'Unknown Error')
            self.counters['errors'][error] += 1
        
        # Name extraction method
        if 'name_extraction_method' in startup:
            self.counters['name_methods'][startup['name_extraction_method']] += 1
        
        # Discovery method
        method = startup.get('method', 'unknown')
        self.counters['discovery_methods'][method] += 1
        
        # Category
        category = startup.get('category', 'uncategorized')
        self.counters['categories'][category] += 1
        
        # Keywords
        keywords = startup.get('matched_keywords', [])
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        for keyword in keywords:
            self.counters['keywords'][keyword] += 1
        
        # Health scores
        score = startup.get('health_relevance_score', 0)
        self.lists['health_scores'].append(score)
    
    def _get_score_distribution(self) -> Dict:
        """Get health score distribution"""
        scores = self.lists['health_scores']
        if not scores:
            return {}
        
        distribution = {}
        for i in range(11):  # 0-10
            distribution[str(i)] = scores.count(i)
        
        return distribution
    
    def _get_verified_startups(self, startups: List[Dict]) -> List[Dict]:
        """Get list of verified health startups"""
        verified = []
        for s in startups:
            if s.get('is_live') and s.get('is_health_related') and not s.get('is_suspicious'):
                verified.append({
                    'name': s.get('company_name', 'Unknown'),
                    'url': s.get('final_url') or s.get('url'),
                    'category': s.get('category', 'uncategorized'),
                    'region': s.get('region', 'Unknown'),
                    'health_score': s.get('health_relevance_score', 0),
                    'language': s.get('language', 'unknown')
                })
        
        # Sort by health score
        return sorted(verified, key=lambda x: x['health_score'], reverse=True)
    
    def _get_dead_urls(self, startups: List[Dict]) -> List[Dict]:
        """Get list of dead URLs"""
        dead = []
        for s in startups:
            if not s.get('is_live', False):
                dead.append({
                    'url': s.get('url'),
                    'error': s.get('error', 'Unknown'),
                    'category': s.get('category', 'uncategorized')
                })
        return dead
    
    def _get_suspicious_urls(self, startups: List[Dict]) -> List[Dict]:
        """Get list of suspicious URLs"""
        suspicious = []
        for s in startups:
            if s.get('is_suspicious', False):
                suspicious.append({
                    'url': s.get('final_url') or s.get('url'),
                    'title': s.get('page_title', ''),
                    'reason': 'Parking page or suspicious content'
                })
        return suspicious
    
    def generate_visualizations(self, summary: Dict, output_prefix: str):
        """Generate visualization charts"""
        if not HAS_MATPLOTLIB:
            logger.warning("Matplotlib not installed. Skipping visualizations.")
            return
            
        try:
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # Set style
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Digital Health Startup Analysis', fontsize=16)
            
            # 1. Overview pie chart
            ax1 = axes[0, 0]
            overview_data = [
                summary['overview']['health_related'],
                summary['overview']['non_health_related'],
                summary['overview']['dead_websites']
            ]
            overview_labels = ['Health-Related', 'Not Health-Related', 'Dead/Unreachable']
            colors = ['#2ecc71', '#e74c3c', '#95a5a6']
            ax1.pie(overview_data, labels=overview_labels, autopct='%1.1f%%', colors=colors)
            ax1.set_title('Website Status Distribution')
            
            # 2. Region distribution
            ax2 = axes[0, 1]
            regions = list(summary['by_region'].keys())
            region_counts = list(summary['by_region'].values())
            ax2.bar(regions, region_counts)
            ax2.set_title('Distribution by Region')
            ax2.set_xlabel('Region')
            ax2.set_ylabel('Count')
            
            # 3. Health score distribution
            ax3 = axes[1, 0]
            scores = list(range(11))
            score_counts = [summary['health_score_distribution'].get(str(i), 0) for i in scores]
            ax3.bar(scores, score_counts, color='skyblue')
            ax3.set_title('Health Relevance Score Distribution')
            ax3.set_xlabel('Health Score')
            ax3.set_ylabel('Count')
            ax3.set_xticks(scores)
            
            # 4. Top keywords
            ax4 = axes[1, 1]
            if summary['top_keywords']:
                keywords = [k[0] for k in summary['top_keywords'][:10]]
                keyword_counts = [k[1] for k in summary['top_keywords'][:10]]
                ax4.barh(keywords, keyword_counts)
                ax4.set_title('Top 10 Health Keywords')
                ax4.set_xlabel('Frequency')
            else:
                ax4.text(0.5, 0.5, 'No keywords found', ha='center', va='center')
                ax4.set_title('Top Health Keywords')
            
            plt.tight_layout()
            plt.savefig(f'{output_prefix}_analysis.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved visualization to {output_prefix}_analysis.png")
            
        except ImportError:
            logger.warning("Matplotlib/Seaborn not installed. Skipping visualizations.")
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")


def generate_markdown_report(summary: Dict, output_file: str):
    """Generate a markdown report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Digital Health Startup Analysis Report\n\n")
        f.write(f"Generated: {summary['generation_timestamp']}\n\n")
        
        # Overview
        f.write("## Overview\n\n")
        overview = summary['overview']
        f.write(f"- **Total URLs Analyzed:** {overview['total_urls_analyzed']}\n")
        f.write(f"- **Live Websites:** {overview['live_websites']} ({overview['success_rate_percent']}%)\n")
        f.write(f"- **Dead/Unreachable:** {overview['dead_websites']}\n")
        f.write(f"- **Health-Related:** {overview['health_related']} ({overview['health_rate_percent']}% of live sites)\n")
        f.write(f"- **Suspicious Pages:** {overview['suspicious_pages']}\n\n")
        
        # Regional Distribution
        f.write("## Regional Distribution\n\n")
        f.write("| Region | Count | Percentage |\n")
        f.write("|--------|-------|------------|\n")
        total = sum(summary['by_region'].values())
        for region, count in sorted(summary['by_region'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            f.write(f"| {region} | {count} | {pct:.1f}% |\n")
        f.write("\n")
        
        # Language Distribution
        f.write("## Language Distribution\n\n")
        f.write("| Language | Count |\n")
        f.write("|----------|-------|\n")
        for lang, count in sorted(summary['by_language'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {lang} | {count} |\n")
        f.write("\n")
        
        # Top Health Keywords
        f.write("## Top Health Keywords\n\n")
        if summary['top_keywords']:
            f.write("| Keyword | Frequency |\n")
            f.write("|---------|-----------||\n")
            for keyword, count in summary['top_keywords']:
                f.write(f"| {keyword} | {count} |\n")
        else:
            f.write("No health keywords found.\n")
        f.write("\n")
        
        # Verified Health Startups
        f.write("## Verified Health Startups\n\n")
        if summary['verified_health_startups']:
            f.write("| Company | URL | Category | Region | Health Score |\n")
            f.write("|---------|-----|----------|--------|---------------|\n")
            for startup in summary['verified_health_startups'][:50]:  # Top 50
                f.write(f"| {startup['name']} | {startup['url']} | {startup['category']} | {startup['region']} | {startup['health_score']} |\n")
        else:
            f.write("No verified health startups found.\n")
        f.write("\n")
        
        # Error Analysis
        if summary['by_error_type']:
            f.write("## Error Analysis\n\n")
            f.write("| Error Type | Count |\n")
            f.write("|------------|-------|\n")
            for error, count in sorted(summary['by_error_type'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"| {error} | {count} |\n")
            f.write("\n")
    
    logger.info(f"Saved markdown report to {output_file}")


def generate_excel_report(summary: Dict, startups: List[Dict], output_file: str):
    """Generate an Excel report with multiple sheets"""
    if not HAS_PANDAS:
        logger.warning("pandas/openpyxl not installed. Skipping Excel report.")
        return
        
    try:
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Overview sheet
            overview_df = pd.DataFrame([summary['overview']])
            overview_df.to_excel(writer, sheet_name='Overview', index=False)
            
            # All startups sheet
            startups_df = pd.DataFrame(startups)
            startups_df.to_excel(writer, sheet_name='All Startups', index=False)
            
            # Verified health startups
            if summary['verified_health_startups']:
                verified_df = pd.DataFrame(summary['verified_health_startups'])
                verified_df.to_excel(writer, sheet_name='Verified Health', index=False)
            
            # Regional analysis
            region_df = pd.DataFrame(list(summary['by_region'].items()), columns=['Region', 'Count'])
            region_df.to_excel(writer, sheet_name='By Region', index=False)
            
            # Error analysis
            if summary['by_error_type']:
                error_df = pd.DataFrame(list(summary['by_error_type'].items()), columns=['Error Type', 'Count'])
                error_df.to_excel(writer, sheet_name='Errors', index=False)
        
        logger.info(f"Saved Excel report to {output_file}")
        
    except ImportError:
        logger.warning("pandas/openpyxl not installed. Skipping Excel report.")
    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive summary from validated startup data')
    parser.add_argument('input_file', help='Validated JSON file from evaluate_health_startups.py')
    parser.add_argument('--output-prefix', default='startup_summary', help='Output file prefix')
    parser.add_argument('--no-viz', action='store_true', help='Skip visualization generation')
    parser.add_argument('--excel', action='store_true', help='Generate Excel report')
    
    args = parser.parse_args()
    
    # Load validated data
    logger.info(f"Loading validated data from {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        startups = json.load(f)
    
    # Handle different formats
    if isinstance(startups, dict):
        if 'urls' in startups:
            startups = startups['urls']
        else:
            # Try to extract startup list from dict
            startup_list = []
            for key, value in startups.items():
                if isinstance(value, dict) and 'url' in value:
                    startup_list.append(value)
            startups = startup_list
    
    if not isinstance(startups, list):
        logger.error("Invalid input format. Expected a list of startups or a dict with 'urls' key.")
        return
    
    logger.info(f"Analyzing {len(startups)} startups")
    
    # Generate summary
    generator = StartupSummaryGenerator()
    summary = generator.analyze_startups(startups)
    
    # Save JSON summary
    summary_file = f"{args.output_prefix}_analysis.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved summary to {summary_file}")
    
    # Generate markdown report
    markdown_file = f"{args.output_prefix}_report.md"
    generate_markdown_report(summary, markdown_file)
    
    # Generate visualizations
    if not args.no_viz:
        generator.generate_visualizations(summary, args.output_prefix)
    
    # Generate Excel report
    if args.excel:
        excel_file = f"{args.output_prefix}_report.xlsx"
        generate_excel_report(summary, startups, excel_file)
    
    # Print summary to console
    print("\n" + "="*50)
    print("DIGITAL HEALTH STARTUP ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total URLs analyzed: {summary['overview']['total_urls_analyzed']}")
    print(f"Live websites: {summary['overview']['live_websites']} ({summary['overview']['success_rate_percent']}%)")
    print(f"Health-related: {summary['overview']['health_related']} ({summary['overview']['health_rate_percent']}% of live)")
    print(f"Top regions: {', '.join(list(summary['by_region'].keys())[:3])}")
    print(f"Verified health startups: {len(summary['verified_health_startups'])}")
    print("="*50)


if __name__ == "__main__":
    main()