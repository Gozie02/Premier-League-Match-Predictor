from dataclasses import dataclass
from pathlib import Path


@dataclass
class LeagueConfig:
    code: str
    name: str
    fbref_history_url: str          # standings/history page (async scraper)
    fbref_fixtures_url: str         # schedule URL (fixtures)
    processed_dir: Path             # base folder for processed data
    elo_csv: Path                   # match-level processed data (ELO_df.csv)
    upcoming_predictions_csv: Path  # next fixtures predictions
    models_dir: Path                # folder holding model artifacts
    outcome_model_path: Path        # 3-way classifier (H/D/A)
    score_model_path: Path          # optional goals model
    core_module: str                # dotted path to this league's core module


# repo_root/src/leagues/premier_league/config.py  -> repo_root
BASE_DIR = Path(__file__).resolve().parents[3]

PROCESSED_DIR = BASE_DIR / "data" / "premier_league" / "processed"
MODELS_DIR = BASE_DIR / "data" / "premier_league" / "models"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

PREMIER_LEAGUE_CONFIG = LeagueConfig(
    code="premier_league",
    name="Premier League",
    fbref_history_url="https://fbref.com/en/comps/9/Premier-League-Stats",
    fbref_fixtures_url="https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
    processed_dir=PROCESSED_DIR,
    elo_csv=PROCESSED_DIR / "ELO_df.csv",
    upcoming_predictions_csv=PROCESSED_DIR / "upcoming_predictions.csv",
    models_dir=MODELS_DIR,
    outcome_model_path=MODELS_DIR / "pl_outcome_model.pkl",   # 3-way classifier
    score_model_path=MODELS_DIR / "pl_score_model.pkl",       # optional regression / Poisson
    core_module="src.leagues.premier_league.core",
)
