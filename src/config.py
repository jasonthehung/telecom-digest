"""
電信產業自動摘要系統 - 設定檔
"""
import os
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class RSSSource:
    """RSS 來源設定"""
    name: str
    url: str
    language: str = "en"


# RSS 新聞來源
RSS_FEEDS: List[RSSSource] = [
    RSSSource("Light Reading", "https://www.lightreading.com/rss.xml"),
    RSSSource("RCR Wireless News", "https://feeds.feedburner.com/rcrwireless/sLmV"),
    RSSSource("Fierce Wireless", "https://www.fiercewireless.com/rss/xml"),
    RSSSource("TechNews 科技新報", "https://technews.tw/feed/", "zh"),
]

# 優先級關鍵字設定
PRIORITY_KEYWORDS: Dict[str, Dict] = {
    "highest": {
        "ericsson": ["ericsson", "愛立信"],
        "taiwan": ["taiwan", "台灣", "cht", "中華電", "台灣大", "遠傳", "ncc"],
        "major_events": ["bankruptcy", "破產", "ban", "禁令", "acquisition", "merger", "併購"],
    },
    "high": {
        "ran": ["open ran", "vran", "c-ran", "o-ran", "radio access network", "massive mimo"],
        "core": ["5g core", "core network", "epc", "核心網", "5gc", "nef", "upf"],
        "new_tech": ["6g", "ai-ran", "network slicing", "mec", "redcap", "ntn", "衛星通訊",
                     "private 5g", "edge computing", "digital twin"],
        "financial": ["earnings", "revenue", "財報", "q1", "q2", "q3", "q4", "profit",
                      "loss", "營收", "quarterly"],
        "partnership": ["partnership", "collaboration", "合作", "contract", "deal",
                        "agreement", "alliance"],
        "ma": ["acquisition", "merger", "m&a", "併購", "收購", "takeover"],
    }
}

# 類別對應
CATEGORY_MAPPING = {
    "ericsson": "ericsson",
    "taiwan": "taiwan",
    "ran": "ran",
    "core": "core",
    "new_tech": "tech",
    "financial": "business",
    "partnership": "business",
    "ma": "business",
    "major_events": "business",
}

# Badge 樣式對應
BADGE_STYLES = {
    "ericsson": ("badge-ericsson", "⭐ Ericsson"),
    "taiwan": ("badge-taiwan", "🇹🇼 台灣"),
    "hot": ("badge-hot", "🔥 焦點"),
    "ran": ("badge-ran", "📡 RAN"),
    "core": ("badge-core", "🔧 Core"),
    "tech": ("badge-tech", "🚀 新技術"),
    "business": ("badge-business", "💼 商業"),
    "partnership": ("badge-partner", "🤝 合作"),
    "ma": ("badge-ma", "🔄 M&A"),
}

# Gemini API 設定
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_MAX_RETRIES = 1
GEMINI_RETRY_DELAY = 5  # 秒

# Email 設定
EMAIL_SUBJECT_DAILY = "📡 電信產業日報 - {date}"

# 新聞處理設定
MAX_NEWS_DAILY = 20
NEWS_LOOKBACK_HOURS = 24

# User-Agent 設定（for DigiTimes）
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

# 環境變數
def get_env(key: str, default: str = None, required: bool = False) -> str:
    """取得環境變數"""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


@dataclass
class AppConfig:
    """應用程式設定"""
    gemini_api_key: str = field(default_factory=lambda: get_env("GEMINI_API_KEY", required=True))
    gmail_user: str = field(default_factory=lambda: get_env("GMAIL_USER", required=True))
    gmail_app_password: str = field(default_factory=lambda: get_env("GMAIL_APP_PASSWORD", required=True))
    recipient_email: str = field(default_factory=lambda: get_env("RECIPIENT_EMAIL", required=True))
    debug_mode: bool = field(default_factory=lambda: get_env("DEBUG_MODE", "false").lower() == "true")
    test_mode: bool = field(default_factory=lambda: get_env("TEST_MODE", "false").lower() == "true")


# Gemini 分析提示詞
GEMINI_PROMPT_TEMPLATE = """你是專業的電信產業分析師。分析以下新聞並產生 JSON 格式摘要。

【優先級規則】
1. Ericsson 相關 → 最高優先級（priority 90-100）
2. 台灣市場相關 → 最高優先級（priority 85-95）
3. 重大事件（併購、破產、禁令）→ 最高優先級（priority 80-95）
4. 包含以下關鍵字的新聞提高優先級：
   - RAN: Open RAN, vRAN, C-RAN, O-RAN → priority 70-85
   - Core: 5G Core, Core Network, EPC → priority 70-85
   - 新技術: 6G, AI-RAN, Network Slicing, MEC, RedCap, NTN → priority 65-80
   - 商業: earnings, M&A, partnership, acquisition → priority 60-75
   - 台灣: Taiwan, CHT, 台灣大, 遠傳, NCC → priority 85-95
5. 其他新聞 → priority 30-60

【分類規則】
- ericsson: Ericsson 相關新聞
- ran: Open RAN, vRAN, C-RAN, O-RAN, RAN 相關
- core: 5G Core, Core Network, EPC 相關
- tech: 6G, AI-RAN, Network Slicing, MEC, 新技術相關
- business: 財報、合作、併購、商業動態
- taiwan: 台灣市場相關
- other: 其他產業新聞

【輸出要求】
- 中文摘要保持 100-150 字
- 專有名詞保留英文（如 Open RAN, 5G Core, MEC）
- 關鍵引述保留原文語言
- 標籤使用中英混合，最多 5 個
- badges 只能使用以下值：Ericsson, Taiwan, RAN, Core, Tech, Business, Partnership, M&A

【輸出格式 JSON】
{{
  "news_items": [
    {{
      "title_zh": "中文標題",
      "title_en": "原文標題（保留原文）",
      "summary_zh": "中文摘要（100-150字，保留專有名詞英文）",
      "key_quote": "關鍵引述（保留原文語言，如無則為空字串）",
      "source": "來源媒體名稱",
      "url": "原文連結",
      "tags": ["標籤1", "標籤2", "標籤3"],
      "badges": ["Ericsson", "RAN"],
      "category": "ericsson|ran|core|tech|business|taiwan|other",
      "priority": 0-100
    }}
  ],
  "daily_trends": "今日產業趨勢觀察（中文，50-100字）",
  "statistics": {{
    "total": 18,
    "by_category": {{"ericsson": 2, "ran": 5, "core": 3, "tech": 4, "business": 3, "taiwan": 1, "other": 0}},
    "by_source": {{"Light Reading": 6, "RCR Wireless News": 5, "Mobile World Live": 4, "DigiTimes": 3}}
  }}
}}

【新聞內容】
{news_content}
"""
