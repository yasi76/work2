#!/usr/bin/env python3
"""
Create a GT subset file for testing the enhanced product extractor
"""

import json

# Ground truth companies
GT_COMPANIES = [
    {"url": "https://www.acalta.de", "company_name": "Acalta GmbH"},
    {"url": "https://www.actimi.com", "company_name": "Actimi GmbH"},
    {"url": "https://www.emmora.de", "company_name": "Ahorn AG"},
    {"url": "https://www.alfa-ai.com", "company_name": "ALFA AI GmbH"},
    {"url": "https://www.apheris.com", "company_name": "apheris AI GmbH"},
    {"url": "https://www.aporize.com/", "company_name": "Aporize"},
    {"url": "https://www.arztlena.com/", "company_name": "Artificy GmbH"},
    {"url": "https://shop.getnutrio.com/", "company_name": "Aurora Life Science GmbH"},
    {"url": "https://www.auta.health/", "company_name": "Auta Health UG"},
    {"url": "https://visioncheckout.com/", "company_name": "auvisus GmbH"},
    {"url": "https://www.avayl.tech/", "company_name": "AVAYL GmbH"},
    {"url": "https://www.avimedical.com/avi-impact", "company_name": "Avi Medical Operations GmbH"},
    {"url": "https://de.becureglobal.com/", "company_name": "BECURE GmbH"},
    {"url": "https://bellehealth.co/de/", "company_name": "Belle Health GmbH"},
    {"url": "https://www.biotx.ai/", "company_name": "biotx.ai GmbH"},
    {"url": "https://www.brainjo.de/", "company_name": "Brainjo GmbH"}
]

# Save to file
with open('gt_subset.json', 'w', encoding='utf-8') as f:
    json.dump(GT_COMPANIES, f, indent=2, ensure_ascii=False)

print(f"Created gt_subset.json with {len(GT_COMPANIES)} ground truth companies")
print("\nYou can now test with:")
print("python3 extract_products_enhanced_v3.py gt_subset.json --max-workers 3 --js auto --debug")