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
import settings


# TODO: Refactor more
# TODO: Generate & Save as one button
# TODO: Checkbox 'open document when finished'
# TODO: Add cancel option
# TODO: Add icon, title, subtitle, instructions
# TODO: get rid of all the selfs
# TODO: Browser compatibility
# TODO: consistent naming
# TODO: readme
# TODO: comments, docstrings


class Application:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bulk Lyrics")
        self.root.geometry("960x720")

        self.textbox = tk.Text(
            self.root, height=20, width=50, font=("TkDefaultFont", 12)
        )
        self.textbox.bind("<Tab>", self.focus_next_widget)
        self.textbox.pack()

        self.save_btn = tk.Button(
            self.root, text="Save as..", command=self.save_as
        )
        self.save_btn.bind("<Return>", self.save_as)

        self.generate_btn = tk.Button(
            self.root, text="Generate document", command=self.generate_document
        )
        self.generate_btn.bind("<Return>", self.generate_document)
        self.generate_btn.pack(pady=10)


        self.cancel_btn = tk.Button(
            self.root, text="Cancel", command=self.cancel
        )
        self.status_text = StringVar()

        self.status_display = tk.Label(self.root, textvariable=self.status_text)

        self.running = True
        self.root.mainloop()

    def cancel(self):
        self.running = False
        self.status_display.pack_forget()
        self.cancel_btn.pack_forget()
        self.generate_btn.pack(pady=10)

    def save_as(self, *event):
        filetypes = [("Word-document", "*.docx")]
        try:
            filepath = filedialog.asksaveasfile(
                filetypes=filetypes,
                defaultextension=filetypes,
                initialfile="Bulk Lyrics",
            )
        except PermissionError:
            messagebox.showwarning(
                title="Access Denied",
                message="Access denied.\nClose the document if it's open and try again.",
            )
            self.save_as()

        filepath = filepath.name
        self.document.save(filepath)
        self.ask_for_open(filepath)

    def ask_for_open(self, path):
        open_file = messagebox.askyesno(
            title="Open document?",
            message=f"Document saved.\nDo you wish to open it right now?",
        )
        if open_file:
            os.system('"' + path + '"')

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def generate_document(self, *event):
        self.running = True
        if self.textbox.get("1.0", tk.END) == "\n":
            messagebox.showwarning(
                title="No Songs", message="Please enter song information."
            )
            return
        
        self.generate_btn.pack_forget()
        self.status_display.pack(pady=10)
        self.cancel_btn.pack()

        self.status_text.set("Loading...\n")
        self.root.update()
        songlist: list = self.get_songlist()

        driver = settings.initiate_driver()
        self.document = Document()

        settings.format_document(self.document)

        song_percentage: float = 100 / len(songlist)
        percent_done: int = 0
        

        for idx, song in enumerate(songlist):
            if not self.running:
                return
            self.status_text.set(f"{round(percent_done)}% completed\n{song}")
            self.root.update()
            soup: BeautifulSoup = self.fetch_song_soup(song, driver)
            song_data: dict = self.extract_song_data(song, soup)

            self.add_song_to_doc(song_data, self.document)

            if idx != len(songlist) - 1:
                self.document.add_page_break()
            percent_done += song_percentage
            
        
        self.status_text.set(f"100% completed.\n")
        self.root.update()
        self.save_btn.pack()

    def extract_song_data(self, song: str, soup: BeautifulSoup) -> dict:
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
            artist = self.delete_extra_text(artist)

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

    def delete_extra_text(self, artist: str) -> str:
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
                "Lyrics Not Found"
            ).font.color.rgb = RGBColor(255, 0, 0)

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
        songlist: str = self.textbox.get("1.0", tk.END)
        songlist: list = songlist.replace("\r", "").replace('"', "").split("\n")
        # Remove redundant spaces and empty strings
        songlist = [re.sub(" +", " ", song).strip() for song in songlist if song]

        return songlist


if __name__ == "__main__":
    Application()
