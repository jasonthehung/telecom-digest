# 📡 Telecom Industry Automated Digest System

[English](README.md) | [Traditional Chinese](README.zh-TW.md)

Automatically fetch telecom industry news RSS feeds, analyze and summarize using Gemini AI, and send emails in a polished HTML format.

## ✨ Features

- **🔄 Automated Execution**: Run daily via GitHub Actions
- **📰 Multi-Source Integration**: Aggregates Light Reading, RCR Wireless News, Fierce Wireless, TechNews, and other major telecom media
- **🤖 AI-Powered Analysis**: Uses Gemini 1.5 Flash for news summarization and classification
- **🎯 Priority Sorting**: Automatically prioritizes Ericsson, Taiwan market, and technical keywords
- **📧 Polished Emails**: Card-style HTML design compatible with major email clients
- **⚠️ Error Notifications**: Sends automatic alerts in case of system errors

## 📋 News Sources

Source | URL | Language
-------|-----|--------
Light Reading | https://www.lightreading.com/rss.xml | English
RCR Wireless News | https://feeds.feedburner.com/rcrwireless/sLmV | English
Fierce Wireless | https://www.fiercewireless.com/rss/xml | English
TechNews | https://technews.tw/feed/ | Chinese

## 🎯 Priority Logic

### Highest Priority (Always Included)
- **Ericsson Related**: Ericsson, 愛立信
- **Taiwan Market**: Taiwan, 台灣, CHT, 中華電, 台灣大, 遠傳, NCC
- **Major Events**: Mergers, bankruptcies, bans

### High Priority (Core Focus)
- **RAN Technology**: Open RAN, vRAN, C-RAN, O-RAN
- **Core Network**: 5G Core, Core Network, EPC
- **New Technologies**: 6G, AI-RAN, Network Slicing, MEC, RedCap, NTN
- **Business Updates**: Financial reports, partnerships, mergers

## 🚀 Quick Start

### 1. Fork the Repository

Click the Fork button at the top right to fork the project to your GitHub account.

### 2. Set GitHub Secrets

Go to Settings > Secrets and variables > Actions, and add the following secrets:

Secret Name | Description | Example
------------|------------|--------
`GEMINI_API_KEY` | Gemini API Key | `AIzaSy...`
`GMAIL_USER` | Gmail account for sending emails | `your_email@gmail.com`
`GMAIL_APP_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop`
`RECIPIENT_EMAIL` | Recipient email | `recipient@example.com`

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
6. Copy the 16-character password (without spaces)

### 4. Enable GitHub Actions

Go to the Actions tab in your repository, click "I understand my workflows, go ahead and enable them."

### 5. Manual Testing

1. Go to Actions tab
2. Select "Daily Telecom News Digest"
3. Click "Run workflow"
4. Check "Test mode" for testing

## 🗓️ Schedule

Task | Time | Cron Expression
-----|------|----------------
Daily Digest | 07:00 Taipei Time | `0 23 * * *` (UTC)

## 💻 Local Development

### Environment Requirements

- Python 3.11+
- pip

### Installation Steps

```bash
# Clone the project
git clone https://github.com/your-username/telecom-digest.git
cd telecom-digest

# Create a virtual environment
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

# Test RSS fetching
python main.py --test-rss

# Test Gemini analysis
python main.py --test-gemini

# Test full workflow (without sending emails, output HTML file)
python main.py --test

# Run daily digest (emails will be sent)
python main.py

# Debug mode
python main.py --debug
```

## 📁 Project Structure

```bash
telecom-digest/
├── .github/
│   └── workflows/
│       └── daily.yml          # Daily workflow
├── src/
│   ├── main.py               # Main program entry
│   ├── config.py             # Configuration and constants
│   ├── rss_fetcher.py        # RSS fetching module
│   ├── analyzer.py           # Gemini analysis module
│   ├── email_sender.py       # Email sending module
│   └── html_template.py      # HTML template generator
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── .gitignore               # Git ignore file
└── README.md                 # Documentation
```

## 📧 Email Content

Daily digest includes:
- 🎯 Ericsson updates (if any)
- 🇹🇼 Taiwan market (if any)
- 🔥 Focus news
- 📡 RAN & Core technology
- 🚀 New technology and innovations
- 💼 Business updates
- 📊 Today's trend observations
- 📌 Other noteworthy items
- 📊 Daily statistics

## ⚠️ Error Handling

System automatically handles the following errors:

Error Type | Handling Method
-----------|----------------
Single RSS source fails | Log and continue with other sources
All RSS sources fail | Send error notification email
Gemini API failure | Retry up to 3 times; if still fails, use backup analysis
Email sending failure | Log to GitHub Actions logs

## 🔧 Custom Settings

### Modify RSS Sources

Edit the `RSS_FEEDS` list in `src/config.py`:

```bash
RSS_FEEDS: List[RSSSource] = [
    RSSSource("Your Source", "https://your-rss-url.com/feed", "en"),
    # Add more sources...
]
```

### Modify Priority Keywords

Edit the `PRIORITY_KEYWORDS` dictionary in `src/config.py`:

```bash
PRIORITY_KEYWORDS = {
    "highest": {
        "your_category": ["keyword1", "keyword2"],
    },
    "high": {
        # ...
    }
}
```

### Modify Execution Time

Edit the cron expression in `.github/workflows/daily.yml`:

```bash
schedule:
  - cron: '0 23 * * *'  # Change to your desired time (UTC)
```

## 📝 Notes

1. **Gemini API Quota**: Free version allows 15 requests per minute
2. **Gmail Security**: Must use an app password
3. **Timezone Conversion**: GitHub Actions runs in UTC
4. **News Deduplication**: Uses URL hash to avoid duplicates

## 📄 License

MIT License
