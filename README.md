# Bulk Lyrics v1.1
Input a list of songs and get a .docx document with all lyrics!

## Release notes
### v1.1 (current)
- Now using requests module to webscrape instead of selenium
- Fixed Bug where special symbols in artist/song name caused a google query issue

### v1.0
- This version has only been tested on a Windows 10 machine with the Google Chrome browser installed.

## Feautures to add
- Cancel button
- Scroll bar
- Prettier UI with custom icons and instructions
- Make it a .exe

## Bugs to address
- delete_extra_text function deletes too much sometimes
- user is not prompted to open file when choosing directory on the second attempt
instead of the first