import os
import requests

def download_pgn(archive_url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Chess PGN Downloader)"
    }
    r = requests.get(archive_url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data.get("pgn", "")

def download_archives(username: str, archive_urls: list[str], save_dir="data/raw"):
    user_dir = os.path.join(save_dir, username)
    os.makedirs(user_dir, exist_ok=True)

    for url in archive_urls:
        year_month = url.split("/")[-2] + "-" + url.split("/")[-1]

        pgn = download_pgn(url)
        output_path = os.path.join(user_dir, f"{year_month}.pgn")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pgn)

        print(f"Saved: {output_path}")

def main():
    username = input("Username: ").strip()
    print("Paste archive URLs, one per line. Enter blank line to finish:")

    archives = []
    while True:
        line = input().strip()
        if not line:
            break
        archives.append(line)

    download_archives(username, archives)

if __name__ == "__main__":
    main()