import requests
import os

# === CONFIG ===
username = "bkchessmaster2"          # Your Chess.com username (lowercase)
save_folder = "games"          # Folder to save PGN files
os.makedirs(save_folder, exist_ok=True)

# Set a proper User-Agent
headers = {"User-Agent": "ChessComDownloader/1.0"}

# 1️⃣ Get all archive URLs
archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
response = requests.get(archives_url, headers=headers)
response.raise_for_status()
archives = response.json()["archives"]

print(f"Found {len(archives)} archives.")

# 2️⃣ Download each archive PGN
for archive_url in archives:
    # Add /pgn to get PGN format
    pgn_url = archive_url + "/pgn"

    # Extract year and month for filename
    parts = archive_url.rstrip("/").split("/")[-2:]
    filename = f"{parts[0]}_{parts[1]}.pgn"
    filepath = os.path.join(save_folder, filename)

    print(f"Downloading {filename} ...")
    r = requests.get(pgn_url, headers=headers)
    if r.status_code == 200:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(r.text)
    else:
        print(f"Failed to download {filename}, status code {r.status_code}")

print("All downloads complete!")