#!/usr/bin/env python3
"""
discover_urls.py - Discovers digital health startup URLs
Outputs: final_startup_urls.json
"""

import json
import logging
from typing import List, Set

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class URLDiscoverer:
    def __init__(self):
        self.all_urls = set()
    
    def get_hardcoded_urls(self) -> List[str]:
        """User's verified hardcoded URLs"""
        return [
            'https://www.acalta.de',
            'https://www.actimi.com',
            'https://www.emmora.de',
            'https://www.alfa-ai.com',
            'https://www.apheris.com',
            'https://www.aporize.com/',
            'https://www.arztlena.com/',
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
            'https://de.caona.eu/',
            'https://www.careanimations.de/',
            'https://sfs-healthcare.com',
            'https://www.climedo.de/',
            'https://www.cliniserve.de/',
            'https://cogthera.de/#erfahren',
            'https://www.comuny.de/',
            'https://curecurve.de/elina-app/',
            'https://www.cynteract.com/de/rehabilitation',
            'https://www.healthmeapp.de/de/',
            'https://deepeye.ai/',
            'https://www.deepmentation.ai/',
            'https://denton-systems.de/',
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
    
    def get_additional_urls(self) -> List[str]:
        """Additional curated startup URLs"""
        return [
            # German Digital Health Leaders
            'https://www.ada.com',
            'https://www.doctolib.de',
            'https://www.kaia-health.com',
            'https://www.teleclinic.com',
            'https://www.zavamed.com',
            'https://www.medwing.com',
            'https://www.felmo.de',
            'https://www.viomedo.de',
            'https://www.caresyntax.com',
            'https://www.merantix.com',
            'https://www.contextflow.com',
            'https://www.heartkinetics.com',
            'https://www.samedi.de',
            'https://www.medigene.com',
            'https://www.smartpatient.eu',
            
            # European Digital Health
            'https://www.doctolib.fr',
            'https://www.livi.co.uk',
            'https://www.babylon.com',
            'https://www.echo.co.uk',
            'https://www.accurx.com',
            'https://www.zava.com',
            'https://www.medgate.ch',
            'https://www.kry.se',
            'https://www.medadom.com',
            'https://www.qare.fr',
            
            # Additional German startups
            'https://www.neosfer.de',
            'https://www.preventicus.com',
            'https://www.thryve.health',
            'https://www.xim.ai',
            'https://www.lindera.de',
            'https://www.kenbi.eu',
            'https://www.mindable.health',
            'https://www.inveox.com',
            'https://www.medipee.com',
            'https://www.skinly.de',
            'https://www.tinnitracks.com',
            'https://www.mediteo.com',
            'https://www.mika.health',
            'https://www.sonormed.de',
            'https://www.vitadock.com'
        ]
    
    def discover_urls(self):
        """Discover all URLs from various sources"""
        logger.info("Starting URL discovery...")
        
        # Add hardcoded URLs
        hardcoded = self.get_hardcoded_urls()
        logger.info(f"Adding {len(hardcoded)} hardcoded URLs")
        self.all_urls.update(hardcoded)
        
        # Add additional curated URLs
        additional = self.get_additional_urls()
        logger.info(f"Adding {len(additional)} additional curated URLs")
        self.all_urls.update(additional)
        
        logger.info(f"Total unique URLs discovered: {len(self.all_urls)}")
    
    def save_results(self):
        """Save discovered URLs to JSON file"""
        urls = sorted(list(self.all_urls))
        
        with open('final_startup_urls.json', 'w', encoding='utf-8') as f:
            json.dump(urls, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(urls)} URLs to final_startup_urls.json")
    
    def run(self):
        """Run the complete discovery process"""
        self.discover_urls()
        self.save_results()


def main():
    discoverer = URLDiscoverer()
    discoverer.run()


if __name__ == "__main__":
    main()