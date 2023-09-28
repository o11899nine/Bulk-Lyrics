#TODO: Marges smal

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from docx import Document
import os
import pyperclip


import time



def main():
    os.system('cls')
    print('Loading. Please wait.')
    driver = setup_driver()
    document = Document()

    songlist = list(pyperclip.paste().replace('\r','').split('\n'))
    os.system('cls')

    for song in songlist:
        print(song)
    
    confirmation = input('\nIs this songlist correct Y/N?').upper()
    if confirmation == 'N':
        quit()

    os.system('cls')
    print('Creating document. Please wait.')
    
    for song in songlist:
        driver.get(f"https://google.com/search?q={song} lyrics")

        accept_cookies(driver)

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        
        add_song_info(soup, document)
        add_song_lyrics(soup, document)

        if song != songlist[-1]:
            document.add_page_break()

    document.save("test.docx")
    os.system('start test.docx')

def accept_cookies(driver):
    try:
        cookie_button = driver.find_element(By.ID, "L2AGLb")
        cookie_button.click()
    except:
        return

def add_song_info(soup, doc):
    song_title = soup.find("div", {"data-attrid": "title"})
    song_artist = soup.find("div", {"data-attrid": "subtitle"})
    doc.add_heading(song_title.text)
    doc.add_paragraph().add_run(song_artist.text).bold=True


def add_song_lyrics(soup, doc):
    song_lyrics = soup.find_all("div", {"jsname": "U8S5sf"})

    for paragraph in song_lyrics:
        p = doc.add_paragraph()
        lines = paragraph.find_all("span", {"jsname": "YS01Ge"})
        for line in lines:
            p.add_run(line.text)
            if line != lines[-1]:
                p.add_run('\n')


def setup_driver():
    options = Options()
    options.page_load_strategy="eager"
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(options=options)

if __name__ == "__main__":
    main()
    
