import requests

def fetch_archives(username: str) -> list[str]:
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    headers = {
        "User-Agent": "Mozilla/5.0 (Chess PGN Downloader)"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    return data.get("archives", [])

def main():
    username = input("Enter Chess.com username: ").strip()
    archives = fetch_archives(username)

    print("\nAvailable archives:")
    for a in archives:
        print(a)

if __name__ == "__main__":
    main()