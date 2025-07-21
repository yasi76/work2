#!/usr/bin/env python3
"""
Helper script to intelligently process startup data files
Detects file type and runs appropriate processing
"""

import json
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def detect_file_type(file_path: str) -> str:
    """Detect the type of startup data file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check if it's a summary file
    if isinstance(data, dict):
        if 'generation_timestamp' in data and 'overview' in data:
            return 'summary_output'
        elif 'discovery_timestamp' in data and 'urls' in data:
            return 'discovery_output'
        elif 'total_evaluated' in data or 'evaluation_time_seconds' in data:
            return 'evaluation_summary'
        else:
            # Check if it contains startup data
            for key, value in data.items():
                if isinstance(value, dict) and 'url' in value:
                    return 'startup_dict'
            return 'unknown_dict'
    
    # Check if it's a list
    elif isinstance(data, list):
        if not data:
            return 'empty_list'
        
        # Check first item
        first_item = data[0]
        if isinstance(first_item, str):
            return 'url_list'
        elif isinstance(first_item, dict):
            if 'is_live' in first_item or 'health_relevance_score' in first_item:
                return 'validated_list'
            else:
                return 'startup_list'
    
    return 'unknown'


def process_file(file_path: str):
    """Process the file based on its type"""
    file_type = detect_file_type(file_path)
    logger.info(f"Detected file type: {file_type}")
    
    if file_type == 'summary_output':
        print("\nThis is a summary output file. You can:")
        print("1. View it directly (it's already a summary)")
        print("2. Extract the verified startups list")
        print("\nExample commands:")
        print(f"  cat {file_path} | jq '.verified_health_startups'")
        
    elif file_type == 'discovery_output':
        print("\nThis is a discovery output file. You should:")
        print("1. First evaluate the URLs")
        print("2. Then generate a summary or extract names")
        print("\nExample commands:")
        print(f"  python evaluate_health_startups.py {file_path}")
        print(f"  python evaluate_health_startups.py {file_path} --output-prefix evaluated")
        
    elif file_type == 'evaluation_summary':
        print("\nThis is an evaluation summary (from evaluate_health_startups.py).")
        print("This is a small summary file, not the full validated data.")
        print("Look for the corresponding '_validated.json' file for full data.")
        
    elif file_type == 'validated_list':
        print("\nThis is a validated startup list. You can:")
        print("1. Generate a comprehensive summary")
        print("2. Extract company names")
        print("\nExample commands:")
        print(f"  python generate_startup_summary.py {file_path}")
        print(f"  python extract_company_names.py {file_path}")
        print(f"  python extract_company_names.py {file_path} --refetch")
        
    elif file_type == 'url_list':
        print("\nThis is a simple URL list. You should:")
        print("1. First evaluate the URLs")
        print("\nExample commands:")
        print(f"  python evaluate_health_startups.py {file_path}")
        
    elif file_type == 'startup_list':
        print("\nThis is a startup list (not yet validated). You should:")
        print("1. First evaluate the URLs")
        print("\nExample commands:")
        print(f"  python evaluate_health_startups.py {file_path}")
        
    else:
        print(f"\nUnknown file type: {file_type}")
        print("Please check the file format.")
    
    # Show file statistics
    print("\nFile statistics:")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        print(f"  - Contains {len(data)} items")
    elif isinstance(data, dict):
        print(f"  - Contains {len(data)} keys")
        if 'urls' in data:
            print(f"  - URLs field contains {len(data['urls'])} items")


def main():
    parser = argparse.ArgumentParser(
        description='Intelligently process startup data files'
    )
    parser.add_argument('file', help='Input JSON file to analyze')
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        logger.error(f"File not found: {args.file}")
        sys.exit(1)
    
    try:
        process_file(args.file)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON file: {args.file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()