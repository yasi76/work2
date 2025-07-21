# Digital Health Startup Summary Generator

This script generates comprehensive analytics and reports from validated digital health startup data produced by `evaluate_health_startups.py`.

## Features

- **Comprehensive Analytics**: Analyzes success rates, health relevance, regional distribution, and more
- **Multiple Output Formats**: JSON summary, Markdown report, Excel workbook, and PNG visualizations
- **Detailed Insights**: Identifies verified health startups, dead URLs, suspicious pages
- **Keyword Analysis**: Tracks most common health-related keywords
- **Error Analysis**: Categorizes and counts different types of failures
- **Visual Reports**: Creates charts for status distribution, regions, health scores, and keywords

## Installation

### Basic Installation

```bash
pip install -r requirements.txt
```

### Full Installation (with visualization and Excel support)

```bash
pip install requests beautifulsoup4 lxml matplotlib seaborn pandas openpyxl
```

## Usage

### Basic Usage

```bash
python generate_startup_summary.py validated_urls.json
```

### Advanced Usage

```bash
python generate_startup_summary.py validated_urls.json --output-prefix health_analysis --excel
```

### Command Line Arguments

- `input_file`: Validated JSON file from evaluate_health_startups.py (required)
- `--output-prefix`: Prefix for output files (default: "startup_summary")
- `--no-viz`: Skip visualization generation (useful if matplotlib not installed)
- `--excel`: Generate Excel report with multiple sheets

## Input Format

The script accepts validated JSON output from `evaluate_health_startups.py`:

```json
[
  {
    "url": "https://example.com",
    "is_live": true,
    "is_health_related": true,
    "company_name": "Example Health",
    "health_relevance_score": 8,
    "region": "DACH",
    "language": "de",
    "matched_keywords": ["health", "medical"],
    ...
  }
]
```

## Output Files

### 1. JSON Summary (`{prefix}_analysis.json`)

Comprehensive statistics including:
- Overview metrics (success rates, health rates)
- Distribution by region, language, category
- Health score distribution
- Top keywords
- Lists of verified startups, dead URLs, suspicious pages

### 2. Markdown Report (`{prefix}_report.md`)

Human-readable report with:
- Overview statistics
- Tables for regional/language distribution
- Top health keywords
- List of verified health startups
- Error analysis

### 3. Visualizations (`{prefix}_analysis.png`)

4-panel chart showing:
- Website status distribution (pie chart)
- Regional distribution (bar chart)
- Health score distribution (histogram)
- Top 10 health keywords (horizontal bar chart)

### 4. Excel Report (`{prefix}_report.xlsx`) - Optional

Multi-sheet workbook containing:
- Overview sheet with summary metrics
- All Startups sheet with full data
- Verified Health sheet with confirmed startups
- By Region sheet with regional analysis
- Errors sheet with error breakdown

## Metrics Explained

### Overview Metrics

- **Total URLs Analyzed**: Total number of URLs processed
- **Live Websites**: URLs returning HTTP 200 status
- **Success Rate**: Percentage of URLs that are live
- **Health-Related**: Live sites with health relevance score ≥ 3
- **Health Rate**: Percentage of live sites that are health-related

### Health Relevance Score

Scale of 0-10 based on health keyword matches:
- 0-2: Not health-related
- 3-5: Possibly health-related
- 6-8: Likely health-related
- 9-10: Definitely health-related

### Regions

- **DACH**: Germany, Austria, Switzerland
- **Europe**: Other European countries
- **Unknown**: Could not determine region

## Example Console Output

```
==================================================
DIGITAL HEALTH STARTUP ANALYSIS SUMMARY
==================================================
Total URLs analyzed: 500
Live websites: 380 (76.0%)
Health-related: 285 (75.0% of live)
Top regions: DACH, Europe, Unknown
Verified health startups: 285
==================================================
```

## Use Cases

1. **Investment Research**: Identify verified digital health startups in specific regions
2. **Market Analysis**: Understand the distribution of health tech companies
3. **Data Quality**: Assess the quality of discovered URLs
4. **Keyword Trends**: Identify common themes in digital health

## Tips

1. Run this after `evaluate_health_startups.py` for best results
2. Use `--excel` flag for detailed analysis in spreadsheet format
3. The markdown report is great for sharing with stakeholders
4. Check the error analysis to improve URL discovery methods

## Troubleshooting

### "No module named 'matplotlib'" error
- Install visualization dependencies: `pip install matplotlib seaborn`
- Or use `--no-viz` flag to skip visualizations

### "No module named 'pandas'" error
- Install Excel dependencies: `pip install pandas openpyxl`
- Or omit the `--excel` flag

### Empty verified startups list
- Check that your URLs are being marked as health-related
- Verify that health_relevance_score threshold is appropriate
- Ensure keywords are being matched correctly