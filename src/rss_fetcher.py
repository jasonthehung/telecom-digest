"""
電信產業自動摘要系統 - RSS 抓取模組
"""
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Tuple
from time import mktime

import feedparser
import requests

from config import RSS_FEEDS, RSSSource, HTTP_HEADERS, PRIORITY_KEYWORDS, CATEGORY_MAPPING, TELECOM_REQUIRED_KEYWORDS

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """新聞項目資料結構"""
    title: str
    link: str
    description: str
    published: datetime
    source: str
    source_language: str = "en"
    url_hash: str = ""

    def __post_init__(self):
        """計算 URL hash 用於去重"""
        if not self.url_hash:
            self.url_hash = hashlib.md5(self.link.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "published": self.published.isoformat(),
            "source": self.source,
            "source_language": self.source_language,
            "url_hash": self.url_hash,
        }


@dataclass
class FetchResult:
    """RSS 抓取結果"""
    source: str
    success: bool
    news_items: List[NewsItem] = field(default_factory=list)
    error_message: str = ""
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RSSFetcher:
    """RSS 新聞抓取器"""

    def __init__(self, lookback_hours: int = 24):
        """
        初始化 RSS 抓取器

        Args:
            lookback_hours: 抓取過去多少小時的新聞
        """
        self.lookback_hours = lookback_hours
        self.seen_hashes: set = set()

    def _parse_custom_date(self, date_str: str) -> Optional[datetime]:
        """嘗試解析自定義日期格式"""
        from dateutil import parser as dateutil_parser

        try:
            # dateutil 可以解析大部分日期格式，包括 "Jan 23, 2026 4:04pm"
            dt = dateutil_parser.parse(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError):
            pass

        # 備用: 手動解析常見格式
        custom_formats = [
            "%b %d, %Y %I:%M%p",     # "Jan 23, 2026 4:04pm"
            "%b %d, %Y %I:%M %p",    # "Jan 23, 2026 4:04 PM"
            "%Y-%m-%d %H:%M:%S",     # ISO 格式
            "%d %b %Y %H:%M:%S",     # "23 Jan 2026 12:00:00"
        ]

        for fmt in custom_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        return None

    def _parse_published_date(self, entry: dict) -> Optional[datetime]:
        """解析發布日期"""
        # 嘗試多種日期欄位
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field_name in date_fields:
            if hasattr(entry, field_name) and getattr(entry, field_name):
                try:
                    parsed = getattr(entry, field_name)
                    dt = datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
                    return dt
                except (TypeError, ValueError, OverflowError):
                    continue

        # 新增: 嘗試解析原始日期字串
        raw_date_fields = ['published', 'updated', 'created']
        for field_name in raw_date_fields:
            raw_date = entry.get(field_name)
            if raw_date:
                parsed_dt = self._parse_custom_date(raw_date)
                if parsed_dt:
                    return parsed_dt

        # 如果沒有日期，返回 None 而不是假設是今天
        return None

    def _clean_html(self, text: str) -> str:
        """清理 HTML 標籤"""
        import re
        # 移除 HTML 標籤
        clean = re.sub(r'<[^>]+>', '', text)
        # 處理 HTML 實體
        clean = clean.replace('&nbsp;', ' ')
        clean = clean.replace('&amp;', '&')
        clean = clean.replace('&lt;', '<')
        clean = clean.replace('&gt;', '>')
        clean = clean.replace('&quot;', '"')
        clean = clean.replace('&#39;', "'")
        # 清理多餘空白
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    def _calculate_preliminary_priority(self, title: str, description: str) -> Tuple[int, str]:
        """
        計算初步優先級分數（用於預過濾）

        Returns:
            Tuple[int, str]: (優先級分數, 主要類別)
        """
        text = f"{title} {description}".lower()
        max_priority = 0
        main_category = "other"

        # 檢查最高優先級關鍵字
        for category, keywords in PRIORITY_KEYWORDS.get("highest", {}).items():
            for keyword in keywords:
                if keyword.lower() in text:
                    priority = 90
                    if priority > max_priority:
                        max_priority = priority
                        main_category = CATEGORY_MAPPING.get(category, "other")

        # 檢查高優先級關鍵字
        for category, keywords in PRIORITY_KEYWORDS.get("high", {}).items():
            for keyword in keywords:
                if keyword.lower() in text:
                    priority = 70
                    if priority > max_priority:
                        max_priority = priority
                        main_category = CATEGORY_MAPPING.get(category, "other")

        # 如果沒有匹配任何關鍵字，給予基礎分數
        if max_priority == 0:
            max_priority = 40

        return max_priority, main_category

    def _is_telecom_related(self, title: str, description: str) -> bool:
        """
        檢查新聞是否與電信相關

        Args:
            title: 新聞標題
            description: 新聞描述

        Returns:
            bool: 是否與電信相關
        """
        text = f"{title} {description}".lower()

        for keyword in TELECOM_REQUIRED_KEYWORDS:
            if keyword.lower() in text:
                return True

        return False

    def fetch_feed(self, source: RSSSource) -> FetchResult:
        """
        抓取單一 RSS Feed

        Args:
            source: RSS 來源設定

        Returns:
            FetchResult: 抓取結果
        """
        logger.info(f"Fetching RSS feed: {source.name} ({source.url})")

        try:
            # 使用 requests 先取得內容（處理特殊 headers）
            response = requests.get(
                source.url,
                headers=HTTP_HEADERS,
                timeout=30
            )
            response.raise_for_status()

            # 使用 feedparser 解析
            feed = feedparser.parse(response.content)

            if feed.bozo and not feed.entries:
                raise ValueError(f"Feed parsing error: {feed.bozo_exception}")

            # 計算時間範圍
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)

            news_items = []
            for entry in feed.entries:
                try:
                    # 解析發布日期
                    published = self._parse_published_date(entry)

                    # 如果無法解析日期，跳過這條新聞（比假設是今天更安全）
                    if published is None:
                        logger.warning(f"Skipping entry with unparsable date: {entry.get('title', 'unknown')[:50]}")
                        continue

                    # 檢查是否在時間範圍內
                    if published < cutoff_time:
                        continue

                    # 取得標題和描述
                    title = self._clean_html(entry.get('title', ''))
                    description = self._clean_html(
                        entry.get('description', '') or
                        entry.get('summary', '') or
                        ''
                    )
                    link = entry.get('link', '')

                    if not title or not link:
                        continue

                    # 建立新聞項目
                    news_item = NewsItem(
                        title=title,
                        link=link,
                        description=description[:500],  # 限制描述長度
                        published=published,
                        source=source.name,
                        source_language=source.language,
                    )

                    # 去重檢查
                    if news_item.url_hash not in self.seen_hashes:
                        self.seen_hashes.add(news_item.url_hash)
                        news_items.append(news_item)

                except Exception as e:
                    logger.warning(f"Error parsing entry from {source.name}: {e}")
                    continue

            logger.info(f"Fetched {len(news_items)} news items from {source.name}")

            return FetchResult(
                source=source.name,
                success=True,
                news_items=news_items,
            )

        except requests.RequestException as e:
            error_msg = f"Network error fetching {source.name}: {e}"
            logger.error(error_msg)
            return FetchResult(
                source=source.name,
                success=False,
                error_message=error_msg,
            )
        except Exception as e:
            error_msg = f"Error fetching {source.name}: {e}"
            logger.error(error_msg)
            return FetchResult(
                source=source.name,
                success=False,
                error_message=error_msg,
            )

    def fetch_all(self) -> Tuple[List[NewsItem], List[str]]:
        """
        抓取所有 RSS Feeds

        Returns:
            Tuple[List[NewsItem], List[str]]: (新聞列表, 錯誤訊息列表)
        """
        all_news: List[NewsItem] = []
        errors: List[str] = []

        for source in RSS_FEEDS:
            result = self.fetch_feed(source)

            if result.success:
                all_news.extend(result.news_items)
            else:
                errors.append(result.error_message)

        # 按發布時間排序（最新的在前）
        all_news.sort(key=lambda x: x.published, reverse=True)

        logger.info(f"Total fetched: {len(all_news)} news items, {len(errors)} errors")

        return all_news, errors

    def fetch_and_prioritize(self, max_items: int = 20) -> Tuple[List[Dict], List[str]]:
        """
        抓取並初步排序新聞

        Args:
            max_items: 最大新聞數量

        Returns:
            Tuple[List[Dict], List[str]]: (排序後的新聞列表, 錯誤訊息列表)
        """
        all_news, errors = self.fetch_all()

        # 計算初步優先級並轉換為字典
        news_with_priority = []
        for news in all_news:
            priority, category = self._calculate_preliminary_priority(
                news.title, news.description
            )
            news_dict = news.to_dict()
            news_dict['preliminary_priority'] = priority
            news_dict['preliminary_category'] = category
            news_with_priority.append(news_dict)

        # 按優先級排序
        news_with_priority.sort(key=lambda x: x['preliminary_priority'], reverse=True)

        # 限制數量
        selected_news = news_with_priority[:max_items]

        logger.info(f"Selected {len(selected_news)} news items for analysis")

        return selected_news, errors


