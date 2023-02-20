#! /usr/bin/env python3
# encoding: utf-8
# Python3 script to clean up HTML files
# Usage: python3 CleanHTML.py <filename>
# Output: <filename>.clean.html

import os
import sys
import bs4

# Try to open the file.
# If it doesn't exist, change the path to readings/ and try that.
def openAndGuessEncoding(filename):
    filename = filename.replace("../", "")
    try:
        # Check for utf-8. Backup is Windows 1252.
        with open(filename, "r", encoding="utf-8") as f:
            file_text = f.read()
    except UnicodeDecodeError:
        print("File is not UTF-8. Trying Windows 1252.")
        try:
            with open(filename, "r", encoding="cp1252") as f:
                file_text = f.read()
        except UnicodeDecodeError():
            raise UnicodeDecodeError("Could not guess file encoding.")
    except FileNotFoundError:
        raise FileNotFoundError("Could not find file: " + filename)

    return file_text


def fixAudioLinks(soup, outer_soup):
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
        audio_file = os.path.basename(audio_file)
        # Add the audio file to the <audio> tag
        tag["src"] = "../audio/" + audio_file
        del tag.attrs["href"]
        # Take all of the contents out of the span tag.
        for child in tag.span.contents:
            tag.append(child)
        # Remove the <span> tag
        tag.span.decompose()

    # Find every <p class="audio-player"> tag inside a table
    # and move it (and its contents) to before that table.
    for table in soup.find_all("table"):
        for tag in table.find_all("p", class_="audio-player"):
            table.insert_before(tag)
            tag.decompose()


def pullFromLink(summary_tag, details_wrapper, table, link, cells):
    # Get the text
    summary_tag.append(cells[0].text)
    summary_tag.append(link or cells[1].text)

    # Get the file
    readings_filename = link["href"].strip()
    try:
        file_text = openAndGuessEncoding(readings_filename)
    except FileNotFoundError:
        print("Could not find file: " + readings_filename)
        file_text = "<body><h1>File not found.</h1></body>"
    except UnicodeDecodeError:
        file_text = "<body><h1>Could not guess encoding.</h1></body>"

    # Parse the file
    file_soup = bs4.BeautifulSoup(file_text, "html.parser")
    # TODO: Run this through the appropriate readings cleaner.
    # Get the body
    file_body = file_soup.find("body")
    # Get rid of any script tags
    for tag in file_body.find_all("script"):
        tag.decompose()
    # Insert the contents of the body into the <details> tag
    details_wrapper.find("details").append(file_body)

    # Insert the <details> tag before the table
    table.insert_before(details_wrapper)
    # Remove the table
    table.decompose()


def handleAnswers(outer_soup, tag):
    # Get the link
    link = tag.find("a")
    # Get the text
    answers_filename = link["href"].strip()
    try:
        file_text = openAndGuessEncoding(answers_filename)
    except FileNotFoundError:
        print("Could not find file: " + answers_filename)
        file_text = "<body><h1>File not found.</h1></body>"
    except UnicodeDecodeError:
        file_text = "<body><h1>Could not guess encoding.</h1></body>"

    # Parse the file
    file_soup = bs4.BeautifulSoup(file_text, "html.parser")
    # Get just the body.
    file_body = file_soup.find("body")
    # Get rid of any script, br, or form tags
    for bad_tag in file_body.find_all(["script", "br", "form"]):
        bad_tag.decompose()
    # If the body's only child is a div, get the div's children.
    if file_body.find("div", recursive=False):
        file_body = file_body.findAll(recursive=False)

    for child in file_body:
        # Make a <details> tag and <summary> tag
        details_tag = outer_soup.new_tag("details")
        summary_tag = outer_soup.new_tag("summary")
        details_tag.append(summary_tag)
        summary_tag.append("Show Answers")
        # Insert the contents of the body into the <details> tag
        details_tag.append(child)
        # Insert the <details> tag before the paragraph
        tag.insert_before(details_tag)


def main():
    # Open the file
    filename = sys.argv[1]
    with open(filename, "r") as f:
        text = f.read()

    # Parse the HTML
    outer_soup = bs4.BeautifulSoup(text, "html.parser")

    # Remove the outer <html>, <head>, and <body> tags.
    # Just get the outer <div> tag for the <body>.
    soup = outer_soup.body.div

    # If there's a table with only one row,
    # get the link from the second <td> and the the text from both <td>s
    # Turn the table into a <summary> tag, with the second <td> first.
    # Pull in the file from the link and put it in the <details> tag.
    for table in soup.find_all("table"):
        if len(table.find_all("tr")) == 1:
            details_wrapper = outer_soup.new_tag("div")
            details_tag = outer_soup.new_tag("details")
            summary_tag = outer_soup.new_tag("summary")
            details_wrapper["class"] = ["details-wrapper"]
            details_tag.append(summary_tag)
            details_wrapper.append(details_tag)

            row = table.find("tr")
            cells = row.find_all("td")
            if len(cells) > 1:
                link = cells[1].find("a")
                if link:
                    pullFromLink(summary_tag, details_wrapper, table, link, cells)

    # Remove all ID attributes
    for tag in soup.find_all(True):
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

    # TODO: Fix every link. They're probably pointing to the wrong place.

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
        # Clean out any empty style attributes
        if tag["style"].strip() in [";", ""]:
            del tag["style"]


    # Remove the following classes:
    # rea, au
    for tag in soup.find_all(class_=True):
        classes = tag["class"]
        classes = [c for c in classes if c not in ["rea", "au"]]
        tag["class"] = classes
        # Clean out any empty class attributes
        if tag["class"] == []:
            del tag["class"]

    # When there's a centered paragraph that says "Answers",
    # Pull the text from the linked file and put it
    # in a <details> tag.
    for tag in soup.find_all("p", align="center"):
        if tag.text.strip().lower() == "answers":
            handleAnswers(outer_soup, tag)
            tag.decompose()

    # Remove id, blank styles, and blank class attributes
    # Remove any completely empty tags except for <p> and <br>
    # If the text of a tag is all-caps, make it title case.
    for tag in soup.find_all():
        if tag.name not in ["p", "br"] and tag.text.strip() == "":
            tag.decompose()
        if tag.text.isupper():
            # Only replace the innermost tags
            if len(tag.find_all()) == 0:
                tag.string = tag.text.title()

    # Remove any table rows where all the cells are empty
    for tag in soup.find_all("tr"):
        if all([cell.text.strip() == "" for cell in tag.find_all("td")]):
            tag.decompose()

    # Switch <a href="whatever.mp3"> to <audio> embeds.
    fixAudioLinks(soup, outer_soup)

    # Prepare the HTML for pretty-printing
    unformatted_tag_list = []

    for i, tag in enumerate(
        soup.find_all(
            [
                "a",
                "b",
                "dd",
                "dt",
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
    with open(filename[:-5] + ".clean.html", "w", encoding="utf-8") as f:
        f.write(pretty_markup)
        # print the location of the file
        print("File written to {0}".format(filename[:-5] + ".clean.html"))


if __name__ == "__main__":
    main()
