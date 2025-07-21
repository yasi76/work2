# 🏢 Company Name Extractor

A lightweight script for extracting company names from healthcare URLs, separated from the heavy mega database operations.

## 🎯 Purpose

This script focuses **only** on company name extraction, making it much faster and lighter than the full MEGA database script. It's perfect when you just need company names without all the detailed metadata.

## ⚡ Key Advantages

- **Fast**: Only reads the first 8KB of each page (just the `<head>` section)
- **Lightweight**: No heavy product/service extraction
- **Smart**: Uses multiple extraction methods (URL domain, page title, meta tags)
- **Flexible**: Can load URLs from discovery files or use manual list

## 🚀 Usage

### Basic Usage
```bash
python3 company_name_extractor.py
```

### How it works

1. **Automatically finds URLs** from:
   - Discovery files from `DYNAMIC_RESEARCH_DISCOVERY.py` (if available)
   - Manual URL list (fallback)
   - Any URL files in the directory

2. **Extracts company names** using:
   - **Meta tags** (og:site_name, application-name) - *Most accurate*
   - **Page title** parsing - *Good for most sites*  
   - **URL domain** extraction - *Fast fallback*

3. **Saves results** to:
   - `company_names_YYYYMMDD_HHMMSS.csv`
   - `company_names_YYYYMMDD_HHMMSS.json`

## 📊 Input Formats Supported

- **Text files**: One URL per line (`*.txt`)
- **JSON files**: List of URLs or objects with `url`/`website` fields
- **CSV files**: With `url` or `website` columns

## 🔧 Configuration

The script automatically:
- Loads URLs from discovery files if available
- Falls back to manual URL list
- Removes duplicates and cleans URLs
- Uses respectful delays (0.5s between requests)

## 📈 Output

Each extracted company gets:
- `url`: Original URL
- `company_name`: Extracted company name
- `extraction_method`: How the name was found
- `status`: Success/Partial/Error
- `raw_title`: Original page title (first 100 chars)
- `extracted_date`: When extraction was performed

## ⚡ Performance

- **~0.5-1 second per URL** (vs 3-5 seconds in mega script)
- **8KB read limit** (vs full page content in mega script)
- **Simple extraction** (vs complex product/service analysis)

## 🔄 Integration

Perfect to use **before** the mega script:
1. Run `company_name_extractor.py` to get quick company names
2. Review and filter the list
3. Use filtered URLs with mega script for detailed analysis

## 🎯 Example Output

```
✅ Acalta (Meta tags)
✅ Actimi (Page title)  
⚠️ Emmora (URL domain (fallback))
✅ Alfa-Ai (Meta tags)
❌ Unknown (Failed)
```

## 💡 Tips

- Run `DYNAMIC_RESEARCH_DISCOVERY.py` first for best URL coverage
- Check the CSV output for quality review
- Use this for quick company identification before detailed analysis