# 🏥 Dynamic Healthcare Company Discovery

**🚀 Automatically finds European healthcare companies and extracts their names & products**

## 🎯 What It Does:

### Step 1: Discover Companies
```bash
python3 DYNAMIC_RESEARCH_DISCOVERY.py
```
- Scrapes Wikipedia healthcare categories live
- Extracts companies from European stock exchanges  
- Generates 500+ potential URLs automatically
- **Output:** URL lists ready for validation

### Step 2: Extract Names & Products
```bash
python3 DYNAMIC_MEGA_HEALTHCARE_DATABASE.py
```
- Loads discovered URLs + your 52 manual URLs
- **Extracts clean company names** from websites
- **Extracts products & services** from website content
- Validates all URLs and creates comprehensive database
- **Output:** Complete CSV/JSON with names, products, and details

## 🎉 Final Database Includes:
- ✅ **Company names** - Extracted from meta tags, titles, domains
- ✅ **Products & services** - AI solutions, medical devices, software platforms
- ✅ **Healthcare categories** - AI/ML, Digital Health, Biotech, Medical Devices
- ✅ **Countries** - Germany, UK, France, Switzerland + 20 more
- ✅ **Source tracking** - Manual vs Dynamically discovered
- ✅ **Validation status** - Active websites vs errors

## 📊 Expected Results:
- **150-300+ companies** with complete profiles
- **Your 52 URLs preserved** + 100+ newly discovered
- **Clean company names** (no more "Welcome to..." titles)
- **Detailed products** (e.g., "AI-powered diagnostic platform")
- **Professional CSV export** ready for analysis

## 🚀 Key Features:
- **No hardcoded URLs** - Everything discovered dynamically
- **Smart name extraction** - Multiple methods with fallbacks  
- **Product intelligence** - Finds what companies actually do
- **European focus** - 25+ European countries covered
- **Scalable** - Easy to add more research sources

**Just run both scripts in order and get your complete healthcare database!**