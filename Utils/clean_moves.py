# Utils/clean_moves.py
import pandas as pd

def clean_moves(df_moves: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize chess move DataFrame.
    
    Steps:
    - Ensure ply is integer
    - Color as category
    - eval_cp as float if possible, else leave mate string
    - Convert clock to seconds
    """
    df = df_moves.copy()

    # Types
    df["ply"] = df["ply"].astype(int)
    df["color"] = df["color"].astype("category")

    # Convert eval_cp to numeric if possible
    def parse_eval(x):
        if pd.isna(x):
            return None
        if isinstance(x, str) and x.startswith("M"):
            return x  # mate
        try:
            return float(x)
        except:
            return None

    df["eval_cp"] = df["eval_cp"].apply(parse_eval)

    # Convert clock to seconds
    def clock_to_sec(clk):
        if pd.isna(clk):
            return None
        parts = clk.split(":")
        try:
            if len(parts) == 3:
                h, m, s = map(float, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(float, parts)
                return m * 60 + s
            return float(parts[0])
        except:
            return None

    df["clock"] = df["clock"].apply(clock_to_sec)

    # Sort by game_id and ply
    df.sort_values(["game_id", "ply"], inplace=True)

    return df