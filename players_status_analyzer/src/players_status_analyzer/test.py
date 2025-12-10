from playwright.sync_api import sync_playwright
import os
import sys
import time
import re
import json
from typing import List, Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from players_status_analyzer.trslate_players_name import translate_players
load_dotenv()
EMAIL = os.getenv("SPORT5_EMAIL", "")
PASSWORD = os.getenv("SPORT5_PASSWORD", "")
MYTEAM_URL = os.getenv(
    "SPORT5_URL", "https://fantasyleague.sport5.co.il/my-team")

# -------- helpers --------


URL = "https://fantasyleague.sport5.co.il/my-team"

# open_and_click_login.py

URL = "https://fantasyleague.sport5.co.il/my-team"

# open_click_login_and_email.py

URL = "https://fantasyleague.sport5.co.il/my-team"


def reverse_strings(items: list[str]) -> list[str]:
    return [s[::-1] for s in items]


def get_starters(url: str, email: str, password: str, headless: bool = True):
    def debug(tag: str):
        try:
            page.screenshot(path=f"debug_{tag}.png", full_page=True)
            print(f"[debug] saved debug_{tag}.png")
        except Exception as e:
            print(f"[debug] screenshot failed: {e}")

    with sync_playwright() as p:
        print(
            f"Launching browser in {'headless' if headless else 'headed'} mode")
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},     # force desktop layout
            locale="he-IL",
            timezone_id="Asia/Jerusalem",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.set_default_timeout(60_000)

        # --- Open page & settle ---
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")

        # --- Best-effort cookie/overlay dismiss ---
        for sel in [
            'button:has-text("אני מסכים")',
            'button:has-text("מאשר")',
            'button:has-text("Accept")',
            'button[aria-label="close"]',
            'button:has-text("סגור")',
        ]:
            try:
                page.locator(sel).first.click(timeout=1500)
            except Exception:
                pass

        # --- Click the login link (robust fallbacks) ---
        try:
            # 1) Accessible role + Hebrew/English names
            login = page.get_by_role("link", name=re.compile(
                "התחברות|התחבר|כניסה|Login|Sign in"))
            login.first.wait_for(state="visible", timeout=10_000)
            login.first.scroll_into_view_if_needed()
            login.first.click()
        except Exception:
            try:
                # 2) Direct href
                loc = page.locator('a[href="/login"]').first
                loc.wait_for(state="visible", timeout=10_000)
                loc.scroll_into_view_if_needed()
                loc.click()
            except Exception:
                try:
                    # 3) Text fallback
                    page.locator(
                        "a:has-text('התחברות'), a:has-text('התחבר'), a:has-text('כניסה')").first.click(timeout=10_000)
                except Exception:
                    # 4) If the menu is collapsed in headless, try opening a menu and retry once
                    try:
                        menu = page.get_by_role(
                            "button", name=re.compile("תפריט|Menu|המבורגר|פתיחה"))
                        menu.first.click(timeout=2000)
                        page.wait_for_timeout(500)
                        page.get_by_role("link", name=re.compile(
                            "התחברות|התחבר|כניסה|Login|Sign in")).first.click(timeout=5000)
                    except Exception:
                        debug("login_click_fail")
                        raise

        page.wait_for_url("**/login*", timeout=20_000)

        # --- Choose email login ---
        try:
            page.get_by_role("button", name=re.compile(
                "כניסה באמצעות אימייל|Login with Email|דוא״ל")).click(timeout=10_000)
        except Exception:
            # sometimes already on the email form
            pass

        # --- Fill credentials (robust labels/attrs) ---
        try:
            page.get_by_role("textbox", name=re.compile(
                "דוא״ל|Email")).fill(email)
        except Exception:
            page.locator(
                'input[type="email"], input[name="email"]').first.fill(email)

        try:
            page.get_by_label(re.compile("סיסמה|Password")).fill(password)
        except Exception:
            page.locator(
                'input[type="password"], input[name="password"]').first.fill(password)

        # --- Submit ---
        try:
            page.get_by_role("button", name=re.compile(
                "התחבר|כניסה|Login|Sign in")).click(timeout=10_000)
        except Exception:
            page.locator(
                "button:has-text('התחבר'), button:has-text('כניסה')").first.click(timeout=10_000)

        # --- Wait for post-login content ---
        try:
            page.goto("https://fantasyleague.sport5.co.il/user-team/118456")
        except PWTimeout:
            # Fallback: wait for a key element on the team page
            page.locator(
                ".players-row .player-name p").first.wait_for(state="visible", timeout=20_000)

        # --- Extract names ---
        name_nodes = page.locator(".players-row .player-name p")
        names = [t.strip()
                 for t in name_nodes.all_text_contents() if t.strip()]
        page.wait_for_timeout(1000)
        browser.close()
        return translate_players(names)


players = get_starters(
    url=URL, email=EMAIL, password=PASSWORD, headless=False)
