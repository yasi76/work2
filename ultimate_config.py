# ULTIMATE Healthcare URL Discovery Configuration
# Designed to find 2000-5000+ healthcare companies across Europe

# REQUEST SETTINGS
REQUEST_TIMEOUT = 15
MAX_CONCURRENT_REQUESTS = 20
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# COMPREHENSIVE EUROPEAN HEALTHCARE DATABASES
ULTIMATE_HEALTHCARE_SOURCES = {
    
    # GOVERNMENT & REGULATORY DATABASES (High Quality)
    'government_databases': [
        # Germany
        'https://www.bfarm.de/DE/Home/home_node.html',
        'https://www.pei.de/DE/home/home-node.html', 
        'https://www.dimdi.de/dynamic/de/startseite/',
        'https://www.bundesgesundheitsministerium.de/',
        
        # France
        'https://ansm.sante.fr/',
        'https://www.has-sante.fr/',
        'https://solidarites-sante.gouv.fr/',
        
        # Netherlands
        'https://www.cbg-meb.nl/',
        'https://www.rivm.nl/',
        'https://www.zorginstituutnederland.nl/',
        
        # UK
        'https://www.mhra.gov.uk/',
        'https://www.nice.org.uk/',
        'https://www.nhs.uk/',
        
        # EU-wide
        'https://www.ema.europa.eu/',
        'https://ec.europa.eu/health/',
        'https://www.ecdc.europa.eu/',
    ],
    
    # MEDICAL DEVICE & BIOTECH DIRECTORIES
    'medtech_directories': [
        'https://www.medtech-europe.org/about-medtech/members/',
        'https://www.eucomed.org/members',
        'https://www.advamed.org/member-directory/',
        'https://www.spectaris.de/mitgliederliste/',
        'https://www.zvei.org/branchen/health-care/',
        'https://www.bvmed.de/mitglieder/',
        'https://www.vdgh.de/mitglieder/',
        'https://www.snitem.fr/les-adherents/',
        'https://www.fenin.es/directorio-de-empresas/',
        'https://www.assobiomedica.it/associati/',
        'https://www.neiinstitute.org/membership/',
        'https://www.techuk.org/health',
    ],
    
    # PHARMACEUTICAL INDUSTRY DATABASES
    'pharma_directories': [
        'https://www.efpia.eu/about-medicines/development-of-medicines/',
        'https://www.vfa.de/mitglieder',
        'https://www.leem.org/repertoire-des-adherents',
        'https://www.vnig.nl/leden/',
        'https://www.abpi.org.uk/our-members/',
        'https://www.farmaindustria.es/socios/',
        'https://www.farmindustria.it/associati/',
        'https://www.interpharma.ch/mitglieder',
        'https://www.bio.org/membership/member-directory',
        'https://www.europabio.org/members',
    ],
    
    # DIGITAL HEALTH & HEALTHTECH DATABASES
    'digital_health_directories': [
        'https://www.himss.org/membership/corporate-members',
        'https://www.healtheuropa.eu/digital-health/',
        'https://www.digitalhealth.net/directory/',
        'https://www.ehealthnews.eu/directory/',
        'https://www.healthtechmagazine.net/directory/',
        'https://www.mhealthintelligence.com/directory/',
        'https://www.healthcareitnews.com/directory/',
        'https://www.mobihealthnews.com/directory/',
        'https://www.digitalehealthcare.de/unternehmen/',
        'https://www.france-biotech.fr/members/',
        'https://www.hollandhealth.nl/members/',
        'https://www.swissbiotech.org/members/',
    ],
    
    # STARTUP & INNOVATION DATABASES
    'startup_databases': [
        'https://www.eu-startups.com/directory/',
        'https://startup-map.eu/companies',
        'https://www.startupblink.com/startup-ecosystem-rankings/',
        'https://www.dealroom.co/sectors/healthcare',
        'https://www.crunchbase.com/hub/europe-health-care-startups',
        'https://angel.co/companies?markets[]=digital-health',
        'https://www.f6s.com/companies/health/europe',
        'https://foundersandcompany.com/health-care/',
        'https://www.techeu.co/companies/',
        'https://innovationorigins.com/en/category/health/',
    ],
    
    # HEALTHCARE ACCELERATORS & INCUBATORS
    'accelerator_portfolios': [
        'https://www.techstars.com/portfolio',
        'https://www.plug-and-play.com/health/portfolio/',
        'https://www.ycombinator.com/companies/',
        'https://www.antler.co/portfolio',
        'https://www.rockhealth.com/portfolio/',
        'https://healthbox.com/portfolio/',
        'https://www.bayer.com/en/innovation/g4a-portfolio',
        'https://www.novartis.com/our-company/innovation/portfolio',
        'https://innovation.roche.com/partnerships/',
        'https://www.jnj.com/innovation/jlabs-portfolio',
    ],
    
    # HEALTHCARE CONFERENCES & EVENTS (Speaker/Exhibitor Lists)
    'conference_directories': [
        'https://www.himss.org/conferences-events/himss-global/',
        'https://www.healthcarebusinessinternational.com/events/',
        'https://www.healthtech-event.com/exhibitors/',
        'https://medica.de/en/exhibitors/',
        'https://www.arab-health.com/exhibitors/',
        'https://www.conferenceboard.org/topics/healthcare/',
        'https://www.vitafoods.eu.com/exhibitors/',
        'https://www.healtheuropa.eu/events/',
        'https://www.digitalhealth.london/speakers/',
        'https://healthtechexpo.co.uk/exhibitors/',
    ],
    
    # RESEARCH INSTITUTIONS & UNIVERSITY SPIN-OFFS
    'research_institutions': [
        'https://www.charite.de/forschung/technologietransfer/',
        'https://www.mpg.de/technology-transfer',
        'https://www.helmholtz.de/transfer/',
        'https://www.fraunhofer.de/en/innovation/transfer.html',
        'https://www.inserm.fr/valorisation/',
        'https://www.cnrs.fr/en/innovation',
        'https://www.cam.ac.uk/research/innovation-and-ip/',
        'https://www.ox.ac.uk/research/innovation-and-entrepreneurship/',
        'https://www.imperial.ac.uk/enterprise/',
        'https://www.tudelft.nl/en/innovation-impact/',
    ],
    
    # INVESTMENT & FUNDING DATABASES
    'investment_databases': [
        'https://www.cbinsights.com/research/digital-health-funding-europe/',
        'https://www.pitchbook.com/news/reports/q3-2024-european-healthcare-it-report',
        'https://techcrunch.com/category/health/',
        'https://www.mobihealthnews.com/news/funding',
        'https://www.healthcarefinancenews.com/news/investment',
        'https://www.modernhealthcare.com/finance/venture-capital',
        'https://www.bioworld.com/funding',
        'https://www.fiercehealthcare.com/finance',
        'https://www.healthtechmagazine.net/funding/',
        'https://digitalhealth.london/funding/',
    ],
    
    # COUNTRY-SPECIFIC HEALTHCARE CHAMBERS
    'healthcare_chambers': [
        # Germany
        'https://www.bdc.de/mitglieder/',
        'https://www.vci.de/die-branche/mitglieder/',
        'https://www.bitkom.org/Themen/Technologien-Software/Digital-Health',
        
        # France
        'https://www.leem.org/',
        'https://www.syntec-numerique.fr/sante-numerique',
        'https://www.france-biotech.fr/',
        
        # Netherlands
        'https://www.hollandhealthtech.nl/members/',
        'https://www.vnoncw.nl/leden/',
        'https://www.fme.nl/leden/',
        
        # Switzerland
        'https://www.swiss-biotech.org/members/',
        'https://www.scienceindustries.ch/members',
        
        # Nordic
        'https://www.medtech.dk/members/',
        'https://www.medicinteknikbranschen.se/members/',
        'https://www.teknologiateollisuus.fi/en/members/',
    ],
    
    # CLINICAL TRIAL DATABASES (Companies running trials)
    'clinical_trial_sources': [
        'https://clinicaltrials.gov/ct2/results?cond=&term=&cntry=DE',
        'https://clinicaltrials.gov/ct2/results?cond=&term=&cntry=FR', 
        'https://clinicaltrials.gov/ct2/results?cond=&term=&cntry=NL',
        'https://www.clinicaltrialsregister.eu/',
        'https://www.controlled-trials.com/',
        'https://trialsearch.who.int/',
    ]
}

