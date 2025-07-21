# Status Code TypeError Fix

## Problem Description

The startup discovery script was encountering a `TypeError` during the smart sorting phase:

```
TypeError: '<=' not supported between instances of 'int' and 'NoneType'
```

This error occurred at line 275 in the `sort_key` function when trying to compare status codes:

```python
elif 300 <= status_code < 400:
```

The issue happens when `status_code` is `None` (NoneType) and the code tries to compare it with integers (300, 400).

## Root Cause

The error occurs when:
1. URLs are scraped or validated
2. Some URLs fail to return a status code (network errors, timeouts, etc.)
3. These failed requests set `status_code` to `None`
4. The sorting function tries to compare `None` with integers
5. Python raises a TypeError because `None` cannot be compared with integers

## Solution Applied

### 1. Safe Comparison Functions

Added helper functions that safely handle `None` values:

```python
def safe_int_comparison(value, default=0):
    """Safely convert value to int for comparison, handling None and invalid types"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
```

### 2. Fixed Smart Sorting

Replaced the problematic `apply_smart_sorting` function with `apply_smart_sorting_safe`:

```python
def apply_smart_sorting_safe(results):
    """Safe version of smart sorting that handles None status_code values"""
    def safe_sort_key(result):
        # Safely get and convert status_code
        status_code = safe_int_comparison(result.get('status_code'), 0)
        
        # Now safe to compare
        if 200 <= status_code < 300:
            status_priority = 10  # Success responses
        elif 300 <= status_code < 400:
            status_priority = 8   # Redirects
        # ... etc
```

### 3. Data Cleaning Function

Added `fix_status_code_data()` to clean data before sorting:

```python
def fix_status_code_data(results):
    """Fix status_code and other numeric fields in results"""
    fixed_results = []
    for result in results:
        fixed_result = result.copy()
        fixed_result['status_code'] = safe_int_comparison(result.get('status_code'), 0)
        fixed_result['confidence'] = safe_int_comparison(result.get('confidence'), 0)
        # ... etc
```

## Files Modified

The following files have been automatically patched:

- ✅ `enhanced_startup_discovery.py`
- ✅ `ultimate_startup_discovery.py`  
- ✅ `google_search_scraper.py`
- ✅ `startup_discovery_fix.py`

## What the Patch Does

1. **Adds Safe Functions**: Inserts helper functions at the top of each file
2. **Replaces Sorting**: Changes `apply_smart_sorting()` calls to `apply_smart_sorting_safe()`
3. **Adds Data Cleaning**: Ensures data is cleaned before sorting
4. **Handles Edge Cases**: Properly handles `None`, invalid strings, and other edge cases

## Testing the Fix

The fix has been tested with problematic data:

```python
test_results = [
    {
        'url': 'https://example1.com',
        'status_code': None,      # This would cause the error
        'confidence': '8',        # String instead of int
        'method': 'Google Search'
    },
    # ... more test cases
]
```

**Result**: ✅ All test cases pass, sorting works correctly

## Manual Application (if needed)

If you need to apply this fix to other scripts manually:

### Option 1: Import the Fix Module

```python
from fix_startup_discovery_error import apply_smart_sorting_safe, fix_status_code_data

# In your discovery function:
results = fix_status_code_data(results)
sorted_results = apply_smart_sorting_safe(results)
```

### Option 2: Use the Decorator

```python
from fix_startup_discovery_error import patch_discover_all_startups

@patch_discover_all_startups
def discover_all_startups(self):
    # Your existing code
    return results
```

### Option 3: Copy the Safe Functions

Copy the safe functions from `fix_startup_discovery_error.py` into your script and replace the problematic sorting function.

## Prevention for Future Scripts

To prevent this error in new scripts:

1. **Always check for None**: Before comparing values, ensure they're not None
2. **Use safe comparison functions**: Implement type checking and default values
3. **Validate data early**: Clean and validate data as soon as it's collected
4. **Add error handling**: Wrap comparisons in try-except blocks

### Example Safe Comparison Pattern:

```python
# Instead of:
if 200 <= status_code < 300:
    # This fails if status_code is None

# Use:
status_code = status_code if status_code is not None else 0
if 200 <= status_code < 300:
    # This works safely
```

## Status Code Mapping

The fixed sorting function uses this priority mapping:

| Status Code Range | Priority | Description |
|------------------|----------|-------------|
| 200-299 | 10 | Success responses (highest priority) |
| 300-399 | 8  | Redirects (still accessible) |
| 0 (None/Unknown) | 5  | Unknown status (neutral) |
| 400-499 | 2  | Client errors (low priority) |
| 500-599 | 1  | Server errors (lowest priority) |
| Other | 3  | Other status codes |

## Files Created by the Fix

- `fix_startup_discovery_error.py` - Complete fix implementation with tests
- `startup_discovery_fix.py` - Simpler fix functions
- `patch_existing_scripts.py` - Automatic patching script
- `STATUS_CODE_FIX_README.md` - This documentation
- `test_backup.json` - Backup of test data

## Verification

To verify the fix is working:

1. Run any of the startup discovery scripts
2. Look for this message: `✅ Successfully sorted X results`
3. No TypeError should occur during the sorting phase

## Future Maintenance

- The fix is backward compatible
- All original functionality is preserved
- Additional error handling is now in place
- The scripts will be more robust against data quality issues

If you encounter any issues with the fix, check that:
1. The patch was applied correctly
2. No syntax errors were introduced
3. The safe functions are available in the script scope