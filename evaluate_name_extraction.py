#!/usr/bin/env python3
"""
Company Name Extraction Accuracy Evaluator
Compares extracted company names against ground truth data to measure accuracy
"""

import json
import csv
import argparse
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Ground truth data
GROUND_TRUTH = {
    "https://www.acalta.de": "Acalta GmbH",
    "https://www.actimi.com": "Actimi GmbH",
    "https://www.emmora.de": "Ahorn AG",
    "https://www.alfa-ai.com": "ALFA AI GmbH",
    "https://www.apheris.com": "apheris AI GmbH",
    "https://www.aporize.com/": "Aporize",
    "https://www.arztlena.com/": "Artificy GmbH",
    "https://shop.getnutrio.com/": "Aurora Life Sciene GmbH",
    "https://www.auta.health/": "Auta Health UG",
    "https://visioncheckout.com/": "auvisus GmbH",
    "https://www.avayl.tech/": "AVAYL GmbH",
    "https://www.avimedical.com/avi-impact": "Avi Medical Operations GmbH",
    "https://de.becureglobal.com/": "BECURE GmbH",
    "https://bellehealth.co/de/": "Belle Health GmbH",
    "https://www.biotx.ai/": "biotx.ai GmbH",
    "https://www.brainjo.de/": "brainjo GmbH",
    "https://brea.app/": "Brea Health GmbH",
    "https://breathment.com/": "Breathment GmbH",
    "https://de.caona.eu/": "Caona Health GmbH",
    "https://www.careanimations.de/": "CAREANIMATIONS GmbH",
    "https://sfs-healthcare.com": "Change IT Solutions GmbH",
    "https://www.climedo.de/": "Climedo Health GmbH",
    "https://www.cliniserve.de/": "Clinicserve GmbH",
    "https://cogthera.de/#erfahren": "Cogthera GmbH",
    "https://www.comuny.de/": "comuny GmbH",
    "https://curecurve.de/elina-app/": "CureCurve Medical AI GmbH",
    "https://www.cynteract.com/de/rehabilitation": "Cynteract GmbH",
    "https://www.healthmeapp.de/de/": "Declareme GmbH",
    "https://deepeye.ai/": "deepeye medical GmbH",
    "https://www.deepmentation.ai/": "deepmentation UG",
    "https://denton-systems.de/": "Denton Systems GmbH",
    "https://www.derma2go.com/": "derma2go Deutschland GmbH",
    "https://www.dianovi.com/": "dianovi GmbH (ehem. MySympto)",
    "http://dopavision.com/": "Dopavision GmbH",
    "https://www.dpv-analytics.com/": "dpv-analytics GmbH",
    "http://www.ecovery.de/": "eCovery GmbH",
    "https://elixionmedical.com/": "Elixion Medical",
    "https://www.empident.de/": "Empident GmbH",
    "https://eye2you.ai/": "eye2you",
    "https://www.fitwhit.de": "FitwHit & LABOR FÜR BIOMECHANIK der JLU-Gießen",
    "https://www.floy.com/": "Floy GmbH",
    "https://fyzo.de/assistant/": "fyzo GmbH",
    "https://www.gesund.de/app": "gesund.de GmbH & Co. KG",
    "https://www.glaice.de/": "GLACIE Health UG",
    "https://gleea.de/": "Gleea Educational Software GmbH",
    "https://www.guidecare.de/": "GuideCare GmbH",
    "https://www.apodienste.com/": "Healthy Codes GmbH",
    "https://www.help-app.de/": "Help Mee Schmerztherapie GmbH",
    "https://www.heynanny.com/": "heynannyly GmbH",
    "https://incontalert.de/": "inContAlert GmbH",
    "https://home.informme.info/": "InformMe GmbH",
    "https://www.kranushealth.com/de/therapien/haeufiger-harndrang": "Kranus Health GmbH",
    "https://www.kranushealth.com/de/therapien/inkontinenz": "Kranus Health GmbH",
}


