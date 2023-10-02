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

import tkinter as tk
from tkinter import messagebox, StringVar, filedialog
from docx import Document
from docx.shared import RGBColor
from bs4 import BeautifulSoup, ResultSet

import helpers
import gui
import settings


# TODO: Margin bovenaan eerste heading
# TODO: Refactor more
# TODO: Show list of lyrics not found
# TODO: Browser compatibility
# TODO: consistent naming
# TODO: readme
# TODO: Op GitHub als CLI program (MWDD account)
# TODO: Tkinter GUI
# TODO: require input
# TODO: comments, docstrings
    
class GUI():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bulk Lyrics")
        self.root.geometry("960x720")

        self.songs_textbox = tk.Text(self.root, height=20, width=50, font=("TkDefaultFont", 12))
        self.songs_textbox.pack(pady=30)
        self.songs_textbox.bind("<Tab>", self.focus_next_widget)

        self.directory_text = StringVar()
        self.directory_text.set("Choose a directory.")
        self.directory_display = tk.Label(self.root, textvariable=self.directory_text)
        self.directory_display.pack()

        self.directory_btn = tk.Button(self.root, text="Choose directory", command=self.choose_dir)
        self.directory_btn.pack()
        self.directory_btn.bind("<Return>", self.choose_dir)

        self.generate_btn = tk.Button(self.root, text="Generate document", command=self.generate_document)
        self.generate_btn.pack()
        self.generate_btn.bind("<Return>", self.generate_document)

        self.status_text = StringVar()
        self.status_display = tk.Label(self.root, textvariable=self.status_text)
        self.status_display.pack()


        self.file = None

        self.root.mainloop()
    
    def choose_dir(self, *event):
        files = [('Word-document', '*.docx')]
        self.file = filedialog.asksaveasfile(filetypes = files, defaultextension = files).name
        self.directory_text.set(f"Directory: {self.file}")

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def generate_document(self, *event):
        if self.file == None:
            messagebox.showwarning(title="No directory chosen", message="Choose a directory first")
            return

        self.status_text.set("Loading...")
        self.root.update()
        songlist: list = self.get_songlist()
        file = self.file

        driver = settings.initiate_driver()
        document = Document()

        settings.format_document(document)
        try:
            song_percentage: float = 100 / len(songlist)
        except ZeroDivisionError:
            print("Work on denying empty input!")
        percent_done: int = 0

        print(len(songlist))

        for idx, song in enumerate(songlist):
            self.status_text.set(f"{round(percent_done)}% completed.\n{song}")
            self.root.update()
            soup: BeautifulSoup = self.fetch_song_soup(song, driver)
            song_data: dict = self.extract_song_data(song, soup)

            self.add_song_to_doc(song_data, document)
            print(idx)
            if idx != len(songlist)-1:
                document.add_page_break()
            percent_done += song_percentage

        self.status_text.set(f"100% completed.")
        self.root.update()
        document.save(file)
        open_file = messagebox.askyesno(
            title="Finished", 
            message=f"Document finished.\nDo you wish to open it right now?"
            )
        if open_file:
            os.system(f'start {file}')


    def extract_song_data(self, song: str, soup: BeautifulSoup) -> dict:
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
            artist = self.delete_extra_text(artist)

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


    def delete_extra_text(self, artist: str) -> str:
        """Deletes the words 'Song by' before the artist. Then returns the artist"""
        # Google displays the artist as "Song by Artist", so the second uppercase
        # letter is the start of the artist's name. The code below finds the index
        # of that second uppercase letter and then removes all text before it
        m: re.Match = re.search(r'^([^A-Z]*[A-Z]){2}', artist)
        try:
            idx: int = m.span()[1]-1
        except:
            return "Unknown Artist"
    
        return artist[idx:]


    def add_song_to_doc(self, song_data: dict, document) -> None:
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


    def fetch_song_soup(self, song: str, driver) -> BeautifulSoup:
        """
        Searches Google for a song's lyrics and returns a BeautifulSoup of
        the search results page.
        """
        driver.get(f"https://google.com/search?q={song} lyrics")
        helpers.accept_cookies(driver)
        html: str = driver.page_source
        return BeautifulSoup(html, "lxml")


    def get_songlist(self) -> list:
        """
        Gets a list of songs from the user, 
        asks for confirmation and returns the songlist
        """
        songlist: str = self.songs_textbox.get("1.0", tk.END)
        songlist: list = songlist.replace("\r", "").split("\n")
        # Remove redundant spaces and empty strings
        songlist = [re.sub(' +', ' ', song).strip() for song in songlist if song]

        return songlist



if __name__ == '__main__':
    GUI()
