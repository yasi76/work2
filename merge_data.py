#!/usr/bin/env python3
"""
merge_data.py - Merges all extracted data into a single CSV file
Inputs: final_startup_urls.json, company_name_mapping.json, product_names.json, finding_ort.json
Outputs: digital_health_startups_complete.csv
"""

import json
import csv
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json_file(filename: str) -> any:
    """Load JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"{filename} not found")
        return None

def merge_data():
    """Merge all data sources into a single dataset"""
    # Load all data files
    urls = load_json_file('final_startup_urls.json')
    if not urls:
        logger.error("No URLs found. Run discover_urls.py first.")
        return
    
    company_names = load_json_file('company_name_mapping.json') or {}
    products = load_json_file('product_names.json') or {}
    locations = load_json_file('finding_ort.json') or {}
    
    # Create merged dataset
    merged_data = []
    for url in urls:
        row = {
            'url': url,
            'company_name': company_names.get(url, ''),
            'products': '; '.join(products.get(url, [])),
            'location': locations.get(url, ''),
            'has_company_name': 'Yes' if url in company_names else 'No',
            'has_products': 'Yes' if url in products else 'No',
            'has_location': 'Yes' if url in locations else 'No'
        }
        merged_data.append(row)
    
    # Sort by company name
    merged_data.sort(key=lambda x: x['company_name'] or x['url'])
    
    # Save to CSV
    output_file = 'digital_health_startups_complete.csv'
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['url', 'company_name', 'products', 'location', 
                     'has_company_name', 'has_products', 'has_location']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_data)
    
    # Print summary statistics
    total = len(merged_data)
    with_names = sum(1 for row in merged_data if row['has_company_name'] == 'Yes')
    with_products = sum(1 for row in merged_data if row['has_products'] == 'Yes')
    with_locations = sum(1 for row in merged_data if row['has_location'] == 'Yes')
    complete = sum(1 for row in merged_data if 
                  row['has_company_name'] == 'Yes' and 
                  row['has_products'] == 'Yes' and 
                  row['has_location'] == 'Yes')
    
    logger.info(f"\nData Merge Summary:")
    logger.info(f"Total companies: {total}")
    logger.info(f"With company names: {with_names} ({with_names/total*100:.1f}%)")
    logger.info(f"With products: {with_products} ({with_products/total*100:.1f}%)")
    logger.info(f"With locations: {with_locations} ({with_locations/total*100:.1f}%)")
    logger.info(f"Complete records: {complete} ({complete/total*100:.1f}%)")
    logger.info(f"\nSaved to: {output_file}")

def main():
    merge_data()

if __name__ == "__main__":
    main()