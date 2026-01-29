# 📡 電信產業自動摘要系統

[English](README.md) | [繁體中文](README.zh-TW.md)

自動抓取電信產業新聞 RSS feeds，使用 Gemini AI 智慧排序篩選，以精美的 HTML 格式寄送郵件摘要。

## ✨ 功能特色

- **🔄 自動化執行**：透過 GitHub Actions 每日自動執行
- **📰 多來源整合**：整合 Light Reading、RCR Wireless News、Fierce Wireless、Fierce Telecom、Total Telecom、TechNews 科技新報等主流電信產業媒體
- **🤖 輕量化 AI 排序**：使用 Gemini 2.0 Flash 進行標題排序（節省約 86% token 用量）
- **🎯 智慧優先排序**：根據 Ericsson、台灣市場、技術關鍵字自動排序
- **📧 精美郵件**：卡片式 HTML 設計，相容主流郵件客戶端
- **⚠️ 錯誤通知**：系統異常時自動發送通知郵件

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                        處理流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: 抓取 RSS Feeds                                      │
│     └── 從 6 個來源彙整新聞                                   │
│              ↓                                               │
│  Step 2: AI 標題排序（輕量化）                                │
│     ├── 2a. 只傳標題給 Gemini                                │
│     ├── 2b. AI 回傳 top 15 排序索引                          │
│     └── 2c. 根據 AI 選擇篩選新聞                             │
│              ↓                                               │
│  Step 3: 準備顯示格式                                        │
│     └── 生成 AnalyzedNews 物件                               │
│              ↓                                               │
│  Step 4: 生成 HTML 郵件                                      │
│              ↓                                               │
│  Step 5: 發送郵件                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Token 優化

系統採用輕量化 AI 方案，大幅降低 API 成本：

| 項目 | 傳統方案 | 輕量化方案 | 節省 |
|------|----------|------------|------|
| 輸入 | ~50 篇 × 500 字 | ~50 標題 × 80 字 | **84%** |
| 輸出 | ~15 摘要 × 300 字 | ~50 索引 ≈ 100 字 | **98%** |
| **總計** | ~30,000 tokens | ~4,100 tokens | **~86%** |

## 📋 新聞來源

| 來源 | URL | 語言 |
|------|-----|------|
| Light Reading | https://www.lightreading.com/rss.xml | 英文 |
| RCR Wireless News | https://www.rcrwireless.com/feed | 英文 |
| Fierce Wireless | https://www.fiercewireless.com/rss/xml | 英文 |
| Fierce Telecom | https://www.fiercetelecom.com/rss/xml | 英文 |
| Total Telecom | https://www.totaltele.com/feed | 英文 |
| TechNews 科技新報 | https://technews.tw/feed/ | 中文 |

## 🎯 優先級邏輯

### 最高優先級
- **Ericsson 相關**：Ericsson、愛立信
- **台灣市場**：Taiwan、台灣、CHT、中華電、台灣大、遠傳、NCC
- **重大事件**：併購、破產、禁令

### 高優先級
- **RAN 技術**：Open RAN、vRAN、C-RAN、O-RAN
- **Core Network**：5G Core、Core Network、EPC
- **新技術**：6G、AI-RAN、Network Slicing、MEC、RedCap、NTN
- **商業動態**：財報、合作、併購

## 🚀 快速開始

### 1. Fork 專案

點擊右上角 Fork 按鈕，將專案 fork 到你的 GitHub 帳號。

### 2. 設定 GitHub Secrets

前往專案 Settings > Secrets and variables > Actions，新增以下 secrets：

