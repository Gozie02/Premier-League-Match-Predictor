# src/common/fbref_fixtures.py

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Tuple

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Internal: async HTML fetch via Playwright
# ---------------------------------------------------------
async def _fetch_fixtures_html(url: str) -> str:
    """
    Fetch the fixtures page HTML using Playwright.
    Handles Cloudflare / JS and returns the rendered HTML as a string.
    """
    logger.info(f"[fixtures] Fetching page: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Safari/537.36"
            )
        )

        try:
            # domcontentloaded is usually enough for FBRef tables
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        except TimeoutError as e:  # PlaywrightTimeoutError alias if you prefer
            logger.warning(f"[fixtures] Timeout loading {url}: {e}. Using partial HTML.")
        except Exception as e:
            logger.error(f"[fixtures] Error navigating to {url}: {e}")
            await browser.close()
            return ""

        html = await page.content()
        await browser.close()
        return html


# ---------------------------------------------------------
# Core async fixture logic: 7 days, then 14, then stop
# ---------------------------------------------------------
async def async_get_upcoming_fixtures(
    league_url: str,
) -> List[Tuple[datetime.date, str, str]]:
    """
    Async: fetch upcoming fixtures from FBRef for a given league.

    Behaviour:
    - First tries fixtures in the next 7 days.
    - If none, expands to 14 days (international break, etc.).
    - If still none, returns [] (off-season / long break).

    Returns list of (date, home, away).
    """
    html = await _fetch_fixtures_html(league_url)
    if not html:
        logger.error("[fixtures] Empty HTML received; returning no fixtures.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": lambda v: v and v.startswith("sched")})
    if not table:
        logger.error("[fixtures] Could not find fixtures table on page.")
        return []

    tbody = table.find("tbody")
    if not tbody:
        logger.error("[fixtures] Fixtures table has no <tbody>.")
        return []

    rows = tbody.find_all("tr")
    all_future_unplayed: List[Tuple[datetime.date, str, str]] = []

    today = datetime.today().date()

    # First collect ALL future, unplayed fixtures
    for row in rows:
        date_cell = row.find("td", {"data-stat": "date"})
        if not date_cell or not date_cell.text.strip():
            continue

        raw_date = date_cell.text.strip()
        match_date = None
        for fmt in ("%Y-%m-%d", "%b %d %Y"):  # FBRef formats
            try:
                match_date = datetime.strptime(raw_date, fmt).date()
                break
            except ValueError:
                continue
        if not match_date:
            continue

        # Skip past matches
        if match_date < today:
            continue

        # Skip already played matches (score cell populated)
        score_cell = row.find("td", {"data-stat": "score"})
        if score_cell and score_cell.text.strip():
            continue

        home_cell = row.find("td", {"data-stat": "home_team"})
        away_cell = row.find("td", {"data-stat": "away_team"})
        if not home_cell or not away_cell:
            continue

        home = home_cell.text.strip()
        away = away_cell.text.strip()
        all_future_unplayed.append((match_date, home, away))

    if not all_future_unplayed:
        logger.warning("[fixtures] No future unplayed fixtures found at all.")
        return []

    # Horizon 1: next 7 days
    horizon_7 = today + timedelta(days=7)
    fixtures_7 = [
        (d, h, a) for (d, h, a) in all_future_unplayed if today <= d <= horizon_7
    ]

    if fixtures_7:
        logger.info(f"[fixtures] Found {len(fixtures_7)} fixtures within 7 days.")
        return fixtures_7

    # Horizon 2: next 14 days
    horizon_14 = today + timedelta(days=14)
    fixtures_14 = [
        (d, h, a) for (d, h, a) in all_future_unplayed if today <= d <= horizon_14
    ]

    if fixtures_14:
        logger.info(
            "[fixtures] No fixtures within 7 days. "
            f"Found {len(fixtures_14)} fixtures within 14 days (likely international break)."
        )
        return fixtures_14

    # Beyond 14 days, assume off-season / long break
    logger.warning(
        "[fixtures] No fixtures within 14 days — likely off-season or extended break."
    )
    return []


# ---------------------------------------------------------
# Sync wrapper (for batch_predict, GitHub Actions, CLI)
# ---------------------------------------------------------
def get_upcoming_fixtures(league_url: str) -> List[Tuple[datetime.date, str, str]]:
    """
    Synchronous wrapper for async_get_upcoming_fixtures.

    Usage from normal scripts:
        fixtures = get_upcoming_fixtures(league_url)
    """
    return asyncio.run(async_get_upcoming_fixtures(league_url))

