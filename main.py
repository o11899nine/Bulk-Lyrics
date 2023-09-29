
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
import re
import docx
from docx.shared import RGBColor
import pyperclip


# TODO: Opmaak van doc
# TODO: Browser compatibility
# TODO: Tkinter GUI

def main() -> None:
    songlist: list = get_songlist()

    print("Setting up...")
    driver = initiate_driver()
    document = docx.Document()

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
    
    first_google_hit = soup.find("a", {"jsname": "UWckNb"})["href"]

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
        doc.add_paragraph().add_run(data["artist"]).bold = True
        
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
        p = doc.add_paragraph()
        p.add_run(f"You might find them here:")
        p.add_run("\n")
        add_hyperlink(p, data["link"], data["link"])


def add_hyperlink(paragraph, text, url):
    """
    Source:
    https://stackoverflow.com/questions/47666642/adding-an-hyperlink-in-msword-by-using-python-docx
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
    # Alternatively, set the run's formatting explicitly
    # new_run.font.color.rgb = docx.shared.RGBColor(0, 0, 255)
    # new_run.font.underline = True

    # Join all the xml elements together
    hyperlink.append(new_run._element)
    paragraph._p.append(hyperlink)
    return hyperlink

# This is only needed if you're using the builtin style above


def get_or_create_hyperlink_style(d):
    """
    Source: 
    https://stackoverflow.com/questions/47666642/adding-an-hyperlink-in-msword-by-using-python-docx

    If this document had no hyperlinks so far, the builtin
       Hyperlink style will likely be missing and we need to add it.
       There's no predefined value, different Word versions
       define it differently.
       This version is how Word 2019 defines it in the
       default theme, excluding a theme reference.
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
    """Clicks on Google's 'accept cookies' button if it pops up"""
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
