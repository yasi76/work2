#!/usr/bin/env python3
"""
Patch script to fix the status_code TypeError in existing startup discovery scripts
"""

import re
import os
from typing import List

def patch_script_file(filepath: str) -> bool:
    """
    Patch a Python script file to include the status_code fix
    """
    try:
        # Read the original file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already patched
        if 'safe_int_comparison' in content:
            print(f"✅ {filepath} is already patched")
            return True
        
        # Add the fix functions at the top after imports
        fix_code = '''
# =============================================================================
# PATCH: Fix for status_code TypeError
# =============================================================================

def safe_int_comparison(value, default=0):
    """Safely convert value to int for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float_comparison(value, default=0.0):
    """Safely convert value to float for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def apply_smart_sorting_safe(results):
    """
    Safe version of smart sorting that handles None status_code values
    """
    def safe_sort_key(result):
        # Safely get and convert status_code
        status_code = safe_int_comparison(result.get('status_code'), 0)
        
        # Calculate status priority with safe comparisons
        if 200 <= status_code < 300:
            status_priority = 10  # Success responses
        elif 300 <= status_code < 400:
            status_priority = 8   # Redirects
        elif status_code == 0:
            status_priority = 5   # Unknown status
        elif 400 <= status_code < 500:
            status_priority = 2   # Client errors
        elif 500 <= status_code < 600:
            status_priority = 1   # Server errors
        else:
            status_priority = 3   # Other status codes
        
        # Safely get other criteria
        confidence = safe_int_comparison(result.get('confidence'), 0)
        health_score = safe_float_comparison(result.get('health_relevance_score'), 0.0)
        
        # Method priority
        method_priority = {
            'User Verified': 100, 'Hardcoded': 95, 'Manual Curation': 90,
            'Conference': 85, 'Google Search': 80, 'Enhanced Discovery': 75,
            'LinkedIn': 70, 'Bing Search': 65, 'News Aggregator': 60,
            'Domain Generation': 50, 'Generated': 40, 'Unknown': 10
        }
        
        method = result.get('method', 'Unknown')
        method_score = method_priority.get(method, 10)
        
        # Calculate composite score
        composite_score = (
            status_priority * 1000 + confidence * 100 + method_score * 10 + health_score
        )
        
        return composite_score
    
    try:
        sorted_results = sorted(results, key=safe_sort_key, reverse=True)
        print(f"✅ Successfully sorted {len(sorted_results)} results")
        return sorted_results
    except Exception as e:
        print(f"⚠️ Error in smart sorting: {e}")
        return results

def fix_status_code_data(results):
    """Fix status_code and other numeric fields in results"""
    fixed_results = []
    for result in results:
        fixed_result = result.copy()
        fixed_result['status_code'] = safe_int_comparison(result.get('status_code'), 0)
        fixed_result['confidence'] = safe_int_comparison(result.get('confidence'), 0)
        fixed_result['health_relevance_score'] = safe_float_comparison(
            result.get('health_relevance_score'), 0.0
        )
        fixed_results.append(fixed_result)
    return fixed_results

# =============================================================================
# END PATCH
# =============================================================================

'''
        
        # Find a good place to insert the patch (after imports)
        lines = content.split('\n')
        import_end_idx = 0
        
        for i, line in enumerate(lines):
            if (line.strip().startswith('import ') or 
                line.strip().startswith('from ') or
                line.strip().startswith('#') or
                line.strip() == ''):
                import_end_idx = i + 1
            else:
                break
        
        # Insert the patch after imports
        lines.insert(import_end_idx, fix_code)
        
        # Replace problematic sorting patterns
        content = '\n'.join(lines)
        
        # Replace calls to apply_smart_sorting with apply_smart_sorting_safe
        content = re.sub(r'\bapply_smart_sorting\(', 'apply_smart_sorting_safe(', content)
        
        # Add status code fix before sorting
        content = re.sub(
            r'(unique_results = self\.apply_smart_sorting\(unique_results\))',
            r'unique_results = fix_status_code_data(unique_results)\n        \1',
            content
        )
        
        # Fix direct status_code comparisons
        content = re.sub(
            r'(\d+) <= status_code < (\d+)',
            r'\1 <= safe_int_comparison(status_code) < \2',
            content
        )
        
        # Write the patched file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully patched {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error patching {filepath}: {e}")
        return False

def main():
    """Main function to patch all Python files in the workspace"""
    print("🔧 Patching startup discovery scripts...")
    print("=" * 50)
    
    # Find all Python files
    python_files = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file not in ['patch_existing_scripts.py', 'fix_startup_discovery_error.py']:
            python_files.append(file)
    
    if not python_files:
        print("No Python files found to patch")
        return
    
    print(f"Found {len(python_files)} Python files to patch:")
    for file in python_files:
        print(f"  • {file}")
    
    print("\nApplying patches...")
    
    success_count = 0
    for file in python_files:
        if patch_script_file(file):
            success_count += 1
    
    print(f"\n📊 Patch Results:")
    print(f"  • Successfully patched: {success_count}/{len(python_files)} files")
    
    if success_count == len(python_files):
        print("\n✅ All files patched successfully!")
        print("The TypeError should now be fixed in your startup discovery scripts.")
    else:
        print(f"\n⚠️ {len(python_files) - success_count} files could not be patched")
        print("You may need to apply the fix manually to these files.")

if __name__ == "__main__":
    main()