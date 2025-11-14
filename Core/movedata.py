import chess
import chess.pgn as ch
import pandas as pd
from pathlib import Path


class MoveData:
    """
    Extract move-level data from a PGN file.
    Each row = one ply (half-move).
    """

    def __init__(self, pgn_path: str):
        self.pgn_path = Path(pgn_path)
        self.moves_list = []
        self._extract_moves()

    # ---------------------------------------------------------
    def _extract_moves(self):
        with open(self.pgn_path, encoding="utf-8", errors="ignore") as pgn:

            game_id = 1  # match MetaData integer game_id

            while True:
                game = ch.read_game(pgn)
                if game is None:
                    break

                board = game.board()
                ply = 1

                for node in game.mainline():
                    if node.move is None:
                        continue

                    move = node.move
                    san = board.san(move)
                    uci = move.uci()

                    # Detect color BEFORE pushing the move
                    color = "white" if board.turn == chess.WHITE else "black"

                    # Extract clock and eval annotations if present
                    clock = None
                    eval_cp = None

                    if node.comment:
                        import re
                        clk_match = re.search(r"\[%clk\s*([0-9:.]+)\]", node.comment)
                        if clk_match:
                            clock = clk_match.group(1)
                        eval_match = re.search(r"\[%eval\s*([#\-\d\.]+)\]", node.comment)
                        if eval_match:
                            eval_str = eval_match.group(1)
                            if eval_str.startswith("#"):
                                eval_cp = f"M{eval_str[1:]}"  # mate in N
                            else:
                                try:
                                    eval_cp = float(eval_str)
                                except ValueError:
                                    eval_cp = None

                    # Apply move first, then get FEN after move
                    board.push(move)
                    fen_after = board.fen()

                    # Store row
                    self.moves_list.append({
                        "game_id": game_id,
                        "ply": ply,
                        "color": color,
                        "move": san,
                        "clock": clock,
                        "eval_cp": eval_cp,
                        "uci": uci,
                        "fen": fen_after,
                    })

                    ply += 1

                game_id += 1

    # ---------------------------------------------------------
    def to_dataframe(self) -> pd.DataFrame:
        """Convert collected move records into a DataFrame with ordered columns."""
        if not self.moves_list:
            return pd.DataFrame()

        df = pd.DataFrame(self.moves_list)

        # Sorting ensures stable ordering
        df.sort_values(by=["game_id", "ply"], inplace=True)

        # Reorder columns
        desired_order = ["game_id", "ply", "color", "move", "clock", "eval_cp", "uci", "fen"]
        df = df[desired_order]

        return df