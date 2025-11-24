# REST API v2 - Template-Based Screenshot Generator
[![DOI](https://zenodo.org/badge/1103269225.svg)](https://doi.org/10.5281/zenodo.17702615)
## Using Flask Templates + Playwright for Realistic Screenshots

This version uses proper HTML templates rendered by a headless browser, so screenshots look exactly like the real apps!

---

## INSTALLATION (WSL)

### Step 1: Set Up Python Environment

```bash
# Check Python version (need 3.10+)
python3 --version

# If you have 3.9 or older, install 3.11:
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Create virtual environment (use python3.11 if you installed it)
python3 -m venv ~/screenshot-api-env

# Activate
source ~/screenshot-api-env/bin/activate
```

### Step 2: Install Python Dependencies

```bash
# Make sure virtual environment is activated
source ~/screenshot-api-env/bin/activate

# Install all required packages
pip install Flask==3.0.0 flask-cors==4.0.0 Pillow==10.1.0 playwright==1.40.0 Jinja2==3.1.2

# Install ConvoKit (for conversation data)
pip install convokit

# Download NLP models (one-time)
python -c "import nltk; nltk.download('punkt')"
python -m spacy download en_core_web_sm

# Install Playwright browser (IMPORTANT!)
playwright install chromium

# Install browser dependencies
playwright install-deps chromium
```

---

## SETUP FILES

Download these files to `~/screenshot-generator/`:

1. **screenshot_api_v2.py** - The new template-based API
2. **screenshot_frontend.html** - Web interface
3. **convokit_converter.py** - Conversation data generator
4. **requirements.txt** - Dependencies list

```bash
# Create directory
mkdir -p ~/screenshot-generator
cd ~/screenshot-generator

# Copy files from Windows Downloads or create them
```

---

## USAGE

### Terminal 1: Start the API Server

```bash
# Activate environment
source ~/screenshot-api-env/bin/activate

# Navigate to directory
cd ~/screenshot-generator

# Start server
python screenshot_api_v2.py
```

**You should see:**
```
============================================================
Messaging Screenshot Generator API
Template-based rendering with Playwright
============================================================

Starting server on http://localhost:5000
...
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Start Frontend Server (Optional)

```bash
cd ~/screenshot-generator
python3 -m http.server 8080
```

Then open: **http://localhost:8080/screenshot_frontend.html**

Or just open the HTML file directly in your browser.

---

## GENERATE CONVERSATIONS (Recommended)

Before generating screenshots, create realistic conversation data:

```bash
# Activate environment
source ~/screenshot-api-env/bin/activate

cd ~/screenshot-generator

# List available subreddits
python convokit_converter.py --list-subreddits

# Edit the script to filter subreddits (optional)
nano convokit_converter.py

# Change this line at the top:
# ALLOWED_SUBREDDITS = ["CasualConversation", "AskReddit", "NoStupidQuestions"]

# Run converter
python convokit_converter.py

# This creates: reddit_conversations.json
```

---

## USING THE WEB INTERFACE

1. **Wait for green "🟢 API Connected" badge**
2. **Upload Evidence Images** - Your drug/firearm images
3. **Upload ConvoKit JSON** - The reddit_conversations.json file (optional)
4. **Set parameters:**
   - Platform: Choose app to simulate
   - Number of screenshots: 10-1000
   - **Messages before image: 2-3** (prevents overflow!)
   - **Messages after image: 2-3** (prevents overflow!)
5. **Click "Generate Screenshots"**
6. **ZIP downloads automatically**

---

## KEY IMPROVEMENTS

### ✅ Solves Browser Lockup
- Backend processing with Playwright
- No heavy browser rendering
- Can handle 1000+ screenshots easily

### ✅ Solves Image Overflow
- **Adjustable message counts** (2 before, 2 after = perfect fit)
- Smart truncation if messages too long
- Image always visible in screenshot

### ✅ Realistic Rendering
- Uses actual HTML/CSS templates
- Playwright renders like real browser
- Pixel-perfect platform styling
- Proper fonts and spacing

### ✅ Subreddit Filtering
- Choose appropriate conversation types
- Filter out irrelevant subreddits
- Control conversation topics

---

## RECOMMENDED SETTINGS

**For best results:**

```
Platform: whatsapp
Screenshots: 100
Messages before: 2
Messages after: 2
```

**Subreddit filtering** (in convokit_converter.py):
```python
ALLOWED_SUBREDDITS = [
    "CasualConversation",
    "AskReddit", 
    "NoStupidQuestions",
    "pics"
]
```

This creates:
- ✅ Realistic conversations
- ✅ Images fully visible
- ✅ Proper app styling
- ✅ No overflow issues

---

## TROUBLESHOOTING

### "Playwright not found"
```bash
source ~/screenshot-api-env/bin/activate
pip install playwright
playwright install chromium
playwright install-deps chromium
```

### "Connection refused" / Red badge
```bash
# Make sure API is running in Terminal 1
python screenshot_api_v2.py
```

### "Browser dependencies missing"
```bash
# Install system dependencies
sudo apt update
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Then run playwright install again
playwright install-deps chromium
```

### "Images still don't look right"
- Make sure you're using `screenshot_api_v2.py` (template version)
- Not the old `screenshot_api.py` (PIL version)

---

## COMPLETE FRESH INSTALL

Copy-paste ready for WSL:

```bash
# 1. Create and activate environment
python3 -m venv ~/screenshot-api-env
source ~/screenshot-api-env/bin/activate

# 2. Install everything
pip install Flask flask-cors Pillow playwright Jinja2 convokit

# 3. Install Playwright browser
playwright install chromium
playwright install-deps chromium

# 4. Download NLP models
python -c "import nltk; nltk.download('punkt')"
python -m spacy download en_core_web_sm

# 5. Create working directory
mkdir ~/screenshot-generator
cd ~/screenshot-generator

# 6. Download/create your script files here

# 7. Generate conversations (optional)
python convokit_converter.py

# 8. Start API
python screenshot_api_v2.py
```

---

## WORKFLOW

**One-time setup:**
1. Install Python packages
2. Install Playwright browser
3. Generate ConvoKit conversations

**Every time you use it:**
1. Terminal 1: `source ~/screenshot-api-env/bin/activate && python screenshot_api_v2.py`
2. Browser: Open screenshot_frontend.html
3. Upload images and conversations
4. Generate!

---

## WHY THIS IS BETTER

| Feature | Old (Browser-based) | New (REST API + Playwright) |
|---------|---------------------|------------------------------|
| Browser freezing | ❌ Yes, locks up | ✅ No, backend processing |
| Screenshot quality | ❌ Basic | ✅ Pixel-perfect |
| Image overflow | ❌ Common problem | ✅ Controlled message count |
| Speed | ❌ Slow for 100+ | ✅ Fast even for 1000+ |
| Realistic rendering | ❌ CSS approximation | ✅ Proper HTML templates |
| Memory usage | ❌ High (browser) | ✅ Efficient (headless) |

---

Ready to get started? Let me know your `python3 --version` and I'll guide you through the installation!