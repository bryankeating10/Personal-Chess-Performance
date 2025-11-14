import chess.pgn as ch
import pandas as pd
from pathlib import Path
from datetime import datetime


class MetaData:
    """
    Extract game-level metadata from a PGN file and return it
    as a clean, analysis-ready DataFrame with sequential game_ids.
    """

    def __init__(self, pgn_path: str):
        self.pgn_path = Path(pgn_path)
        self.metadata_list = []
        self._extract_metadata()

    # ---------------------------------------------------------
    def _extract_metadata(self):
        """Read the PGN file and extract metadata for all games."""
        with open(self.pgn_path, encoding="utf-8", errors="ignore") as pgn:

            game_id = 1  # <<-- sequential integer ID

            while True:
                game = ch.read_game(pgn)
                if game is None:
                    break

                headers = dict(game.headers)

                # Assign stable sequential ID
                headers["game_id"] = game_id
                game_id += 1

                # Add source tracking
                headers["source_file"] = str(self.pgn_path)
                headers["parsed_at"] = datetime.utcnow().isoformat()

                self.metadata_list.append(headers)

    # ---------------------------------------------------------
    def to_dataframe(self) -> pd.DataFrame:
        """Return a DataFrame with one row per game."""
        if not self.metadata_list:
            return pd.DataFrame()

        df = pd.DataFrame(self.metadata_list)

        # Set game_id as index (cleaner)
        if "game_id" in df.columns:
            df.set_index("game_id", inplace=True)

        return df