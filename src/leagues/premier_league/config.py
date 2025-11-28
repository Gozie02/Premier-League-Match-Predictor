# src/leagues/premier_league/config.py

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LeagueConfig:
    code: str
    name: str
    fbref_history_url: str         # standings/history page (for async scraper)
    fbref_fixtures_url: str        # schedule URL (for batch predictions)
    processed_dir: Path            # base folder for processed data
    elo_csv: Path                  # ELO_df.csv path
    upcoming_predictions_csv: Path # upcoming_predictions.csv path
    core_module: str               # dotted path to module defining predict_match


# Resolve repo root assuming:
# repo_root/src/leagues/premier_league/config.py
BASE_DIR = Path(__file__).resolve().parents[3]

PROCESSED_DIR = BASE_DIR / "data" / "premier_league" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

PREMIER_LEAGUE_CONFIG = LeagueConfig(
    code="premier_league",
    name="Premier League",
    fbref_history_url="https://fbref.com/en/comps/9/Premier-League-Stats",
    fbref_fixtures_url="https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
    processed_dir=PROCESSED_DIR,
    elo_csv=PROCESSED_DIR / "ELO_df.csv",
    upcoming_predictions_csv=PROCESSED_DIR / "upcoming_predictions.csv",
    core_module="src.leagues.premier_league.core",  # where predict_match will live
)

