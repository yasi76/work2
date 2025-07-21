#!/usr/bin/env python3

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
        if 200 <= safe_int_comparison(status_code) < 300:
            status_priority = 10  # Success responses
        elif 300 <= safe_int_comparison(status_code) < 400:
            status_priority = 8   # Redirects
        elif status_code == 0:
            status_priority = 5   # Unknown status
        elif 400 <= safe_int_comparison(status_code) < 500:
            status_priority = 2   # Client errors
        elif 500 <= safe_int_comparison(status_code) < 600:
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


"""
Fix for the startup discovery script TypeError: '<=' not supported between instances of 'int' and 'NoneType'
This fix handles None status_code values in the smart sorting function.
"""

def apply_smart_sorting_fix(results):
    """
    Fixed version of the smart sorting function that handles None status_code values
    """
    def sort_key(result):
        # Get status_code, default to 0 if None
        status_code = result.get('status_code')
        if status_code is None:
            status_code = 0
        
        # Convert to int if it's a string
        try:
            status_code = int(status_code)
        except (ValueError, TypeError):
            status_code = 0
        
        # Calculate priority score based on status code
        if 200 <= safe_int_comparison(status_code) < 300:
            status_priority = 10  # Success responses
        elif 300 <= safe_int_comparison(status_code) < 400:
            status_priority = 8   # Redirects (still accessible)
        elif status_code == 0 or status_code is None:
            status_priority = 5   # Unknown status
        elif 400 <= safe_int_comparison(status_code) < 500:
            status_priority = 2   # Client errors
        elif 500 <= safe_int_comparison(status_code) < 600:
            status_priority = 1   # Server errors
        else:
            status_priority = 3   # Other status codes
        
        # Get other sorting criteria
        confidence = result.get('confidence', 0)
        try:
            confidence = int(confidence) if confidence is not None else 0
        except (ValueError, TypeError):
            confidence = 0
        
        # Health relevance score
        health_score = result.get('health_relevance_score', 0)
        try:
            health_score = float(health_score) if health_score is not None else 0
        except (ValueError, TypeError):
            health_score = 0
        
        # Method priority
        method_priority = {
            'User Verified': 10,
            'Hardcoded': 10,
            'Manual Curation': 9,
            'Google Search': 8,
            'Enhanced Discovery': 7,
            'Bing Search': 6,
            'Domain Generation': 5,
            'Generated': 4,
            'News Aggregator': 6,
            'LinkedIn': 7,
            'Conference': 8
        }
        
        method = result.get('method', 'Unknown')
        method_score = method_priority.get(method, 1)
        
        # Combine all scores (higher is better)
        total_score = (
            status_priority * 100 +  # Status code is most important
            confidence * 10 +        # Confidence is second
            health_score * 5 +       # Health relevance
            method_score            # Method priority
        )
        
        return total_score
    
    try:
        sorted_results = sorted(results, key=sort_key, reverse=True)
        return sorted_results
    except Exception as e:
        print(f"Error in smart sorting: {e}")
        # Fallback: return original results if sorting fails
        return results

def fix_status_code_issues(results):
    """
    Fix status_code issues in results list
    """
    fixed_results = []
    for result in results:
        # Make a copy of the result
        fixed_result = result.copy()
        
        # Fix status_code field
        status_code = fixed_result.get('status_code')
        if status_code is None:
            fixed_result['status_code'] = 0
        else:
            try:
                fixed_result['status_code'] = int(status_code)
            except (ValueError, TypeError):
                fixed_result['status_code'] = 0
        
        # Ensure other numeric fields are properly typed
        confidence = fixed_result.get('confidence')
        if confidence is not None:
            try:
                fixed_result['confidence'] = int(confidence)
            except (ValueError, TypeError):
                fixed_result['confidence'] = 0
        else:
            fixed_result['confidence'] = 0
        
        health_score = fixed_result.get('health_relevance_score')
        if health_score is not None:
            try:
                fixed_result['health_relevance_score'] = float(health_score)
            except (ValueError, TypeError):
                fixed_result['health_relevance_score'] = 0.0
        else:
            fixed_result['health_relevance_score'] = 0.0
        
        fixed_results.append(fixed_result)
    
    return fixed_results

if __name__ == "__main__":
    print("This is a fix module for startup discovery status_code issues.")
    print("Import and use apply_smart_sorting_fix() and fix_status_code_issues() functions.")