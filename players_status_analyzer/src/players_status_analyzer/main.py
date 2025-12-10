#!/usr/bin/env python
import sys
import warnings
import json
from pathlib import Path
from datetime import datetime
from .crew import PlayersStatusAnalyzer
from players_status_analyzer.get_sport5_starters import get_starters
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv("SPORT5_EMAIL", "")
PASSWORD = os.getenv("SPORT5_PASSWORD", "")
MYTEAM_URL = os.getenv(
    "SPORT5_URL", "https://fantasyleague.sport5.co.il/my-team"
)

URL = "https://fantasyleague.sport5.co.il/my-team"

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run_for_a_single_user(player_name: str) -> dict:
    """Run the crew for a single player and RETURN a dict instead of printing."""
    print(f"Running for player: {player_name}")
    inputs = {
        "player_name": player_name,
        "current_date": datetime.now().astimezone().date().isoformat(),
    }

    try:
        res = PlayersStatusAnalyzer().crew().kickoff(inputs=inputs)

        # Convert Pydantic model / result object to a plain dict
        if hasattr(res, "model_dump"):          # Pydantic v2
            data = res.model_dump()
        elif hasattr(res, "dict"):              # Pydantic v1
            data = res.dict()
        else:
            data = dict(res)

        # Make sure we know which player this belongs to
        data["player_name"] = player_name

        # Optional: small summary line to console
        print(f"  -> {player_name}: {data.get('status')}")

        return data

    except Exception as e:
        print(f"Error for {player_name}: {e}", file=sys.stderr)
        # Return an error record so you still see something in the file
        return {
            "player_name": player_name,
            "status": "error",
            "reason": str(e),
            "sources": [],
            "as_of": datetime.now().astimezone().isoformat(),
        }


def run():
    """
    Run the crew for all starters and write results to a JSON file.
    """
    players = get_starters(url=URL, email=EMAIL,
                           password=PASSWORD, headless=False)

    results = []
    for player in players:
        result = run_for_a_single_user(player)
        results.append(result)

    # Build filename with timestamp so you don’t overwrite previous runs
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    output_path = Path(f"ucl_player_status_{timestamp}.json")

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(results)} player statuses to {output_path}")


if __name__ == "__main__":
    run()
