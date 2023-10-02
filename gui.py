import tkinter as tk 
from tkinter import messagebox

def create_gui():
    root = tk.Tk()
    root.title("Bulk Lyrics")

    label = tk.Label(root, text="Enter a list of songs (one per line):")
    label.pack()

    textbox = tk.Text(root, height=10)
    textbox.pack()

    submit_button = tk.Button(root, text="Generate Lyrics",
                           command=lambda: generate_lyrics(textbox.get("1.0", tk.END)))
    submit_button.pack()

    def generate_lyrics(song_list):
        # Your existing code to generate lyrics goes here
        # You can access the user's input via the song_list parameter
        # For example:
        # songlist = song_list.split("\n")
        # ... (rest of your code)

        messagebox.showinfo("Lyrics Generated",
                            "Lyrics have been generated and saved.")

    root.mainloop()
