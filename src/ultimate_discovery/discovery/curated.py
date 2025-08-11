from __future__ import annotations

from typing import List
from ..models import UrlRecord


CURATED_URLS: List[str] = [
    # German Digital Health Leaders
    "https://www.ada.com",
    "https://www.doctolib.de",
    "https://www.kaia-health.com",
    "https://www.teleclinic.com",
    "https://www.zavamed.com",
    "https://www.medwing.com",
    "https://www.felmo.de",
    "https://www.viomedo.de",
    "https://www.caresyntax.com",
    "https://www.merantix.com",
    "https://www.contextflow.com",
    "https://www.heartkinetics.com",
    "https://www.samedi.de",
    "https://www.medigene.com",
    "https://www.smartpatient.eu",
    # European Digital Health
    "https://www.doctolib.fr",
    "https://www.livi.co.uk",
    "https://www.babylon.com",
    "https://www.echo.co.uk",
    "https://www.accurx.com",
    "https://www.zava.com",
    "https://www.medgate.ch",
    "https://www.kry.se",
    "https://www.medadom.com",
    "https://www.qare.fr",
    "https://www.1177.se",
    "https://www.netdoktor.dk",
    "https://www.opensafely.org",
    # AI & Analytics
    "https://www.owkin.com",
    "https://www.benevolent.ai",
    "https://www.exscientia.ai",
    "https://www.healx.io",
    "https://www.insilico.com",
    # MedTech & Devices (Enterprise)
    "https://www.siemens-healthineers.com",
    "https://www.philips.com/healthcare",
    "https://www.getinge.com",
    "https://www.elekta.com",
    "https://www.fresenius.com",
    "https://www.braun.com",
    # Pharma & Biotech (Enterprise)
    "https://www.bayer.com",
    "https://www.boehringer-ingelheim.com",
    "https://www.merckgroup.com",
    "https://www.qiagen.com",
    "https://www.roche.com",
    "https://www.novartis.com",
    "https://www.sanofi.com",
    "https://www.gsk.com",
    "https://www.astrazeneca.com",
    # Emerging Startups
    "https://www.mindmaze.com",
    "https://www.sophia-genetics.com",
    "https://www.iqvia.com",
    "https://www.veracyte.com",
    "https://www.tempus.com",
    "https://www.flatiron.com",
    "https://www.paige.ai",
    "https://www.path.ai",
    "https://www.viz.ai",
    "https://www.arterys.com",
]

ENTERPRISE_HOST_KEYWORDS = [
    "siemens-healthineers",
    "philips",
    "bayer",
    "boehringer",
    "merck",
    "qiagen",
    "roche",
    "novartis",
    "sanofi",
    "gsk",
    "astrazeneca",
    "getinge",
    "elekta",
    "fresenius",
    "braun",
    "iqvia",
]


class CuratedSource:
    def discover(self) -> List[UrlRecord]:
        records: List[UrlRecord] = []
        for u in CURATED_URLS:
            category = (
                "Enterprise/Non-Startup"
                if any(key in u for key in ENTERPRISE_HOST_KEYWORDS)
                else "Curated Health Tech"
            )
            rec = UrlRecord(
                url=u,
                source="Curated List",
                confidence=8,
                category=category,
                country="Europe/International",
                method="Manual Curation",
            )
            records.append(rec)
        return records