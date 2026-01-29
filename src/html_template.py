"""
電信產業自動摘要系統 - HTML 模板生成模組
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from analyzer import AnalyzedNews, AnalysisResult


# Badge CSS 類別對應
BADGE_CLASS_MAP = {
    "Ericsson": ("badge-ericsson", "⭐ Ericsson"),
    "Taiwan": ("badge-taiwan", "🇹🇼 台灣"),
    "RAN": ("badge-ran", "📡 RAN"),
    "Core": ("badge-core", "🔧 Core"),
    "Tech": ("badge-tech", "🚀 新技術"),
    "Business": ("badge-business", "💼 商業"),
    "Partnership": ("badge-partner", "🤝 合作"),
    "M&A": ("badge-ma", "🔄 M&A"),
}

# 類別圖示
CATEGORY_ICONS = {
    "ericsson": "🎯",
    "ran": "📡",
    "core": "🔧",
    "tech": "🚀",
    "business": "💼",
    "taiwan": "🇹🇼",
    "other": "📌",
}

# 類別邊框顏色
CATEGORY_BORDER_COLORS = {
    "ericsson": "#dc2626",
    "ran": "#3b82f6",
    "core": "#2563eb",
    "tech": "#06b6d4",
    "business": "#10b981",
    "taiwan": "#ef4444",
    "other": "#667eea",
}


def generate_badge_html(badges: List[str]) -> str:
    """生成 badge HTML"""
    html_parts = []
    for badge in badges:
        if badge in BADGE_CLASS_MAP:
            css_class, label = BADGE_CLASS_MAP[badge]
            html_parts.append(f'<span class="badge {css_class}">{label}</span>')
    return "\n".join(html_parts)


def generate_news_card(news: AnalyzedNews, is_featured: bool = False) -> str:
    """
    生成新聞卡片 HTML

    Args:
        news: 分析後的新聞
        is_featured: 是否為焦點新聞

    Returns:
        str: 新聞卡片 HTML
    """
    border_color = CATEGORY_BORDER_COLORS.get(news.category, "#667eea")
    badges_html = generate_badge_html(news.badges)

    # 如果是焦點新聞，加上焦點標籤
    if is_featured and "🔥 焦點" not in badges_html:
        badges_html = '<span class="badge badge-hot">🔥 焦點</span>\n' + badges_html

    # 關鍵引述區塊
    quote_html = ""
    if news.key_quote:
        quote_html = f'''
        <div class="quote">
            <strong>💬 關鍵引述：</strong>
            <em>{news.key_quote}</em>
        </div>
        '''

    # 標籤
    tags_html = " · ".join(news.tags) if news.tags else ""

    return f'''
    <div class="news-card" style="border-left-color: {border_color};">
        <h2>{news.title_zh}</h2>

        <div class="summary">
            <strong>📝 摘要：</strong>{news.summary_zh}
        </div>

        {quote_html}

        <div class="metadata">
            <div><strong>🌐 原文標題：</strong>{news.title_en}</div>
            <div><strong>📰 來源：</strong>{news.source}</div>
        </div>

        <div class="footer">
            <div class="tags">{tags_html}</div>
            <a href="{news.url}" class="read-more">閱讀全文 →</a>
        </div>
    </div>
    '''


def generate_section(title: str, icon: str, news_items: List[AnalyzedNews], is_featured: bool = False) -> str:
    """生成新聞區塊"""
    if not news_items:
        return ""

    cards_html = "\n".join([generate_news_card(n, is_featured) for n in news_items])

    return f'''
    <div class="section">
        <div class="section-title">{icon} {title}</div>
        {cards_html}
    </div>
    '''


def generate_other_news_list(news_items: List[AnalyzedNews]) -> str:
    """生成其他新聞列表"""
    if not news_items:
        return ""

    items_html = "\n".join([
        f'<li><a href="{n.url}">{n.title_zh}</a> ({n.source})</li>'
        for n in news_items
    ])

    return f'''
    <div class="section">
        <div class="section-title">📌 其他值得關注</div>
        <ul class="other-news">
            {items_html}
        </ul>
    </div>
    '''


def generate_stats_section(statistics: Dict) -> str:
    """生成統計區塊"""
    total = statistics.get('total', 0)
    by_category = statistics.get('by_category', {})
    by_source = statistics.get('by_source', {})

    ericsson_count = by_category.get('ericsson', 0)
    ran_count = by_category.get('ran', 0) + by_category.get('core', 0)
    business_count = by_category.get('business', 0)

    # 來源分布
    source_items = "\n".join([
        f'<div style="display: flex; justify-content: space-between; margin: 5px 0;">'
        f'<span>{source}</span><span style="font-weight: bold;">{count}</span></div>'
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True)
    ])

    return f'''
    <div class="section">
        <div class="stats-box">
            <div class="section-title">📊 今日統計</div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">總新聞數</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{ericsson_count}</div>
                    <div class="stat-label">Ericsson 相關</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{ran_count}</div>
                    <div class="stat-label">RAN/Core</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{business_count}</div>
                    <div class="stat-label">商業動態</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e0e7ff;">
                <strong>📰 來源分布</strong>
                <div style="margin-top: 10px;">
                    {source_items}
                </div>
            </div>
        </div>
    </div>
    '''


def generate_daily_email_html(result: AnalysisResult, date_str: str) -> str:
    """
    生成每日郵件 HTML

    Args:
        result: 分析結果
        date_str: 日期字串

    Returns:
        str: 完整的 HTML 郵件內容
    """
    news_items = result.news_items

    # 直接生成所有新聞卡片（不分類）
    all_cards_html = "\n".join([generate_news_card(n) for n in news_items])

    sections_html = f'''
    <div class="section">
        <div class="section-title">📰 今日新聞 ({len(news_items)} 則)</div>
        {all_cards_html}
    </div>
    '''

    # 統計資訊
    stats_html = generate_stats_section(result.statistics)

    total_count = len(news_items)

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>電信產業日報 - {date_str}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }}

        .section {{
            padding: 20px;
            border-bottom: 1px solid #eee;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}

        .news-card {{
            background: #f8fafc;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #667eea;
            border: 1px solid #e2e8f0;
        }}

        .badges {{
            margin-bottom: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-right: 5px;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        .badge-ericsson {{ background: #dc2626; color: white; }}
        .badge-taiwan {{ background: #ef4444; color: white; }}
        .badge-hot {{ background: #f97316; color: white; }}
        .badge-ran {{ background: #3b82f6; color: white; }}
        .badge-core {{ background: #2563eb; color: white; }}
        .badge-tech {{ background: #06b6d4; color: white; }}
        .badge-business {{ background: #10b981; color: white; }}
        .badge-partner {{ background: #059669; color: white; }}
        .badge-ma {{ background: #047857; color: white; }}

        .news-card h2 {{
            margin: 10px 0;
            font-size: 18px;
            color: #1f2937;
            line-height: 1.4;
        }}

        .summary {{
            margin: 15px 0;
            line-height: 1.6;
            color: #4b5563;
        }}

        .quote {{
            margin: 15px 0;
            padding: 10px 15px;
            background: #f9fafb;
            border-left: 3px solid #667eea;
            font-style: italic;
            color: #6b7280;
        }}

        .metadata {{
            margin: 15px 0;
            font-size: 14px;
            color: #6b7280;
        }}
        .metadata div {{
            margin: 5px 0;
        }}

        .footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
        }}

        .tags {{
            font-size: 12px;
            color: #9ca3af;
        }}

        .read-more {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .read-more:hover {{
            text-decoration: underline;
        }}

        .trends-box {{
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }}

        .stats-box {{
            background: #f0f9ff;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 10px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            font-size: 12px;
            color: #6b7280;
            margin-top: 5px;
        }}

        .other-news {{
            padding: 10px 0;
            list-style: none;
            margin: 0;
            padding-left: 0;
        }}
        .other-news li {{
            margin: 10px 0;
            padding: 10px;
            background: #f9fafb;
            border-radius: 6px;
            color: #4b5563;
        }}
        .other-news li a {{
            color: #667eea;
            text-decoration: none;
        }}
        .other-news li a:hover {{
            text-decoration: underline;
        }}

        .email-footer {{
            text-align: center;
            padding: 20px;
            color: #9ca3af;
            font-size: 12px;
            background: #f9fafb;
        }}

        /* 響應式設計 */
        @media only screen and (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .header {{
                padding: 20px;
            }}
            .section {{
                padding: 15px;
            }}
            .news-card {{
                padding: 15px;
            }}
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📡 電信產業日報</h1>
            <p>{date_str} | 共 {total_count} 則新聞</p>
        </div>

        {sections_html}

        <!-- Footer -->
        <div class="email-footer">
            <p>此郵件由電信產業自動摘要系統自動發送</p>
            <p>Powered by Gemini AI | 資料來源：Light Reading, RCR Wireless News, Mobile World Live, DigiTimes</p>
        </div>
    </div>
</body>
</html>'''


def generate_error_email_html(error_type: str, error_details: str, timestamp: str, github_url: str = "") -> str:
    """
    生成錯誤通知郵件

    Args:
        error_type: 錯誤類型
        error_details: 錯誤詳細資訊
        timestamp: 時間戳
        github_url: GitHub Actions URL

    Returns:
        str: 錯誤郵件 HTML
    """
    github_link = f'<p><a href="{github_url}">查看完整 logs →</a></p>' if github_url else ""

    return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>電信日報系統錯誤通知</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            padding: 30px;
        }}
        .content {{
            padding: 30px;
        }}
        .error-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .error-type {{
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 10px;
        }}
        .error-details {{
            color: #7f1d1d;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #9ca3af;
            font-size: 12px;
            background: #f9fafb;
        }}
        a {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ 電信日報系統錯誤通知</h1>
            <p>執行時間：{timestamp}</p>
        </div>
        <div class="content">
            <div class="error-box">
                <div class="error-type">錯誤類型：{error_type}</div>
                <div class="error-details">{error_details}</div>
            </div>
            <p>系統將在下次排程時間重試。</p>
            {github_link}
        </div>
        <div class="footer">
            <p>此為自動發送的錯誤通知郵件</p>
        </div>
    </div>
</body>
</html>'''