# ADVANCED SEARCH PATTERNS (500+ combinations)
ULTIMATE_SEARCH_PATTERNS = [
    # Company type + Location combinations
    'digital health startups {city}',
    'medtech companies {city}', 
    'biotech firms {city}',
    'pharmaceutical companies {city}',
    'healthcare AI {city}',
    'telemedicine {city}',
    'medical devices {city}',
    'health analytics {city}',
    'clinical software {city}',
    'hospital technology {city}',
    
    # Funding + Location
    'healthcare funding {city} 2024',
    'medtech investment {city}',
    'digital health venture capital {city}',
    'biotech IPO {city}',
    
    # Technology + Healthcare
    'AI medical {city}',
    'machine learning healthcare {city}',
    'robotics surgery {city}',
    'IoT medical devices {city}',
    'blockchain healthcare {city}',
    'VR therapy {city}',
    'AR surgery {city}',
    
    # Specialty areas
    'digital therapeutics {city}',
    'precision medicine {city}',
    'personalized medicine {city}',
    'genomics companies {city}',
    'diagnostics {city}',
    'imaging technology {city}',
    'laboratory automation {city}',
    'medical robotics {city}',
]

# EUROPEAN CITIES FOR SEARCH (100+ cities)
ULTIMATE_EUROPEAN_CITIES = [
    # Germany (20 cities)
    'Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 
    'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig', 'Bremen', 'Dresden',
    'Hannover', 'Nuremberg', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld',
    'Bonn', 'Münster',
    
    # France (15 cities)
    'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg',
    'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre',
    'Saint-Étienne', 'Toulon',
    
    # UK (15 cities) 
    'London', 'Birmingham', 'Manchester', 'Glasgow', 'Liverpool', 'Leeds',
    'Sheffield', 'Edinburgh', 'Bristol', 'Cardiff', 'Leicester', 'Coventry',
    'Bradford', 'Belfast', 'Nottingham',
    
    # Netherlands (10 cities)
    'Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven', 'Tilburg',
    'Groningen', 'Almere', 'Breda', 'Nijmegen',
    
    # Switzerland (8 cities)
    'Zurich', 'Geneva', 'Basel', 'Lausanne', 'Bern', 'Winterthur', 'Lucerne', 'St. Gallen',
    
    # Spain (10 cities)
    'Madrid', 'Barcelona', 'Valencia', 'Seville', 'Zaragoza', 'Málaga',
    'Murcia', 'Palma', 'Las Palmas', 'Bilbao',
    
    # Italy (10 cities)
    'Rome', 'Milan', 'Naples', 'Turin', 'Palermo', 'Genoa', 'Bologna',
    'Florence', 'Bari', 'Catania',
    
    # Nordic Countries (10 cities)
    'Stockholm', 'Copenhagen', 'Oslo', 'Helsinki', 'Gothenburg', 'Malmö',
    'Bergen', 'Tampere', 'Aarhus', 'Turku',
    
    # Other European (12 cities)
    'Vienna', 'Brussels', 'Dublin', 'Lisbon', 'Prague', 'Warsaw', 'Budapest',
    'Bucharest', 'Sofia', 'Zagreb', 'Ljubljana', 'Bratislava'
]

