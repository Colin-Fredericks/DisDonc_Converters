#! /usr/bin/env python3
#########################
# Table converter for Dis Donc
# Takes in an HTML file with a "Conversation" table
# and outputs a better, cleaner version.
#########################

import sys
import glob
import BeautifulSoup


"""
Conversion notes
================

Original format:
<table border="0" cellspacing="0" cellpadding="0" width="391">
 <tr>
  <td>
  <p><a CLASS="rea" HREF="../readings/119.html " target="_blank"><span>(1.19)</span></a></p>
  </td>
  <td>
  <p><span>Christine</span></p>
  </td>
  <td>
  <p><a CLASS="au" HREF="../audio/frchc143.mp3 " target="_blank" > <span
 >Bonjour, Pierre!</span></a></p>
  </td>
 </tr>
 </table>

 New format:
 <div class="conversation">
    <p>Christine</p>
    <details class="simple">
      <summary>Bonjour, Pierre!</summary>
      <!-- All of this comes from ../readings/119.html -->
      <dt>Bonjour</dt>
      <dd>hello, good morning</dd>
      <dt>Pierre</dt>
      <dd>masculine given name (Equiv. Peter)</dd>
      <dt>Bonjour, Pierre.</dt>
      <dd>Hello, Pierre.</dd>
    </details>
    <p class="audio-player">
        <audio controls src="../audio/frchc119.mp3"></audio>
    </p>
</div>

Note that the new format is a 3-wide grid, not a table or a bunch of nested divs.
"""

def processReadings(filename: str):
    """Processes a readings file so that we can include it in our new HTML structure.
    Keyword arguments: filename -- the name of the readings file
    Returns: a new BeautifulSoup object with the new structure
    """
    # Open the file using with
    with(open(filename, "r")) as f:
        soup = BeautifulSoup.BeautifulSoup(f)

    #################################
    # TODO: Pick up here next time. #
    #################################

    pass

def processFile(soup: BeautifulSoup.BeautifulSoup):
    """Processes a single file.
    Keyword arguments: soup -- the BeautifulSoup object for the file
    Returns: a new BeautifulSoup object with the new structure
    """
    # Get the table
    table = soup.find("table")
    # Create a new soup to hold the new structure
    new_soup = BeautifulSoup.BeautifulSoup()
    # The new structure will be a div with class "conversation"
    conversation = new_soup.new_tag("div", **{"class": "conversation"})
    new_soup.append(conversation)

    # Go through the table row by row.
    rows = table.findAll("tr")
    for row in rows:
        # In each row, the second TD has the speaker
        speaker = row.findAll("td")[1].string
        conversation.append(new_soup.new_tag("p", string=speaker))

        # The first TD has the readings filename
        readings_filename = row.findAll("td")[0].find("a")["href"]
        readings_soup = processReadings(readings_filename)
        # We're going to include the readings in a details tag
        details = new_soup.new_tag("details", **{"class": "simple"})
        conversation.append(details)
        # The summary is the speaker's sentence, from the span next to the audio.
        summary = new_soup.new_tag("summary", string=row.findAll("td")[2].find("span").string)
        details.append(summary)
        # The details will contain the readings
        details.append(readings_soup)

        # The third TD has the audio
        audio_filename = row.findAll("td")[2].find("a")["href"]
        audio = new_soup.new_tag("p", **{"class": "audio-player"})
        audio.append(new_soup.new_tag("audio", **{"controls": "", "src": audio_filename}))
        conversation.append(audio)

    # Get everything after the table but before the script tag.
    # We'll put it at the end of the new file.
    after_table = table.findNextSiblings()
    for tag in after_table:
        if tag.name == "script":
            break
        conversation.append(tag)

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
        with(open(filename, "r")) as f:
            soup = BeautifulSoup.BeautifulSoup(f)

        # Process the file
        new_soup = processFile(soup)

        # Wrap that in a standard HTML structure
        html = BeautifulSoup.BeautifulSoup()
        html.append(new_soup.new_tag("doctype", **{"html": ""}))
        html.append(new_soup.new_tag("html"))
        html.html.append(new_soup.new_tag("head"))
        html.html.head.append(new_soup.new_tag("encoding", **{"charset": "utf-8"}))
        html.html.append(new_soup.new_tag("body"))
        html.html.body.append(new_soup)

        # Write the new file
        new_filename = filename + ".new"
        print("Writing %s..." % new_filename)
        with(open(new_filename, "w")) as f:
            # Write the HTML structure and pretty-print it
            f.write(html.prettify())


# If called as a package, use main()
if __name__ == "__main__":
    main()
