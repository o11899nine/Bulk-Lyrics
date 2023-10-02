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


# TODO: Browser compatibility
# TODO: consistent naming
# TODO: Check if filename exists
# TODO: readme
# TODO: Op GitHub als CLI program (MWDD account)
# TODO: Tkinter GUI
# TODO: comments, docstrings


def main() -> None:
    songlist: list = get_songlist()
    filename: str = input("Enter filename: ")

    print("Loading...")
    driver = settings.initiate_driver()
    document = Document()

    settings.format_document(document)

    songs_not_found: list = []
    for song in songlist:
        print(f"Fetching data for {song}")
        soup: BeautifulSoup = fetch_song_soup(song, driver)
        song_data: dict = extract_song_data(song, soup)

        if song_data["lyrics"] == False:
            songs_not_found.append(song)


        add_song_to_doc(song_data, document)

        if song != songlist[-1]:
            document.add_page_break()

    document.save(f"testdocs/{filename}.docx")

    warn_not_found(songs_not_found)
   
    print(f"Saved lyrics in {filename}.docx")
    os.system(f'start testdocs/{filename}.docx')

def warn_not_found(songs_not_found: list) -> None:
    if len(songs_not_found) != 0:
        print("Lyrics not found for:")
        for song in songs_not_found:
            print(f"- {song}")


def extract_song_data(song: str, soup: BeautifulSoup) -> dict:
    '''
    Finds a song's title, artist and lyrics in the song's BeautifulSoup and 
    returns a dict with that info. If a song's lyrics are not found, the user's 
    input is used for the song's title and google's first hit for the song's 
    lyrics is stored in the dict
    '''

    lyrics: ResultSet = soup.find_all("div", {"jsname": "U8S5sf"})

    if len(lyrics) == 0:
        title: str = song
        artist: bool = False
        lyrics: bool = False
    else:
        title: str = soup.find("div", {"data-attrid": "title"}).text
        artist: str = soup.find("div", {"data-attrid": "subtitle"}).text
        artist = delete_extra_text(artist)

    try:
        first_google_hit: str = soup.find("a", {"jsname": "UWckNb"})["href"]
    except:
        first_google_hit: bool = False

    song_data: dict = {
        "title": title,
        "artist": artist,
        "lyrics": lyrics,
        "link": first_google_hit
    }

    return song_data


def delete_extra_text(artist: str) -> str:
    """Deletes the words 'Song by' before the artist. Then returns the artist"""
    # Google displays the artist as "Song by Artist", so the second uppercase
    # letter is the start of the artist's name. The code below finds the index
    # of that second uppercase letter and then removes all text before it
    m: re.Match = re.search(r'^([^A-Z]*[A-Z]){2}', artist)
    idx: int = m.span()[1]-1
    return artist[idx:]


def add_song_to_doc(song_data: dict, document) -> None:
    """Adds a song's title, artist and lyrics to the document"""

    document.add_heading(song_data["title"].title())

    if song_data["artist"]:
        document.add_paragraph(song_data["artist"].title(), style="Subtitle")

    if song_data["lyrics"]:
        for paragraph in song_data["lyrics"]:
            lines: ResultSet = paragraph.find_all("span", {"jsname": "YS01Ge"})
            p = document.add_paragraph()
            for line in lines:
                p.add_run(line.text)
                if line != lines[-1]:
                    p.add_run("\n")
    else:
        document.add_paragraph().add_run(
            "Lyrics Not Found").font.color.rgb = RGBColor(255, 0, 0)

        if song_data["link"]:
            p = document.add_paragraph()
            p.add_run(f"Try here: ")
            helpers.add_hyperlink(p, song_data["link"], song_data["link"])


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
    # Remove redundant spaces and empty strings
    songlist = [re.sub(' +', ' ', song).strip() for song in songlist if song]

    return songlist


if __name__ == "__main__":
    main()
