# 🚀 Free 3-Part URL Discovery System

A comprehensive system for finding, evaluating, and extracting company names from European health tech startup URLs using **only FREE tools**.

## 🎯 Overview

This system is designed to:
1. **Find URLs** - Discover European health tech startup URLs from multiple free sources
2. **Evaluate URLs** - Test accessibility, SSL, and content quality of discovered URLs  
3. **Extract Company Names** - Extract company names from working URLs using content analysis

### ✨ Key Features

- 🆓 **100% FREE** - No paid APIs or tools required
- 👤 **User URLs Included** - Your hardcoded URLs are prioritized
- 🌍 **European Focus** - Targets German, EU, and international health tech companies
- 📊 **Comprehensive Analysis** - DNS, HTTP, SSL, content analysis
- 📁 **Multiple Output Formats** - CSV, JSON, and detailed reports
- ⚡ **Rate Limited** - Respectful request timing

## 🏗️ System Architecture

```
Part 1: URL Finder
├── User Hardcoded URLs (Priority)
├── German Startups Directory
├── EU Startup Databases  
├── Conference Exhibitors
├── GitHub Health Projects
├── University Spin-offs
├── Accelerator Portfolios
└── Domain Generation

Part 2: URL Evaluator  
├── DNS Resolution Testing
├── HTTP/HTTPS Accessibility
├── SSL Certificate Validation
├── Response Time Measurement
├── Content Quality Analysis
└── Health Tech Classification

Part 3: Company Name Extractor
├── Page Title Analysis
├── Meta Tag Extraction
├── Schema.org Structured Data
├── Copyright Notice Mining
├── Header Content Analysis
└── Domain Name Parsing
```

## 📋 Your Hardcoded URLs (Included)

Your 53 URLs are hardcoded as the **priority source** in Part 1:

```python
# Sample of your URLs (all 53 are included)
'https://www.acalta.de',
'https://www.actimi.com', 
'https://www.emmora.de',
'https://www.alfa-ai.com',
# ... and 49 more
```

## 🚀 Quick Start

### Option 1: Run All Parts Together (Recommended)

```bash
python3 run_all_parts.py
```

This runs all three parts sequentially and provides a complete analysis.

### Option 2: Run Parts Individually

```bash
# Part 1: Find URLs
python3 part1_url_finder.py

# Part 2: Evaluate URLs (uses Part 1 output)
python3 part2_url_evaluator.py

# Part 3: Extract Company Names (uses Part 2 output)  
python3 part3_company_name_extractor.py
```

## 📊 Expected Output

### Part 1: URL Discovery
- **Input**: Multiple free sources + your hardcoded URLs
- **Output**: 
  - `discovered_urls_part1_TIMESTAMP.csv` - All discovered URLs
  - `discovered_urls_part1_TIMESTAMP.json` - Detailed results
- **Expected**: 400-600 unique URLs

### Part 2: URL Evaluation  
- **Input**: URLs from Part 1
- **Output**:
  - `working_urls_TIMESTAMP.csv` - Verified working URLs
  - `problematic_urls_TIMESTAMP.csv` - Failed URLs with reasons
  - `url_evaluation_part2_detailed_TIMESTAMP.json` - Full analysis
- **Expected**: 60-80% success rate

### Part 3: Company Name Extraction
- **Input**: Working URLs from Part 2
- **Output**:
  - `successful_companies_TIMESTAMP.csv` - Company directory
  - `company_directory_TIMESTAMP.csv` - Complete results
  - `company_extraction_part3_detailed_TIMESTAMP.json` - Detailed analysis
- **Expected**: 70-90% extraction success rate

## 📁 File Structure

```
📦 Free URL Discovery System
├── 📜 part1_url_finder.py           # Part 1: URL Discovery
├── 📜 part2_url_evaluator.py        # Part 2: URL Evaluation  
├── 📜 part3_company_name_extractor.py # Part 3: Company Name Extraction
├── 📜 run_all_parts.py              # Master script (runs all parts)
├── 📜 README.md                     # This documentation
└── 📁 Output Files (generated)
    ├── 📊 discovered_urls_part1_*.csv
    ├── 📊 working_urls_*.csv
    ├── 📊 successful_companies_*.csv
    └── 📊 Various JSON detail files
```

