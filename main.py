# BULK LYRICS by MW DIGITAL DEVELOPMENT

# This program takes a list of songs from the user, searches for the lyrics
# to each song on Google and puts all those lyrics in a single .docx file.
# If a song's lyrics are not found, a link to the first google
# hit for that song's lyrics is saved and displayed to the user later.

import re
import tkinter as tk
from tkinter import messagebox, StringVar

from docx import Document
from docx.shared import RGBColor
from bs4 import BeautifulSoup, ResultSet

import helpers
from songs import fetch_song_soup, extract_song_data
import settings

# TODO: readme
# TODO: comments
# TODO: is songs.py necesarry?


class Application:
    def __init__(self) -> None:
        
        self.root = tk.Tk()
        self.root.title("Bulk Lyrics")
        self.root.geometry("600x600")

        placeholder: str = "Nirvana - Smells Like Teen Spirit\nBohemian Rhapsody\nThe Beatles Hey Jude"
        
        self.textbox = tk.Text(self.root, height=20, width=50, font=("", 12))
        self.textbox.insert(1.0, placeholder)
        self.textbox.bind("<Tab>", self.focus_next_widget)
        self.textbox.pack(pady=(40,20))

        self.run_btn = tk.Button(self.root, text="Generate document", command=self.run)
        self.run_btn.bind("<Return>", self.run)
        self.run_btn.bind("<Tab>", self.focus_next_widget)
        self.run_btn.pack()

        self.save_btn = tk.Button(self.root, text="Save as..", command=self.save_as)
        self.save_btn.bind("<Return>", self.save_as)
        self.save_btn.bind("<Tab>", self.focus_next_widget)

        self.no_save_btn = tk.Button(self.root, text="Don't save", command=self.display_reset)
        self.no_save_btn.bind("<Return>", self.display_reset)
        self.no_save_btn.bind("<Tab>", self.focus_next_widget)

        self.status_text = StringVar()
        self.status_display = tk.Label(self.root, textvariable=self.status_text)

        self.root.mainloop()


    def run(self, *event) -> None:
        """
        Is called when the user clicks 'generate document'.
        """
        if not self.check_for_input():
            return

        self.display_running()
        self.setup_driver()
        self.setup_document()
        self.generate_document()
        self.display_finished()


    def display_running(self) -> None:
        """
        Shows/hides relevant buttons/text when the program is running
        """
        self.run_btn.pack_forget()
        self.status_display.pack()
        self.change_status_text("Loading...\n")


    def display_reset(self) -> None:
        """
        Shows/hides relevant buttons/text when the program is reset
        """
        self.status_display.pack_forget()
        self.save_btn.pack_forget()
        self.no_save_btn.pack_forget()
        self.run_btn.pack()


    def display_finished(self) -> None:
        """
        Shows/hides relevant buttons/text when the program is finished
        """
        self.save_btn.pack(pady=10)
        self.no_save_btn.pack()
        self.change_status_text(f"100% completed")


    def change_status_text(self, text: str) -> None:
        """
        Takes a string 'text' and updates the UI's status display to it.
        """
        self.status_text.set(text)
        self.root.update()


    def save_as(self, *event) -> None:
        """
        Is called when the user clicks the 'Save as..' button.
        Prompts the user to choose a save location and then saves the docx there.
        When the file is saved, the user is asked whether they want to open the file.
        """
        path: str = helpers.choose_directory()

        if path:
            self.document.save(path)
            self.display_reset()
            helpers.ask_to_open_file(path)
        else:
            return

    def focus_next_widget(self, event) -> str:
        """
        Allows the user to jump from one field/button to the next.
        """
        event.widget.tk_focusNext().focus()
        return "break"


    def check_for_input(self) -> bool:
        """
        Checks whether the user has entered at least one character in the textbox
        """
        if self.textbox.get("1.0", tk.END) == "\n":
            messagebox.showwarning(
                title="No Songs", message="Please enter song information."
            )
            return False
        return True


    def setup_driver(self) -> None:
        """
        Shows a loading text and calls the initiate_driver function
        """
        self.change_status_text("Initiating driver...\n")
        self.driver = settings.initiate_driver()


    def setup_document(self) -> None:
        """
        Shows a loading text, initiates the docx and calls the format_document function
        """
        self.change_status_text("Preparing document...\n")
        self.document = Document()
        settings.format_document(self.document)


    def generate_document(self) -> None:
        """
        Takes the user's list of songs and loops over the songs.
        For each song, webscrapes Google for the lyrics.
        Then, adds the song and lyrics to the docx and adds a page break.
        """
        songlist: list = self.get_songlist()

        song_progress_percentage: float = 100 / len(songlist)
        total_progress_percentage: int = 0

        for idx, song in enumerate(songlist):
            self.change_status_text(f"{round(total_progress_percentage)}% completed\n{song}")

            soup: BeautifulSoup = fetch_song_soup(song, self.driver)
            song_data: dict = extract_song_data(song, soup)

            self.add_song_to_doc(song_data, self.document)

            if idx != len(songlist) - 1:
                self.document.add_page_break()

            total_progress_percentage += song_progress_percentage


    def add_song_to_doc(self, song_data: dict, document) -> None:
        """
        Adds a song's title, artist and lyrics to the document
        """

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
