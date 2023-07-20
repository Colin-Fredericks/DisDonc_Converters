#! /usr/bin/env python3
#########################
# Table converter for Dis Donc
# Takes in an HTML file with a "Conversation" table
# and outputs a better, cleaner version.
#########################

import sys
import bs4
import glob


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
    print(filename)
    # Open the file using with()
    with(open(filename, "r", errors="ignore", encoding="Windows-1252")) as f:
        soup = bs4.BeautifulSoup(f, "html.parser", from_encoding="Windows-1252")

    # Get the table
    table = soup.find("table")
    # Create a new soup to hold the new structure
    new_soup = bs4.BeautifulSoup("", "html.parser")

    # Each row turns into a dt/dd pair.
    rows = table.findAll("tr")
    for row in rows:
        columns = row.findAll("td")
        # Skip the first column.
        # The second column is the sentence
        # print(len(columns))
        if len(columns) > 1:
            sentence = columns[1].text
        else:
            sentence = ""
        # The third column is the translation
        if len(columns) > 2:
            translation = columns[2].text
        else:
            translation = ""
        # Add the dt/dd pair to the new soup
        dt = new_soup.new_tag("dt")
        dt.string = sentence
        new_soup.append(dt)
        dd = new_soup.new_tag("dd")
        dd.string = translation
        new_soup.append(dd)
    
    return new_soup


    #################################
    # TODO: Pick up here next time. #
    #################################

    pass

def processFile(soup: bs4.BeautifulSoup):
    """Processes a single file.
    Keyword arguments: soup -- the BeautifulSoup object for the file
    Returns: a new BeautifulSoup object with the new structure
    """
    # Get the table
    table = soup.find("table")
    # Create a new soup to hold the new structure
    new_soup = bs4.BeautifulSoup("", "html.parser")
    # The new structure will be a div with class "conversation"
    conversation = new_soup.new_tag("div", **{"class": "conversation"})
    new_soup.append(conversation)

    # Go through the table row by row.
    rows = table.findAll("tr")
    for row in rows:
        # If there's only one td, it's a comment or stage direction.
        if len(row.findAll("td")) == 1:
            # Add the comment to the new soup
            comment = new_soup.new_tag("p")
            comment.string = row.find("td").text
            # This is inside a 3-wide grid, so we need to span the columns.
            # Add "grid-column: span 3;" to the style.
            if "style" in comment:
                comment["style"] = comment["style"] + "grid-column: span 3;"
            else:
                comment["style"] = "grid-column: span 3;"
            conversation.append(comment)
            continue
        # In each row, the second TD has the speaker
        speaker = row.findAll("td")[1]
        # Add the speaker to the new soup
        speaker_tag = new_soup.new_tag("p")
        speaker_tag.string = speaker.text
        conversation.append(speaker_tag)

        # The first TD has the readings filename
        try:
            readings_filename = row.findAll("td")[0].find("a")["href"].strip()
        except TypeError:
            # If there's no readings, skip this row
            continue
        except KeyError:
            # If we can't find an a or its href, skip this row
            continue
        readings_soup = processReadings(readings_filename)
        # We're going to include the readings in a details tag
        details = new_soup.new_tag("details", **{"class": "simple"})
        conversation.append(details)
        # The summary is the speaker's sentence, from the text next to the audio.
        summary = new_soup.new_tag("summary")
        if len(row.findAll("td")) > 2:
            if row.findAll("td")[2] is not None:
                # print(row.findAll("td")[2])
                summary.string = row.findAll("td")[2].text
        else:
            summary.string = "No summary"
        details.append(summary)
        # The details will contain the readings
        details.append(readings_soup)

        # The third TD has the audio
        if len(row.findAll("td")) >2:
            audio_filename = row.findAll("td")[2].find("a")["href"]
        else:
            audio_filename = "No audio"
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
        with(open(filename, "r", errors="ignore")) as f:
            soup = bs4.BeautifulSoup(f, "html.parser")

        # Process the file
        new_soup = processFile(soup)

        # Wrap that in a standard HTML structure
        html = bs4.BeautifulSoup("", "html.parser")
        html.append(new_soup.new_tag("doctype", **{"html": ""}))
        html.append(new_soup.new_tag("html"))
        html.html.append(new_soup.new_tag("head"))
        html.html.head.append(new_soup.new_tag("encoding", **{"charset": "utf-8"}))
        html.html.append(new_soup.new_tag("body"))
        html.html.body.append(new_soup)

        # Write the new file
        new_filename = filename[:-5] + ".new.html"
        print("Writing %s..." % new_filename)
        with(open(new_filename, "w", encoding="utf-8")) as f:
            # Write the HTML structure
            f.write(html.prettify())


# If called as a package, use main()
if __name__ == "__main__":
    main()
