# Utils/clean_meta.py
import pandas as pd

def clean_metadata(df_meta: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize chess metadata DataFrame.
    
    Steps:
    - Convert dates to datetime
    - Ratings to integers
    - Standardize results
    - Fill missing values if needed
    """
    df = df_meta.copy()

    # Standardize date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert ratings to numeric
    for col in ["WhiteElo", "BlackElo"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Standardize results
    if "Result" in df.columns:
        df["Result"] = df["Result"].replace({
            "1-0": "1-0",
            "0-1": "0-1",
            "1/2-1/2": "1/2-1/2"
        })

    # Fill NaNs with default values if needed
    df.fillna({"WhiteElo": 0, "BlackElo": 0}, inplace=True)

    # Ensure game_id is integer index
    if "game_id" in df.columns:
        df["game_id"] = df["game_id"].astype(int)
        df.set_index("game_id", inplace=True)

    return df