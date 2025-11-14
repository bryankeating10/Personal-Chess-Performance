from pathlib import Path
import requests
from datetime import datetime
from typing import List, Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Chess PGN Downloader)"
}


# -----------------------------
# Archive Retrieval & Filtering
# -----------------------------

def fetch_archives(username: str) -> List[str]:
    """Fetch the list of monthly archive URLs for a Chess.com user."""
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("archives", [])


def download_pgn(url: str) -> str:
    """Download raw PGN text for a monthly archive."""
    pgn_url = url.rstrip("/") + "/pgn"   # safe trailing slash handling
    r = requests.get(pgn_url, headers=HEADERS)
    r.raise_for_status()
    return r.text


def parse_year_month(s: str) -> datetime:
    """Convert YYYY-MM → datetime."""
    return datetime.strptime(s, "%Y-%m")


def filter_archives(archives: List[str],
                    start: Optional[str],
                    end: Optional[str]) -> List[str]:
    """Filter archive URLs within a given date range."""
    if not archives:
        return []

    dated_archives = []
    for url in archives:
        year = url.split("/")[-2]
        month = url.split("/")[-1]
        dt = parse_year_month(f"{year}-{month}")
        dated_archives.append((dt, url))

    # Ensure chronological order
    dated_archives.sort(key=lambda x: x[0])

    # Determine start and end boundaries
    start_dt = parse_year_month(start) if start else dated_archives[0][0]
    end_dt = parse_year_month(end) if end else dated_archives[-1][0]

    return [
        url for dt, url in dated_archives
        if start_dt <= dt <= end_dt
    ]


# -----------------------------
# Main Download Function
# -----------------------------

def download_user(username: str,
                  start: Optional[str] = None,
                  end: Optional[str] = None,
                  output: Optional[str] = None) -> str:
    """
    Download combined PGN data for a user over a given date range.

    Writes output to the project's Data/PGN directory unless an absolute
    `output` path is provided.

    Returns
    -------
    str : path to written PGN file.
    """
    username = username.lower()

    # Determine project root:
    # <project_root>/Utils/download_user.py
    project_root = Path(__file__).resolve().parents[1]

    # Project PGN directory
    pgn_dir = project_root / "Data" / "PGN"
    pgn_dir.mkdir(parents=True, exist_ok=True)

    # Determine output file
    if output:
        out_path = Path(output)
        if out_path.is_absolute():        # Absolute path → use directly
            final_path = out_path
            final_path.parent.mkdir(parents=True, exist_ok=True)
        else:                              # Relative path → under Data/PGN
            final_path = pgn_dir / out_path
            final_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        final_path = pgn_dir / f"{username}_data.pgn"

    # Enforce .pgn extension
    if final_path.suffix.lower() != ".pgn":
        final_path = final_path.with_suffix(".pgn")

    # --------------------
    # Fetch and filter
    # --------------------
    print(f"Fetching archives for: {username}")
    archives = fetch_archives(username)

    if not archives:
        raise ValueError("No Chess.com archives found for this user.")

    print("Filtering archives...")
    selected = filter_archives(archives, start, end)

    if not selected:
        raise ValueError("No archives match the selected date range.")

    print(f"Selected {len(selected)} archives:")
    for u in selected:
        print("  →", u)

    # --------------------
    # Download PGN
    # --------------------
    print(f"\nDownloading {len(selected)} archives...")
    all_pgn = []

    for url in selected:
        url_str = str(url)  # ensure it's a string
        last7 = url_str[-7:]  # get last 7 characters
        print(f"  → Downloading {last7}")
        pgn = download_pgn(url)
        if pgn.strip():
            all_pgn.append(pgn)


    # --------------------
    # Save output
    # --------------------
    print(f"\nSaving PGN...")
    # Ensure final newline for parser compatibility
    content = "\n\n".join(all_pgn).rstrip() + "\n"

    with open(final_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Done.")