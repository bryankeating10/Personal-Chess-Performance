# Utils/add_eval.py
import chess.engine
import pandas as pd

def add_engine_eval(df_moves: pd.DataFrame, engine_path: str, depth: int = 15) -> pd.DataFrame:
    """
    Add Stockfish evaluation to move DataFrame.
    Creates new column 'eval_stockfish' in centipawns.
    
    Note: evals mate as +M#/-M# strings.
    """
    df = df_moves.copy()
    df["eval_stockfish"] = None

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    for idx, row in df.iterrows():
        fen = row["fen"]
        board = chess.Board(fen)
        info = engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info.get("score")
        if score is not None:
            if score.is_mate():
                df.at[idx, "eval_stockfish"] = f"M{score.mate()}"
            else:
                df.at[idx, "eval_stockfish"] = score.white().score()  # centipawns

    engine.quit()
    return df