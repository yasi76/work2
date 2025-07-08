"""
URL Validator and Cleaner for Healthcare Startup Discovery System

This module provides functionality to validate, clean, and filter URLs
to ensure high-quality results while avoiding social media and unwanted domains.
"""

import re
import logging
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urlparse, urljoin, parse_qs
import validators
import requests
from requests.exceptions import RequestException
import tldextract
from robotstxt import RobotsTxtParser
import time

from config import EXCLUDED_DOMAINS, TIMEOUT, USER_AGENTS

# Set up logging
logger = logging.getLogger(__name__)


class URLValidator:
    """
    URL validation and cleaning utility
    
    This class provides comprehensive URL validation, cleaning,
    and filtering functionality for the healthcare startup discovery system.
    """
    
    def __init__(self):
        """Initialize the URL validator"""
        self.excluded_domains = EXCLUDED_DOMAINS.copy()
        self.robots_cache = {}  # Cache for robots.txt data
        self.domain_cache = {}  # Cache for domain validation results
        self.user_agents = USER_AGENTS
        self.current_user_agent_index = 0
        
        # Additional patterns to exclude
        self.excluded_patterns = [
            r'linkedin\.com',
            r'facebook\.com',
            r'twitter\.com',
            r'instagram\.com',
            r'youtube\.com',
            r'pinterest\.com',
            r'tiktok\.com',
            r'snapchat\.com',
            r'reddit\.com',
            r'quora\.com',
            r'stackoverflow\.com',
            r'github\.com/(?!.*healthcare|.*medical|.*health)',  # Allow healthcare-related GitHub repos
            r'.*\.pdf$',  # Exclude PDF files
            r'.*\.doc[x]?$',  # Exclude Word documents
            r'.*\.ppt[x]?$',  # Exclude PowerPoint files
            r'.*\.(jpg|jpeg|png|gif|bmp|svg)$',  # Exclude image files
            r'.*\.(mp4|avi|mov|wmv|flv)$',  # Exclude video files
            r'.*\.(mp3|wav|ogg|m4a)$',  # Exclude audio files
        ]
        
        logger.info("URLValidator initialized successfully")
    
    def get_user_agent(self) -> str:
        """Get next user agent for rotation"""
        user_agent = self.user_agents[self.current_user_agent_index]
        self.current_user_agent_index = (self.current_user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    def clean_url(self, url: str) -> str:
        """
        Clean and normalize a URL
        
        Args:
            url: Raw URL to clean
            
        Returns:
            Cleaned URL
        """
        if not url:
            return ""
        
        # Remove leading/trailing whitespace
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        
        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'gclid', 'fbclid', 'msclkid', '_ga', '_gl', 'ref', 'source',
            'campaign_id', 'ad_id', 'campaign', 'medium'
        }
        
        # Parse query parameters and remove tracking ones
        if parsed.query:
            query_params = parse_qs(parsed.query)
            cleaned_params = {
                k: v for k, v in query_params.items() 
                if k not in tracking_params
            }
            
            # Rebuild query string
            if cleaned_params:
                from urllib.parse import urlencode
                query_string = urlencode(cleaned_params, doseq=True)
            else:
                query_string = ""
        else:
            query_string = ""
        
        # Remove fragment (everything after #)
        fragment = ""
        
        # Rebuild URL
        from urllib.parse import urlunparse
        cleaned_url = urlunparse((
            parsed.scheme,
            parsed.netloc.lower(),  # Normalize domain to lowercase
            parsed.path.rstrip('/'),  # Remove trailing slash from path
            parsed.params,
            query_string,
            fragment
        ))
        
        return cleaned_url
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid
        """
        if not url:
            return False
        
        # Basic URL validation
        if not validators.url(url):
            return False
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        
        # Check if scheme is HTTP/HTTPS
        if parsed.scheme not in ('http', 'https'):
            return False
        
        # Check if domain exists
        if not parsed.netloc:
            return False
        
        # Extract domain components
        try:
            domain_info = tldextract.extract(url)
            domain = f"{domain_info.domain}.{domain_info.suffix}"
        except Exception:
            return False
        
        # Check against excluded domains
        if domain.lower() in self.excluded_domains:
            return False
        
        # Check against excluded patterns
        for pattern in self.excluded_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def is_company_website(self, url: str) -> bool:
        """
        Determine if URL likely points to a company website
        
        Args:
            url: URL to analyze
            
        Returns:
            True if likely a company website
        """
        if not url:
            return False
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Check for obvious non-company indicators
        non_company_indicators = [
            'blog.', 'news.', 'press.', 'media.', 'support.',
            'help.', 'docs.', 'api.', 'dev.', 'developer.',
            'forum.', 'community.', 'wiki.'
        ]
        
        for indicator in non_company_indicators:
            if domain.startswith(indicator):
                return False
        
        # Check path for non-company indicators
        non_company_paths = [
            '/blog/', '/news/', '/press/', '/media/',
            '/support/', '/help/', '/docs/', '/api/',
            '/forum/', '/community/', '/wiki/'
        ]
        
        for path_indicator in non_company_paths:
            if path.startswith(path_indicator):
                return False
        
        # Positive indicators for company websites
        company_indicators = [
            'www.', 'app.', 'portal.', 'platform.'
        ]
        
        # Check if it's a root domain or has company indicators
        if path in ('', '/') or any(domain.startswith(indicator) for indicator in company_indicators):
            return True
        
        # Check for company-like paths
        company_paths = [
            '/about', '/company', '/team', '/contact',
            '/products', '/services', '/solutions'
        ]
        
        for company_path in company_paths:
            if path.startswith(company_path):
                return True
        
        return False
    
    def check_robots_txt(self, url: str, user_agent: str = '*') -> bool:
        """
        Check if URL is allowed by robots.txt
        
        Args:
            url: URL to check
            user_agent: User agent to check for
            
        Returns:
            True if allowed by robots.txt
        """
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Check cache first
            if base_url in self.robots_cache:
                robots_parser = self.robots_cache[base_url]
            else:
                # Fetch and parse robots.txt
                robots_url = urljoin(base_url, '/robots.txt')
                
                try:
                    response = requests.get(
                        robots_url,
                        timeout=TIMEOUT,
                        headers={'User-Agent': self.get_user_agent()}
                    )
                    
                    if response.status_code == 200:
                        robots_parser = RobotsTxtParser()
                        robots_parser.set_url(robots_url)
                        robots_parser.read()
                        self.robots_cache[base_url] = robots_parser
                    else:
                        # If robots.txt doesn't exist, assume allowed
                        return True
                        
                except RequestException:
                    # If we can't fetch robots.txt, assume allowed
                    return True
            
            # Check if URL is allowed
            return robots_parser.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Default to allowed if check fails
    
    def is_accessible(self, url: str) -> Tuple[bool, int]:
        """
        Check if URL is accessible (returns 200 status)
        
        Args:
            url: URL to check
            
        Returns:
            Tuple of (is_accessible, status_code)
        """
        try:
            response = requests.head(
                url,
                timeout=TIMEOUT,
                headers={'User-Agent': self.get_user_agent()},
                allow_redirects=True
            )
            
            # Consider 2xx and 3xx status codes as accessible
            is_accessible = 200 <= response.status_code < 400
            return is_accessible, response.status_code
            
        except RequestException as e:
            logger.debug(f"URL {url} not accessible: {e}")
            return False, 0
    
    def extract_domain_info(self, url: str) -> Dict[str, str]:
        """
        Extract detailed domain information
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with domain information
        """
        try:
            domain_info = tldextract.extract(url)
            parsed = urlparse(url)
            
            return {
                'domain': domain_info.domain,
                'suffix': domain_info.suffix,
                'subdomain': domain_info.subdomain,
                'full_domain': f"{domain_info.domain}.{domain_info.suffix}",
                'netloc': parsed.netloc,
                'scheme': parsed.scheme,
                'path': parsed.path
            }
        except Exception as e:
            logger.warning(f"Error extracting domain info from {url}: {e}")
            return {}
    
    def deduplicate_urls(self, urls: List[str]) -> List[str]:
        """
        Remove duplicate URLs, keeping the cleanest version
        
        Args:
            urls: List of URLs to deduplicate
            
        Returns:
            Deduplicated list of URLs
        """
        if not urls:
            return []
        
        # Clean all URLs first
        cleaned_urls = []
        for url in urls:
            try:
                cleaned = self.clean_url(url)
                if cleaned and self.is_valid_url(cleaned):
                    cleaned_urls.append(cleaned)
            except Exception as e:
                logger.debug(f"Error cleaning URL {url}: {e}")
                continue
        
        # Group by domain and keep the best URL for each domain
        domain_urls = {}
        
        for url in cleaned_urls:
            domain_info = self.extract_domain_info(url)
            full_domain = domain_info.get('full_domain', '')
            
            if not full_domain:
                continue
            
            if full_domain not in domain_urls:
                domain_urls[full_domain] = []
            
            domain_urls[full_domain].append(url)
        
        # Select best URL for each domain
        deduplicated = []
        
        for domain, domain_url_list in domain_urls.items():
            # Prefer company website URLs
            company_urls = [url for url in domain_url_list if self.is_company_website(url)]
            
            if company_urls:
                # Sort by URL length (shorter is usually better for company sites)
                best_url = min(company_urls, key=len)
            else:
                # If no obvious company URLs, take the shortest one
                best_url = min(domain_url_list, key=len)
            
            deduplicated.append(best_url)
        
        return deduplicated
    
    def validate_and_filter_urls(
        self, 
        urls: List[str], 
        check_accessibility: bool = False,
        check_robots: bool = True
    ) -> List[Dict[str, any]]:
        """
        Comprehensive URL validation and filtering
        
        Args:
            urls: List of URLs to validate
            check_accessibility: Whether to check if URLs are accessible
            check_robots: Whether to check robots.txt compliance
            
        Returns:
            List of dictionaries with URL and validation information
        """
        validated_urls = []
        
        # First deduplicate
        unique_urls = self.deduplicate_urls(urls)
        
        for url in unique_urls:
            url_info = {
                'url': url,
                'is_valid': False,
                'is_company_website': False,
                'is_accessible': None,
                'status_code': None,
                'robots_allowed': None,
                'domain_info': {},
                'validation_errors': []
            }
            
            try:
                # Basic validation
                if not self.is_valid_url(url):
                    url_info['validation_errors'].append('Invalid URL format or excluded domain')
                    continue
                
                url_info['is_valid'] = True
                
                # Check if it's a company website
                url_info['is_company_website'] = self.is_company_website(url)
                
                # Extract domain information
                url_info['domain_info'] = self.extract_domain_info(url)
                
                # Check robots.txt if requested
                if check_robots:
                    try:
                        url_info['robots_allowed'] = self.check_robots_txt(url)
                        if not url_info['robots_allowed']:
                            url_info['validation_errors'].append('Blocked by robots.txt')
                    except Exception as e:
                        logger.debug(f"Error checking robots.txt for {url}: {e}")
                        url_info['robots_allowed'] = True  # Default to allowed
                
                # Check accessibility if requested
                if check_accessibility:
                    try:
                        is_accessible, status_code = self.is_accessible(url)
                        url_info['is_accessible'] = is_accessible
                        url_info['status_code'] = status_code
                        
                        if not is_accessible:
                            url_info['validation_errors'].append(f'Not accessible (status: {status_code})')
                    except Exception as e:
                        logger.debug(f"Error checking accessibility for {url}: {e}")
                        url_info['is_accessible'] = False
                        url_info['validation_errors'].append('Accessibility check failed')
                
                # Only include URLs that pass all checks
                if (url_info['is_valid'] and 
                    (not check_robots or url_info['robots_allowed']) and
                    (not check_accessibility or url_info['is_accessible'])):
                    
                    validated_urls.append(url_info)
                
            except Exception as e:
                logger.error(f"Error validating URL {url}: {e}")
                url_info['validation_errors'].append(f'Validation error: {str(e)}')
            
            # Add delay to avoid overwhelming servers
            if check_accessibility:
                time.sleep(0.1)
        
        return validated_urls
    
    def filter_company_urls(self, url_infos: List[Dict[str, any]]) -> List[str]:
        """
        Filter to get only company website URLs
        
        Args:
            url_infos: List of URL information dictionaries
            
        Returns:
            List of company website URLs
        """
        company_urls = []
        
        for url_info in url_infos:
            if (url_info.get('is_valid', False) and 
                url_info.get('is_company_website', False) and
                not url_info.get('validation_errors', [])):
                
                company_urls.append(url_info['url'])
        
        return company_urls