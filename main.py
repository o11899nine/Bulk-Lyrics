import logging
# logging.basicConfig(
#     level=logging.DEBUG, format=" %(asctime)s -  %(levelname)s -  %(message)s"
# )

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time





def main():
    driver = setup_driver()

    song_title = input("Enter song information: ")
    url = f"https://google.com/search?q={song_title} lyrics"
    driver.get(url)
    cookie_button = driver.find_element(By.ID, "L2AGLb")
    cookie_button.click()

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    lyrics = soup.find_all("div", {"jsname": "U8S5sf"})
    print_lyrics(lyrics)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=chrome_options)


def print_lyrics(lyrics):
    for paragraph in lyrics:
        lines = paragraph.find_all("span", {"jsname": "YS01Ge"})
        for line in lines:
            print(line.text)
        print()


if __name__ == "__main__":
    main()
