#!/usr/bin/env python3
"""
Comprehensive fix for startup discovery TypeError: '<=' not supported between instances of 'int' and 'NoneType'

This script provides patches for common issues in startup discovery scripts where status_code
comparisons fail when status_code is None.

Usage:
1. Copy this fix into your startup discovery script
2. Replace the problematic apply_smart_sorting function with apply_smart_sorting_safe
3. Use fix_status_code_data to clean your data before sorting
"""

import json
import csv
from typing import List, Dict, Any, Optional

def safe_int_comparison(value: Any, default: int = 0) -> int:
    """Safely convert value to int for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_comparison(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def apply_smart_sorting_safe(results: List[Dict]) -> List[Dict]:
    """
    Safe version of smart sorting that handles None status_code values and other type issues
    
    This replaces the problematic apply_smart_sorting function that was causing:
    TypeError: '<=' not supported between instances of 'int' and 'NoneType'
    """
    def safe_sort_key(result: Dict) -> tuple:
        # Safely get and convert status_code
        status_code = safe_int_comparison(result.get('status_code'), 0)
        
        # Calculate status priority with safe comparisons
        if 200 <= status_code < 300:
            status_priority = 10  # Success responses (highest priority)
        elif 300 <= status_code < 400:
            status_priority = 8   # Redirects (still accessible)
        elif status_code == 0:
            status_priority = 5   # Unknown status (neutral)
        elif 400 <= status_code < 500:
            status_priority = 2   # Client errors (low priority)
        elif 500 <= status_code < 600:
            status_priority = 1   # Server errors (lowest priority)
        else:
            status_priority = 3   # Other status codes
        
        # Safely get other criteria
        confidence = safe_int_comparison(result.get('confidence'), 0)
        health_score = safe_float_comparison(result.get('health_relevance_score'), 0.0)
        
        # Method priority mapping
        method_priority = {
            'User Verified': 100,
            'Hardcoded': 95,
            'Manual Curation': 90,
            'Conference': 85,
            'Google Search': 80,
            'Enhanced Discovery': 75,
            'LinkedIn': 70,
            'Bing Search': 65,
            'News Aggregator': 60,
            'Domain Generation': 50,
            'Generated': 40,
            'Unknown': 10
        }
        
        method = result.get('method', 'Unknown')
        method_score = method_priority.get(method, 10)
        
        # Source priority (if available)
        source_priority = {
            'User Verified': 100,
            'Official Directory': 90,
            'Search Engine': 80,
            'News Source': 70,
            'Social Media': 60,
            'Generated': 50,
            'Unknown': 10
        }
        
        source = result.get('source', 'Unknown')
        source_score = source_priority.get(source, 10)
        
        # Calculate composite score (all values are now safe integers/floats)
        composite_score = (
            status_priority * 1000 +    # Status code (most important)
            confidence * 100 +          # Confidence score
            method_score * 10 +         # Discovery method
            source_score * 5 +          # Source reliability
            health_score * 1            # Health relevance
        )
        
        # Return tuple for sorting (higher values first)
        return (
            status_priority,
            confidence,
            method_score,
            source_score,
            health_score,
            composite_score
        )
    
    try:
        # Sort with safe key function (reverse=True for highest values first)
        sorted_results = sorted(results, key=safe_sort_key, reverse=True)
        print(f"✅ Successfully sorted {len(sorted_results)} results")
        return sorted_results
        
    except Exception as e:
        print(f"⚠️ Error in smart sorting: {e}")
        print("Returning original results without sorting")
        return results

def fix_status_code_data(results: List[Dict]) -> List[Dict]:
    """
    Fix status_code and other numeric fields in results to prevent TypeError
    
    This function cleans the data before sorting to ensure all numeric fields
    are properly typed and None values are handled.
    """
    fixed_results = []
    
    for result in results:
        # Create a copy to avoid modifying original
        fixed_result = result.copy()
        
        # Fix status_code field
        fixed_result['status_code'] = safe_int_comparison(result.get('status_code'), 0)
        
        # Fix confidence field
        fixed_result['confidence'] = safe_int_comparison(result.get('confidence'), 0)
        
        # Fix health relevance score
        fixed_result['health_relevance_score'] = safe_float_comparison(
            result.get('health_relevance_score'), 0.0
        )
        
        # Ensure string fields have defaults
        fixed_result['method'] = result.get('method', 'Unknown')
        fixed_result['source'] = result.get('source', 'Unknown')
        fixed_result['url'] = result.get('url', '')
        fixed_result['category'] = result.get('category', 'Unknown')
        fixed_result['country'] = result.get('country', 'Unknown')
        
        fixed_results.append(fixed_result)
    
    print(f"✅ Fixed data types for {len(fixed_results)} results")
    return fixed_results

def patch_discover_all_startups(discover_function):
    """
    Decorator to patch discover_all_startups functions to handle the sorting error
    """
    def patched_discover(*args, **kwargs):
        try:
            # Call original function
            results = discover_function(*args, **kwargs)
            
            # If results contain a 'urls' list, fix that
            if isinstance(results, dict) and 'urls' in results:
                print("🔧 Applying status_code fix to results...")
                results['urls'] = fix_status_code_data(results['urls'])
                results['urls'] = apply_smart_sorting_safe(results['urls'])
            
            # If results is a list, fix that directly
            elif isinstance(results, list):
                print("🔧 Applying status_code fix to results...")
                results = fix_status_code_data(results)
                results = apply_smart_sorting_safe(results)
            
            return results
            
        except Exception as e:
            print(f"⚠️ Error in patched discover function: {e}")
            # Try to return something useful even if there's an error
            try:
                return discover_function(*args, **kwargs)
            except:
                return {'urls': [], 'error': str(e)}
    
    return patched_discover

def create_emergency_backup(results: List[Dict], filename: str = "emergency_backup_results.json"):
    """
    Create an emergency backup of results before applying fixes
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"🔒 Emergency backup created: {filename}")
    except Exception as e:
        print(f"⚠️ Could not create backup: {e}")

