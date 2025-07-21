#!/usr/bin/env python3
"""
Digital Health Startup URL Evaluator
Evaluates a list of discovered startup URLs to check if they are live, 
health-related, and relevant to the European/German digital health ecosystem.
"""

import json
import csv
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import logging
from datetime import datetime
import re
from typing import Dict, List, Tuple, Optional
import concurrent.futures
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup_evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Health-related keywords for multiple languages
HEALTH_KEYWORDS = {
    'english': [
        'health', 'medical', 'care', 'therapy', 'doctor', 'patient', 
        'wellness', 'mental', 'clinical', 'pharma', 'medicine', 'hospital',
        'diagnostic', 'treatment', 'healthcare', 'telemedicine', 'digital health',
        'biotech', 'medtech', 'ehealth', 'mhealth'
    ],
    'german': [
        'gesundheit', 'medizin', 'pflege', 'therapie', 'arzt', 'ärztin',
        'patient', 'wellness', 'mental', 'klinik', 'pharma', 'krankenhaus',
        'diagnostik', 'behandlung', 'gesundheitswesen', 'telemedizin',
        'digital health', 'biotech', 'medtech', 'ehealth', 'mhealth',
        'praxis', 'apotheke', 'gesundheitsapp'
    ],
    'french': [
        'santé', 'médical', 'soin', 'thérapie', 'médecin', 'patient',
        'bien-être', 'mental', 'clinique', 'pharma', 'hôpital',
        'diagnostic', 'traitement', 'télémédecine'
    ],
    'dutch': [
        'gezondheid', 'medisch', 'zorg', 'therapie', 'arts', 'patiënt',
        'welzijn', 'mentaal', 'kliniek', 'ziekenhuis', 'behandeling'
    ]
}

# European ccTLDs
EUROPEAN_CCTLDS = [
    '.de', '.at', '.ch', '.fr', '.nl', '.be', '.lu', '.dk', '.se', '.no',
    '.fi', '.es', '.pt', '.it', '.gr', '.pl', '.cz', '.sk', '.hu', '.ro',
    '.bg', '.hr', '.si', '.ee', '.lv', '.lt', '.eu'
]

# User agent to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


