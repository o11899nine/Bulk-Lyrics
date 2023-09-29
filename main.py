
# BULK LYRICS by MW DIGITAL DEVELOPMENT

# This program takes a list of songs from the user, searches for the lyrics
# to each song on Google and puts all those lyrics in a single .docx file.
# If a song's lyrics are not found, a link to the first google
# hit for that song's lyrics is saved and displayed to the user later.

# User input might look something like this:
# mardy bum arctic monkeys
# everlong foo fighters
# bohemian rhapsody


from bs4 import BeautifulSoup, ResultSet
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

def main() -> None:
    songlist: list = get_songlist()

    print("Setting up...")
    driver = initiate_driver()
    document = Document()

    for user_song in songlist:
        print(f"Fetching info for {user_song}")
        soup: BeautifulSoup = fetch_song_soup(user_song, driver)
        song_data: dict = get_song_data(user_song, soup)

        add_song_to_doc(song_data, document)

        if user_song != songlist[-1]:
            document.add_page_break()

    filename: str = input("Enter filename: ")
    document.save(f"testdocs/{filename}.docx")
    print(f"Saved all lyrics in {filename}.docx")


def get_song_data(user_song: str, soup: BeautifulSoup) -> dict:
    '''
    Finds a song's title, artist and lyrics in the song's BeautifulSoup,
    If a song's lyrics are not found, the user's input is used for the song's title
    '''

    lyrics: ResultSet = soup.find_all("div", {"jsname": "U8S5sf"})

    if len(lyrics) == 0:
        title: str = user_song
        artist: bool = False
        lyrics: bool = False
        
    else:
        title: str = soup.find("div", {"data-attrid": "title"}).text
        artist: str = soup.find("div", {"data-attrid": "subtitle"}).text

    return {"title": title, "artist": artist, "lyrics": lyrics}


def add_song_to_doc(data: dict, doc) -> None:
    """Adds a song's title, artist and lyrics to the document"""

    doc.add_heading(data["title"].title())
    if data["artist"]:
        doc.add_paragraph().add_run(data["artist"]).bold = True

    if data["lyrics"]:
        for paragraph in data["lyrics"]:
            p = doc.add_paragraph()
            lines: ResultSet = paragraph.find_all("span", {"jsname": "YS01Ge"})
            for line in lines:
                p.add_run(line.text)
                if line != lines[-1]:
                    p.add_run("\n")
    else:
        doc.add_paragraph().add_run("Lyrics Not Found")


def fetch_song_soup(song: str, driver) -> BeautifulSoup:
    """
    Searches Google for the song lyrics and returns a BeautifulSoup of
    the search results page.
    """
    driver.get(f"https://google.com/search?q={song} lyrics")
    accept_cookies(driver)
    html: str = driver.page_source
    return BeautifulSoup(html, "lxml")


def get_songlist() -> list:
    """
    Gets a list of songs from the user, 
    asks for confirmation and returns the songlist
    """
    songlist: list = pyperclip.paste().replace("\r", "").split("\n")
    # Remove empty strings
    songlist = [song for song in songlist if song]

    for song in songlist:
        print(song)

    confirmation = input("Press Enter to continue or type Q to quit.")
    if confirmation.upper() == "Q":
        quit()

    return songlist


def accept_cookies(driver) -> None:
    """Clicks on Google's 'accept cookies' button"""
    try:
        cookie_button = driver.find_element(By.ID, "L2AGLb")
        cookie_button.click()
    except:
        return


def initiate_driver() -> webdriver.Chrome:
    """Sets up and returns the Selenium Chrome webdriver"""
    options = Options()
    options.page_load_strategy = "eager"
    options.add_argument("--headless")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)


if __name__ == "__main__":
    main()