class NameEvaluator:
    def __init__(self, ground_truth: Dict[str, str]):
        self.ground_truth = ground_truth
        self.results = []
        
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison (remove trailing slashes, etc.)"""
        if not url:
            return ""
        
        # Parse URL
        parsed = urlparse(url.lower())
        
        # Reconstruct without fragment and with normalized path
        path = parsed.path.rstrip('/')
        if not path:
            path = '/'
            
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        return normalized
    
    def normalize_name(self, name: str) -> str:
        """Normalize company name for comparison"""
        if not name:
            return ""
        
        # Strip whitespace and convert to lowercase
        normalized = name.strip().lower()
        
        # Remove common company suffixes for comparison (optional)
        # Uncomment if you want to ignore legal suffixes in comparison
        # suffixes = ['gmbh', 'ag', 'ug', 'kg', 'ohg', 'e.v.', 'ltd', 'inc', 'corp']
        # for suffix in suffixes:
        #     normalized = normalized.replace(f' {suffix}', '').replace(f' {suffix}.', '')
        
        return normalized
    
    def calculate_similarity(self, extracted: str, ground_truth: str) -> float:
        """Calculate similarity score between two strings"""
        if not extracted or not ground_truth:
            return 0.0
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, 
                               self.normalize_name(extracted), 
                               self.normalize_name(ground_truth)).ratio()
    
    def evaluate_extraction(self, startup_data: Dict) -> Optional[Dict]:
        """Evaluate a single startup's name extraction"""
        # Get URL from startup data
        url = startup_data.get('url', '')
        if not url:
            url = startup_data.get('final_url', '')
        
        if not url:
            return None
        
        # Normalize URL for lookup
        normalized_url = self.normalize_url(url)
        
        # Check all ground truth URLs for a match
        for gt_url, gt_name in self.ground_truth.items():
            if self.normalize_url(gt_url) == normalized_url:
                extracted_name = startup_data.get('company_name', 'Unknown')
                
                # Check if names match (case-insensitive)
                is_correct = self.normalize_name(extracted_name) == self.normalize_name(gt_name)
                
                # Calculate similarity
                similarity = self.calculate_similarity(extracted_name, gt_name)
                
                result = {
                    'url': url,
                    'ground_truth_url': gt_url,
                    'extracted_name': extracted_name,
                    'ground_truth_name': gt_name,
                    'is_correct': is_correct,
                    'similarity_score': round(similarity, 3),
                    'extraction_method': startup_data.get('name_extraction_method', 'unknown')
                }
                
                return result
        
        return None
    
    def evaluate_file(self, input_file: str) -> Tuple[List[Dict], Dict]:
        """Evaluate all startups in a file"""
        logger.info(f"Loading data from {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different data formats
        if isinstance(data, list):
            startups = data
        elif isinstance(data, dict) and 'urls' in data:
            startups = data['urls']
        else:
            startups = []
            for key, value in data.items():
                if isinstance(value, dict) and 'url' in value:
                    startups.append(value)
        
        # Evaluate each startup
        self.results = []
        for startup in startups:
            result = self.evaluate_extraction(startup)
            if result:
                self.results.append(result)
        
        # Calculate statistics
        stats = self.calculate_statistics()
        
        return self.results, stats
    
    def calculate_statistics(self) -> Dict:
        """Calculate evaluation statistics"""
        if not self.results:
            return {
                'total_evaluated': 0,
                'correct': 0,
                'incorrect': 0,
                'accuracy': 0.0,
                'average_similarity': 0.0
            }
        
        correct = sum(1 for r in self.results if r['is_correct'])
        incorrect = len(self.results) - correct
        accuracy = (correct / len(self.results)) * 100
        avg_similarity = sum(r['similarity_score'] for r in self.results) / len(self.results)
        
        # Group by extraction method
        method_stats = {}
        for result in self.results:
            method = result['extraction_method']
            if method not in method_stats:
                method_stats[method] = {'total': 0, 'correct': 0}
            method_stats[method]['total'] += 1
            if result['is_correct']:
                method_stats[method]['correct'] += 1
        
        return {
            'total_evaluated': len(self.results),
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': round(accuracy, 2),
            'average_similarity': round(avg_similarity, 3),
            'method_stats': method_stats
        }
    
    def print_results(self, stats: Dict, use_color: bool = True):
        """Print evaluation results to console"""
        if not use_color:
            Colors.GREEN = Colors.RED = Colors.YELLOW = Colors.BLUE = Colors.RESET = Colors.BOLD = ''
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
        print(f"{Colors.BOLD}COMPANY NAME EXTRACTION EVALUATION REPORT{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")
        
        # Overall statistics
        print(f"{Colors.CYAN}OVERALL STATISTICS:{Colors.RESET}")
        print(f"Total URLs in ground truth: {len(self.ground_truth)}")
        print(f"Total URLs evaluated: {stats['total_evaluated']}")
        print(f"Coverage: {(stats['total_evaluated']/len(self.ground_truth)*100):.1f}%\n")
        
        print(f"{Colors.GREEN}Correct extractions: {stats['correct']}{Colors.RESET}")
        print(f"{Colors.RED}Incorrect extractions: {stats['incorrect']}{Colors.RESET}")
        print(f"{Colors.BOLD}Accuracy: {stats['accuracy']}%{Colors.RESET}")
        print(f"Average similarity score: {stats['average_similarity']}\n")
        
        # Method statistics
        if stats['method_stats']:
            print(f"{Colors.CYAN}EXTRACTION METHOD PERFORMANCE:{Colors.RESET}")
            for method, method_stat in sorted(stats['method_stats'].items(), 
                                            key=lambda x: x[1]['correct']/x[1]['total'] if x[1]['total'] > 0 else 0, 
                                            reverse=True):
                accuracy = (method_stat['correct'] / method_stat['total'] * 100) if method_stat['total'] > 0 else 0
                print(f"  {method}: {method_stat['correct']}/{method_stat['total']} ({accuracy:.1f}%)")
            print()
        
        # Individual results
        print(f"{Colors.CYAN}DETAILED RESULTS:{Colors.RESET}")
        print(f"{'='*80}")
        
        # Sort results: incorrect first, then by URL
        sorted_results = sorted(self.results, key=lambda x: (x['is_correct'], x['url']))
        
        for result in sorted_results:
            status_color = Colors.GREEN if result['is_correct'] else Colors.RED
            status_text = "✓ CORRECT" if result['is_correct'] else "✗ INCORRECT"
            
            print(f"\n{Colors.BLUE}URL:{Colors.RESET} {result['url']}")
            print(f"{Colors.YELLOW}Extracted:{Colors.RESET} {result['extracted_name']}")
            print(f"{Colors.YELLOW}Ground Truth:{Colors.RESET} {result['ground_truth_name']}")
            print(f"{status_color}Status: {status_text}{Colors.RESET}")
            print(f"Similarity: {result['similarity_score']} | Method: {result['extraction_method']}")
            print(f"{'-'*80}")
    
    def save_results(self, output_prefix: str):
        """Save evaluation results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save CSV report
        csv_file = f"{output_prefix}_evaluation_report_{timestamp}.csv"
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            if self.results:
                fieldnames = ['url', 'extracted_name', 'ground_truth_name', 'is_correct', 
                            'similarity_score', 'extraction_method']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.results:
                    writer.writerow({
                        'url': result['url'],
                        'extracted_name': result['extracted_name'],
                        'ground_truth_name': result['ground_truth_name'],
                        'is_correct': 'Correct' if result['is_correct'] else 'Incorrect',
                        'similarity_score': result['similarity_score'],
                        'extraction_method': result['extraction_method']
                    })
        
        logger.info(f"Saved CSV report to {csv_file}")
        
        # Save JSON report
        json_file = f"{output_prefix}_evaluation_report_{timestamp}.json"
        stats = self.calculate_statistics()
        
        report_data = {
            'evaluation_timestamp': timestamp,
            'statistics': stats,
            'results': self.results,
            'ground_truth_size': len(self.ground_truth)
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON report to {json_file}")
        
        # Save incorrect extractions for review
        incorrect_file = f"{output_prefix}_incorrect_extractions_{timestamp}.txt"
        incorrect_results = [r for r in self.results if not r['is_correct']]
        
        if incorrect_results:
            with open(incorrect_file, 'w', encoding='utf-8') as f:
                f.write("INCORRECT EXTRACTIONS FOR REVIEW\n")
                f.write("="*80 + "\n\n")
                
                for result in incorrect_results:
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"Extracted: {result['extracted_name']}\n")
                    f.write(f"Expected: {result['ground_truth_name']}\n")
                    f.write(f"Method: {result['extraction_method']}\n")
                    f.write(f"Similarity: {result['similarity_score']}\n")
                    f.write("-"*40 + "\n\n")
            
            logger.info(f"Saved incorrect extractions to {incorrect_file}")


def main():
    parser = argparse.ArgumentParser(description='Evaluate company name extraction accuracy')
    parser.add_argument('input_file', help='JSON file with extracted company names')
    parser.add_argument('--output-prefix', default='name', help='Output file prefix')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--ground-truth', help='Custom ground truth JSON file')
    parser.add_argument('--fuzzy-threshold', type=float, default=0.8, 
                       help='Similarity threshold for fuzzy matching (0-1)')
    
    args = parser.parse_args()
    
    # Load custom ground truth if provided
    ground_truth = GROUND_TRUTH
    if args.ground_truth:
        try:
            with open(args.ground_truth, 'r', encoding='utf-8') as f:
                ground_truth = json.load(f)
            logger.info(f"Loaded custom ground truth from {args.ground_truth}")
        except Exception as e:
            logger.error(f"Failed to load ground truth file: {e}")
            return
    
    # Create evaluator and run evaluation
    evaluator = NameEvaluator(ground_truth)
    results, stats = evaluator.evaluate_file(args.input_file)
    
    # Print results
    evaluator.print_results(stats, use_color=not args.no_color)
    
    # Save results
    evaluator.save_results(args.output_prefix)
    
    # Print summary
    print(f"\n{Colors.BOLD if not args.no_color else ''}EVALUATION COMPLETE{Colors.RESET if not args.no_color else ''}")
    print(f"Files saved with prefix: {args.output_prefix}_evaluation_report_*")


if __name__ == "__main__":
    main()