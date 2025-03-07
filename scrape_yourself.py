
import requests
from bs4 import BeautifulSoup

def scrape_lottery_data():
    url = "https://floridalottery.com/games/scratch-offs"  # Adjust based on actual data location
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    print(dir(response))
    print(response.text)
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    print("made soup")
    # Modify the selector based on the structure of the website
    games = soup.find_all("div", class_="scratch-off-game")  

    for game in games:
        title = game.find("h3").text.strip()
        price = game.find("span", class_="game-price").text.strip()
        print(f"Game: {title}, Price: {price}")

if __name__ == "__main__":
    scrape_lottery_data()

