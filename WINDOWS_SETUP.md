# Healthcare Startup Discovery System - Windows Setup Guide

## 🪟 For Windows Users with Python 3.13

This guide is specifically for Windows users who have encountered dependency errors with the original requirements.

### ✅ System Requirements

- **Windows 10/11**
- **Python 3.13.5** (or any Python 3.7+)
- **Internet connection** for downloading packages

### 🚀 Quick Test (No Installation Required)

First, test the core functionality without installing anything:

```cmd
python simple_demo.py
```

This will show you exactly what the system does with zero dependencies!

### 📦 Installation Options

#### Option 1: Automatic Installation (Recommended)

```cmd
install-windows.bat
```

This will:
- Create a virtual environment
- Install minimal dependencies first
- Try full installation (with graceful fallbacks)
- Test the system
- Set up all directories

#### Option 2: Manual Installation

1. **Create virtual environment:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

2. **Install minimal dependencies:**
```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
```

3. **Test basic functionality:**
```cmd
python demo.py
```

4. **Optional - Install full dependencies:**
```cmd
python -m pip install -r requirements.txt
```

### 🔧 Fixed Dependency Issues

**Original Problems:**
- ❌ `asyncio==3.4.3` (shouldn't be installed - it's built-in)
- ❌ Exact version pinning causing conflicts
- ❌ Missing fallbacks for unavailable packages

**Solutions Implemented:**
- ✅ Removed `asyncio` from requirements (built into Python 3.7+)
- ✅ Used version ranges instead of exact pins
- ✅ Added graceful fallbacks for optional dependencies
- ✅ Separated minimal vs. full requirements

### 📋 Updated Requirements

**Minimal (Always Works):**
```
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pandas>=2.0.0
nltk>=3.8.0
validators>=0.22.0
python-dotenv>=1.0.0
tqdm>=4.66.0
colorama>=0.4.6
```

**Optional (Enhanced Features):**
```
scikit-learn>=1.3.0
langdetect>=1.0.9
tldextract>=5.0.0
fake-useragent>=1.4.0
```

### 🏃‍♂️ Running the System

After installation:

```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Run the full discovery system
python main.py

# Or run the demo
python demo.py
```

### 🛠️ Troubleshooting

#### Problem: "python: command not found"
**Solution:** Use `python3` or ensure Python is in your PATH.

#### Problem: Dependency conflicts
**Solution:** Use the minimal requirements:
```cmd
python -m pip install -r requirements-minimal.txt
```

#### Problem: SSL certificate errors
**Solution:** The code includes SSL workarounds for NLTK downloads.

#### Problem: Import errors
**Solution:** The code gracefully handles missing dependencies:
- NLTK not available → Uses basic text processing
- scikit-learn not available → Uses simple keyword matching
- langdetect not available → Defaults to English

### 📊 What Works Without Full Dependencies

The system is designed to work even with minimal dependencies:

| Feature | Minimal Install | Full Install |
|---------|----------------|--------------|
| Healthcare keyword detection | ✅ Basic | ✅ Advanced |
| URL validation | ✅ Full | ✅ Full |
| Text processing | ✅ Simple | ✅ Advanced NLP |
| Output generation | ✅ Full | ✅ Full |
| Web scraping | ✅ Full | ✅ Full |
| Language detection | ❌ English only | ✅ Multi-language |
| Semantic similarity | ❌ Keyword only | ✅ ML-powered |

### 🎯 Expected Output

After running `python main.py`, you'll get:

```
healthcare_startups_20241208_143022.csv     # Company data
healthcare_startups_20241208_143022.json    # Complete results
healthcare_startups_20241208_143022_summary.txt  # Statistics
healthcare_discovery.log                    # Detailed logs
```

### 📞 Still Having Issues?

If you encounter problems:

1. **Try the simple demo first:**
   ```cmd
   python simple_demo.py
   ```

2. **Check Python version:**
   ```cmd
   python --version
   ```

3. **Check pip version:**
   ```cmd
   python -m pip --version
   ```

4. **Reinstall with verbose output:**
   ```cmd
   python -m pip install -v -r requirements-minimal.txt
   ```

### 💡 Pro Tips

- **Use virtual environments** to avoid system conflicts
- **Start with minimal install** and add features incrementally  
- **Check logs** in `healthcare_discovery.log` for detailed info
- **The system works progressively** - more dependencies = more features

---

**Note:** This system is designed to be robust and work across different environments. Even if some advanced features aren't available, the core functionality will still discover healthcare startups effectively!