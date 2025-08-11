from __future__ import annotations

from typing import List
from ..models import UrlRecord


USER_VERIFIED_URLS: List[str] = [
    "https://www.acalta.de",
    "https://www.actimi.com",
    "https://www.emmora.de",
    "https://www.alfa-ai.com",
    "https://www.apheris.com",
    "https://www.aporize.com/",
    "https://www.arztlena.com/",
    "https://shop.getnutrio.com/",
    "https://www.auta.health/",
    "https://visioncheckout.com/",
    "https://www.avayl.tech/",
    "https://www.avimedical.com/avi-impact",
    "https://de.becureglobal.com/",
    "https://bellehealth.co/de/",
    "https://www.biotx.ai/",
    "https://www.brainjo.de/",
    "https://brea.app/",
    "https://breathment.com/",
    "https://de.caona.eu/",
    "https://www.careanimations.de/",
    "https://sfs-healthcare.com",
    "https://www.climedo.de/",
    "https://www.cliniserve.de/",
    "https://cogthera.de/#erfahren",
    "https://www.comuny.de/",
    "https://curecurve.de/elina-app/",
    "https://www.cynteract.com/de/rehabilitation",
    "https://www.healthmeapp.de/de/",
    "https://deepeye.ai/",
    "https://www.deepmentation.ai/",
    "https://denton-systems.de/",
    "https://www.derma2go.com/",
    "https://www.dianovi.com/",
    "http://dopavision.com/",
    "https://www.dpv-analytics.com/",
    "http://www.ecovery.de/",
    "https://elixionmedical.com/",
    "https://www.empident.de/",
    "https://eye2you.ai/",
    "https://www.fitwhit.de",
    "https://www.floy.com/",
    "https://fyzo.de/assistant/",
    "https://www.gesund.de/app",
    "https://www.glaice.de/",
    "https://gleea.de/",
    "https://www.guidecare.de/",
    "https://www.apodienste.com/",
    "https://www.help-app.de/",
    "https://www.heynanny.com/",
    "https://incontalert.de/",
    "https://home.informme.info/",
    "https://www.kranushealth.com/de/therapien/haeufiger-harndrang",
    "https://www.kranushealth.com/de/therapien/inkontinenz",
]


class HardcodedSource:
    def discover(self) -> List[UrlRecord]:
        return [
            UrlRecord(
                url=u,
                source="User Verified",
                confidence=10,
                category="Verified Health Tech",
                country="Germany/Europe",
                method="Hardcoded",
            )
            for u in USER_VERIFIED_URLS
        ]