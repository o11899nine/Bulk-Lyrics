# BULK LYRICS by MW DIGITAL DEVELOPMENT

# This program takes a list of songs from the user, searches for the lyrics
# to each song on Google and puts all those lyrics in a single .docx file.
# If a song's lyrics are not found, a link to the first google
# hit for that song's lyrics is saved and displayed to the user later.

# User input might look something like this:
# mardy bum arctic monkeys
# everlong foo fighters
# bohemian rhapsody

import re
import os

import pyperclip
from docx import Document
from docx.shared import RGBColor
from bs4 import BeautifulSoup, ResultSet

import helpers
import settings


# TODO: Margin bovenaan eerste heading
# TODO: Refactor more
# TODO: Browser compatibility
# TODO: Tkinter GUI


def main() -> None:
    songlist: list = get_songlist()

    print("Loading...")
    driver = settings.initiate_driver()
    document = Document()

    settings.format_document(document)

    for user_song in songlist:
        print(f"Fetching data for {user_song}")
        soup: BeautifulSoup = fetch_song_soup(user_song, driver)
        song_data: dict = get_song_data(user_song, soup)

        add_song_to_doc(song_data, document)

        if user_song != songlist[-1]:
            document.add_page_break()

    filename: str = input("Enter filename: ")
    document.save(f"testdocs/{filename}.docx")
    print(f"Saved all lyrics in {filename}.docx")
    os.system(f'start testdocs/{filename}.docx')


def get_song_data(user_song: str, soup: BeautifulSoup) -> dict:
    '''
    Finds a song's title, artist and lyrics in the song's BeautifulSoup and 
    returns a dict with that info. If a song's lyrics are not found, the user's 
    input is used for the song's title and google's first hit for the song's 
    lyrics is stored in the dict
    '''

    lyrics: ResultSet = soup.find_all("div", {"jsname": "U8S5sf"})

    if len(lyrics) == 0:
        title = user_song
        artist = False
        lyrics = False

    else:
        title: str = soup.find("div", {"data-attrid": "title"}).text
        artist: str = soup.find("div", {"data-attrid": "subtitle"}).text
        artist = delete_extra_text(artist)
    try:
        first_google_hit = soup.find("a", {"jsname": "UWckNb"})["href"]
    except:
        first_google_hit = False

    return {"title": title, "artist": artist, "lyrics": lyrics, "link": first_google_hit}


def delete_extra_text(artist: str) -> str:
    """Deletes the words 'Song by' before the artist. Then returns the artist"""
    # Google displays the artist as "Song by Artist", so the second uppercase
    # letter is the start of the artist's name. The code below finds the index
    # of that second uppercase letter and then removes all text before it
    m: re.Match = re.search(r'^([^A-Z]*[A-Z]){2}', artist)
    idx: int = m.span()[1]-1
    return artist[idx:]


def add_song_to_doc(data: dict, doc) -> None:
    """Adds a song's title, artist and lyrics to the document"""

    doc.add_heading(data["title"].title())

    if data["artist"]:
        doc.add_paragraph(data["artist"].title(), style="Subtitle")

    if data["lyrics"]:
        for paragraph in data["lyrics"]:
            lines: ResultSet = paragraph.find_all("span", {"jsname": "YS01Ge"})
            p = doc.add_paragraph()
            for line in lines:
                p.add_run(line.text)
                if line != lines[-1]:
                    p.add_run("\n")
    else:
        doc.add_paragraph().add_run("Lyrics Not Found").font.color.rgb = RGBColor(255, 0, 0)
        if data["link"]:
            p = doc.add_paragraph()
            p.add_run(f"Try here:")
            helpers.add_hyperlink(p, data["link"], data["link"])


def fetch_song_soup(song: str, driver) -> BeautifulSoup:
    """
    Searches Google for a song's lyrics and returns a BeautifulSoup of
    the search results page.
    """
    driver.get(f"https://google.com/search?q={song} lyrics")
    helpers.accept_cookies(driver)
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

    return songlist


if __name__ == "__main__":
    main()