class HealthStartupEvaluator:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def evaluate_url(self, startup_data: Dict) -> Dict:
        """Evaluate a single startup URL"""
        url = startup_data.get('url', '')
        if not url:
            logger.warning("No URL provided in startup data")
            return self._create_error_result(startup_data, "No URL provided")
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        logger.info(f"Evaluating: {url}")
        
        try:
            # Send GET request
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            # Process successful response
            if response.status_code == 200:
                return self._process_successful_response(startup_data, response)
            else:
                return self._create_result(
                    startup_data, 
                    status_code=response.status_code,
                    is_live=False,
                    error=f"HTTP {response.status_code}"
                )
                
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for {url}")
            return self._create_error_result(startup_data, "Timeout")
        except requests.exceptions.SSLError:
            logger.warning(f"SSL Error for {url}")
            return self._create_error_result(startup_data, "SSL Error")
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection Error for {url}")
            return self._create_error_result(startup_data, "Connection Error")
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return self._create_error_result(startup_data, f"Error: {str(e)}")
    
    def _process_successful_response(self, startup_data: Dict, response: requests.Response) -> Dict:
        """Process a successful HTTP response"""
        final_url = response.url
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title and description
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        # Detect language
        language = self._detect_language(soup, response)
        
        # Calculate health relevance score
        combined_text = f"{title} {description}".lower()
        health_score, matched_keywords = self._calculate_health_score(combined_text, language)
        
        # Determine region
        region = self._determine_region(final_url, language)
        
        # Check if it's a parking page or suspicious
        is_suspicious = self._is_suspicious_page(title, description, soup)
        
        return self._create_result(
            startup_data,
            status_code=200,
            final_url=final_url,
            page_title=title,
            meta_description=description,
            health_relevance_score=health_score,
            is_live=True,
            is_health_related=(health_score >= 3),
            language=language,
            region=region,
            matched_keywords=matched_keywords,
            is_suspicious=is_suspicious
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description as fallback
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def _detect_language(self, soup: BeautifulSoup, response: requests.Response) -> str:
        """Detect page language"""
        # Check HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            lang = html_tag['lang'].lower()[:2]
            return lang
        
        # Check Content-Language header
        content_lang = response.headers.get('Content-Language', '').lower()[:2]
        if content_lang:
            return content_lang
        
        return 'unknown'
    
    def _calculate_health_score(self, text: str, language: str) -> Tuple[int, List[str]]:
        """Calculate health relevance score based on keyword matches"""
        matched_keywords = []
        
        # Determine which keyword sets to use
        keyword_sets = ['english']  # Always check English keywords
        
        if language == 'de':
            keyword_sets.append('german')
        elif language == 'fr':
            keyword_sets.append('french')
        elif language == 'nl':
            keyword_sets.append('dutch')
        elif language in ['at', 'ch']:  # Austrian and Swiss German
            keyword_sets.append('german')
        
        # Count keyword matches
        for keyword_set in keyword_sets:
            if keyword_set in HEALTH_KEYWORDS:
                for keyword in HEALTH_KEYWORDS[keyword_set]:
                    if keyword.lower() in text:
                        matched_keywords.append(keyword)
        
        # Remove duplicates
        matched_keywords = list(set(matched_keywords))
        
        # Calculate score (0-10)
        score = min(10, len(matched_keywords))
        
        return score, matched_keywords
    
    def _determine_region(self, url: str, language: str) -> str:
        """Determine region based on ccTLD and language"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check ccTLD
        for tld in EUROPEAN_CCTLDS:
            if domain.endswith(tld):
                if tld == '.de' or tld == '.at' or tld == '.ch':
                    return 'DACH'
                else:
                    return 'Europe'
        
        # Check language
        if language in ['de']:
            return 'DACH'
        elif language in ['fr', 'nl', 'es', 'it', 'pt']:
            return 'Europe'
        
        return 'Unknown'
    
    def _is_suspicious_page(self, title: str, description: str, soup: BeautifulSoup) -> bool:
        """Check if the page is suspicious (parking page, etc.)"""
        suspicious_indicators = [
            'domain for sale',
            'domain parking',
            'buy this domain',
            'diese domain steht zum verkauf',
            'domain zu verkaufen',
            'coming soon',
            'under construction'
        ]
        
        combined_text = f"{title} {description}".lower()
        
        for indicator in suspicious_indicators:
            if indicator in combined_text:
                return True
        
        # Check for very short content
        body_text = soup.get_text().strip()
        if len(body_text) < 100:
            return True
        
        return False
    
    def _create_result(self, startup_data: Dict, **kwargs) -> Dict:
        """Create a result dictionary"""
        result = startup_data.copy()
        result.update({
            'evaluation_timestamp': datetime.now().isoformat(),
            'status_code': kwargs.get('status_code', 0),
            'final_url': kwargs.get('final_url', ''),
            'page_title': kwargs.get('page_title', ''),
            'meta_description': kwargs.get('meta_description', ''),
            'health_relevance_score': kwargs.get('health_relevance_score', 0),
            'is_live': kwargs.get('is_live', False),
            'is_health_related': kwargs.get('is_health_related', False),
            'language': kwargs.get('language', 'unknown'),
            'region': kwargs.get('region', 'Unknown'),
            'matched_keywords': kwargs.get('matched_keywords', []),
            'is_suspicious': kwargs.get('is_suspicious', False),
            'error': kwargs.get('error', '')
        })
        return result
    
    def _create_error_result(self, startup_data: Dict, error: str) -> Dict:
        """Create an error result"""
        return self._create_result(
            startup_data,
            is_live=False,
            error=error
        )


def load_input_data(file_path: str) -> List[Dict]:
    """Load startup data from JSON or CSV file"""
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif file_path.endswith('.csv'):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    else:
        raise ValueError("Input file must be .json or .csv")


def save_results(results: List[Dict], output_prefix: str):
    """Save results to both JSON and CSV files"""
    # Save JSON
    json_file = f"{output_prefix}_validated.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON results to {json_file}")
    
    # Save CSV
    csv_file = f"{output_prefix}_validated.csv"
    if results:
        # Flatten matched_keywords for CSV
        for result in results:
            result['matched_keywords'] = ', '.join(result.get('matched_keywords', []))
        
        keys = results[0].keys()
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        logger.info(f"Saved CSV results to {csv_file}")


def evaluate_startups_parallel(startups: List[Dict], max_workers: int = 10) -> List[Dict]:
    """Evaluate multiple startups in parallel"""
    evaluator = HealthStartupEvaluator()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_startup = {
            executor.submit(evaluator.evaluate_url, startup): startup 
            for startup in startups
        }
        
        # Process completed tasks
        for future in concurrent.futures.as_completed(future_to_startup):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                startup = future_to_startup[future]
                logger.error(f"Error processing {startup.get('url', 'unknown')}: {str(e)}")
                results.append(evaluator._create_error_result(startup, str(e)))
    
    return results


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate digital health startup URLs')
    parser.add_argument('input_file', help='Input JSON or CSV file with startup URLs')
    parser.add_argument('--output-prefix', default='startups', help='Output file prefix')
    parser.add_argument('--max-workers', type=int, default=10, help='Maximum parallel workers')
    
    args = parser.parse_args()
    
    # Load input data
    logger.info(f"Loading startup data from {args.input_file}")
    startups = load_input_data(args.input_file)
    logger.info(f"Loaded {len(startups)} startups")
    
    # Evaluate startups
    start_time = time.time()
    results = evaluate_startups_parallel(startups, max_workers=args.max_workers)
    
    # Calculate statistics
    elapsed_time = time.time() - start_time
    live_count = sum(1 for r in results if r['is_live'])
    health_count = sum(1 for r in results if r['is_health_related'])
    suspicious_count = sum(1 for r in results if r.get('is_suspicious', False))
    
    logger.info(f"\nEvaluation completed in {elapsed_time:.2f} seconds")
    logger.info(f"Total URLs evaluated: {len(results)}")
    logger.info(f"Live websites: {live_count}")
    logger.info(f"Health-related: {health_count}")
    logger.info(f"Suspicious/parking pages: {suspicious_count}")
    
    # Save results
    save_results(results, args.output_prefix)
    
    # Generate summary report
    summary = {
        'total_evaluated': len(results),
        'live_websites': live_count,
        'health_related': health_count,
        'suspicious_pages': suspicious_count,
        'evaluation_time_seconds': elapsed_time,
        'average_time_per_url': elapsed_time / len(results) if results else 0,
        'region_distribution': {},
        'error_distribution': {}
    }
    
    # Count regions and errors
    for result in results:
        region = result.get('region', 'Unknown')
        summary['region_distribution'][region] = summary['region_distribution'].get(region, 0) + 1
        
        if result.get('error'):
            error_type = result['error'].split(':')[0]
            summary['error_distribution'][error_type] = summary['error_distribution'].get(error_type, 0) + 1
    
    # Save summary
    summary_file = f"{args.output_prefix}_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved summary to {summary_file}")


if __name__ == "__main__":
    main()