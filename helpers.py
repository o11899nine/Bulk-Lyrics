import docx
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, ResultSet
import re
import os
from tkinter import messagebox, filedialog

def save_location():
    filetypes = [("Word-document", "*.docx")]
    path = None
    try:
        path = filedialog.asksaveasfile(
            filetypes=filetypes,
            defaultextension=filetypes,
            initialfile="Bulk Lyrics",
        )
    except PermissionError:
        messagebox.showwarning(
            title="Access Denied",
            message="Access denied.\nClose the document if it's open and try again.",
        )
        save_location()
    if path:
        return path.name
    else:
        return None

def accept_cookies(driver) -> None:
    """Clicks on Google's 'accept cookies' button if it pops up"""
    try:
        cookie_button = driver.find_element(By.ID, "L2AGLb")
        cookie_button.click()
    except:
        return

def add_hyperlink(paragraph, text: str, url: str):
    """
    Source:
    https://stackoverflow.com/questions/47666642/adding-an-hyperlink-in-msword-by-using-python-docx

    Adds a hyperlink to a document
    """
    # This gets access to the document.xml.rels file and gets a new relation id value
    part = paragraph.part
    r_id = part.relate_to(
        url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    # Create the w:hyperlink tag and add needed values
    hyperlink = docx.oxml.shared.OxmlElement('w:hyperlink')
    hyperlink.set(docx.oxml.shared.qn('r:id'), r_id, )

    # Create a new run object (a wrapper over a 'w:r' element)
    new_run = docx.text.run.Run(
        docx.oxml.shared.OxmlElement('w:r'), paragraph)
    new_run.text = text

    # Set the run's style to the builtin hyperlink style, defining it if necessary
    new_run.style = get_or_create_hyperlink_style(part.document)

    # Join all the xml elements together
    hyperlink.append(new_run._element)
    paragraph._p.append(hyperlink)

    return hyperlink


def get_or_create_hyperlink_style(d):
    """
    Source: 
    https://stackoverflow.com/questions/47666642/adding-an-hyperlink-in-msword-by-using-python-docx

    If this document had no hyperlinks so far, the builtin
    Hyperlink style will likely be missing and we need to add it.
    There's no predefined value, different Word versions define it differently.
    This version is how Word 2019 defines it in the efault theme, 
    excluding a theme reference.
    """
    if "Hyperlink" not in d.styles:
        if "Default Character Font" not in d.styles:
            ds = d.styles.add_style("Default Character Font",
                                    docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                    True)
            ds.element.set(docx.oxml.shared.qn('w:default'), "1")
            ds.priority = 1
            ds.hidden = True
            ds.unhide_when_used = True
            del ds
        hs = d.styles.add_style("Hyperlink",
                                docx.enum.style.WD_STYLE_TYPE.CHARACTER,
                                True)
        hs.base_style = d.styles["Default Character Font"]
        hs.unhide_when_used = True
        hs.font.color.rgb = docx.shared.RGBColor(0x05, 0x63, 0xC1)
        hs.font.underline = True
        del hs

    return "Hyperlink"

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


def ask_to_open_file(path):
    open_file = messagebox.askyesno(
        title="Document saved",
        message=f"Document saved.\nDo you want to open it right now?",
    )

    if open_file:
        os.system('"' + path + '"')