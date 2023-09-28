import logging
# logging.basicConfig(
#     level=logging.DEBUG, format=" %(asctime)s -  %(levelname)s -  %(message)s"
# )

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from docx import Document
import os





def main():
    song = input("Enter song info: ")
    url = f"https://google.com/search?q={song} lyrics"
    driver = setup_driver()
    driver.get(url)
    cookie_button = driver.find_element(By.ID, "L2AGLb")
    cookie_button.click()

    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    song_title = soup.find("div", {"data-attrid": "title"}).text
    song_artist = soup.find("div", {"data-attrid": "subtitle"}).text
    song_lyrics = soup.find_all("div", {"jsname": "U8S5sf"})

    document = Document()
    document.add_heading(song_title)
    document.add_heading(song_artist, 2)
    # document.add_paragraph(song_lyrics)
    print_lyrics(song_lyrics, document)
    document.save("test.docx")
    os.system('start test.docx')


def setup_driver():
    options = Options()
    options.page_load_strategy="eager"
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=options)


def print_lyrics(lyrics, document):
    for paragraph in lyrics:
        lines = paragraph.find_all("span", {"jsname": "YS01Ge"})
        for line in lines:
            document.add_paragraph(line)


if __name__ == "__main__":
    main()
