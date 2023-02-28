#! /usr/bin/env python3
#########################
# Table converter for Dis Donc
# Takes in an HTML file with an "Un Peu Plus" table
# and outputs a better, cleaner version.
#########################

import sys
import bs4
import glob


def processFile(soup: bs4.BeautifulSoup):
    """Processes a single file.
    Keyword arguments: soup -- the BeautifulSoup object for the file
    Returns: a new BeautifulSoup object with the new structure
    """

    new_soup = bs4.BeautifulSoup()

    # There will probably be several tables. Handle them all.
    for table in soup.find_all("table"):
        # In the first row, the middle cell has a link to the audio file.
        # Pull that out in front of the table as an audio element.
        audio = table.tr.td.find_next_sibling().find("a")
        if audio is not None:
            audio = audio.extract()
            audio.name = "audio"
            audio.attrs["controls"] = ""
            audio.attrs["src"] = audio.attrs["href"]
            del audio.attrs["href"]
            del audio.attrs["target"]
            new_soup.append(audio)
        
        # Create a new div to hold the conversation
        conversation = new_soup.new_tag("div", **{"class": "conversation"})

        # After that, go row by row.
        rows = table.find_all("tr")
        for row in rows:
            # Ignore the first column.
            # The second column has the french.
            # The third column has the english.
            french = row.find_all("td")[1]
            english = row.find_all("td")[2]


            #TODO: Pick up here.

    # Get everything after the last table.
    after_table = table.find_next_siblings()
    # Add it to the new soup
    for sibling in after_table:
        new_soup.append(sibling)

    return new_soup


def main():
    """Opens files and sends them to be processed."""
    # Get the file name from the command line arguments
    if len(sys.argv) < 2:
        print("Usage: Conversations.py <filename>")
        return
    # Parse the filename with glob to handle multiple files
    filename = sys.argv[1]
    files = glob.glob(filename)
    if len(files) == 0:
        print("No files found")
        return

    # Read the files with BeautifulSoup
    for filename in files:
        print("Reading %s..." % filename)
        with (open(filename, "r", errors="ignore")) as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        # Process the file
        new_soup = processFile(soup)

        # Wrap that in a standard HTML structure
        html = bs4.BeautifulSoup()
        html.append(new_soup.new_tag("doctype", **{"html": ""}))
        html.append(new_soup.new_tag("html"))
        html.html.append(new_soup.new_tag("head"))
        html.html.head.append(new_soup.new_tag("encoding", **{"charset": "utf-8"}))
        html.html.append(new_soup.new_tag("body"))
        html.html.body.append(new_soup)

        # Write the new file
        new_filename = filename[:-5] + ".new.html"
        print("Writing %s..." % new_filename)
        with (open(new_filename, "w")) as f:
            # Write the HTML structure
            f.write(html.prettify())


# If called as a package, use main()
if __name__ == "__main__":
    main()
