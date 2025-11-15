# Utils/add_eval.py

import chess
import chess.engine
import pandas as pd


def add_engine_eval(df_moves: pd.DataFrame, engine_path: str, depth: int = 15):
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    df = df_moves.copy()
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
            df.at[idx, "eval_stockfish"] = None
            continue
        board.push(move)

        # Engine analysis
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        pov = info["score"].pov(board.turn)    # POV of side to move

        # Mate case
        if pov.is_mate():
            df.at[idx, "eval_stockfish"] = f"M{pov.mate()}"
        else:
            # Centipawn score
            df.at[idx, "eval_stockfish"] = pov.score()

    engine.quit()
    return df