def validate_fixed_results(results: List[Dict]) -> bool:
    """
    Validate that the fixed results are properly formatted
    """
    if not isinstance(results, list):
        print("❌ Results is not a list")
        return False
    
    for i, result in enumerate(results):
        if not isinstance(result, dict):
            print(f"❌ Result {i} is not a dict")
            return False
        
        # Check that status_code is an integer
        status_code = result.get('status_code')
        if not isinstance(status_code, int):
            print(f"❌ Result {i} status_code is not an integer: {type(status_code)}")
            return False
        
        # Check that confidence is an integer
        confidence = result.get('confidence')
        if not isinstance(confidence, int):
            print(f"❌ Result {i} confidence is not an integer: {type(confidence)}")
            return False
    
    print(f"✅ All {len(results)} results are properly formatted")
    return True

# Example usage and test
if __name__ == "__main__":
    print("🔧 Startup Discovery Error Fix Tool")
    print("=" * 50)
    
    # Test data with problematic None values
    test_results = [
        {
            'url': 'https://example1.com',
            'status_code': None,  # This would cause the error
            'confidence': '8',    # String instead of int
            'health_relevance_score': None,
            'method': 'Google Search'
        },
        {
            'url': 'https://example2.com',
            'status_code': 200,
            'confidence': 9,
            'health_relevance_score': 0.85,
            'method': 'User Verified'
        },
        {
            'url': 'https://example3.com',
            'status_code': '404',  # String instead of int
            'confidence': None,   # None instead of int
            'health_relevance_score': '0.5',  # String instead of float
            'method': 'Generated'
        }
    ]
    
    print("📊 Testing with problematic data...")
    print(f"Original data: {len(test_results)} results")
    
    # Create backup
    create_emergency_backup(test_results, "test_backup.json")
    
    # Fix the data
    fixed_results = fix_status_code_data(test_results)
    
    # Validate the fixes
    if validate_fixed_results(fixed_results):
        print("✅ Data fix successful")
        
        # Test sorting
        sorted_results = apply_smart_sorting_safe(fixed_results)
        print(f"✅ Sorting successful: {len(sorted_results)} results")
        
        # Show results
        print("\n📋 Fixed and sorted results:")
        for i, result in enumerate(sorted_results):
            print(f"  {i+1}. {result['url']} (status: {result['status_code']}, confidence: {result['confidence']})")
    
    else:
        print("❌ Data fix failed")
    
    print("\n💡 To use this fix in your startup discovery script:")
    print("1. Import this module: from fix_startup_discovery_error import *")
    print("2. Replace your apply_smart_sorting with apply_smart_sorting_safe")
    print("3. Use fix_status_code_data before sorting")
    print("4. Or use the @patch_discover_all_startups decorator")