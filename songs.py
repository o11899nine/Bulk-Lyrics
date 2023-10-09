import re
from bs4 import BeautifulSoup, ResultSet
from selenium.webdriver.common.by import By

def fetch_song_soup(song: str, driver) -> BeautifulSoup:
    """
    Searches Google for a song's lyrics and returns a BeautifulSoup of
    the search results page.
    """
    driver.get(f"https://google.com/search?q={song} lyrics")
    accept_cookies(driver)
    html: str = driver.page_source
    return BeautifulSoup(html, "lxml")


def extract_song_data(song: str, soup: BeautifulSoup) -> dict:
    """
    Finds a song's title, artist and lyrics in the song's BeautifulSoup and
    returns a dict with that info. If a song's lyrics are not found, the user's
    input is used for the song's title and google's first hit for the song's
    lyrics is stored in the dict
    """
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
        "link": first_google_hit,
    }

    return song_data


def delete_extra_text(artist: str) -> str:
    """Deletes the words 'Song by' before the artist. Then returns the artist"""
    # Google displays the artist as "Song by Artist", so the second uppercase
    # letter is the start of the artist's name. The code below finds the index
    # of that second uppercase letter and then removes all text before it
    m: re.Match = re.search(r"^([^A-Z]*[A-Z]){2}", artist)
    try:
        idx: int = m.span()[1] - 1
    except:
        return "Unknown Artist"

    return artist[idx:]


def accept_cookies(driver) -> None:
    """Clicks on Google's 'accept cookies' button if it pops up"""
    try:
        cookie_button = driver.find_element(By.ID, "L2AGLb")
        cookie_button.click()
    except:
        return