def format_news_for_gemini(news_items: List[Dict]) -> str:
    """
    將新聞格式化為 Gemini 分析用的文字

    Args:
        news_items: 新聞列表

    Returns:
        str: 格式化的新聞文字
    """
    formatted = []

    for i, news in enumerate(news_items, 1):
        formatted.append(f"""
---
【新聞 {i}】
標題: {news['title']}
來源: {news['source']}
語言: {news['source_language']}
發布時間: {news['published']}
連結: {news['link']}
摘要: {news['description']}
---
""")

    return "\n".join(formatted)


def format_titles_for_ranking(news_items: List[Dict]) -> str:
    """
    只格式化標題給 AI 排序用（輕量化方案）

    Args:
        news_items: 新聞列表

    Returns:
        str: 格式化的標題列表
    """
    lines = []
    for i, news in enumerate(news_items):
        lines.append(f"[{i}] {news['title']}")
    return "\n".join(lines)


if __name__ == "__main__":
    # 測試用
    logging.basicConfig(level=logging.INFO)

    fetcher = RSSFetcher(lookback_hours=48)  # 測試時抓取 48 小時
    news, errors = fetcher.fetch_and_prioritize(max_items=10)

    print(f"\n=== Fetched {len(news)} news items ===\n")
    for item in news[:5]:
        print(f"[{item['preliminary_priority']}] {item['title'][:60]}...")
        print(f"    Source: {item['source']}")
        print(f"    Category: {item['preliminary_category']}")
        print()

    if errors:
        print(f"\n=== Errors ({len(errors)}) ===")
        for error in errors:
            print(f"  - {error}")
