#! /usr/bin/env python3
# Python3 script to clean up HTML files
# Usage: python3 CleanHTML.py <filename>
# Output: <filename>.clean

import sys
import bs4


def main():
    # Open the file
    filename = sys.argv[1]
    with open(filename, "r") as f:
        text = f.read()

    # Parse the HTML
    soup = bs4.BeautifulSoup(text, "html.parser")

    # Remove all ID attributes
    for tag in soup.find_all(id=True):
        del tag["id"]

    # Remove the following attributes:
    # width, height, border, cellspacing, cellpadding, valign, align
    for tag in soup.find_all(["table", "td", "th", "tr"]):
        for attr in [
            "width",
            "height",
            "border",
            "cellspacing",
            "cellpadding",
            "valign",
            "align",
        ]:
            if attr in tag.attrs:
                del tag[attr]

    # Stop telling things to align left; that's the default.
    for tag in soup.find_all(align="left"):
        del tag["align"]

    # Better audio links
    # Original structure: <p><a class="au" href=" ../../audio/fr18t46.mp3 " target="_blank"><span style="font-size: 12pt;">Écoutez.</span></a></p>
    # New structure:
    # <p class="audio-player">
    #   <audio controls src="../audio/frchc119.mp3"></audio>
    # </p>

    # Find all of the audio links
    for tag in soup.find_all("a", class_="au"):
        # Add the audio-player class to the parent <p> tag
        tag.parent["class"] = "audio-player"
        # Turn the <a> tag into an <audio> tag
        tag.name = "audio"
        tag["controls"] = ""
        # Get the audio file name
        audio_file = tag["href"].strip()
        audio_file = audio_file.replace("../../audio/", "")
        audio_file = audio_file.replace(" ", "%20")
        # Add the audio file to the <audio> tag
        tag["src"] = "../audio/" + audio_file
        # Remove the <span> tag
        tag.span.decompose()

    # Remove all of the following elements from the style attribute:
    # font-family, font-size, line-height, margin-top, margin-bottom
    for tag in soup.find_all(style=True):
        styles = tag["style"].split(";")
        styles = [s.strip() for s in styles]
        styles = [s for s in styles if s != ""]
        styles = [s for s in styles if not s.startswith("font-family:")]
        styles = [s for s in styles if not s.startswith("font-size:")]
        styles = [s for s in styles if not s.startswith("line-height:")]
        styles = [s for s in styles if not s.startswith("margin-top:")]
        styles = [s for s in styles if not s.startswith("margin-bottom:")]
        tag["style"] = "; ".join(styles)

    # Remove any blank style attributes
    for tag in soup.find_all(style=True):
        if tag["style"].strip() in [";", ""]:
            del tag["style"]

    # If the text of a tag is all-caps, make it title case.
    for tag in soup.find_all():
        if tag.text.isupper():
            tag.string = tag.text.title()

    # Prepare the HTML for pretty-printing
    unformatted_tag_list = []

    for i, tag in enumerate(
        soup.find_all(
            [
                "a",
                "b",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "i",
                "p",
                "span",
                "strong",
                "em",
            ]
        )
    ):
        unformatted_tag_list.append(str(tag))
        tag.replace_with("{" + "unformatted_tag_list[{0}]".format(i) + "}")

    pretty_markup = soup.prettify().format(unformatted_tag_list=unformatted_tag_list)

    # Write the new file, pretty-printed.
    with open(filename[:-5] + ".clean.html", "w") as f:
        f.write(pretty_markup)


if __name__ == "__main__":
    main()