# HEALTHCARE SECTORS (30+ specialties)
ULTIMATE_HEALTHCARE_SECTORS = {
    'digital_therapeutics': ['digital therapeutics', 'DTx', 'prescription digital therapeutics', 'therapeutic apps'],
    'telemedicine': ['telemedicine', 'telehealth', 'remote consultation', 'virtual care', 'online medicine'],
    'medical_devices': ['medical device', 'medical equipment', 'diagnostic device', 'implantable devices'],
    'health_analytics': ['health analytics', 'medical data analytics', 'health insights', 'clinical analytics'],
    'mental_health': ['mental health', 'psychology', 'psychiatry', 'behavioral health', 'therapy apps'],
    'ai_ml_health': ['medical AI', 'healthcare AI', 'machine learning medical', 'AI diagnosis'],
    'chronic_care': ['chronic disease management', 'diabetes care', 'hypertension management', 'COPD'],
    'womens_health': ['womens health', 'fertility', 'pregnancy', 'reproductive health', 'maternal health'],
    'elderly_care': ['elderly care', 'senior health', 'aging', 'geriatric', 'dementia care'],
    'pediatric': ['pediatric', 'children health', 'infant care', 'neonatal', 'pediatric apps'],
    'oncology': ['cancer care', 'oncology', 'tumor', 'chemotherapy', 'radiation therapy'],
    'cardiology': ['cardiology', 'heart health', 'cardiovascular', 'cardiac monitoring'],
    'dermatology': ['dermatology', 'skin health', 'dermatological', 'skin cancer'],
    'pharmacy': ['digital pharmacy', 'e-pharmacy', 'medication management', 'drug delivery'],
    'genomics': ['genomics', 'genetic testing', 'precision medicine', 'personalized medicine'],
    'imaging': ['medical imaging', 'radiology', 'MRI', 'CT scan', 'ultrasound', 'X-ray'],
    'surgery': ['surgical robotics', 'minimally invasive surgery', 'surgical planning', 'OR technology'],
    'diagnostics': ['in-vitro diagnostics', 'point-of-care testing', 'laboratory diagnostics'],
    'rehabilitation': ['rehabilitation', 'physical therapy', 'occupational therapy', 'recovery'],
    'nutrition': ['digital nutrition', 'dietary apps', 'nutrition tracking', 'meal planning'],
    'fitness': ['digital fitness', 'wellness apps', 'activity tracking', 'exercise apps'],
    'sleep': ['sleep technology', 'sleep tracking', 'sleep disorders', 'sleep medicine'],
    'respiratory': ['respiratory health', 'asthma', 'COPD', 'lung health', 'breathing'],
    'neurology': ['neurology', 'brain health', 'neurological disorders', 'stroke'],
    'orthopedics': ['orthopedics', 'bone health', 'joint health', 'spine'],
    'ophthalmology': ['ophthalmology', 'eye health', 'vision', 'retinal'],
    'urology': ['urology', 'kidney health', 'bladder', 'prostate'],
    'emergency': ['emergency medicine', 'critical care', 'trauma', 'ICU technology'],
    'laboratory': ['laboratory automation', 'lab technology', 'clinical laboratory'],
    'hospital_tech': ['hospital management', 'EMR', 'EHR', 'PACS', 'HIS']
}