| Secret 名稱 | 說明 | 範例 |
|-------------|------|------|
| `GEMINI_API_KEY` | Gemini API 金鑰 | `AIzaSy...` |
| `GMAIL_USER` | 發送郵件的 Gmail 帳號 | `your_email@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail 應用程式密碼 | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | 收件人 Email | `recipient@example.com` |

### 3. 取得 API 金鑰與密碼

#### Gemini API Key
1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點擊「Create API Key」
3. 複製 API Key

#### Gmail 應用程式密碼
1. 前往 [Google 帳號設定](https://myaccount.google.com/security)
2. 確認已啟用「兩步驟驗證」
3. 前往「安全性」>「兩步驟驗證」>「應用程式密碼」
4. 選擇「郵件」和「其他（自訂名稱）」
5. 輸入名稱（如：Telecom Digest）
6. 複製 16 位元密碼

### 4. 啟用 GitHub Actions

前往專案的 Actions 頁面，點擊「I understand my workflows, go ahead and enable them」。

### 5. 手動測試

1. 前往 Actions 頁面
2. 選擇「Daily Telecom News Digest」
3. 點擊「Run workflow」
4. 勾選「測試模式」進行測試

## 🗓️ 執行排程

| 任務 | 執行時間 | Cron 表達式 |
|------|----------|-------------|
| 每日摘要 | 台北時間 07:00 | `0 23 * * *` (UTC) |

## 💻 本地開發

### 環境需求

- Python 3.11+
- pip

### 安裝步驟

```bash
# 複製專案
git clone https://github.com/your-username/telecom-digest.git
cd telecom-digest

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 .\venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env 填入實際值
```

### 本地測試

```bash
cd src

# 測試 RSS 抓取
python main.py --test-rss

# 測試 Gemini AI 排序
python main.py --test-gemini

# 測試完整流程（輸出 HTML，不發送郵件）
python main.py --test

# 執行每日摘要（會發送郵件）
python main.py

# 除錯模式
python main.py --debug
```

## 📁 專案結構

```
telecom-digest/
├── .github/
│   └── workflows/
│       └── daily.yml          # 每日執行工作流程
├── src/
│   ├── main.py               # 主程式入口
│   ├── config.py             # 設定檔與常數
│   ├── rss_fetcher.py        # RSS 抓取模組
│   ├── analyzer.py           # Gemini 分析模組
│   ├── email_sender.py       # Email 發送模組
│   └── html_template.py      # HTML 模板生成
├── output/                   # 測試輸出目錄
├── requirements.txt          # Python 依賴
├── .env.example             # 環境變數範例
├── .gitignore               # Git 忽略檔案
├── README.md                # 英文說明文件
└── README.zh-TW.md          # 中文說明文件
```

## 📧 郵件內容

每日摘要包含：
- 🎯 Ericsson 動態（如有）
- 🇹🇼 台灣市場（如有）
- 🔥 焦點新聞
- 📡 RAN & Core 技術
- 🚀 新技術與創新
- 💼 商業動態
- 📊 今日統計

## ⚠️ 錯誤處理

| 錯誤類型 | 處理方式 |
|----------|----------|
| RSS 單一來源失敗 | 記錄並繼續處理其他來源 |
| RSS 全部失敗 | 發送錯誤通知郵件 |
| Gemini API 失敗 | 使用關鍵字排序作為備援 |
| Email 發送失敗 | 記錄到 GitHub Actions logs |

## 🔧 自訂設定

### 修改 RSS 來源

編輯 `src/config.py` 中的 `RSS_FEEDS` 列表：

```python
RSS_FEEDS: List[RSSSource] = [
    RSSSource("Your Source", "https://your-rss-url.com/feed", "en"),
    # 新增更多來源...
]
```

### 修改優先級關鍵字

編輯 `src/config.py` 中的 `PRIORITY_KEYWORDS` 字典：

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

### 修改 AI 排序提示詞

編輯 `src/config.py` 中的 `GEMINI_RANKING_PROMPT` 來自訂排序規則。

### 修改執行時間

編輯 `.github/workflows/daily.yml` 中的 cron 表達式：

```yaml
schedule:
  - cron: '0 23 * * *'  # 修改為你需要的時間（UTC）
```

## 📝 注意事項

1. **Gemini API 額度**：免費版有速率限制，輕量化方案可最大化使用效益
2. **Gmail 安全性**：必須使用應用程式密碼（非一般密碼）
3. **時區轉換**：GitHub Actions 使用 UTC 時區，請相應調整 cron
4. **新聞去重**：使用 URL hash 避免重複新聞

## 📄 授權

MIT License
