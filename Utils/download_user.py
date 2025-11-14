import requests
from datetime import datetime
from typing import List, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Chess PGN Downloader)"
}


def fetch_archives(username: str) -> List[str]:
    """Fetch the list of monthly archive URLs for a Chess.com user."""
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("archives", [])


def download_pgn(url: str) -> str:
    """Download PGN text from an archive URL."""
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("pgn", "")


def parse_year_month(s: str) -> datetime:
    """Convert YYYY-MM → datetime."""
    return datetime.strptime(s, "%Y-%m")


def filter_archives(archives: List[str],
                    start: Optional[str],
                    end: Optional[str]) -> List[str]:
    """Filter archive URLs within a given date range."""
    if not start and not end:
        return archives

    dated_archives = []
    for url in archives:
        year = url.split("/")[-2]
        month = url.split("/")[-1]
        dt = parse_year_month(f"{year}-{month}")
        dated_archives.append((dt, url))

    start_dt = parse_year_month(start) if start else min(dt for dt, _ in dated_archives)
    end_dt = parse_year_month(end) if end else max(dt for dt, _ in dated_archives)

    return [
        url for dt, url in dated_archives
        if start_dt <= dt <= end_dt
    ]


def download_user_data(username: str,
                       start: Optional[str] = None,
                       end: Optional[str] = None,
                       output: Optional[str] = None) -> str:
    """
    Download combined PGN data for a user over a given date range.

    Parameters
    ----------
    username : str
        Chess.com username (case-insensitive)
    start : str or None
        Start date "YYYY-MM" (inclusive)
    end : str or None
        End date "YYYY-MM" (inclusive)
    output : str or None
        Output filename. Defaults to "{username}_data.pgn"

    Returns
    -------
    str
        Path to written PGN file.
    """
    username = username.lower()
    output_file = f"../Data/PGN/{output}" if output else f"../Data/PGN/{username}_data.pgn"

    print(f"Fetching archives for: {username}")
    archives = fetch_archives(username)

    if not archives:
        raise ValueError("No Chess.com archives found for this user.")

    print("Filtering archives...")
    selected = filter_archives(archives, start, end)

    if not selected:
        raise ValueError("No archives match the selected date range.")

    print(f"Downloading {len(selected)} archives...")
    all_pgn = []
    for url in selected:
        print(f" → {url}")
        pgn = download_pgn(url)
        if pgn:
            all_pgn.append(pgn)

    print(f"Saving PGN to {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_pgn))

    print("Done.")
    return output_file