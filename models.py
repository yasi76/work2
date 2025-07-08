"""
Data models for Healthcare Startup Discovery System

This module defines the data structures used throughout the application
to represent companies, sources, and results.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime
from enum import Enum
import validators


class SourceType(Enum):
    """Enumeration of different source types for company discovery"""
    DIRECTORY = "directory"
    NEWS = "news"
    API = "api"
    SEARCH_ENGINE = "search_engine"
    WEBSITE = "website"
    PRESS_RELEASE = "press_release"


class Country(Enum):
    """Enumeration of target European countries"""
    GERMANY = "germany"
    AUSTRIA = "austria"
    SWITZERLAND = "switzerland"
    NETHERLANDS = "netherlands"
    BELGIUM = "belgium"
    FRANCE = "france"
    ITALY = "italy"
    SPAIN = "spain"
    PORTUGAL = "portugal"
    POLAND = "poland"
    CZECH_REPUBLIC = "czech_republic"
    HUNGARY = "hungary"
    ROMANIA = "romania"
    BULGARIA = "bulgaria"
    CROATIA = "croatia"
    SLOVENIA = "slovenia"
    SLOVAKIA = "slovakia"
    ESTONIA = "estonia"
    LATVIA = "latvia"
    LITHUANIA = "lithuania"
    FINLAND = "finland"
    SWEDEN = "sweden"
    DENMARK = "denmark"
    NORWAY = "norway"
    IRELAND = "ireland"
    UNITED_KINGDOM = "united_kingdom"
    UNKNOWN = "unknown"


@dataclass
class CompanyInfo:
    """
    Data class representing a healthcare startup/SME
    
    Attributes:
        name: Company name
        url: Primary company URL
        description: Company description/summary
        country: Detected or specified country
        source_type: How this company was discovered
        source_url: URL where company info was found
        confidence_score: Healthcare relevance confidence (0.0-1.0)
        keywords_matched: Healthcare keywords found in company info
        discovered_at: When this company was discovered
        additional_urls: Other URLs associated with the company
        metadata: Additional metadata about the company
    """
    name: str
    url: str
    description: str = ""
    country: Country = Country.UNKNOWN
    source_type: SourceType = SourceType.WEBSITE
    source_url: str = ""
    confidence_score: float = 0.0
    keywords_matched: Set[str] = field(default_factory=set)
    discovered_at: datetime = field(default_factory=datetime.now)
    additional_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        # Validate main URL
        if not validators.url(self.url):
            raise ValueError(f"Invalid URL: {self.url}")
        
        # Clean and validate additional URLs
        self.additional_urls = [
            url for url in self.additional_urls 
            if validators.url(url)
        ]
        
        # Ensure confidence score is within valid range
        self.confidence_score = max(0.0, min(1.0, self.confidence_score))
        
        # Clean company name
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Company name cannot be empty")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'url': self.url,
            'description': self.description,
            'country': self.country.value,
            'source_type': self.source_type.value,
            'source_url': self.source_url,
            'confidence_score': self.confidence_score,
            'keywords_matched': list(self.keywords_matched),
            'discovered_at': self.discovered_at.isoformat(),
            'additional_urls': self.additional_urls,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CompanyInfo':
        """Create CompanyInfo from dictionary"""
        return cls(
            name=data['name'],
            url=data['url'],
            description=data.get('description', ''),
            country=Country(data.get('country', 'unknown')),
            source_type=SourceType(data.get('source_type', 'website')),
            source_url=data.get('source_url', ''),
            confidence_score=data.get('confidence_score', 0.0),
            keywords_matched=set(data.get('keywords_matched', [])),
            discovered_at=datetime.fromisoformat(data.get('discovered_at', datetime.now().isoformat())),
            additional_urls=data.get('additional_urls', []),
            metadata=data.get('metadata', {})
        )


@dataclass
class ScrapingResult:
    """
    Result of a scraping operation
    
    Attributes:
        companies: List of discovered companies
        source_url: URL that was scraped
        source_type: Type of source
        success: Whether scraping was successful
        error_message: Error message if scraping failed
        scraped_at: When scraping was performed
        total_urls_found: Total URLs discovered (before filtering)
        filtered_urls: URLs after filtering
        processing_time: Time taken for scraping in seconds
    """
    companies: List[CompanyInfo] = field(default_factory=list)
    source_url: str = ""
    source_type: SourceType = SourceType.WEBSITE
    success: bool = True
    error_message: str = ""
    scraped_at: datetime = field(default_factory=datetime.now)
    total_urls_found: int = 0
    filtered_urls: int = 0
    processing_time: float = 0.0
    
    def add_company(self, company: CompanyInfo):
        """Add a company to the result"""
        self.companies.append(company)
        self.filtered_urls += 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'companies': [company.to_dict() for company in self.companies],
            'source_url': self.source_url,
            'source_type': self.source_type.value,
            'success': self.success,
            'error_message': self.error_message,
            'scraped_at': self.scraped_at.isoformat(),
            'total_urls_found': self.total_urls_found,
            'filtered_urls': self.filtered_urls,
            'processing_time': self.processing_time
        }


@dataclass
class DiscoverySession:
    """
    Represents a complete discovery session
    
    Attributes:
        session_id: Unique identifier for this session
        started_at: When session started
        completed_at: When session completed (None if ongoing)
        total_companies: Total unique companies discovered
        sources_scraped: Number of sources scraped
        results: List of scraping results
        errors: List of errors encountered
        configuration: Configuration used for this session
    """
    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_companies: int = 0
    sources_scraped: int = 0
    results: List[ScrapingResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    configuration: Dict[str, str] = field(default_factory=dict)
    
    def add_result(self, result: ScrapingResult):
        """Add a scraping result to the session"""
        self.results.append(result)
        self.sources_scraped += 1
        if result.success:
            self.total_companies += len(result.companies)
        else:
            self.errors.append(f"Error scraping {result.source_url}: {result.error_message}")
    
    def complete_session(self):
        """Mark session as completed"""
        self.completed_at = datetime.now()
    
    def get_all_companies(self) -> List[CompanyInfo]:
        """Get all companies from all results, deduplicated by URL"""
        companies_dict = {}
        for result in self.results:
            for company in result.companies:
                # Use URL as key for deduplication
                if company.url not in companies_dict:
                    companies_dict[company.url] = company
                else:
                    # Merge information if we have the same company from multiple sources
                    existing = companies_dict[company.url]
                    existing.keywords_matched.update(company.keywords_matched)
                    existing.additional_urls.extend(company.additional_urls)
                    # Keep the higher confidence score
                    if company.confidence_score > existing.confidence_score:
                        existing.confidence_score = company.confidence_score
                        existing.description = company.description
        
        return list(companies_dict.values())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_companies': self.total_companies,
            'sources_scraped': self.sources_scraped,
            'results': [result.to_dict() for result in self.results],
            'errors': self.errors,
            'configuration': self.configuration
        }