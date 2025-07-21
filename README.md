# 🚀 Improved Startup Discovery System

**Production-ready discovery of European digital health startups with comprehensive expansion**

## 🎯 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Basic usage
python3 improved_startup_discovery.py

# Enhanced usage (with GitHub token)
export GITHUB_TOKEN=your_github_token
python3 improved_startup_discovery.py
```

## ✨ Key Features

### 🔍 **Comprehensive Discovery Sources**
- **6 Directory Sources**: StartupBlink, Sifted, MedTech Europe, German Accelerator + more
- **20 Smart Search Queries**: Location + vertical combinations across Europe
- **5 News Aggregators**: EU-Startups, HealthTech Alpha, specialized health directories
- **Enhanced GitHub**: 6 queries with API token support + retry logic
- **LinkedIn References**: Search-based startup mentions and lists

### 🛡️ **Quality & Validation**
- **Domain Filtering**: 50+ banned domains, hosting platforms filtered out
- **URL Health Checks**: Only working URLs included (is_alive=True)
- **Multi-Language Support**: English, German, French keyword scanning
- **Industry Auto-Labeling**: AI/ML, Telemedicine, MedTech, Pharma, etc.
- **Smart Deduplication**: Domain + title/meta signature matching

### 📊 **Smart Organization**
- **Confidence-Based Sorting**: High quality results first
- **Health Relevance Priority**: Health-related startups prioritized
- **Separated Output Files**: Verified, discovered, and generated categories
- **Comprehensive Metadata**: Industry labels, countries, health scores

## 📁 Output Files

- `verified_startups_YYYYMMDD_HHMMSS.csv` - Highest confidence (9-10)
- `discovered_startups_YYYYMMDD_HHMMSS.csv` - Medium confidence (5-8)
- `generated_startups_YYYYMMDD_HHMMSS.csv` - Lower confidence (1-4)
- `comprehensive_results_YYYYMMDD_HHMMSS.json` - Complete data with metadata
- `discovery_summary_YYYYMMDD_HHMMSS.txt` - Human-readable report

## 🔧 JSON to CSV Conversion

```bash
# Convert comprehensive JSON results to CSV
python3 json_to_csv_converter.py comprehensive_results_YYYYMMDD_HHMMSS.json
```

## 🏆 Results Expected

- **5-10x Dataset Growth** through expanded sources
- **Multi-Country Coverage**: Germany, France, UK, Netherlands, Switzerland, Austria, etc.
- **Industry Intelligence**: Auto-categorized by health tech verticals
- **Production Quality**: Filtered, validated, and sorted results
- **100% Free**: No paid APIs or services required

## 🎯 Perfect For

- Health tech market research
- Startup ecosystem analysis  
- Investment pipeline development
- Partnership discovery
- Competitive intelligence