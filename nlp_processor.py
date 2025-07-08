"""
NLP Processor for Healthcare Startup Discovery System

This module handles text processing, healthcare keyword detection,
and relevance scoring for discovered companies.
"""

import re
import logging
from typing import List, Set, Tuple, Dict
from collections import Counter

# Essential imports
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import PorterStemmer, SnowballStemmer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available. Basic text processing will be used.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Basic similarity scoring will be used.")

try:
    from langdetect import detect, LangDetectError
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("Warning: langdetect not available. Language detection disabled.")

from config import HEALTHCARE_KEYWORDS, STARTUP_KEYWORDS, TARGET_COUNTRIES, MIN_CONFIDENCE_SCORE, MIN_TEXT_LENGTH

# Set up logging
logger = logging.getLogger(__name__)


class HealthcareNLPProcessor:
    """
    NLP processor for analyzing text content and determining healthcare relevance
    
    This class provides functionality to:
    - Detect healthcare-related keywords
    - Calculate relevance scores
    - Extract company information from text
    - Detect geographic location mentions
    
    Gracefully handles missing dependencies with fallback implementations.
    """
    
    def __init__(self):
        """Initialize the NLP processor with available resources"""
        # Try to download NLTK data if available
        if NLTK_AVAILABLE:
            self._download_nltk_data()
            # Initialize stemmers for different languages
            try:
                self.english_stemmer = PorterStemmer()
                self.german_stemmer = SnowballStemmer('german')
                self.stemmers_available = True
            except Exception as e:
                logger.warning(f"Could not initialize stemmers: {e}")
                self.stemmers_available = False
        else:
            self.stemmers_available = False
        
        # Prepare keyword sets for faster lookup
        self.healthcare_keywords = {kw.lower() for kw in HEALTHCARE_KEYWORDS}
        self.startup_keywords = {kw.lower() for kw in STARTUP_KEYWORDS}
        self.country_keywords = {country.lower() for country in TARGET_COUNTRIES}
        
        # Create stemmed versions of keywords for better matching (if available)
        if self.stemmers_available:
            self.stemmed_healthcare_keywords = self._create_stemmed_keywords(self.healthcare_keywords)
            self.stemmed_startup_keywords = self._create_stemmed_keywords(self.startup_keywords)
        else:
            self.stemmed_healthcare_keywords = self.healthcare_keywords
            self.stemmed_startup_keywords = self.startup_keywords
        
        # Initialize TF-IDF vectorizer for semantic similarity (if available)
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1
                )
                self.sklearn_available = True
            except Exception as e:
                logger.warning(f"Could not initialize TF-IDF vectorizer: {e}")
                self.sklearn_available = False
        else:
            self.sklearn_available = False
        
        # Healthcare reference text for similarity comparison
        self.healthcare_reference_text = " ".join(HEALTHCARE_KEYWORDS)
        
        logger.info("HealthcareNLPProcessor initialized successfully")
        logger.info(f"NLTK available: {NLTK_AVAILABLE}")
        logger.info(f"Sklearn available: {SKLEARN_AVAILABLE}")
        logger.info(f"Langdetect available: {LANGDETECT_AVAILABLE}")
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        if not NLTK_AVAILABLE:
            return
            
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading NLTK data...")
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            except Exception as e:
                logger.warning(f"Could not download NLTK data: {e}")
    
    def _create_stemmed_keywords(self, keywords: Set[str]) -> Set[str]:
        """Create stemmed versions of keywords for better matching"""
        if not self.stemmers_available:
            return keywords
            
        stemmed = set()
        for keyword in keywords:
            try:
                # Try English stemming
                stemmed.add(self.english_stemmer.stem(keyword))
                # Try German stemming
                stemmed.add(self.german_stemmer.stem(keyword))
            except Exception:
                # If stemming fails, use original keyword
                stemmed.add(keyword)
        return stemmed
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Detected language code (e.g., 'en', 'de')
        """
        if not LANGDETECT_AVAILABLE:
            return 'en'  # Default to English
            
        try:
            return detect(text)
        except:
            return 'en'  # Default to English
    
    def preprocess_text(self, text: str, language: str = 'en') -> List[str]:
        """
        Preprocess text for analysis
        
        Args:
            text: Input text to preprocess
            language: Language of the text
            
        Returns:
            List of preprocessed tokens
        """
        if not text or len(text) < MIN_TEXT_LENGTH:
            return []
        
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Tokenize (with or without NLTK)
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text)
            except:
                # Fallback to simple split if NLTK fails
                tokens = text.split()
        else:
            tokens = text.split()
        
        # Remove stopwords (if NLTK available)
        if NLTK_AVAILABLE:
            try:
                stop_words = set(stopwords.words('english'))
                if language == 'de':
                    stop_words.update(stopwords.words('german'))
            except:
                # Use basic stopwords if NLTK fails
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        else:
            # Basic English stopwords
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        
        # Filter tokens
        tokens = [
            token for token in tokens 
            if len(token) > 2 and token not in stop_words
        ]
        
        return tokens
    
    def extract_healthcare_keywords(self, text: str) -> Tuple[Set[str], float]:
        """
        Extract healthcare keywords from text and calculate relevance score
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (matched_keywords, relevance_score)
        """
        if not text:
            return set(), 0.0
        
        text_lower = text.lower()
        matched_keywords = set()
        
        # Direct keyword matching
        for keyword in self.healthcare_keywords:
            if keyword in text_lower:
                matched_keywords.add(keyword)
        
        # Stemmed keyword matching for partial matches (if available)
        if self.stemmers_available:
            language = self.detect_language(text)
            tokens = self.preprocess_text(text, language)
            
            stemmer = self.german_stemmer if language == 'de' else self.english_stemmer
            try:
                stemmed_tokens = {stemmer.stem(token) for token in tokens}
                
                # Check for stemmed keyword matches
                for stemmed_keyword in self.stemmed_healthcare_keywords:
                    if stemmed_keyword in stemmed_tokens:
                        # Find original keyword that matches this stem
                        for original_keyword in self.healthcare_keywords:
                            try:
                                if stemmer.stem(original_keyword) == stemmed_keyword:
                                    matched_keywords.add(original_keyword)
                                    break
                            except:
                                continue
            except Exception as e:
                logger.debug(f"Error in stemmed matching: {e}")
        
        # Calculate relevance score based on keyword density and diversity
        if not matched_keywords:
            return matched_keywords, 0.0
        
        # Base score from keyword matches
        keyword_score = len(matched_keywords) / max(len(self.healthcare_keywords), 10)
        
        # Density score (how often healthcare terms appear)
        tokens = self.preprocess_text(text)
        total_words = len(tokens) if tokens else 1
        density_score = len(matched_keywords) / max(total_words, 10)
        
        # Combine scores
        relevance_score = min(1.0, (keyword_score * 0.7) + (density_score * 0.3))
        
        return matched_keywords, relevance_score
    
    def calculate_semantic_similarity(self, text: str) -> float:
        """
        Calculate semantic similarity to healthcare domain using TF-IDF
        
        Args:
            text: Input text to analyze
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not self.sklearn_available or not text or len(text) < MIN_TEXT_LENGTH:
            return 0.0
        
        try:
            # Combine reference text and input text
            corpus = [self.healthcare_reference_text, text]
            
            # Compute TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Return similarity between reference and input text
            return float(similarity_matrix[0, 1])
        
        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def detect_geographic_location(self, text: str) -> List[str]:
        """
        Detect mentions of target countries/regions in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected countries
        """
        text_lower = text.lower()
        detected_countries = []
        
        for country in self.country_keywords:
            if country in text_lower:
                detected_countries.append(country)
        
        # Additional patterns for country detection
        country_patterns = {
            r'\bgerman\b|\bdeutsch\b|\bgermany\b|\bdeutschland\b': 'germany',
            r'\baustrian\b|\baustria\b|\bösterreich\b': 'austria',
            r'\bswiss\b|\bswitzerland\b|\bschweiz\b': 'switzerland',
            r'\bdutch\b|\bnetherlands\b|\bniederlande\b': 'netherlands',
            r'\bbelgian\b|\bbelgium\b|\bbelgien\b': 'belgium',
            r'\bfrench\b|\bfrance\b|\bfrankreich\b': 'france',
            r'\bitalian\b|\bitaly\b|\bitalien\b': 'italy',
            r'\bspanish\b|\bspain\b|\bspanien\b': 'spain',
            r'\bpolish\b|\bpoland\b|\bpolen\b': 'poland',
            r'\bbritish\b|\buk\b|\bunited kingdom\b|\bengland\b': 'united_kingdom'
        }
        
        for pattern, country in country_patterns.items():
            if re.search(pattern, text_lower):
                if country not in detected_countries:
                    detected_countries.append(country)
        
        return detected_countries
    
    def is_startup_related(self, text: str) -> bool:
        """
        Check if text contains startup-related keywords
        
        Args:
            text: Input text to analyze
            
        Returns:
            True if startup-related keywords are found
        """
        text_lower = text.lower()
        
        for keyword in self.startup_keywords:
            if keyword in text_lower:
                return True
        
        return False
    
    def calculate_overall_confidence(self, text: str, url: str = "") -> Tuple[float, Set[str], List[str]]:
        """
        Calculate overall confidence score for healthcare relevance
        
        Args:
            text: Input text to analyze
            url: URL of the source (optional, for additional context)
            
        Returns:
            Tuple of (confidence_score, matched_keywords, detected_countries)
        """
        if not text:
            return 0.0, set(), []
        
        # Extract healthcare keywords and get keyword-based score
        matched_keywords, keyword_score = self.extract_healthcare_keywords(text)
        
        # Calculate semantic similarity (if available)
        semantic_score = self.calculate_semantic_similarity(text)
        
        # Check for startup relevance
        startup_relevant = self.is_startup_related(text)
        startup_bonus = 0.1 if startup_relevant else 0.0
        
        # Detect geographic relevance
        detected_countries = self.detect_geographic_location(text)
        geographic_bonus = 0.1 if detected_countries else 0.0
        
        # URL analysis for additional context
        url_score = 0.0
        if url:
            url_lower = url.lower()
            if any(keyword in url_lower for keyword in ['health', 'medical', 'med', 'bio', 'clinic']):
                url_score = 0.1
        
        # Combine all scores (adjust weights if sklearn not available)
        if self.sklearn_available:
            confidence_score = min(1.0, 
                (keyword_score * 0.4) + 
                (semantic_score * 0.3) + 
                startup_bonus + 
                geographic_bonus + 
                url_score
            )
        else:
            # Give more weight to keyword score if semantic similarity unavailable
            confidence_score = min(1.0, 
                (keyword_score * 0.7) + 
                startup_bonus + 
                geographic_bonus + 
                url_score
            )
        
        return confidence_score, matched_keywords, detected_countries
    
    def extract_company_name_from_text(self, text: str) -> str:
        """
        Attempt to extract company name from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Extracted company name or empty string
        """
        # Simple heuristics for company name extraction
        if NLTK_AVAILABLE:
            try:
                sentences = sent_tokenize(text)
            except:
                sentences = text.split('.')
        else:
            sentences = text.split('.')
        
        # Look for patterns like "Company Name is..." or "Company Name offers..."
        company_patterns = [
            r'^([A-Z][a-zA-Z\s&]+)(?:\s+is\s+|\s+offers\s+|\s+provides\s+)',
            r'([A-Z][a-zA-Z\s&]+)(?:\s+GmbH|\s+AG|\s+Ltd|\s+Inc|\s+Corp)',
            r'^([A-Z][a-zA-Z\s&]+)(?:\s*[-–]\s*)',
        ]
        
        for sentence in sentences[:3]:  # Check first 3 sentences
            for pattern in company_patterns:
                match = re.search(pattern, sentence.strip())
                if match:
                    company_name = match.group(1).strip()
                    if len(company_name) > 2 and len(company_name) < 50:
                        return company_name
        
        return ""
    
    def is_healthcare_relevant(self, text: str, url: str = "", min_confidence: float = None) -> bool:
        """
        Determine if text/URL is healthcare relevant
        
        Args:
            text: Text content to analyze
            url: URL for additional context
            min_confidence: Minimum confidence threshold (uses config default if None)
            
        Returns:
            True if healthcare relevant
        """
        if min_confidence is None:
            min_confidence = MIN_CONFIDENCE_SCORE
        
        confidence_score, _, _ = self.calculate_overall_confidence(text, url)
        return confidence_score >= min_confidence