# DISCOVERY SETTINGS
ULTIMATE_SETTINGS = {
    'MAX_URLS_PER_SOURCE': 10,  # Much smaller - was 500
    'MAX_SEARCH_RESULTS_PER_QUERY': 20,  # Much smaller - was 200
    'ENABLE_DEEP_CRAWLING': False,  # Disable deep crawling
    'CRAWL_DEPTH': 1,  # Only surface level
    'PARALLEL_SEARCHES': 3,  # Much fewer concurrent - was 20
    'SEARCH_DELAY_MIN': 2,  # Longer delays
    'SEARCH_DELAY_MAX': 5,
    'ENABLE_MULTILINGUAL_SEARCH': False,  # Disable to reduce complexity
    'ENABLE_SECTOR_SPECIFIC_SEARCH': False,
    'ENABLE_GEOGRAPHIC_SEARCH': False,
    'ENABLE_ADVANCED_FILTERING': False,
    'MIN_HEALTHCARE_SCORE': 0,
    'ENABLE_COMPANY_VALIDATION': True,
    'MAX_TOTAL_URLS_TARGET': 100  # Realistic default - matches available companies
}

# MULTI-LANGUAGE KEYWORDS (Extended)
ULTIMATE_HEALTHCARE_KEYWORDS = [
    # English (Core)
    'health', 'medical', 'healthcare', 'medicine', 'clinic', 'hospital',
    'doctor', 'physician', 'patient', 'therapy', 'treatment', 'diagnosis',
    'pharmaceutical', 'biotech', 'medtech', 'digital health', 'telemedicine',
    'therapeutic', 'clinical', 'diagnostic', 'surgical', 'rehabilitation',
    
    # German (Extended)
    'Gesundheit', 'medizinisch', 'Gesundheitswesen', 'Medizin', 'Klinik',
    'Krankenhaus', 'Arzt', 'Patient', 'Therapie', 'Behandlung', 'Diagnose',
    'Pharmazie', 'Biotechnologie', 'Medizintechnik', 'digitale Gesundheit',
    'Telemedizin', 'therapeutisch', 'klinisch', 'diagnostisch', 'chirurgisch',
    
    # French (Extended)
    'santé', 'médical', 'médecine', 'clinique', 'hôpital', 'médecin',
    'patient', 'thérapie', 'traitement', 'diagnostic', 'pharmaceutique',
    'biotechnologie', 'technologie médicale', 'santé numérique', 'télémédecine',
    
    # Dutch (Extended)
    'gezondheid', 'medisch', 'geneeskunde', 'kliniek', 'ziekenhuis', 'arts',
    'patiënt', 'therapie', 'behandeling', 'diagnose', 'farmaceutisch',
    'biotechnologie', 'medische technologie', 'digitale zorg', 'telegeneeskunde',
    
    # Spanish (Extended)
    'salud', 'médico', 'medicina', 'clínica', 'hospital', 'doctor',
    'paciente', 'terapia', 'tratamiento', 'diagnóstico', 'farmacéutico',
    'biotecnología', 'tecnología médica', 'salud digital', 'telemedicina',
    
    # Italian (Extended)
    'salute', 'medico', 'medicina', 'clinica', 'ospedale', 'dottore',
    'paziente', 'terapia', 'trattamento', 'diagnosi', 'farmaceutico',
    'biotecnologia', 'tecnologia medica', 'salute digitale', 'telemedicina',
    
    # Nordic Languages
    'hälsa', 'medicinsk', 'sjukhus', 'läkare', 'sundhed', 'medicinsk',
    'sygehus', 'læge', 'helse', 'medisinsk', 'sykehus', 'lege'
]


