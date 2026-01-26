#!/usr/bin/env python3
"""
電信產業自動摘要系統 - 主程式入口
"""
import argparse
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional

from dotenv import load_dotenv

from config import (
    AppConfig,
    MAX_NEWS_DAILY,
    NEWS_LOOKBACK_HOURS,
    EMAIL_SUBJECT_DAILY,
)
from rss_fetcher import RSSFetcher, format_news_for_gemini
from analyzer import GeminiAnalyzer, create_fallback_analysis
from email_sender import create_email_sender
from html_template import (
    generate_daily_email_html,
    generate_error_email_html,
)


# 設定日誌
def setup_logging(debug: bool = False):
    """設定日誌系統"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


logger = logging.getLogger(__name__)


def get_taiwan_time() -> datetime:
    """取得台灣時間"""
    utc_now = datetime.now(timezone.utc)
    taiwan_tz = timezone(timedelta(hours=8))
    return utc_now.astimezone(taiwan_tz)


def format_date_taiwan(dt: Optional[datetime] = None) -> str:
    """格式化台灣日期"""
    if dt is None:
        dt = get_taiwan_time()
    return dt.strftime("%Y年%m月%d日 (%a)")


def run_daily_digest(config: AppConfig, test_mode: bool = False) -> bool:
    """
    執行每日摘要

    Args:
        config: 應用程式設定
        test_mode: 測試模式

    Returns:
        bool: 是否成功
    """
    logger.info("=" * 60)
    logger.info("Starting Daily Digest")
    logger.info("=" * 60)

    date_str = format_date_taiwan()
    errors = []

    try:
        # Step 1: 抓取 RSS
        logger.info("Step 1: Fetching RSS feeds...")
        fetcher = RSSFetcher(lookback_hours=NEWS_LOOKBACK_HOURS)
        news_items, fetch_errors = fetcher.fetch_and_prioritize(max_items=MAX_NEWS_DAILY)

        if fetch_errors:
            errors.extend(fetch_errors)
            logger.warning(f"RSS fetch errors: {len(fetch_errors)}")

        if not news_items:
            error_msg = "No news items fetched from any source"
            logger.error(error_msg)

            # 發送錯誤通知
            if not test_mode:
                send_error_notification(config, "RSS 抓取失敗", error_msg)
            return False

        logger.info(f"Fetched {len(news_items)} news items")

        # Step 2: 直接使用 fallback 分析（不依賴 Gemini API）
        logger.info("Step 2: Creating news summary...")
        result = create_fallback_analysis(news_items)
        logger.info(f"Analysis complete: {len(result.news_items)} items processed")

        # Step 3: 生成 HTML
        logger.info("Step 3: Generating HTML email...")
        html_content = generate_daily_email_html(result, date_str)

        # 測試模式：儲存 HTML 到檔案
        if test_mode:
            output_file = f"output/daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            os.makedirs("output", exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Test mode: HTML saved to {output_file}")
            return True

        # Step 4: 發送 Email
        logger.info("Step 4: Sending email...")
        sender = create_email_sender(config.gmail_user, config.gmail_app_password)

        subject = EMAIL_SUBJECT_DAILY.format(date=date_str)
        email_result = sender.send(
            to=config.recipient_email,
            subject=subject,
            html_content=html_content,
        )

        if not email_result.success:
            logger.error(f"Failed to send email: {email_result.message}")
            return False

        logger.info("✅ Daily digest sent successfully!")
        return True

    except Exception as e:
        error_msg = f"Unexpected error in daily digest: {e}"
        logger.exception(error_msg)

        if not test_mode:
            send_error_notification(config, "系統錯誤", error_msg)

        return False


def send_error_notification(config: AppConfig, error_type: str, error_details: str):
    """
    發送錯誤通知郵件

    Args:
        config: 應用程式設定
        error_type: 錯誤類型
        error_details: 錯誤詳細資訊
    """
    try:
        timestamp = get_taiwan_time().strftime("%Y-%m-%d %H:%M:%S (台北時間)")
        github_url = os.getenv("GITHUB_SERVER_URL", "")
        if github_url:
            repo = os.getenv("GITHUB_REPOSITORY", "")
            run_id = os.getenv("GITHUB_RUN_ID", "")
            github_url = f"{github_url}/{repo}/actions/runs/{run_id}"

        html_content = generate_error_email_html(
            error_type=error_type,
            error_details=error_details,
            timestamp=timestamp,
            github_url=github_url,
        )

        sender = create_email_sender(config.gmail_user, config.gmail_app_password)
        sender.send(
            to=config.recipient_email,
            subject=f"⚠️ 電信日報系統錯誤 - {error_type}",
            html_content=html_content,
        )

        logger.info("Error notification sent")

    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")


def test_rss_only():
    """僅測試 RSS 抓取"""
    logger.info("Testing RSS fetch only...")

    fetcher = RSSFetcher(lookback_hours=48)
    news_items, errors = fetcher.fetch_and_prioritize(max_items=10)

    print(f"\n{'=' * 60}")
    print(f"Fetched {len(news_items)} news items")
    print(f"{'=' * 60}\n")

    for i, item in enumerate(news_items[:5], 1):
        print(f"[{i}] {item['title'][:70]}...")
        print(f"    Source: {item['source']}")
        print(f"    Priority: {item['preliminary_priority']}")
        print(f"    Category: {item['preliminary_category']}")
        print()

    if errors:
        print(f"\n{'=' * 60}")
        print("Errors:")
        for error in errors:
            print(f"  - {error}")


def test_gemini_only(api_key: str):
    """僅測試 Gemini 分析"""
    logger.info("Testing Gemini analysis only...")

    # 先抓取新聞
    fetcher = RSSFetcher(lookback_hours=48)
    news_items, _ = fetcher.fetch_and_prioritize(max_items=5)

    if not news_items:
        print("No news items to analyze")
        return

    # 分析
    news_content = format_news_for_gemini(news_items)
    analyzer = GeminiAnalyzer(api_key)
    result = analyzer.analyze_daily(news_content)

    print(f"\n{'=' * 60}")
    print(f"Analysis Success: {result.success}")
    print(f"{'=' * 60}\n")

    if result.success:
        print(f"Analyzed {len(result.news_items)} items\n")

        for item in result.news_items[:3]:
            print(f"📰 {item.title_zh}")
            print(f"   Category: {item.category}")
            print(f"   Priority: {item.priority}")
            print(f"   Badges: {item.badges}")
            print()

        print(f"\n📊 Daily Trends:\n{result.daily_trends}")
    else:
        print(f"Error: {result.error_message}")


def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(
        description="電信產業自動摘要系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python main.py                      # 執行每日摘要
  python main.py --test               # 測試模式（不發送郵件）
  python main.py --test-rss           # 僅測試 RSS 抓取
  python main.py --test-gemini        # 僅測試 Gemini 分析
        """
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="測試模式（生成 HTML 但不發送郵件）"
    )
    parser.add_argument(
        "--test-rss",
        action="store_true",
        help="僅測試 RSS 抓取功能"
    )
    parser.add_argument(
        "--test-gemini",
        action="store_true",
        help="僅測試 Gemini 分析功能"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="啟用除錯模式"
    )

    args = parser.parse_args()

    # 載入環境變數
    load_dotenv()

    # 設定日誌
    setup_logging(debug=args.debug)

    # 處理測試命令
    if args.test_rss:
        test_rss_only()
        return

    if args.test_gemini:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not set")
            sys.exit(1)
        test_gemini_only(api_key)
        return

    # 載入設定
    try:
        config = AppConfig()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # 執行每日摘要
    success = run_daily_digest(config, test_mode=args.test)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
