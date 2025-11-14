import requests
import os

# === CONFIG ===
username = "BKChessMaster2"   # Replace with your Chess.com username
save_folder = "chess_games"       # Folder where PGN files will be saved
os.makedirs(save_folder, exist_ok=True)

# 1️⃣ Get all archive URLs for your account
archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
response = requests.get(archives_url)
response.raise_for_status()
archives = response.json()["archives"]

print(f"Found {len(archives)} archives.")

# 2️⃣ Download each archive PGN
for archive_url in archives:
    # Add /pgn to get the PGN version
    pgn_url = archive_url + "/pgn"
    month = archive_url.rstrip("/").split("/")[-2:]
    filename = f"{month[0]}_{month[1]}.pgn"  # e.g., 2023_08.pgn
    filepath = os.path.join(save_folder, filename)

    print(f"Downloading {filename} ...")
    r = requests.get(pgn_url)
    if r.status_code == 200:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(r.text)
    else:
        print(f"Failed to download {filename}, status code {r.status_code}")

print("All downloads complete!")