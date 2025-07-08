"""
Configuration file for Healthcare Startup Discovery System

This module contains all configuration constants, API settings,
and keyword definitions for discovering healthcare startups.
"""

import os
from typing import List, Dict, Set

# API Configuration
CRUNCHBASE_API_KEY = os.getenv('CRUNCHBASE_API_KEY', '')
LINKEDIN_API_KEY = os.getenv('LINKEDIN_API_KEY', '')

# Rate limiting configuration
DEFAULT_DELAY = 1.0  # seconds between requests
MAX_CONCURRENT_REQUESTS = 10
RETRY_ATTEMPTS = 3
TIMEOUT = 30  # seconds

# Geographic focus
TARGET_COUNTRIES = {
    'germany', 'deutschland', 'german', 'deutsch',
    'austria', 'österreich', 'switzerland', 'schweiz',
    'netherlands', 'niederlande', 'belgium', 'belgien',
    'france', 'frankreich', 'italy', 'italien',
    'spain', 'spanien', 'portugal', 'poland', 'polen',
    'czech republic', 'tschechien', 'hungary', 'ungarn',
    'romania', 'rumänien', 'bulgaria', 'bulgarien',
    'croatia', 'kroatien', 'slovenia', 'slowenien',
    'slovakia', 'slowakei', 'estonia', 'estland',
    'latvia', 'lettland', 'lithuania', 'litauen',
    'finland', 'finnland', 'sweden', 'schweden',
    'denmark', 'dänemark', 'norway', 'norwegen',
    'ireland', 'irland', 'united kingdom', 'uk',
    'england', 'scotland', 'wales'
}

# Healthcare keywords (English and German)
HEALTHCARE_KEYWORDS = {
    # English terms
    'healthcare', 'health tech', 'healthtech', 'digital health',
    'medical technology', 'medtech', 'biotech', 'biotechnology',
    'telemedicine', 'telehealth', 'mhealth', 'ehealth',
    'pharmaceutical', 'pharma', 'clinical', 'medical device',
    'diagnostics', 'therapeutics', 'patient care', 'wellness',
    'fitness', 'nutrition', 'mental health', 'therapy',
    'hospital', 'clinic', 'doctor', 'physician', 'nurse',
    'surgery', 'surgical', 'radiology', 'cardiology',
    'oncology', 'neurology', 'dermatology', 'pediatrics',
    'geriatrics', 'rehabilitation', 'physiotherapy',
    'medical AI', 'health AI', 'medical analytics',
    'health data', 'electronic health records', 'EHR',
    'health insurance', 'medical imaging', 'genomics',
    'precision medicine', 'personalized medicine',
    'drug discovery', 'clinical trials', 'medical research',
    
    # German terms
    'gesundheitswesen', 'gesundheit', 'medizin', 'medizinisch',
    'gesundheitstechnik', 'medizintechnik', 'biotechnik',
    'telemedizin', 'digitale gesundheit', 'e-health',
    'pharmazie', 'pharmazeutisch', 'klinik', 'krankenhaus',
    'arzt', 'ärztin', 'patient', 'therapie', 'behandlung',
    'diagnose', 'diagnostik', 'chirurgie', 'operation',
    'radiologie', 'kardiologie', 'onkologie', 'neurologie',
    'dermatologie', 'pädiatrie', 'geriatrie',
    'rehabilitation', 'physiotherapie', 'wellness',
    'fitness', 'ernährung', 'psychische gesundheit',
    'gesundheitsdaten', 'medizinische ki', 'gesundheits-ki',
    'arzneimittel', 'medikament', 'clinical trial',
    'klinische studie', 'medizinische forschung'
}

# Business/startup keywords
STARTUP_KEYWORDS = {
    'startup', 'start-up', 'company', 'unternehmen', 'firma',
    'gmbh', 'ag', 'ltd', 'inc', 'corporation', 'corp',
    'ventures', 'technologies', 'solutions', 'systems',
    'platform', 'app', 'software', 'saas', 'api',
    'innovation', 'digital', 'tech', 'technology'
}

# URLs to exclude (social media, general directories, etc.)
EXCLUDED_DOMAINS = {
    'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
    'youtube.com', 'pinterest.com', 'tiktok.com', 'snapchat.com',
    'wikipedia.org', 'google.com', 'bing.com', 'yahoo.com',
    'amazon.com', 'ebay.com', 'alibaba.com', 'aliexpress.com',
    'reddit.com', 'quora.com', 'stackoverflow.com'
}

# Directories and sources to scrape
STARTUP_DIRECTORIES = [
    'https://www.crunchbase.com',
    'https://angel.co',
    'https://www.startupranking.com',
    'https://www.f6s.com',
    'https://www.eu-startups.com',
    'https://german-startups.com',
    'https://www.healthtech-capital.com',
    'https://www.healthcarestartups.eu'
]

# News and press release sources
NEWS_SOURCES = [
    'https://www.healthcareit-news.com',
    'https://www.mobihealthnews.com',
    'https://www.fiercehealthcare.com',
    'https://www.healthtechzone.com',
    'https://www.digital-health-magazine.com',
    'https://www.healtheuropa.eu',
    'https://www.healthcareglobal.com'
]

# Search engines for additional discovery
SEARCH_ENGINES = {
    'google': 'https://www.google.com/search?q={}',
    'bing': 'https://www.bing.com/search?q={}',
    'duckduckgo': 'https://duckduckgo.com/?q={}'
}

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Output configuration
OUTPUT_FORMATS = ['csv', 'json']
DEFAULT_OUTPUT_FORMAT = 'csv'
OUTPUT_FILENAME = 'healthcare_startups'

# Selenium/Playwright configuration
HEADLESS_BROWSER = True
BROWSER_TIMEOUT = 30
SCREENSHOT_ON_ERROR = False

# NLP Configuration
MIN_CONFIDENCE_SCORE = 0.7  # Minimum confidence for healthcare classification
MIN_TEXT_LENGTH = 100  # Minimum text length for NLP processing

# API endpoints and search queries
CRUNCHBASE_SEARCH_QUERY = "healthcare OR medtech OR biotech OR digital health"
GERMAN_SEARCH_QUERIES = [
    "deutsche healthcare startups",
    "medizintechnik startups deutschland",
    "gesundheitstechnik unternehmen",
    "digital health startups europe",
    "european medtech companies"
]

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'healthcare_discovery.log'