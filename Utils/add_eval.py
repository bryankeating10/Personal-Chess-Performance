# Utils/add_eval.py

import chess
import chess.engine
import pandas as pd
import numpy as np
import time


def add_engine_eval(df_moves: pd.DataFrame, engine_path: str, depth: int = 15):
    """
    Adds Stockfish evaluation in 'eval' column ONLY where eval is missing.
    Also stores the raw engine eval in 'eval_stockfish'.

    - If original eval exists → keep it
    - If eval is None/NaN → fill with Stockfish
    - Prints progress every 100 games with ETA
    """

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    df = df_moves.copy()

    # Ensure columns exist
    if "eval" not in df.columns:
        df["eval"] = None
    if "eval_stockfish" not in df.columns:
        df["eval_stockfish"] = None

    seen_game = None
    board = None
    start_time = time.time()
    games_processed = 0
    total_games = df["game_id"].max()

    for idx, row in df.iterrows():

        # Detect new game
        if row["game_id"] != seen_game:
            seen_game = row["game_id"]
            board = chess.Board()
            games_processed += 1

            # Print progress every 100 games
            if games_processed % 100 == 0 or games_processed == total_games:
                elapsed = time.time() - start_time
                avg_per_game = elapsed / games_processed
                remaining_games = total_games - games_processed
                eta_sec = int(avg_per_game * remaining_games)
                eta_min, eta_sec = divmod(eta_sec, 60)
                print(f"Processed {games_processed} games... ETA: {eta_min} min {eta_sec} sec")

        # Apply move
        move = chess.Move.from_uci(row["uci"])
        if not board.is_legal(move):
            continue

        board.push(move)

        # Stockfish analysis
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        pov = info["score"].pov(board.turn)

        # Mate or centipawn
        if pov.is_mate():
            sf_eval = f"M{pov.mate()}"
        else:
            sf_eval = pov.score()  # integer centipawn

        # Always store raw eval
        df.at[idx, "eval_stockfish"] = sf_eval

        # Only overwrite eval if missing
        current_eval = row["eval"]
        if pd.isna(current_eval) or current_eval is None:
            df.at[idx, "eval"] = sf_eval

    engine.quit()
    return df