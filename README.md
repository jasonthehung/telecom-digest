# 📡 Telecom Industry Automated Digest System

[English](README.md) | [繁體中文](README.zh-TW.md)

Automatically fetch telecom industry news RSS feeds, use Gemini AI for intelligent ranking and filtering, and send polished HTML email digests.

## ✨ Features

- **🔄 Automated Execution**: Daily automated runs via GitHub Actions
- **📰 Multi-Source Integration**: Aggregates Light Reading, RCR Wireless News, Fierce Wireless, Fierce Telecom, Total Telecom, TechNews and other major telecom media
- **🤖 Lightweight AI Ranking**: Uses Gemini 2.0 Flash for title-based news ranking (~86% token savings)
- **🎯 Smart Prioritization**: Automatically prioritizes Ericsson, Taiwan market, and technical keywords
- **📧 Polished Emails**: Card-style HTML design compatible with major email clients
- **⚠️ Error Notifications**: Automatic alerts when system errors occur

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Processing Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Fetch RSS Feeds                                     │
│     └── Aggregate news from 6 sources                        │
│              ↓                                               │
│  Step 2: AI Title Ranking (Lightweight)                      │
│     ├── 2a. Send TITLES ONLY to Gemini                       │
│     ├── 2b. AI returns top 15 ranked indices                 │
│     └── 2c. Filter news based on AI selection                │
│              ↓                                               │
│  Step 3: Prepare Display Format                              │
│     └── Generate AnalyzedNews objects                        │
│              ↓                                               │
│  Step 4: Generate HTML Email                                 │
│              ↓                                               │
│  Step 5: Send Email                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Token Optimization

The system uses a lightweight AI approach that significantly reduces API costs:

| Item | Traditional | Lightweight | Savings |
|------|-------------|-------------|---------|
| Input | ~50 articles × 500 chars | ~50 titles × 80 chars | **84%** |
| Output | ~15 summaries × 300 chars | ~50 indices ≈ 100 chars | **98%** |
| **Total** | ~30,000 tokens | ~4,100 tokens | **~86%** |

## 📋 News Sources

| Source | URL | Language |
|--------|-----|----------|
| Light Reading | https://www.lightreading.com/rss.xml | English |
| RCR Wireless News | https://www.rcrwireless.com/feed | English |
| Fierce Wireless | https://www.fiercewireless.com/rss/xml | English |
| Fierce Telecom | https://www.fiercetelecom.com/rss/xml | English |
| Total Telecom | https://www.totaltele.com/feed | English |
| TechNews 科技新報 | https://technews.tw/feed/ | Chinese |

## 🎯 Priority Logic

### Highest Priority
- **Ericsson Related**: Ericsson, 愛立信
- **Taiwan Market**: Taiwan, 台灣, CHT, 中華電, 台灣大, 遠傳, NCC
- **Major Events**: Mergers, bankruptcies, bans

### High Priority
- **RAN Technology**: Open RAN, vRAN, C-RAN, O-RAN
- **Core Network**: 5G Core, Core Network, EPC
- **New Technologies**: 6G, AI-RAN, Network Slicing, MEC, RedCap, NTN
- **Business Updates**: Financial reports, partnerships, mergers

## 🚀 Quick Start

### 1. Fork the Repository

Click the Fork button at the top right to fork the project to your GitHub account.

### 2. Set GitHub Secrets

Go to Settings > Secrets and variables > Actions, and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `GEMINI_API_KEY` | Gemini API Key | `AIzaSy...` |
| `GMAIL_USER` | Gmail account for sending | `your_email@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Recipient email | `recipient@example.com` |

### 3. Obtain API Key and Password

#### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the API Key

#### Gmail App Password
1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Enable Two-Step Verification
3. Go to Security > Two-Step Verification > App Passwords
4. Choose "Mail" and "Other (Custom name)"
5. Enter a name (e.g., Telecom Digest)
6. Copy the 16-character password

### 4. Enable GitHub Actions

Go to Actions tab and click "I understand my workflows, go ahead and enable them."

### 5. Manual Testing

1. Go to Actions tab
2. Select "Daily Telecom News Digest"
3. Click "Run workflow"
4. Check "Test mode" for testing

## 🗓️ Schedule

| Task | Time | Cron Expression |
|------|------|-----------------|
| Daily Digest | 07:00 Taipei Time | `0 23 * * *` (UTC) |

## 💻 Local Development

### Requirements

- Python 3.11+
- pip

### Installation

```bash
# Clone the project
git clone https://github.com/your-username/telecom-digest.git
cd telecom-digest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with actual values
```

### Local Testing

```bash
cd src

# Test RSS fetching only
python main.py --test-rss

# Test Gemini AI ranking
python main.py --test-gemini

# Test full workflow (output HTML, no email)
python main.py --test

# Run daily digest (sends email)
python main.py

# Debug mode
python main.py --debug
```

## 📁 Project Structure

```
telecom-digest/
├── .github/
│   └── workflows/
│       └── daily.yml          # Daily workflow
├── src/
│   ├── main.py               # Main entry point
│   ├── config.py             # Configuration & constants
│   ├── rss_fetcher.py        # RSS fetching module
│   ├── analyzer.py           # Gemini analysis module
│   ├── email_sender.py       # Email sending module
│   └── html_template.py      # HTML template generator
├── output/                   # Test output directory
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables example
├── .gitignore               # Git ignore file
├── README.md                # English documentation
└── README.zh-TW.md          # Chinese documentation
```

## 📧 Email Content

Daily digest includes:
- 🎯 Ericsson updates (if any)
- 🇹🇼 Taiwan market news (if any)
- 🔥 Focus news
- 📡 RAN & Core technology
- 🚀 New technologies & innovations
- 💼 Business updates
- 📊 Daily statistics

## ⚠️ Error Handling

| Error Type | Handling |
|------------|----------|
| Single RSS source fails | Log and continue with others |
| All RSS sources fail | Send error notification email |
| Gemini API failure | Fallback to keyword-based ranking |
| Email sending failure | Log to GitHub Actions |

## 🔧 Customization

### Modify RSS Sources

Edit `RSS_FEEDS` in `src/config.py`:

```python
RSS_FEEDS: List[RSSSource] = [
    RSSSource("Your Source", "https://your-rss-url.com/feed", "en"),
    # Add more sources...
]
```

### Modify Priority Keywords

Edit `PRIORITY_KEYWORDS` in `src/config.py`:

```python
PRIORITY_KEYWORDS = {
    "highest": {
        "your_category": ["keyword1", "keyword2"],
    },
    "high": {
        # ...
    }
}
```

### Modify AI Ranking Prompt

Edit `GEMINI_RANKING_PROMPT` in `src/config.py` to customize ranking criteria.

### Modify Schedule

Edit cron expression in `.github/workflows/daily.yml`:

```yaml
schedule:
  - cron: '0 23 * * *'  # Change to your preferred time (UTC)
```

## 📝 Notes

1. **Gemini API Quota**: Free tier has rate limits; the lightweight approach minimizes usage
2. **Gmail Security**: Must use app password (not regular password)
3. **Timezone**: GitHub Actions runs in UTC; adjust cron accordingly
4. **Deduplication**: Uses URL hash to avoid duplicate news

## 📄 License

MIT License
