#!/usr/bin/env python3
"""
European Health Tech Startup & SME Finder
Discover legitimate health tech startups and SMEs across Europe and Germany
"""

import csv
import json
from datetime import datetime
from typing import Dict, List, Set
import re

class EuropeanStartupFinder:
    def __init__(self):
        self.working_urls = self._load_working_urls()
        self.startup_databases = self._load_startup_sources()
        self.european_countries = self._load_european_countries()
        
    def _load_working_urls(self) -> List[str]:
        """Load the 49 working URLs from validation (removing the 4 broken ones)"""
        return [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://www.emmora.de',
            'https://www.alfa-ai.com',
            'https://www.apheris.com',
            'https://www.aporize.com/',
            'https://shop.getnutrio.com/',
            'https://www.auta.health/',
            'https://visioncheckout.com/',
            'https://www.avayl.tech/',
            'https://www.avimedical.com/avi-impact',
            'https://de.becureglobal.com/',
            'https://bellehealth.co/de/',
            'https://www.biotx.ai/',
            'https://www.brainjo.de/',
            'https://brea.app/',
            'https://breathment.com/',
            'https://www.careanimations.de/',
            'https://sfs-healthcare.com',
            'https://www.climedo.de/',
            'https://www.cliniserve.de/',
            'https://cogthera.de/#erfahren',
            'https://www.comuny.de/',
            'https://curecurve.de/elina-app/',
            'https://www.healthmeapp.de/de/',
            'https://deepeye.ai/',
            'https://www.deepmentation.ai/',
            'https://www.derma2go.com/',
            'https://www.dianovi.com/',
            'http://dopavision.com/',
            'https://www.dpv-analytics.com/',
            'http://www.ecovery.de/',
            'https://elixionmedical.com/',
            'https://www.empident.de/',
            'https://eye2you.ai/',
            'https://www.fitwhit.de',
            'https://www.floy.com/',
            'https://fyzo.de/assistant/',
            'https://www.gesund.de/app',
            'https://www.glaice.de/',
            'https://gleea.de/',
            'https://www.guidecare.de/',
            'https://www.apodienste.com/',
            'https://www.help-app.de/',
            'https://www.heynanny.com/',
            'https://incontalert.de/',
            'https://home.informme.info/',
            'https://www.kranushealth.com/de/therapien/haeufiger-harndrang',
            'https://www.kranushealth.com/de/therapien/inkontinenz'
        ]
    
    def _load_startup_sources(self) -> Dict:
        """Database of startup discovery sources and methods"""
        return {
            'accelerators_incubators': {
                'Rocket Internet (Germany)': {
                    'focus': 'Digital health, e-commerce',
                    'portfolio_examples': ['HelloFresh', 'Zalando'],
                    'discovery_method': 'Check portfolio companies on rocket-internet.com'
                },
                'Techstars Berlin': {
                    'focus': 'Health tech, AI, digital health',
                    'discovery_method': 'Browse techstars.com/accelerators/berlin portfolio'
                },
                'GTEC Health Hub (Austria)': {
                    'focus': 'Digital health startups',
                    'discovery_method': 'Check gtec.health portfolio and events'
                },
                'Health Hub Hamburg': {
                    'focus': 'Digital health innovation',
                    'discovery_method': 'Browse healthhub-hamburg.de member companies'
                },
                'APX (Berlin)': {
                    'focus': 'Early-stage B2B startups',
                    'discovery_method': 'Check apx.ac portfolio companies'
                },
                'Founders Factory': {
                    'focus': 'Health tech and digital health',
                    'discovery_method': 'Browse foundersfactory.com portfolio'
                }
            },
            'funding_platforms': {
                'Crunchbase': {
                    'search_terms': ['health tech', 'digital health', 'medtech', 'biotech'],
                    'countries': ['Germany', 'Switzerland', 'France', 'UK', 'Netherlands'],
                    'url': 'crunchbase.com'
                },
                'AngelList (Wellfound)': {
                    'search_terms': ['healthcare', 'health tech', 'digital health'],
                    'url': 'wellfound.com'
                },
                'PitchBook': {
                    'focus': 'Private market data',
                    'url': 'pitchbook.com'
                }
            },
            'startup_directories': {
                'German Startups': {
                    'url': 'german-startups.com',
                    'categories': ['Health', 'Digital Health', 'MedTech']
                },
                'EU-Startups': {
                    'url': 'eu-startups.com',
                    'focus': 'European startup ecosystem'
                },
                'Startup Blink': {
                    'url': 'startupblink.com',
                    'focus': 'Global startup ecosystem rankings'
                },
                'F6S': {
                    'url': 'f6s.com',
                    'focus': 'Global startup community'
                }
            },
            'health_tech_specific': {
                'Digital Health Hub': {
                    'url': 'digitalhealthhub.de',
                    'focus': 'German digital health ecosystem'
                },
                'Health Europa': {
                    'url': 'healtheuropa.eu',
                    'focus': 'European health innovation'
                },
                'MedTech Europe': {
                    'url': 'medtecheurope.org',
                    'focus': 'Medical technology companies'
                },
                'EIT Health': {
                    'url': 'eithealth.eu',
                    'focus': 'European health innovation network'
                }
            },
            'government_innovation': {
                'Germany EXIST Program': {
                    'url': 'exist.de',
                    'focus': 'University-based startups'
                },
                'German Federal Ministry BMWi': {
                    'focus': 'Innovation funding recipients',
                    'programs': ['EXIST', 'ZIM', 'Digital Hub Initiative']
                },
                'Swiss CTI/Innosuisse': {
                    'url': 'innosuisse.ch',
                    'focus': 'Swiss innovation promotion'
                },
                'French Tech': {
                    'url': 'lafrenchtech.com',
                    'focus': 'French tech ecosystem'
                }
            }
        }
    
    def _load_european_countries(self) -> Dict:
        """European countries with startup ecosystems"""
        return {
            'Germany': {
                'startup_hubs': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt'],
                'health_clusters': ['BioM Munich', 'Health Hub Hamburg', 'Charité Berlin'],
                'domain_extensions': ['.de'],
                'startup_density': 'Very High'
            },
            'Switzerland': {
                'startup_hubs': ['Zurich', 'Basel', 'Geneva', 'Lausanne'],
                'health_clusters': ['Basel Pharma Cluster', 'Health Valley'],
                'domain_extensions': ['.ch'],
                'startup_density': 'Very High'
            },
            'United Kingdom': {
                'startup_hubs': ['London', 'Cambridge', 'Oxford', 'Edinburgh'],
                'health_clusters': ['Cambridge Biomedical Campus', 'Oxford Health Tech'],
                'domain_extensions': ['.co.uk', '.uk'],
                'startup_density': 'Very High'
            },
            'France': {
                'startup_hubs': ['Paris', 'Lyon', 'Lille', 'Toulouse'],
                'health_clusters': ['Medicen Paris', 'Lyonbiopôle'],
                'domain_extensions': ['.fr'],
                'startup_density': 'High'
            },
            'Netherlands': {
                'startup_hubs': ['Amsterdam', 'Eindhoven', 'Rotterdam'],
                'health_clusters': ['Health~Holland', 'Eindhoven MedTech'],
                'domain_extensions': ['.nl'],
                'startup_density': 'High'
            },
            'Sweden': {
                'startup_hubs': ['Stockholm', 'Gothenburg', 'Malmö'],
                'health_clusters': ['Stockholm Life Science', 'Medicon Valley'],
                'domain_extensions': ['.se'],
                'startup_density': 'High'
            },
            'Denmark': {
                'startup_hubs': ['Copenhagen', 'Aarhus'],
                'health_clusters': ['Medicon Valley', 'Health Tech Hub'],
                'domain_extensions': ['.dk'],
                'startup_density': 'High'
            },
            'Finland': {
                'startup_hubs': ['Helsinki', 'Turku', 'Tampere'],
                'health_clusters': ['HealthTech Finland'],
                'domain_extensions': ['.fi'],
                'startup_density': 'Medium-High'
            },
            'Austria': {
                'startup_hubs': ['Vienna', 'Graz', 'Linz'],
                'health_clusters': ['GTEC Health Hub', 'LISAvienna'],
                'domain_extensions': ['.at'],
                'startup_density': 'Medium-High'
            },
            'Belgium': {
                'startup_hubs': ['Brussels', 'Antwerp', 'Ghent'],
                'health_clusters': ['Flanders Bio', 'BioWin'],
                'domain_extensions': ['.be'],
                'startup_density': 'Medium'
            },
            'Spain': {
                'startup_hubs': ['Barcelona', 'Madrid', 'Valencia'],
                'health_clusters': ['Biocat', 'Madrid Health Tech'],
                'domain_extensions': ['.es'],
                'startup_density': 'Medium'
            },
            'Italy': {
                'startup_hubs': ['Milan', 'Rome', 'Turin'],
                'health_clusters': ['Lombardy Life Sciences', 'Rome Biotech'],
                'domain_extensions': ['.it'],
                'startup_density': 'Medium'
            },
            'Poland': {
                'startup_hubs': ['Warsaw', 'Krakow', 'Wrocław'],
                'health_clusters': ['LifeScience Kraków', 'MedTech Poland'],
                'domain_extensions': ['.pl'],
                'startup_density': 'Growing'
            },
            'Czech Republic': {
                'startup_hubs': ['Prague', 'Brno'],
                'health_clusters': ['Czech Pharma', 'Brno MedTech'],
                'domain_extensions': ['.cz'],
                'startup_density': 'Growing'
            }
        }
    
    def generate_discovery_strategies(self) -> Dict:
        """Generate comprehensive startup discovery strategies"""
        strategies = {
            'web_scraping_targets': self._get_web_scraping_targets(),
            'api_sources': self._get_api_sources(),
            'manual_research_methods': self._get_manual_research_methods(),
            'domain_generation_patterns': self._get_domain_patterns(),
            'event_networking': self._get_event_sources(),
            'social_media_discovery': self._get_social_media_sources()
        }
        
        return strategies
    
    def _get_web_scraping_targets(self) -> List[Dict]:
        """Target websites for systematic startup discovery"""
        return [
            {
                'name': 'Crunchbase',
                'url': 'crunchbase.com',
                'search_method': 'Advanced search filters',
                'filters': {
                    'industries': ['Health Care', 'Digital Health', 'Medical Device', 'Biotechnology'],
                    'locations': ['Germany', 'Europe'],
                    'company_types': ['Startup', 'Early Stage Venture'],
                    'funding_status': ['Seed', 'Series A', 'Series B']
                },
                'data_points': ['company_name', 'website', 'description', 'funding', 'location']
            },
            {
                'name': 'AngelList (Wellfound)',
                'url': 'wellfound.com',
                'search_method': 'Job/company search',
                'filters': {
                    'markets': ['Healthcare', 'Digital Health', 'Medical Devices'],
                    'locations': ['Berlin', 'Munich', 'Hamburg', 'Zurich', 'London', 'Paris'],
                    'company_size': ['1-10', '11-50', '51-200']
                },
                'data_points': ['startup_name', 'website', 'description', 'team_size', 'funding_stage']
            },
            {
                'name': 'German Startups Database',
                'url': 'german-startups.com',
                'search_method': 'Category browsing',
                'categories': ['Digital Health', 'MedTech', 'Health', 'AI in Healthcare'],
                'data_points': ['company_name', 'website', 'founding_year', 'location', 'description']
            },
            {
                'name': 'EU-Startups',
                'url': 'eu-startups.com',
                'search_method': 'Country and sector filtering',
                'focus': 'European startup ecosystem coverage',
                'data_points': ['startup_name', 'website', 'country', 'sector', 'funding_news']
            },
            {
                'name': 'Startup Genome',
                'url': 'startupgenome.com',
                'search_method': 'Ecosystem reports',
                'focus': 'Regional startup ecosystem data',
                'data_points': ['ecosystem_ranking', 'top_companies', 'success_stories']
            }
        ]
    
    def _get_api_sources(self) -> List[Dict]:
        """API sources for automated startup discovery"""
        return [
            {
                'name': 'Crunchbase API',
                'url': 'data.crunchbase.com/docs',
                'access': 'Paid API',
                'capabilities': [
                    'Company search by industry/location',
                    'Funding data access',
                    'Real-time startup database'
                ],
                'rate_limits': '1000+ requests/day (paid plans)',
                'data_quality': 'Very High'
            },
            {
                'name': 'PitchBook API',
                'url': 'pitchbook.com/platform/excel-plugin',
                'access': 'Enterprise subscription',
                'capabilities': [
                    'Private market data',
                    'Venture capital database',
                    'M&A information'
                ],
                'data_quality': 'Very High'
            },
            {
                'name': 'Clearbit Company API',
                'url': 'clearbit.com/enrichment',
                'access': 'Paid API',
                'capabilities': [
                    'Company enrichment data',
                    'Website classification',
                    'Industry tagging'
                ],
                'use_case': 'Enrich discovered domains with company data'
            },
            {
                'name': 'BuiltWith API',
                'url': 'builtwith.com/api',
                'access': 'Paid API',
                'capabilities': [
                    'Technology stack detection',
                    'Website categorization',
                    'Industry classification'
                ],
                'use_case': 'Identify health tech companies by technology stack'
            }
        ]
    
    def _get_manual_research_methods(self) -> List[Dict]:
        """Manual research methods for startup discovery"""
        return [
            {
                'method': 'University Technology Transfer Offices',
                'description': 'Contact tech transfer offices at major universities',
                'target_universities': [
                    'Technical University of Munich (TUM)',
                    'Charité Berlin',
                    'ETH Zurich',
                    'University of Cambridge',
                    'Imperial College London',
                    'Sorbonne University',
                    'Karolinska Institute'
                ],
                'approach': 'Request spin-off company lists, startup portfolios'
            },
            {
                'method': 'Accelerator Portfolio Mining',
                'description': 'Systematically go through accelerator portfolios',
                'target_accelerators': [
                    'Techstars (Berlin, London, Paris)',
                    'Rocket Internet Portfolio',
                    'APX Berlin',
                    'Founders Factory',
                    'Station F (Paris)',
                    'L39 (London)',
                    'Swiss Startup Factory'
                ],
                'data_extraction': 'Company names, websites, descriptions, funding stages'
            },
            {
                'method': 'Healthcare Conference Exhibitor Lists',
                'description': 'Extract startup data from health tech conferences',
                'target_conferences': [
                    'HIMSS Europe',
                    'Health 2.0 Europe',
                    'Digital Health Summit',
                    'MedTech Breakthrough',
                    'BioEurope',
                    'LSX World Congress'
                ],
                'data_sources': 'Exhibitor directories, speaker lists, award winners'
            },
            {
                'method': 'Government Grant Recipients',
                'description': 'Research government innovation program recipients',
                'programs': [
                    'German EXIST Program',
                    'Horizon Europe Health',
                    'Swiss Innosuisse',
                    'French Tech Visa recipients',
                    'UK Innovate funding'
                ],
                'data_access': 'Public grant databases, program announcements'
            },
            {
                'method': 'Venture Capital Portfolio Analysis',
                'description': 'Analyze VC firm portfolios for health tech investments',
                'target_vcs': [
                    'Earlybird Venture Capital',
                    'Target Partners',
                    'Cavalry Ventures',
                    'Atomico',
                    'Index Ventures',
                    'Accel Partners',
                    'Wellington Partners'
                ],
                'focus': 'Health tech, digital health, medtech investments'
            }
        ]
    
    def _get_domain_patterns(self) -> Dict:
        """Domain generation patterns for systematic discovery"""
        return {
            'health_keywords': [
                'health', 'med', 'care', 'cure', 'heal', 'therapy', 'clinic', 'doc',
                'patient', 'wellness', 'digital', 'smart', 'ai', 'tech', 'app',
                'gesundheit', 'medizin', 'arzt', 'therapie', 'klinik', 'patient'
            ],
            'business_suffixes': [
                'tech', 'ai', 'app', 'platform', 'solutions', 'systems', 'labs',
                'innovations', 'digital', 'smart', 'pro', 'plus', 'hub', 'connect'
            ],
            'domain_patterns': [
                '{keyword}.{tld}',
                '{keyword}{suffix}.{tld}',
                '{prefix}{keyword}.{tld}',
                'get{keyword}.{tld}',
                'my{keyword}.{tld}',
                '{keyword}app.{tld}',
                '{keyword}tech.{tld}'
            ],
            'european_tlds': ['.de', '.ch', '.fr', '.co.uk', '.nl', '.se', '.dk', '.fi', '.at', '.be', '.es', '.it'],
            'common_tlds': ['.com', '.io', '.ai', '.app', '.tech', '.health']
        }
    
    def _get_event_sources(self) -> List[Dict]:
        """Health tech events and conferences for networking discovery"""
        return [
            {
                'event': 'HIMSS Europe',
                'location': 'Various European cities',
                'frequency': 'Annual',
                'focus': 'Health IT and digital health',
                'startup_opportunities': 'Startup showcase, exhibitor hall, pitch competitions'
            },
            {
                'event': 'Health 2.0 Europe',
                'location': 'Various European cities',
                'frequency': 'Annual',
                'focus': 'Digital health innovation',
                'startup_opportunities': 'Developer challenges, startup pitches'
            },
            {
                'event': 'Digital Health Summit',
                'location': 'Berlin, Germany',
                'frequency': 'Annual',
                'focus': 'German digital health ecosystem',
                'startup_opportunities': 'German health tech startups showcase'
            },
            {
                'event': 'MedTech Breakthrough Awards',
                'location': 'Various',
                'frequency': 'Annual',
                'focus': 'Medical technology innovation',
                'startup_opportunities': 'Award winners, breakthrough startups'
            },
            {
                'event': 'TechCrunch Disrupt Berlin',
                'location': 'Berlin, Germany',
                'frequency': 'Biennial',
                'focus': 'Startup ecosystem',
                'startup_opportunities': 'Startup battlefield, exhibitor startups'
            },
            {
                'event': 'Slush',
                'location': 'Helsinki, Finland',
                'frequency': 'Annual',
                'focus': 'Nordic startup ecosystem',
                'startup_opportunities': 'Startup pitches, investor meetings'
            },
            {
                'event': 'WebSummit',
                'location': 'Lisbon, Portugal',
                'frequency': 'Annual',
                'focus': 'European tech ecosystem',
                'startup_opportunities': 'Alpha program, startup exhibitions'
            }
        ]
    
    def _get_social_media_sources(self) -> List[Dict]:
        """Social media platforms for startup discovery"""
        return [
            {
                'platform': 'LinkedIn',
                'search_methods': [
                    'Company search by industry (Healthcare Technology)',
                    'People search (Founder, CEO + Health Tech)',
                    'Group monitoring (Digital Health groups)',
                    'Hashtag tracking (#HealthTech, #DigitalHealth)'
                ],
                'automation_tools': ['LinkedIn Sales Navigator', 'LinkedIn API']
            },
            {
                'platform': 'Twitter/X',
                'search_methods': [
                    'Hashtag monitoring (#HealthTech, #MedTech, #DigitalHealth)',
                    'Bio keyword search (CEO, Founder + health)',
                    'Location-based search (Berlin health tech)',
                    'List monitoring (Health tech investors, accelerators)'
                ],
                'automation_tools': ['Twitter API v2', 'Social listening tools']
            },
            {
                'platform': 'Product Hunt',
                'search_methods': [
                    'Category browsing (Health & Fitness)',
                    'Maker following (health tech makers)',
                    'Collection monitoring (health tech collections)'
                ],
                'data_points': ['Product websites', 'maker profiles', 'launch announcements']
            },
            {
                'platform': 'GitHub',
                'search_methods': [
                    'Repository search (health tech topics)',
                    'Organization discovery (health startups)',
                    'Developer profile analysis'
                ],
                'indicators': ['Health-related repositories', 'organization websites']
            }
        ]
    
    def generate_discovery_plan(self) -> Dict:
        """Generate comprehensive 30-day startup discovery plan"""
        plan = {
            'week_1': {
                'focus': 'Database and API Setup',
                'tasks': [
                    'Set up Crunchbase access for health tech company search',
                    'Configure AngelList search filters for European health startups',
                    'Create automated monitoring for German Startups database',
                    'Set up social media monitoring for health tech hashtags'
                ],
                'expected_output': '50-100 new startups'
            },
            'week_2': {
                'focus': 'Accelerator and VC Portfolio Mining',
                'tasks': [
                    'Extract portfolio companies from top 20 European health tech VCs',
                    'Mine accelerator websites for health tech graduates',
                    'Research university tech transfer office spin-offs',
                    'Analyze government grant recipient lists'
                ],
                'expected_output': '100-200 new startups'
            },
            'week_3': {
                'focus': 'Conference and Event Research',
                'tasks': [
                    'Extract exhibitor lists from major health tech conferences',
                    'Research award winners from innovation competitions',
                    'Analyze speaker lists from health tech events',
                    'Monitor startup pitch competition results'
                ],
                'expected_output': '75-150 new startups'
            },
            'week_4': {
                'focus': 'Validation and Enhancement',
                'tasks': [
                    'Validate all discovered URLs for accessibility',
                    'Enrich company data with funding, team size, description',
                    'Categorize by health tech vertical (AI, medtech, digital health)',
                    'Create final curated database with quality scores'
                ],
                'expected_output': 'Validated database of 200-400 startups'
            }
        }
        
        return plan
    
    def save_discovery_guide(self, filename: str = "european_health_startup_discovery_guide"):
        """Save comprehensive startup discovery guide"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate all strategies
        strategies = self.generate_discovery_strategies()
        discovery_plan = self.generate_discovery_plan()
        
        # Save comprehensive guide
        guide_filename = f"{filename}_{timestamp}.json"
        guide_data = {
            'current_working_urls': self.working_urls,
            'working_url_count': len(self.working_urls),
            'removed_broken_urls': [
                'https://www.arztlena.com/',
                'https://de.caona.eu/',
                'https://www.cynteract.com/de/rehabilitation',
                'https://denton-systems.de/'
            ],
            'discovery_strategies': strategies,
            'discovery_plan': discovery_plan,
            'european_countries': self.european_countries,
            'startup_sources': self.startup_databases,
            'generation_timestamp': datetime.now().isoformat()
        }
        
        with open(guide_filename, 'w', encoding='utf-8') as f:
            json.dump(guide_data, f, indent=2, ensure_ascii=False)
        
        # Save working URLs CSV
        urls_filename = f"working_health_tech_urls_{timestamp}.csv"
        with open(urls_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'status', 'category'])
            
            for url in self.working_urls:
                # Categorize URL
                if any(term in url.lower() for term in ['health', 'med', 'care', 'clinic', 'patient']):
                    category = 'Direct Health'
                elif any(term in url.lower() for term in ['ai', 'tech', 'digital', 'app']):
                    category = 'Health Tech'
                else:
                    category = 'Health Adjacent'
                
                writer.writerow([url, 'Working', category])
        
        # Save discovery action plan
        plan_filename = f"startup_discovery_action_plan_{timestamp}.txt"
        with open(plan_filename, 'w', encoding='utf-8') as f:
            f.write("EUROPEAN HEALTH TECH STARTUP DISCOVERY ACTION PLAN\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"CURRENT STATUS:\n")
            f.write(f"✅ Working URLs: {len(self.working_urls)}\n")
            f.write(f"❌ Removed broken URLs: 4\n")
            f.write(f"🎯 Success rate: 92.5%\n\n")
            
            f.write("DISCOVERY METHODS TO FIND MORE STARTUPS:\n\n")
            
            # Web scraping targets
            f.write("1. WEB SCRAPING TARGETS:\n")
            for target in strategies['web_scraping_targets']:
                f.write(f"   • {target['name']} ({target['url']})\n")
                f.write(f"     Method: {target['search_method']}\n")
                if 'filters' in target:
                    f.write(f"     Focus: {', '.join(target['filters'].get('industries', []))}\n")
                f.write("\n")
            
            # Manual research methods
            f.write("2. MANUAL RESEARCH METHODS:\n")
            for method in strategies['manual_research_methods']:
                f.write(f"   • {method['method']}\n")
                f.write(f"     {method['description']}\n\n")
            
            # 30-day plan
            f.write("3. 30-DAY DISCOVERY PLAN:\n")
            for week, details in discovery_plan.items():
                f.write(f"\n   {week.upper()}: {details['focus']}\n")
                for task in details['tasks']:
                    f.write(f"     - {task}\n")
                f.write(f"     Expected: {details['expected_output']}\n")
            
            f.write(f"\n🎯 GOAL: Discover 200-400 additional European health tech startups\n")
            f.write(f"📊 Target total: 250-450 verified health tech URLs\n")
        
        return {
            'guide_file': guide_filename,
            'urls_file': urls_filename,
            'plan_file': plan_filename,
            'working_urls': len(self.working_urls)
        }

def main():
    """Main function to generate startup discovery system"""
    print("🚀 EUROPEAN HEALTH TECH STARTUP & SME DISCOVERY SYSTEM")
    print("=" * 70)
    
    # Initialize finder
    finder = EuropeanStartupFinder()
    
    print(f"✅ CURRENT STATUS:")
    print(f"  • Working URLs: {len(finder.working_urls)}")
    print(f"  • Removed broken URLs: 4")
    print(f"  • Success rate: 92.5%")
    
    print(f"\n🎯 DISCOVERY CAPABILITIES:")
    print(f"  • {len(finder.startup_databases['accelerators_incubators'])} accelerator/incubator sources")
    print(f"  • {len(finder.startup_databases['funding_platforms'])} funding platform sources")
    print(f"  • {len(finder.startup_databases['startup_directories'])} startup directory sources")
    print(f"  • {len(finder.european_countries)} European countries covered")
    
    strategies = finder.generate_discovery_strategies()
    print(f"\n📋 DISCOVERY METHODS:")
    print(f"  • {len(strategies['web_scraping_targets'])} web scraping targets")
    print(f"  • {len(strategies['api_sources'])} API sources")
    print(f"  • {len(strategies['manual_research_methods'])} manual research methods")
    print(f"  • {len(strategies['event_networking'])} networking events")
    
    # Generate discovery plan
    discovery_plan = finder.generate_discovery_plan()
    print(f"\n📅 30-DAY DISCOVERY PLAN:")
    for week, details in discovery_plan.items():
        print(f"  • {week}: {details['focus']} ({details['expected_output']})")
    
    print(f"\n💾 SAVING COMPREHENSIVE DISCOVERY SYSTEM...")
    
    # Save all discovery materials
    results = finder.save_discovery_guide()
    
    print(f"\n✅ DISCOVERY SYSTEM CREATED:")
    print(f"  📋 Comprehensive guide: {results['guide_file']}")
    print(f"  🔗 Working URLs: {results['urls_file']}")
    print(f"  📅 Action plan: {results['plan_file']}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Use the discovery methods to find 200-400 more startups")
    print(f"  2. Focus on German and European health tech ecosystems")
    print(f"  3. Validate all new URLs before adding to database")
    print(f"  4. Target goal: 250-450 total verified health tech URLs")
    
    print(f"\n💡 RECOMMENDED PRIORITIES:")
    print(f"  🥇 Crunchbase health tech search (highest quality)")
    print(f"  🥈 Accelerator portfolio mining (high startup density)")
    print(f"  🥉 Conference exhibitor lists (active companies)")
    print(f"  4️⃣ Government grant recipients (funded startups)")
    
    return results

if __name__ == "__main__":
    results = main()