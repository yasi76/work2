"""
Utility functions for Healthcare Startup Discovery System

This module contains common utility functions used throughout the system.
"""

import logging
import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import csv

# Set up logging
logger = logging.getLogger(__name__)


def setup_logging(log_file: str = "healthcare_discovery.log", log_level: str = "INFO"):
    """
    Set up logging configuration
    
    Args:
        log_file: Path to log file
        log_level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def create_file_hash(content: str) -> str:
    """
    Create MD5 hash of content for caching/deduplication
    
    Args:
        content: Content to hash
        
    Returns:
        MD5 hash string
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        filepath: Path to save file
        indent: JSON indentation
        
    Returns:
        True if successful
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False


def load_json(filepath: str) -> Optional[Any]:
    """
    Load data from JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded data or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return None


def save_csv(data: List[Dict], filepath: str) -> bool:
    """
    Save list of dictionaries to CSV file
    
    Args:
        data: List of dictionaries to save
        filepath: Path to save file
        
    Returns:
        True if successful
    """
    try:
        if not data:
            logger.warning("No data to save to CSV")
            return False
        
        fieldnames = data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        logger.error(f"Error saving CSV to {filepath}: {e}")
        return False


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def clean_filename(filename: str) -> str:
    """
    Clean filename to be filesystem-safe
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure directory exists, create if necessary
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def format_number(number: int) -> str:
    """
    Format number with thousands separators
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    return f"{number:,}"


def calculate_rate_limit_delay(requests_made: int, time_window: int = 60, max_requests: int = 60) -> float:
    """
    Calculate delay needed for rate limiting
    
    Args:
        requests_made: Number of requests made in time window
        time_window: Time window in seconds
        max_requests: Maximum requests allowed in time window
        
    Returns:
        Delay in seconds
    """
    if requests_made >= max_requests:
        return time_window / max_requests
    return 0.0


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_recent_file(filepath: str, hours: int = 24) -> bool:
    """
    Check if file was modified recently
    
    Args:
        filepath: Path to file
        hours: Number of hours to consider recent
        
    Returns:
        True if file is recent
    """
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return False
        
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        threshold = datetime.now() - timedelta(hours=hours)
        
        return modified_time > threshold
    except Exception as e:
        logger.error(f"Error checking file age for {filepath}: {e}")
        return False


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    try:
        return Path(filepath).stat().st_size / (1024 * 1024)
    except Exception as e:
        logger.error(f"Error getting file size for {filepath}: {e}")
        return 0.0


def validate_url_format(url: str) -> bool:
    """
    Simple URL format validation
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL format is valid
    """
    import re
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain name
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.error(f"Error extracting domain from {url}: {e}")
        return ""


def normalize_company_name(name: str) -> str:
    """
    Normalize company name for comparison
    
    Args:
        name: Company name to normalize
        
    Returns:
        Normalized company name
    """
    # Convert to lowercase
    name = name.lower().strip()
    
    # Remove common business suffixes
    suffixes = ['gmbh', 'ag', 'ltd', 'inc', 'corp', 'llc', 'limited', 'corporation']
    for suffix in suffixes:
        if name.endswith(f' {suffix}'):
            name = name[:-len(suffix)-1].strip()
    
    # Remove special characters
    import re
    name = re.sub(r'[^\w\s]', '', name)
    
    # Normalize whitespace
    name = ' '.join(name.split())
    
    return name


class ProgressTracker:
    """Simple progress tracker for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        current_time = time.time()
        
        # Update every 5 seconds or on completion
        if current_time - self.last_update >= 5 or self.current >= self.total:
            self._print_progress()
            self.last_update = current_time
    
    def _print_progress(self):
        """Print current progress"""
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = format_duration(eta)
        else:
            eta_str = "unknown"
        
        print(f"{self.description}: {self.current}/{self.total} "
              f"({percentage:.1f}%) - ETA: {eta_str}")
    
    def complete(self):
        """Mark as complete"""
        self.current = self.total
        elapsed = time.time() - self.start_time
        print(f"{self.description} completed in {format_duration(elapsed)}")


def batch_process(items: List[Any], batch_size: int = 100):
    """
    Generator to process items in batches
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with nested key support
    
    Args:
        dictionary: Dictionary to get value from
        key: Key (supports dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        keys = key.split('.')
        value = dictionary
        
        for k in keys:
            value = value[k]
        
        return value
    except (KeyError, TypeError, AttributeError):
        return default