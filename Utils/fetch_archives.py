import requests

def fetch_archives(username: str) -> list[str]:
    url = f"https://api.chess.com/pub/player/{username}/games/archives"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    archives = data.get("archives", [])
    return archives

def main():
    username = input("Enter Chess.com username: ").strip()
    archives = fetch_archives(username)

    print("\nAvailable archives:")
    for a in archives:
        print(a)

if __name__ == "__main__":
    main()