from playwright.sync_api import sync_playwright
import os
import sys
import time
import re
import json
from typing import List, Optional
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # show the browser
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    # 1) Click the "התחברות" link
    page.click('a[href="/login"].btn.btn-xl.btn-light.rounded-pill.w-100')
    page.wait_for_url("**/login*")
    page.wait_for_timeout(5000)

    # 2) Click the "כניסה באמצעות אימייל" button
    # Most robust: by role + accessible name (Hebrew)
    page.get_by_role("button", name="כניסה באמצעות אימייל").click()
    page.wait_for_timeout(3000)
    try:
        page.get_by_role("textbox", name="דוא״ל").fill(EMAIL)
    except Exception:
        # Fallback (direct attributes):
        page.fill('input[type="email"][name="email"]', EMAIL)
    try:
        page.get_by_label("סיסמה").fill(PASSWORD)  # uses aria-label
    except Exception:
        page.fill('input[type="password"][name="password"]', PASSWORD)

    page.get_by_role("button", name="התחבר").click()

    # Optional: wait for the post-login page (likely back to /my-team)
    page.wait_for_url("**/my-team*", timeout=15000)

    name_nodes = page.locator(".players-row .player-name p")
    names = [t.strip() for t in name_nodes.all_text_contents() if t.strip()]

    print("Players:")
    for n in names:
        print("-", n)

    # Optional: give you a moment to see the result
    page.wait_for_timeout(5000)
    browser.close()