## 🛠️ Technical Details

### Part 1: Free URL Discovery Methods

1. **User Hardcoded URLs** - Your 53 provided URLs (priority)
2. **German Startups** - Health tech companies from German startup directories
3. **EU Startups** - Companies from European startup databases
4. **Conference Exhibitors** - Health tech conference participant lists
5. **GitHub Projects** - Open source health tech projects
6. **University Spin-offs** - Academic health tech companies
7. **Accelerator Portfolios** - Startup accelerator portfolio companies
8. **Domain Generation** - Systematic health tech domain patterns

### Part 2: URL Evaluation Criteria

1. **DNS Resolution** - Can the domain be resolved?
2. **HTTP Accessibility** - Does the website respond?
3. **SSL Validation** - Is HTTPS properly configured?
4. **Response Time** - How fast does the site load?
5. **Content Analysis** - Does it contain health tech keywords?
6. **Quality Assessment** - Content length and structure

### Part 3: Company Name Extraction Methods

1. **Page Title Analysis** - Extract company names from `<title>` tags
2. **Meta Tag Mining** - Search `author`, `og:site_name`, etc.
3. **Schema.org Data** - Parse structured Organization data
4. **Copyright Notices** - Extract names from copyright text
5. **Header Analysis** - Find company names in H1/H2 tags
6. **Domain Parsing** - Convert domain names to company names

## 📈 Expected Results

Based on the system design and your hardcoded URLs:

- **Total URLs Discovered**: ~500-700 unique URLs
- **Working URLs**: ~300-450 URLs (60-80% success rate)
- **Company Names Extracted**: ~250-400 companies (70-90% success rate)

### Quality Metrics

- **High Confidence Companies**: Companies with confidence scores >7.0
- **Medium Confidence Companies**: Companies with confidence scores 4.0-7.0  
- **Low Confidence Companies**: Companies with confidence scores <4.0

## 🔍 Free Tools Used

### Built-in Python Libraries
- `urllib.request` - HTTP requests
- `socket` - DNS resolution
- `ssl` - SSL certificate validation
- `re` - Pattern matching
- `json` - Data serialization
- `csv` - Spreadsheet output

### Manual Research Sources
- German-startups.com directory browsing
- EU-Startups.com database review
- GitHub health tech repository discovery
- Conference website exhibitor list review
- University technology transfer office listings

## ⚠️ Important Notes

### Rate Limiting
- System includes 1-2 second delays between requests
- Respectful of server resources
- No aggressive scraping

### Legal Compliance
- Only accesses publicly available information
- Respects robots.txt when possible
- Uses standard browser user agents

### Quality Assurance
- Multiple validation methods for each URL
- Confidence scoring for company names
- Detailed error logging and reporting

## 🎯 Success Criteria

The system is considered successful if it:

1. ✅ **Includes all your hardcoded URLs** as priority sources
2. ✅ **Discovers 400+ unique URLs** from free sources
3. ✅ **Validates 60%+ of URLs** as working and accessible
4. ✅ **Extracts company names** from 70%+ of working URLs
5. ✅ **Uses only free tools** - no paid APIs required
6. ✅ **Provides confidence scores** for extracted company names
7. ✅ **Generates comprehensive reports** in multiple formats

## 🎉 Final Output

After completion, you'll have:

- 📊 **Company Directory** - Complete list of European health tech companies
- 🌐 **Verified URLs** - Working website URLs with quality scores  
- 🏢 **Company Names** - Extracted with confidence ratings
- 📈 **Quality Metrics** - Success rates and performance statistics
- 📁 **Multiple Formats** - CSV for spreadsheets, JSON for analysis

## 🚀 Ready to Start?

Run the master script to begin the complete 3-part process:

```bash
python3 run_all_parts.py
```

The system will:
1. 🔍 Discover URLs from all free sources
2. 🧪 Test and validate each URL
3. 🏢 Extract company names with confidence scores
4. 📊 Generate comprehensive reports

**Estimated completion time**: 15-30 minutes depending on number of URLs discovered.

---

*🆓 This system uses only free tools and methods - no paid APIs required!*