"""
電信產業自動摘要系統 - Gemini 分析模組
"""
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import google.generativeai as genai

from config import (
    GEMINI_MODEL,
    GEMINI_MAX_RETRIES,
    GEMINI_RETRY_DELAY,
    GEMINI_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


@dataclass
class AnalyzedNews:
    """分析後的新聞項目"""
    title_zh: str
    title_en: str
    summary_zh: str
    key_quote: str
    source: str
    url: str
    tags: List[str]
    badges: List[str]
    category: str
    priority: int

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "title_zh": self.title_zh,
            "title_en": self.title_en,
            "summary_zh": self.summary_zh,
            "key_quote": self.key_quote,
            "source": self.source,
            "url": self.url,
            "tags": self.tags,
            "badges": self.badges,
            "category": self.category,
            "priority": self.priority,
        }


@dataclass
class AnalysisResult:
    """Gemini 分析結果"""
    success: bool
    news_items: List[AnalyzedNews] = field(default_factory=list)
    daily_trends: str = ""
    statistics: Dict = field(default_factory=dict)
    error_message: str = ""
    raw_response: str = ""


class GeminiAnalyzer:
    """Gemini API 分析器"""

    def __init__(self, api_key: str):
        """
        初始化 Gemini 分析器

        Args:
            api_key: Gemini API 金鑰
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"Initialized Gemini analyzer with model: {GEMINI_MODEL}")

    def _extract_json(self, text: str) -> Optional[Dict]:
        """
        從回應文字中提取 JSON

        Args:
            text: Gemini 回應文字

        Returns:
            Optional[Dict]: 解析後的 JSON 物件，失敗則為 None
        """
        # 嘗試找到 JSON 區塊
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # 直接的 JSON 物件
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # 清理可能的問題字元
                    cleaned = match.strip()
                    if not cleaned.startswith('{'):
                        continue
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    continue

        return None

    def _validate_news_item(self, item: Dict) -> bool:
        """驗證新聞項目是否完整"""
        required_fields = ['title_zh', 'title_en', 'summary_zh', 'source', 'url', 'category', 'priority']
        return all(field in item for field in required_fields)

    def _normalize_category(self, category: str) -> str:
        """正規化類別名稱"""
        valid_categories = ['ericsson', 'ran', 'core', 'tech', 'business', 'taiwan', 'other']
        category = category.lower().strip()
        return category if category in valid_categories else 'other'

    def _normalize_badges(self, badges: List[str]) -> List[str]:
        """正規化標籤"""
        valid_badges = ['Ericsson', 'Taiwan', 'RAN', 'Core', 'Tech', 'Business', 'Partnership', 'M&A']
        normalized = []
        for badge in badges:
            # 找到最接近的有效標籤
            for valid in valid_badges:
                if badge.lower() == valid.lower():
                    normalized.append(valid)
                    break
        return list(set(normalized))[:4]  # 最多 4 個標籤

    def analyze_daily(self, news_content: str) -> AnalysisResult:
        """
        分析每日新聞

        Args:
            news_content: 格式化的新聞內容

        Returns:
            AnalysisResult: 分析結果
        """
        prompt = GEMINI_PROMPT_TEMPLATE.format(news_content=news_content)

        for attempt in range(GEMINI_MAX_RETRIES):
            try:
                logger.info(f"Calling Gemini API (attempt {attempt + 1}/{GEMINI_MAX_RETRIES})")

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=8192,
                    )
                )

                if not response.text:
                    raise ValueError("Empty response from Gemini")

                # 提取 JSON
                result_json = self._extract_json(response.text)
                if not result_json:
                    raise ValueError("Could not extract JSON from response")

                # 解析新聞項目
                news_items = []
                for item in result_json.get('news_items', []):
                    if not self._validate_news_item(item):
                        logger.warning(f"Skipping invalid news item: {item.get('title_en', 'Unknown')}")
                        continue

                    news_items.append(AnalyzedNews(
                        title_zh=item.get('title_zh', ''),
                        title_en=item.get('title_en', ''),
                        summary_zh=item.get('summary_zh', ''),
                        key_quote=item.get('key_quote', ''),
                        source=item.get('source', ''),
                        url=item.get('url', ''),
                        tags=item.get('tags', [])[:5],
                        badges=self._normalize_badges(item.get('badges', [])),
                        category=self._normalize_category(item.get('category', 'other')),
                        priority=min(100, max(0, int(item.get('priority', 50)))),
                    ))

                # 按優先級排序
                news_items.sort(key=lambda x: x.priority, reverse=True)

                logger.info(f"Successfully analyzed {len(news_items)} news items")

                return AnalysisResult(
                    success=True,
                    news_items=news_items,
                    daily_trends=result_json.get('daily_trends', ''),
                    statistics=result_json.get('statistics', {}),
                    raw_response=response.text,
                )

            except Exception as e:
                error_msg = f"Gemini API error (attempt {attempt + 1}): {e}"
                logger.error(error_msg)

                if attempt < GEMINI_MAX_RETRIES - 1:
                    logger.info(f"Retrying in {GEMINI_RETRY_DELAY} seconds...")
                    time.sleep(GEMINI_RETRY_DELAY)
                else:
                    return AnalysisResult(
                        success=False,
                        error_message=error_msg,
                    )

        return AnalysisResult(
            success=False,
            error_message="Max retries exceeded",
        )


def create_fallback_analysis(news_items: List[Dict]) -> AnalysisResult:
    """
    建立備用分析結果（當 Gemini API 失敗時使用）

    Args:
        news_items: 原始新聞列表

    Returns:
        AnalysisResult: 備用分析結果
    """
    analyzed_items = []

    for item in news_items:
        analyzed_items.append(AnalyzedNews(
            title_zh=item.get('title', ''),
            title_en=item.get('title', ''),
            summary_zh=item.get('description', '')[:150],
            key_quote='',
            source=item.get('source', ''),
            url=item.get('link', ''),
            tags=[],
            badges=[],
            category=item.get('preliminary_category', 'other'),
            priority=item.get('preliminary_priority', 50),
        ))

    # 計算統計
    stats = {
        "total": len(analyzed_items),
        "by_category": {},
        "by_source": {},
    }

    for item in analyzed_items:
        stats["by_category"][item.category] = stats["by_category"].get(item.category, 0) + 1
        stats["by_source"][item.source] = stats["by_source"].get(item.source, 0) + 1

    return AnalysisResult(
        success=True,
        news_items=analyzed_items,
        daily_trends="（Gemini API 暫時無法使用，此為自動產生的備用內容）",
        statistics=stats,
    )


if __name__ == "__main__":
    # 測試用
    import os
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not set")
        exit(1)

    # 測試分析
    analyzer = GeminiAnalyzer(api_key)

    test_content = """
---
【新聞 1】
標題: Ericsson wins 5G contract with major European operator
來源: Light Reading
語言: en
發布時間: 2024-01-15T10:00:00+00:00
連結: https://example.com/news1
摘要: Ericsson has announced a major 5G contract win with a leading European telecom operator, valued at approximately $500 million over five years.
---

---
【新聞 2】
標題: Open RAN deployment challenges remain despite progress
來源: RCR Wireless News
語言: en
發布時間: 2024-01-15T09:00:00+00:00
連結: https://example.com/news2
摘要: Industry experts discuss the ongoing challenges in Open RAN deployment, including integration complexity and performance optimization.
---
"""

    result = analyzer.analyze_daily(test_content)

    if result.success:
        print(f"\n=== Analysis Result ===")
        print(f"News items: {len(result.news_items)}")
        print(f"Daily trends: {result.daily_trends}")
        print(f"\nTop news:")
        for item in result.news_items[:3]:
            print(f"  [{item.priority}] {item.title_zh}")
            print(f"      Category: {item.category}, Badges: {item.badges}")
    else:
        print(f"Analysis failed: {result.error_message}")