class UltimateConfig:
    """Configuration class for Ultimate Healthcare Discovery"""
    
    def __init__(self):
        # Request settings
        self.REQUEST_TIMEOUT = REQUEST_TIMEOUT
        self.MAX_CONCURRENT_REQUESTS = MAX_CONCURRENT_REQUESTS
        self.USER_AGENT = USER_AGENT
        
        # Discovery settings
        self.MAX_URLS_PER_SOURCE = ULTIMATE_SETTINGS['MAX_URLS_PER_SOURCE']
        self.MAX_SEARCH_RESULTS_PER_QUERY = ULTIMATE_SETTINGS['MAX_SEARCH_RESULTS_PER_QUERY'] 
        self.PARALLEL_SEARCHES = ULTIMATE_SETTINGS['PARALLEL_SEARCHES']
        self.MAX_TOTAL_URLS_TARGET = ULTIMATE_SETTINGS['MAX_TOTAL_URLS_TARGET']
        self.MIN_HEALTHCARE_SCORE = ULTIMATE_SETTINGS['MIN_HEALTHCARE_SCORE']
        
        # Healthcare sources
        self.HEALTHCARE_SOURCES = ULTIMATE_HEALTHCARE_SOURCES
        self.HEALTHCARE_KEYWORDS = ULTIMATE_HEALTHCARE_KEYWORDS
        self.EUROPEAN_CITIES = ULTIMATE_EUROPEAN_CITIES
        self.HEALTHCARE_SECTORS = ULTIMATE_HEALTHCARE_SECTORS