
# BULK LYRICS by MW DIGITAL DEVELOPMENT

# This program takes a list of songs from the user, searches for the lyrics
# to each song on Google and puts all those lyrics in a single .docx file.
# If a song's lyrics are not found, a link to the first google
# hit for that song's lyrics is saved and displayed to the user later.

# User input might look something like this:
    # mardy bum arctic monkeys
    # everlong foo fighters
    # bohemian rhapsody


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from docx import Document
import pyperclip


# TODO: Opmaak van doc
# TODO: Browser compatibility
# TODO: Tkinter GUI
# TODO: Song niet gevonden: save link to first hit, show links
# TODO: "liedje vna" weg

def main():
    songlist = get_songlist()

    print("Setting up...")
    driver = initiate_driver()
    document = Document()

    for song in songlist:
        print(f"Fetching info for {song}")
        soup = fetch_song_soup(song, driver)

        add_song_to_doc(soup, document, song)

        if song != songlist[-1]:
            document.add_page_break()

    filename = input("Enter filename: ")
    document.save(f"testdocs/{filename}.docx")
    print(f"Finished Document saved as {filename}.docx")

def add_song_to_doc(soup, document, song):
    lyrics = soup.find_all("div", {"jsname": "U8S5sf"})
    if len(lyrics) == 0:
        print("Lyrics not found")
        add_song_not_found(song, document)
    else:
        print(f"Lyrics found")
        add_song_info(soup, document)
        add_song_lyrics(soup, document)

def add_song_not_found(song, doc):
    """Adds user song info and 'not found' text to the document"""
    doc.add_heading(song.title())
    doc.add_paragraph().add_run("Lyrics not found")

def fetch_song_soup(song, driver):
    """
    Searches Google for the song lyrics and returns a BeautifulSoup of
    the search results page.
    """
    driver.get(f"https://google.com/search?q={song} lyrics")
    accept_cookies(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    print(type(soup))
    return soup

def get_songlist():
    """
    Gets a list of songs from the user, 
    asks for confirmation and returns the songlist
    """
    songlist = list(pyperclip.paste().replace("\r", "").split("\n"))

    for song in songlist:
        print(song)
    
    confirmation = input("\nPress Enter to continue or type Q to quit.").upper()
    if confirmation == "Q":
        quit()

    return songlist

def accept_cookies(driver):
    """Clicks on Google's 'accept cookies' button"""
    try:
        cookie_button = driver.find_element(By.ID, "L2AGLb")
        cookie_button.click()
    except:
        return

def add_song_info(soup, doc):
    """Adds a song's title and artist to the document"""

    song_title = soup.find("div", {"data-attrid": "title"})
    song_artist = soup.find("div", {"data-attrid": "subtitle"})
    doc.add_heading(song_title.text)
    doc.add_paragraph().add_run(song_artist.text).bold=True


def add_song_lyrics(soup, doc):
    """Add a song's lyrics to the document"""
    song_lyrics = soup.find_all("div", {"jsname": "U8S5sf"})

    for paragraph in song_lyrics:
        p = doc.add_paragraph()
        lines = paragraph.find_all("span", {"jsname": "YS01Ge"})
        for line in lines:
            p.add_run(line.text)
            if line != lines[-1]:
                p.add_run("\n")


def initiate_driver():
    """Sets up and returns the Selenium Chrome webdriver"""
    options = Options()
    options.page_load_strategy="eager"
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

if __name__ == "__main__":
    main()
    
