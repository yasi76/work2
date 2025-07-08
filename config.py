# Configuration settings for healthcare URL discovery and validation

# Keywords that indicate healthcare-related content
HEALTHCARE_KEYWORDS = [
    'health', 'medical', 'therapy', 'patient', 'doctor', 'clinic', 'hospital',
    'medicine', 'healthcare', 'wellness', 'fitness', 'nutrition', 'pharma',
    'telemedicine', 'digital health', 'AI health', 'medical AI', 'biotech',
    'medtech', 'rehabilitation', 'diagnosis', 'treatment', 'care', 'mental health',
    'psychology', 'psychiatry', 'dental', 'surgery', 'therapeutic', 'clinical',
    'prevention', 'screening', 'monitoring', 'symptom', 'disease', 'condition',
    'recovery', 'healing', 'cure', 'medication', 'prescription', 'dosage',
    'vital signs', 'heart rate', 'blood pressure', 'diabetes', 'cancer',
    'covid', 'vaccine', 'immunization', 'allergy', 'chronic', 'acute'
]

# Domains to exclude (social media, login pages, etc.)
EXCLUDED_DOMAINS = [
    'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
    'youtube.com', 'tiktok.com', 'snapchat.com', 'pinterest.com',
    'reddit.com', 'discord.com', 'telegram.org', 'whatsapp.com',
    'login.', 'auth.', 'signin.', 'signup.', 'register.', 'account.',
    'admin.', 'dashboard.', 'portal.', 'intranet.', 'internal.'
]

# URL patterns to exclude
EXCLUDED_PATTERNS = [
    '/login', '/signin', '/signup', '/register', '/auth', '/account',
    '/admin', '/dashboard', '/portal', '/privacy', '/terms', '/contact',
    '/about-us', '/impressum', '/datenschutz', '/cookies'
]

# HTTP request settings
REQUEST_TIMEOUT = 10  # seconds
MAX_CONCURRENT_REQUESTS = 20
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Search settings
GOOGLE_SEARCH_QUERIES = [
    'digital health startups Germany',
    'healthcare AI companies Europe',
    'medical technology startups',
    'telemedicine platforms Germany',
    'health tech companies Berlin',
    'digital therapeutics Europe',
    'medical AI startups',
    'healthcare innovation Germany'
]

# Output settings
OUTPUT_FORMATS = ['csv', 'json']
MAX_URLS_PER_SOURCE = 50