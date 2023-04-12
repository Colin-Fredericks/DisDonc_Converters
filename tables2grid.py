#! /usr/bin/env python3
#########################
# Table-to-grid converter
#########################

import sys
import bs4
import glob


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

        # Get every table in the file
        tables = soup.findAll("table")
        for table in tables:
            # How many columns are there?
            columns = len(table.findAll("tr")[0].findAll("td"))
            # Make a div with two-grid, three-grid, or four-grid
            grid = soup.new_tag("div", **{"class": ""})
            if columns == 1:
                grid["class"].append("one-grid") # Kind of a no-op class right now...
            if columns == 2:
                grid["class"].append("two-grid")
            elif columns == 3:
                grid["class"].append("three-grid")
            elif columns == 4:
                grid["class"].append("four-grid")

            # Make a div in the grid for each td in the table
            for row in table.findAll("tr"):
                for td in row.findAll("td"):
                    div = soup.new_tag("div")

                    # Remove any td or p wrapping the content
                    if td.p:
                        div.append(td.p)
                    else:
                        div.append(td)

                    # If this div has a <p> as its only child, remove the <p>
                    if len(div.contents) == 1 and div.contents[0].name == "p":
                        div.contents[0].unwrap()

                    grid.append(div)

            # Replace the table with the grid
            table.replaceWith(grid)

        # Write the new file
        new_filename = filename[:-5] + ".new.html"
        print("Writing %s..." % new_filename)
        with (open(new_filename, "w")) as f:
            # Write the HTML structure
            f.write(soup.prettify())


# If called as a package, use main()
if __name__ == "__main__":
    main()
