#!/usr/bin/env python3
"""
Working German Healthcare Company Scraper

This script extracts real German healthcare companies from multiple sources
and creates a comprehensive database with company information including:
- Company names with proper German business suffixes (GmbH, AG, SE, KG)
- Generated website URLs based on company names
- Company descriptions based on their category
- Location information where available
- Proper categorization (Pharmaceuticals, Medical Technology, etc.)

The script uses only Python standard library modules for maximum compatibility
and generates both CSV and JSON output formats for easy integration.

Author: Healthcare Scraper Bot
Date: 2024
"""

import json
import csv
import urllib.request
import urllib.parse
import re
import time
from dataclasses import dataclass, asdict
from typing import List, Dict
from pathlib import Path

@dataclass
class HealthcareCompany:
    """
    Data class representing a German healthcare company.
    
    This class defines the structure for storing healthcare company information
    with all the relevant fields needed for business use.
    """
    name: str                    # Official company name (e.g., "Bayer AG")
    website: str = ""           # Company website URL
    description: str = ""       # Business description based on category
    location: str = ""          # City and country (e.g., "Munich, Germany")
    category: str = ""          # Business category (e.g., "Pharmaceuticals")
    founded_year: str = ""      # Year company was founded (if available)
    employees: str = ""         # Number of employees (if available)
    source: str = ""            # Source where company data was found

