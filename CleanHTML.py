#! /usr/bin/env python3
# Python3 script to clean up HTML files
# Usage: python3 CleanHTML.py <filename>
# Output: <filename>.clean

import sys
import bs4

# TODO: Something in here is removing the <a> tag around the word ANSWER.


def main():
    # Open the file
    filename = sys.argv[1]
    with open(filename, "r") as f:
        text = f.read()

    # Parse the HTML
    soup = bs4.BeautifulSoup(text, "html.parser")

    # Remove the outer <html>, <head>, and <body> tags.
    # Just get the outer <div> tag for the <body>.
    soup = soup.body.div

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

    # Remove the following classes:
    # rea, au
    for tag in soup.find_all(class_=True):
        classes = tag["class"]
        classes = [c for c in classes if c not in ["rea", "au"]]
        tag["class"] = classes

    # Remove any blank style or class attributes
    for tag in soup.find_all(style=True):
        if tag["style"].strip() in [";", ""]:
            del tag["style"]
        if tag["class"].strip() in [";", ""]:
            del tag["class"]

    # If the text of a tag is all-caps, make it title case.
    for tag in soup.find_all():
        if tag.text.isupper():
            tag.string = tag.text.title()

    # Find every <p class="audio-player"> tag
    # Move it and its <audio> tag to just before the table
    for tag in soup.find_all("p", class_="audio-player"):
        audio_tag = tag.find("audio")
        tag.decompose()
        table = soup.find("table")
        table.insert_before(audio_tag)
        table.insert_before(tag)


    """ Not sure why this part isn't working.
    The new_tag method isn't working - it's NoneType.

    # If there's a table with only one row,
    # get the link from the second <td> and the the text from both <td>s
    # Turn the table into a <summary> tag, with the second <td> first.
    for table in soup.find_all("table"):
        if len(table.find_all("tr")) == 1:
            print(str(soup.new_tag))
            details_tag = soup.new_tag("details")
            summary_tag = soup.new_tag("summary")
            details_tag.append(summary_tag)

            row = table.find("tr")
            cells = row.find_all("td")
            link = cells[1].find("a")
            # Get the text
            summary_tag.append(link)
            summary_tag.append("<span>" + cells[0].text + "</span>")

            TODO: this part might be a problem.
            # Get the file
            readings_filename = link["href"].strip()
            # Try to open the file.
            # If it doesn't exist, change the path to readings/ and try that.
            try:
                with open(readings_filename, "r") as f:
                    file_text = f.read()
            except FileNotFoundError:
                readings_filename = readings_filename.replace("../../readings/", "readings/")
                try:
                    with open(readings_filename, "r") as f:
                        file_text = f.read()
                except FileNotFoundError:
                    file_text = "<body><h1>File not found.</h1></body>"

            # Parse the file
            file_soup = bs4.BeautifulSoup(file_text, "html.parser")
            # Get the body
            file_body = file_soup.find("body")
            # Get rid of any script tags
            for tag in file_body.find_all("script"):
                tag.decompose()
            # Insert the contents of the body into the <details> tag
            details_tag.append(file_body)

            TODO: ok, problem part over.

            # Insert the <details> tag before the table
            table.insert_before(details_tag)
            # Remove the table
            table.decompose()
    """

    # Remove any table rows where all the cells are empty
    for tag in soup.find_all("tr"):
        if all([cell.text.strip() == "" for cell in tag.find_all("td")]):
            tag.decompose()

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
    with open(filename[:-5] + ".clean.html", "w") as f:
        f.write(pretty_markup)
        # print the location of the file
        print("File written to {0}".format(filename[:-5] + ".clean.html"))


if __name__ == "__main__":
    main()
