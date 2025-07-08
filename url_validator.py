"""
URL validation module for checking if URLs are live, reachable, and healthcare-related.
Uses asyncio and aiohttp for fast, concurrent URL validation.
"""

import asyncio
import aiohttp
import time
import requests
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup
import config
import utils


class URLValidator:
    """
    Validates URLs to check if they are live, reachable, and healthcare-related.
    """
    
    def __init__(self):
        """Initialize the URL validator with session settings."""
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT)
        self.headers = {'User-Agent': config.USER_AGENT}
        
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(limit=config.MAX_CONCURRENT_REQUESTS)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_single_url(self, url: str) -> Dict:
        """
        Check a single URL for accessibility and healthcare relevance.
        
        Args:
            url (str): URL to check
            
        Returns:
            Dict: Validation results containing status, healthcare relevance, etc.
        """
        result = {
            'url': url,
            'is_live': False,
            'is_healthcare': False,
            'status_code': None,
            'title': '',
            'description': '',
            'error': None,
            'response_time': None
        }
        
        # Skip if URL should be excluded
        if utils.should_exclude_url(url):
            result['error'] = 'Excluded by filter rules'
            return result
        
        # Check URL format
        if not utils.is_valid_url_format(url):
            result['error'] = 'Invalid URL format'
            return result
        
        try:
            start_time = time.time()
            
            # Make HTTP request
            async with self.session.get(url, allow_redirects=True) as response:
                result['status_code'] = response.status
                result['response_time'] = time.time() - start_time
                
                # Consider URL live if status is 2xx or 3xx
                if 200 <= response.status < 400:
                    result['is_live'] = True
                    
                    # Try to get page content for healthcare analysis
                    try:
                        content = await response.text()
                        result.update(self._analyze_page_content(content, url))
                    except Exception as e:
                        # URL is live but we couldn't analyze content
                        result['error'] = f'Content analysis failed: {str(e)}'
                        # Still check URL itself for healthcare keywords
                        result['is_healthcare'] = utils.is_healthcare_related('', url)
                else:
                    result['error'] = f'HTTP {response.status}'
                    
        except asyncio.TimeoutError:
            result['error'] = 'Request timeout'
        except aiohttp.ClientError as e:
            result['error'] = f'Client error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        return result
    
    def _analyze_page_content(self, html_content: str, url: str) -> Dict:
        """
        Analyze HTML content to extract title, description and check healthcare relevance.
        
        Args:
            html_content (str): HTML content of the page
            url (str): URL of the page
            
        Returns:
            Dict: Analysis results with title, description, and healthcare flag
        """
        analysis = {
            'title': '',
            'description': '',
            'is_healthcare': False
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                analysis['title'] = title_tag.get_text().strip()
            
            # Extract meta description
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag:
                analysis['description'] = description_tag.get('content', '').strip()
            
            # If no meta description, try to get text from the page
            if not analysis['description']:
                # Get first paragraph or div with substantial text
                for tag in soup.find_all(['p', 'div'], limit=10):
                    text = tag.get_text().strip()
                    if len(text) > 50:  # Only consider substantial text
                        analysis['description'] = text[:200] + ('...' if len(text) > 200 else '')
                        break
            
            # Check if content is healthcare-related
            combined_text = f"{analysis['title']} {analysis['description']}"
            analysis['is_healthcare'] = utils.is_healthcare_related(combined_text, url)
            
        except Exception as e:
            # If parsing fails, just check URL for healthcare keywords
            analysis['is_healthcare'] = utils.is_healthcare_related('', url)
        
        return analysis
    
    async def validate_urls(self, urls: List[str]) -> List[Dict]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            urls (List[str]): List of URLs to validate
            
        Returns:
            List[Dict]: List of validation results
        """
        print(f"Starting validation of {len(urls)} URLs...")
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        
        async def validate_with_semaphore(url):
            async with semaphore:
                return await self.check_single_url(url)
        
        # Run all validations concurrently
        tasks = [validate_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions that occurred
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                validated_results.append({
                    'url': urls[i],
                    'is_live': False,
                    'is_healthcare': False,
                    'status_code': None,
                    'title': '',
                    'description': '',
                    'error': f'Validation failed: {str(result)}',
                    'response_time': None
                })
            else:
                validated_results.append(result)
        
        return validated_results


def _run_validation_sync(urls: List[str]) -> List[Dict]:
    """
    Synchronous fallback validation when asyncio.run() is not available.
    Uses requests instead of aiohttp for compatibility.
    """
    print(f"Starting synchronous validation of {len(urls)} URLs...")
    
    results = []
    
    for i, url in enumerate(urls, 1):
        if i % 10 == 0:  # Progress indicator
            print(f"Processed {i}/{len(urls)} URLs...")
        
        result = {
            'url': url,
            'is_live': False,
            'is_healthcare': False,
            'status_code': None,
            'title': '',
            'description': '',
            'error': None,
            'response_time': None
        }
        
        # Skip if URL should be excluded
        if utils.should_exclude_url(url):
            result['error'] = 'Excluded by filter rules'
            results.append(result)
            continue
        
        # Check URL format
        if not utils.is_valid_url_format(url):
            result['error'] = 'Invalid URL format'
            results.append(result)
            continue
        
        try:
            start_time = time.time()
            
            # Make HTTP request with requests instead of aiohttp
            response = requests.get(
                url, 
                timeout=config.REQUEST_TIMEOUT,
                headers={'User-Agent': config.USER_AGENT},
                allow_redirects=True
            )
            
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - start_time
            
            # Consider URL live if status is 2xx or 3xx
            if 200 <= response.status_code < 400:
                result['is_live'] = True
                
                # Analyze page content for healthcare relevance
                try:
                    content = response.text
                    analysis = _analyze_page_content_sync(content, url)
                    result.update(analysis)
                except Exception as e:
                    # URL is live but we couldn't analyze content
                    result['error'] = f'Content analysis failed: {str(e)}'
                    # Still check URL itself for healthcare keywords
                    result['is_healthcare'] = utils.is_healthcare_related('', url)
            else:
                result['error'] = f'HTTP {response.status_code}'
                
        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout'
        except requests.exceptions.RequestException as e:
            result['error'] = f'Request error: {str(e)}'
        except Exception as e:
            result['error'] = f'Unexpected error: {str(e)}'
        
        results.append(result)
    
    return results


def _analyze_page_content_sync(html_content: str, url: str) -> Dict:
    """
    Synchronous version of page content analysis.
    """
    analysis = {
        'title': '',
        'description': '',
        'is_healthcare': False
    }
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            analysis['title'] = title_tag.get_text().strip()
        
        # Extract meta description
        description_tag = soup.find('meta', attrs={'name': 'description'})
        if description_tag:
            analysis['description'] = description_tag.get('content', '').strip()
        
        # If no meta description, try to get text from the page
        if not analysis['description']:
            # Get first paragraph or div with substantial text
            for tag in soup.find_all(['p', 'div'], limit=10):
                text = tag.get_text().strip()
                if len(text) > 50:  # Only consider substantial text
                    analysis['description'] = text[:200] + ('...' if len(text) > 200 else '')
                    break
        
        # Check if content is healthcare-related
        combined_text = f"{analysis['title']} {analysis['description']}"
        analysis['is_healthcare'] = utils.is_healthcare_related(combined_text, url)
        
    except Exception as e:
        # If parsing fails, just check URL for healthcare keywords
        analysis['is_healthcare'] = utils.is_healthcare_related('', url)
    
    return analysis


def clean_and_validate_urls(initial_urls: List[str]) -> List[Dict]:
    """
    Main function to clean and validate a list of URLs.
    
    Args:
        initial_urls (List[str]): Initial list of URLs to process
        
    Returns:
        List[Dict]: Validated and cleaned URLs with metadata
    """
    print("=== URL Validation and Cleaning Process ===")
    
    # Step 1: Clean and deduplicate URLs
    print(f"Step 1: Cleaning {len(initial_urls)} initial URLs...")
    cleaned_urls = utils.deduplicate_urls(initial_urls)
    print(f"After cleaning and deduplication: {len(cleaned_urls)} URLs")
    
    # Step 2: Validate URLs asynchronously
    print("Step 2: Validating URLs (checking if live and healthcare-related)...")
    
    async def run_validation():
        async with URLValidator() as validator:
            return await validator.validate_urls(cleaned_urls)
    
    # Run the async validation - handle existing event loop
    def get_event_loop_policy():
        """Get appropriate event loop for the current environment."""
        try:
            loop = asyncio.get_running_loop()
            return loop, True  # Loop is running
        except RuntimeError:
            return None, False  # No running loop
    
    loop, is_running = get_event_loop_policy()
    
    if is_running:
        # We're in an existing event loop (like Jupyter), use different approach
        print("Detected existing event loop, using alternative validation method...")
        validation_results = _run_validation_sync(cleaned_urls)
    else:
        # No existing loop, safe to use asyncio.run()
        validation_results = asyncio.run(run_validation())
    
    # Step 3: Filter results
    live_urls = [r for r in validation_results if r['is_live']]
    healthcare_urls = [r for r in live_urls if r['is_healthcare']]
    
    print(f"Step 3: Filtering results...")
    print(f"  - Live URLs: {len(live_urls)}")
    print(f"  - Healthcare-related URLs: {len(healthcare_urls)}")
    
    # Add source information
    for result in validation_results:
        result['source'] = 'Validated list'
    
    return validation_results


# Example usage and testing
if __name__ == "__main__":
    # Test URLs from the provided list
    test_urls = [
        "https://www.acalta.de",
        "https://www.actimi.com",
        "https://www.emmora.de",
        "https://www.alfa-ai.com",
        "https://www.apheris.com"
    ]
    
    print("Testing URL validator...")
    results = clean_and_validate_urls(test_urls)
    
    for result in results:
        print(f"\nURL: {result['url']}")
        print(f"Live: {result['is_live']}")
        print(f"Healthcare: {result['is_healthcare']}")
        print(f"Status: {result['status_code']}")
        print(f"Title: {result['title'][:50]}...")
        if result['error']:
            print(f"Error: {result['error']}")