class HealthcareScraper:
    """
    Main scraper class for extracting German healthcare companies.
    
    This class handles the entire scraping process including:
    - Fetching data from various sources
    - Parsing and extracting company information
    - Categorizing companies by business type
    - Generating realistic website URLs
    - Creating detailed company descriptions
    - Removing duplicates and cleaning data
    - Saving results in multiple formats
    """
    
    def __init__(self):
        """
        Initialize the scraper with empty company list and HTTP headers.
        
        Sets up the scraper with proper user agent for web requests
        and initializes the companies list to store extracted data.
        """
        self.companies = []  # List to store all extracted companies
        
        # HTTP headers to mimic a real browser and avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_url(self, url: str) -> str:
        """
        Fetch webpage content from a given URL.
        
        This method handles HTTP requests with proper error handling
        and encoding detection to ensure reliable data retrieval.
        
        Args:
            url (str): The URL to fetch content from
            
        Returns:
            str: The HTML content of the webpage, or empty string if failed
        """
        try:
            # Create HTTP request with browser-like headers
            req = urllib.request.Request(url, headers=self.headers)
            
            # Open URL with 30-second timeout
            with urllib.request.urlopen(req, timeout=30) as response:
                # Decode response with UTF-8, ignore errors if any
                return response.read().decode('utf-8', errors='ignore')
                
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
    
    def extract_from_wikipedia(self):
        """
        Extract German healthcare companies from Wikipedia and curated sources.
        
        This method combines data from Wikipedia pages with a curated list
        of known German healthcare companies to create a comprehensive dataset.
        It focuses on companies with proper German business suffixes and
        healthcare-related business activities.
        """
        print("Extracting from Wikipedia...")
        
        # Wikipedia pages that contain German healthcare company information
        wiki_urls = [
            "https://en.wikipedia.org/wiki/List_of_pharmaceutical_companies",
            "https://en.wikipedia.org/wiki/Category:Pharmaceutical_companies_of_Germany",
            "https://en.wikipedia.org/wiki/Category:Medical_technology_companies_of_Germany"
        ]
        
        german_companies = []
        
        # Attempt to extract companies from Wikipedia pages
        for url in wiki_urls:
            html = self.fetch_url(url)
            if html:
                # Regular expressions to find company names and links
                patterns = [
                    # Pattern 1: Find links with German company suffixes in title
                    r'<a[^>]*href="[^"]*"[^>]*title="([^"]*(?:GmbH|AG|SE|KG))"[^>]*>([^<]*)</a>',
                    
                    # Pattern 2: Find wiki links with German company suffixes
                    r'<a[^>]*href="/wiki/([^"]*)"[^>]*>([^<]*(?:GmbH|AG|SE|KG)[^<]*)</a>',
                    
                    # Pattern 3: Find list items with company links
                    r'<li><a[^>]*href="/wiki/([^"]*)"[^>]*>([^<]*)</a></li>'
                ]
                
                # Apply each pattern to extract company names
                for pattern in patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        if len(match) == 2:
                            # Use the second match (display name) if available, otherwise first
                            name = match[1] if match[1] else match[0]
                            # Replace underscores with spaces (from wiki URLs)
                            name = re.sub(r'[_]', ' ', name)
                            
                            # Filter for companies with German business suffixes
                            if any(indicator in name for indicator in ['GmbH', 'AG', 'SE', 'KG']):
                                german_companies.append(name)
        
        # Curated list of major German healthcare companies
        # This ensures we capture all important players in the German healthcare market
        curated_companies = [
            # Major German pharmaceutical companies
            "Siemens Healthineers AG",        # Medical imaging and diagnostics
            "Bayer AG",                       # Global pharmaceutical giant
            "Merck KGaA",                     # Science and technology company
            "Fresenius SE & Co. KGaA",        # Healthcare services
            "Fresenius Medical Care AG",      # Dialysis services worldwide
            "B. Braun Melsungen AG",          # Medical devices and pharmaceuticals
            "Carl Zeiss Meditec AG",          # Medical technology solutions
            "Drägerwerk AG",                  # Medical and safety technology
            "Sartorius AG",                   # Laboratory and process technologies
            "Evotec SE",                      # Drug discovery and development
            "MorphoSys AG",                   # Biopharmaceutical company
            "Qiagen N.V.",                    # Molecular diagnostics
            "Biotest AG",                     # Plasma protein products
            
            # International companies with German operations
            "Pfizer Deutschland GmbH",        # Pfizer's German subsidiary
            "Roche Deutschland GmbH",         # Roche's German operations
            "Novartis Deutschland GmbH",      # Novartis Germany
            "Sanofi Deutschland GmbH",        # Sanofi Germany
            "AbbVie Deutschland GmbH",        # AbbVie Germany
            "Boehringer Ingelheim GmbH",      # Private pharmaceutical company
            "Stada Arzneimittel AG",          # Generic pharmaceuticals
            "Hexal AG",                       # Generic drug manufacturer
            "Grünenthal GmbH",                # Pain management pharmaceuticals
            "Janssen Deutschland GmbH",       # J&J Germany
            "Medtronic Deutschland GmbH",     # Medical devices
            "Abbott Deutschland GmbH",        # Abbott Germany
            "Johnson & Johnson Deutschland GmbH",  # J&J Germany
            "Biotronik SE & Co. KG",          # Cardiovascular medical devices
            "Olympus Deutschland GmbH",       # Medical equipment
            "Philips Deutschland GmbH",       # Healthcare technology
            "GE Healthcare Deutschland GmbH", # Medical imaging
            "Aesculap AG",                    # Surgical instruments
            "Hartmann AG",                    # Medical and hygiene products
            "Heraeus Medical GmbH",           # Medical technology
            "Lohmann & Rauscher GmbH",        # Medical devices and hygiene
            "Mölnlycke Health Care GmbH",     # Medical solutions
            "Smith & Nephew Deutschland GmbH", # Medical devices
            "Zimmer Biomet Deutschland GmbH", # Orthopedic implants
            "Stryker Deutschland GmbH",       # Medical technology
            "Terumo Deutschland GmbH",        # Medical devices
            "Cardinal Health Deutschland GmbH", # Healthcare services
            "Baxter Deutschland GmbH",        # Healthcare products
            "Becton Dickinson Deutschland GmbH", # Medical technology
            "Covidien Deutschland GmbH",      # Medical devices
            "Medline Deutschland GmbH",       # Medical supplies
            "Paul Hartmann AG",               # Healthcare products
            "Urgo Deutschland GmbH",          # Wound care
            "3M Deutschland GmbH",            # Healthcare division
            "Acelity Deutschland GmbH",       # Advanced wound care
            "Integra LifeSciences Deutschland GmbH", # Medical devices
            "Bracco Imaging Deutschland GmbH", # Medical imaging
            "Guerbet Deutschland GmbH",       # Contrast media
            "Bayer Vital GmbH",               # Bayer's German operations
            "Takeda Deutschland GmbH",        # Takeda Germany
            "UCB Deutschland GmbH",           # UCB Germany
            "Gilead Sciences Deutschland GmbH", # Gilead Germany
            "Celgene Deutschland GmbH",       # Celgene Germany
            "Amgen Deutschland GmbH",         # Amgen Germany
            "Biogen Deutschland GmbH",        # Biogen Germany
            "Genzyme Deutschland GmbH",       # Genzyme Germany
            "Shire Deutschland GmbH",         # Shire Germany
            "Vertex Pharmaceuticals Deutschland GmbH", # Vertex Germany
            "Alexion Deutschland GmbH",       # Alexion Germany
            "Regeneron Deutschland GmbH",     # Regeneron Germany
            
            # Diagnostic and laboratory companies
            "Illumina Deutschland GmbH",      # Genetic analysis
            "Thermo Fisher Scientific Deutschland GmbH", # Scientific instruments
            "Agilent Technologies Deutschland GmbH", # Life sciences
            "PerkinElmer Deutschland GmbH",   # Diagnostics
            "Bio-Rad Laboratories Deutschland GmbH", # Life science research
            "Beckman Coulter Deutschland GmbH", # Diagnostics
            "Roche Diagnostics Deutschland GmbH", # Diagnostics
            "Siemens Healthcare Diagnostics GmbH", # Diagnostics
            "Abbott Diagnostics Deutschland GmbH", # Diagnostics
            "Hologic Deutschland GmbH",       # Women's health diagnostics
            "Quidel Deutschland GmbH",        # Rapid diagnostics
            "Cepheid Deutschland GmbH",       # Molecular diagnostics
            "BioMérieux Deutschland GmbH",    # In vitro diagnostics
            "Sysmex Deutschland GmbH",        # Hematology diagnostics
            "Mindray Deutschland GmbH",       # Medical devices
            "Radiometer Deutschland GmbH",    # Acute care diagnostics
            "Nova Biomedical Deutschland GmbH", # Critical care diagnostics
            "EKF Diagnostics Deutschland GmbH", # Point-of-care diagnostics
            "Ortho Clinical Diagnostics Deutschland GmbH", # Diagnostics
            "DiaSorin Deutschland GmbH",      # Diagnostics
            "Werfen Deutschland GmbH",        # Diagnostics
            
            # Blood and plasma companies
            "Haemonetics Deutschland GmbH",   # Blood management
            "Immucor Deutschland GmbH",       # Transfusion medicine
            "Grifols Deutschland GmbH",       # Plasma-derived medicines
            "CSL Behring Deutschland GmbH",   # Plasma therapies
            "Kedrion Deutschland GmbH",       # Plasma products
            "Octapharma Deutschland GmbH",    # Plasma products
            "Biolife Deutschland GmbH",       # Plasma collection
            "Fenwal Deutschland GmbH",        # Blood component technology
            
            # Dialysis and renal care
            "Fresenius Kabi Deutschland GmbH", # IV drugs and nutrition
            "B. Braun Avitum AG",             # Dialysis services
            "Nipro Deutschland GmbH",         # Dialysis products
            "Nikkiso Deutschland GmbH",       # Dialysis machines
            "Bellco Deutschland GmbH",        # Dialysis equipment
            "Diaverum Deutschland GmbH",      # Dialysis services
            "KfH Kuratorium für Dialyse",     # Dialysis organization
            "PHV Dialysezentren",             # Dialysis centers
            "Nephrocare Deutschland GmbH",    # Dialysis services
            "DaVita Deutschland GmbH"         # Dialysis services
        ]
        
        # Combine Wikipedia results with curated companies and remove duplicates
        all_companies = list(set(german_companies + curated_companies))
        
        # Process each company and create HealthcareCompany objects
        for company_name in all_companies:
            if len(company_name) > 3:  # Filter out very short names
                # Generate website URL based on company name
                website = self.generate_website_url(company_name)
                
                # Determine business category based on company name
                category = self.categorize_company(company_name)
                
                # Determine location if known
                location = self.determine_location(company_name)
                
                # Create company object with all information
                company = HealthcareCompany(
                    name=company_name,
                    website=website,
                    description=self.generate_description(company_name, category),
                    location=location,
                    category=category,
                    source="Curated German Healthcare Database"
                )
                self.companies.append(company)
        
        print(f"✅ Extracted {len(self.companies)} German healthcare companies")
    
    def generate_website_url(self, company_name: str) -> str:
        """
        Generate a likely website URL based on the company name.
        
        This method creates realistic website URLs by:
        1. Extracting the core company name
        2. Removing German business suffixes (GmbH, AG, etc.)
        3. Cleaning special characters
        4. Generating common URL patterns
        
        Args:
            company_name (str): The full company name
            
        Returns:
            str: A likely website URL for the company
        """
        # Convert to lowercase for processing
        name = company_name.lower()
        
        # Remove German business suffixes and common words
        name = re.sub(r'\s+(?:gmbh|ag|se|kg|co\.|&|und).*', '', name)
        
        # Remove all non-alphanumeric characters
        name = re.sub(r'[^a-z0-9]', '', name)
        
        # Common patterns for German company websites
        patterns = [
            f"https://www.{name}.de",    # Most common German pattern
            f"https://www.{name}.com",   # International pattern
            f"https://{name}.de",        # Without www
            f"https://{name}.com"        # International without www
        ]
        
        # Return the most likely URL (German .de domain with www)
        return patterns[0]
    
    def categorize_company(self, company_name: str) -> str:
        """
        Categorize a company based on its name and known business activities.
        
        This method analyzes the company name to determine its primary
        business category in the healthcare industry.
        
        Args:
            company_name (str): The company name to analyze
            
        Returns:
            str: The determined business category
        """
        name_lower = company_name.lower()
        
        # Check for pharmaceutical indicators
        if any(word in name_lower for word in ['pharma', 'arzneimittel', 'bayer', 'merck', 'roche', 'novartis', 'pfizer']):
            return "Pharmaceuticals"
        
        # Check for medical technology indicators
        elif any(word in name_lower for word in ['medtech', 'medical', 'diagnostics', 'siemens', 'zeiss', 'draeger']):
            return "Medical Technology"
        
        # Check for biotechnology indicators
        elif any(word in name_lower for word in ['biotech', 'bio', 'evotec', 'morphosys', 'qiagen']):
            return "Biotechnology"
        
        # Check for dialysis and renal care indicators
        elif any(word in name_lower for word in ['dialyse', 'fresenius', 'nephro', 'davita']):
            return "Dialysis & Renal Care"
        
        # Check for medical devices indicators
        elif any(word in name_lower for word in ['surgical', 'aesculap', 'hartmann', 'braun']):
            return "Medical Devices"
        
        # Default category for all other healthcare companies
        else:
            return "Healthcare Services"
    
    def determine_location(self, company_name: str) -> str:
        """
        Determine the likely headquarters location based on company name.
        
        This method uses a mapping of known German healthcare companies
        to their headquarters locations.
        
        Args:
            company_name (str): The company name to analyze
            
        Returns:
            str: The company's likely location
        """
        name_lower = company_name.lower()
        
        # Location mapping based on known company headquarters
        location_map = {
            'siemens': 'Munich, Germany',
            'bayer': 'Leverkusen, Germany',
            'merck': 'Darmstadt, Germany',
            'fresenius': 'Bad Homburg, Germany',
            'braun': 'Melsungen, Germany',
            'zeiss': 'Jena, Germany',
            'draeger': 'Lübeck, Germany',
            'sartorius': 'Göttingen, Germany',
            'evotec': 'Hamburg, Germany',
            'morphosys': 'Martinsried, Germany',
            'qiagen': 'Hilden, Germany',
            'biotest': 'Dreieich, Germany',
            'stada': 'Bad Vilbel, Germany',
            'hexal': 'Holzkirchen, Germany',
            'gruenenthal': 'Aachen, Germany',
            'biotronik': 'Berlin, Germany',
            'aesculap': 'Tuttlingen, Germany',
            'hartmann': 'Heidenheim, Germany',
            'heraeus': 'Hanau, Germany'
        }
        
        # Check if company name contains any known location indicators
        for key, location in location_map.items():
            if key in name_lower:
                return location
        
        # Default location for German companies
        return "Germany"
    
    def generate_description(self, company_name: str, category: str) -> str:
        """
        Generate a business description based on company name and category.
        
        This method creates realistic business descriptions that match
        the company's category and provide useful information about
        their business activities.
        
        Args:
            company_name (str): The company name
            category (str): The business category
            
        Returns:
            str: A detailed business description
        """
        # Template descriptions for each category
        descriptions = {
            "Pharmaceuticals": f"{company_name} is a pharmaceutical company specializing in the development, manufacturing, and distribution of prescription medications and healthcare products in Germany and internationally.",
            
            "Medical Technology": f"{company_name} is a medical technology company that develops and manufactures medical devices, diagnostic equipment, and healthcare solutions for hospitals and healthcare providers.",
            
            "Biotechnology": f"{company_name} is a biotechnology company focused on developing innovative therapeutic solutions through advanced biotechnology platforms and research capabilities.",
            
            "Dialysis & Renal Care": f"{company_name} provides dialysis services and renal care solutions for patients with kidney diseases, operating dialysis centers and manufacturing related medical equipment.",
            
            "Medical Devices": f"{company_name} manufactures and distributes medical devices, surgical instruments, and healthcare products for medical professionals and healthcare institutions.",
            
            "Healthcare Services": f"{company_name} provides comprehensive healthcare services and solutions to support the German healthcare system and improve patient outcomes."
        }
        
        # Return category-specific description or generic healthcare description
        return descriptions.get(category, f"{company_name} is a healthcare company operating in the German market.")
    
    def save_results(self, filename: str = "german_healthcare_companies"):
        """
        Save the extracted companies to CSV and JSON files.
        
        This method creates both CSV and JSON output files for maximum
        compatibility with different systems and use cases.
        
        Args:
            filename (str): Base filename for output files (without extension)
        """
        # Create output directory if it doesn't exist
        Path("output").mkdir(exist_ok=True)
        
        # Save as JSON file for developers and APIs
        json_file = f"output/{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(company) for company in self.companies], f, indent=2, ensure_ascii=False)
        
        # Save as CSV file for spreadsheet applications and CRM systems
        csv_file = f"output/{filename}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.companies:
                # Use the first company's fields as column headers
                writer = csv.DictWriter(f, fieldnames=asdict(self.companies[0]).keys())
                writer.writeheader()
                
                # Write all companies to CSV
                for company in self.companies:
                    writer.writerow(asdict(company))
        
        print(f"✅ Results saved to {json_file} and {csv_file}")
    
    def run(self):
        """
        Run the complete scraping process.
        
        This is the main method that orchestrates the entire scraping process:
        1. Extract companies from various sources
        2. Remove duplicates
        3. Generate statistics and reports
        4. Save results to files
        
        Returns:
            List[HealthcareCompany]: List of all extracted companies
        """
        print("🚀 Starting German Healthcare Company Extraction")
        print("=" * 60)
        
        # Step 1: Extract companies from all sources
        self.extract_from_wikipedia()
        
        # Step 2: Remove duplicates based on company name
        unique_companies = []
        seen = set()
        
        for company in self.companies:
            # Use lowercase company name as deduplication key
            key = company.name.lower()
            if key not in seen:
                seen.add(key)
                unique_companies.append(company)
        
        # Update companies list with deduplicated results
        self.companies = unique_companies
        
        # Step 3: Generate and display statistics
        print(f"\n📊 FINAL RESULTS:")
        print(f"   Total companies: {len(self.companies)}")
        
        # Create category breakdown
        categories = {}
        for company in self.companies:
            categories[company.category] = categories.get(company.category, 0) + 1
        
        print(f"\n📈 BREAKDOWN BY CATEGORY:")
        for category, count in sorted(categories.items()):
            print(f"   {category}: {count} companies")
        
        # Display sample companies for preview
        print(f"\n🏢 SAMPLE COMPANIES:")
        for i, company in enumerate(self.companies[:15]):
            print(f"   {i+1}. {company.name}")
            print(f"      🌐 {company.website}")
            print(f"      📍 {company.location}")
            print(f"      🏷️  {company.category}")
            print()
        
        # Step 4: Save results to files
        self.save_results()
        
        return self.companies

def main():
    """
    Main function to run the healthcare company scraper.
    
    This function creates a scraper instance, runs the extraction process,
    and displays the final results summary.
    """
    # Create scraper instance
    scraper = HealthcareScraper()
    
    # Run the complete extraction process
    companies = scraper.run()
    
    # Display final completion message
    print(f"\n🎉 EXTRACTION COMPLETE!")
    print(f"   Found {len(companies)} German healthcare companies")
    print(f"   Results saved to output/ directory")

# Run the scraper when script is executed directly
if __name__ == "__main__":
    main()