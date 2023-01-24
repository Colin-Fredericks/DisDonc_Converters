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

"""


def processFile(filename: str):
    """Processes a single file.
    Keyword arguments: filename -- the name of the file to process
    """
    pass


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
        f = open(filename, "r")
        soup = BeautifulSoup.BeautifulSoup(f)
        f.close()
        # Process the file
        new_soup = processFile(soup)
        # Write the new file
        new_filename = filename + ".new"
        print("Writing %s..." % new_filename)
        f = open(new_filename, "w")
        f.write(str(new_soup))
        f.close()


# If called as a package, use main()
if __name__ == "__main__":
    main()
