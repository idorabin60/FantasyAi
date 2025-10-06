#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from players_status_analyzer.crew import PlayersStatusAnalyzer
from players_status_analyzer.get_sport5_starters import get_starters
from dotenv import load_dotenv
import os


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


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run_for_a_single_user(player_name):
    """Run the crew for a single player"""
    inputs = {
        'player_name': player_name,
        "current_date": datetime.now().astimezone().date().isoformat()
    }
    try:
        res = PlayersStatusAnalyzer().crew().kickoff(inputs=inputs)
        print(res)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def run():
    """
    Run the crew.
    """
    players = get_starters(
        url=URL, email=EMAIL, password=PASSWORD, headless=True)
    for player in players:
        run_for_a_single_user(player)
