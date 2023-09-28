import logging
# logging.basicConfig(
#     level=logging.DEBUG, format=" %(asctime)s -  %(levelname)s -  %(message)s"
# )

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



def main():
    song_info = input("Enter song info: ")
    url = f"https://google.com/search?q={song_info} lyrics"
    driver = setup_driver()
    driver.get(url)
    cookie_button = driver.find_element(By.ID, "L2AGLb")
    cookie_button.click()

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    lyrics = soup.find_all("div", {"jsname": "U8S5sf"})
    print_lyrics(lyrics)

def setup_driver():
    options = Options()
    options.page_load_strategy='eager'
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=options)


def print_lyrics(lyrics):
    for paragraph in lyrics:
        lines = paragraph.find_all("span", {"jsname": "YS01Ge"})
        for line in lines:
            print(line.text)
        print()


if __name__ == "__main__":
    main()
