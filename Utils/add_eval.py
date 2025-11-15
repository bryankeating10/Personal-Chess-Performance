# Utils/add_eval.py

import chess
import chess.engine
import pandas as pd
import numpy as np


def add_engine_eval(df_moves: pd.DataFrame, engine_path: str, depth: int = 15):
    """
    Adds Stockfish evaluation in 'eval' column ONLY where eval is missing.
    Also stores the raw engine eval in 'eval_stockfish'.

    - If original eval exists → keep it
    - If eval is None/NaN → fill with Stockfish
    """

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    df = df_moves.copy()

    # Make sure eval exists
    if "eval" not in df.columns:
        df["eval"] = None

    # Add stockfish column (may be useful for comparison)
    df["eval_stockfish"] = None

    seen_game = None
    board = None

    for idx, row in df.iterrows():

        # Reset board when new game begins
        if row["game_id"] != seen_game:
            board = chess.Board()
            seen_game = row["game_id"]

        # Apply move
        move = chess.Move.from_uci(row["uci"])
        if not board.is_legal(move):
            continue

        board.push(move)

        # Run engine only if needed OR to populate eval_stockfish
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        pov = info["score"].pov(board.turn)

        # Convert score to Mx / centipawn
        if pov.is_mate():
            new_eval = f"M{pov.mate()}"
        else:
            new_eval = pov.score()  # integer centipawn

        # Always add raw Stockfish eval
        df.at[idx, "eval_stockfish"] = new_eval

        # Existing eval?
        current_eval = row["eval"]

        if pd.isna(current_eval) or current_eval is None:
            # No existing eval → replace with stockfish score
            df.at[idx, "eval"] = new_eval
        else:
            # Existing eval → keep it, do not overwrite
            pass

    engine.quit()
    return df