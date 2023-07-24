#! /usr/bin/env python3

##############################
# Finds audio tags whose source attribute is out of sequence
# and writes them to a file with line numbers
##############################

import argparse
import glob
import bs4 as bs


def main():
    # Read in the file to be processed. Use glob for wildcards.
    parser = argparse.ArgumentParser(
        description="Find audio tags whose source attribute is out of sequence and write them to a file with line numbers."
    )
    parser.add_argument(
        "file", help="The file to be processed. Use wildcards for multiple files."
    )
    args = parser.parse_args()
    files = glob.glob(args.file)

    # Process each file
    for file in files:
        # Get a list of all the audio tags in the HTML file using beautiful soup
        line_numbers = []
        source_list = []
        missing_mp3 = []
        error_count = 0
        with open(file, "r") as f:
            soup = bs.BeautifulSoup(f, "html.parser")
            audio_tags = soup.find_all("audio")

        # Create a list of the source attributes and the line numbers for each one.
        # The line numbers are used to find the audio tags in the original file.
        # Because there are duplicates, we need to skip any lines that
        # are already in our list.
        with open(file, "r") as f:
            for line_number, line in enumerate(f, 1):
                if line_number not in line_numbers:
                    for tag in audio_tags:
                        if "src" in tag.attrs:
                            if tag["src"] in line:
                                line_numbers.append(line_number)
                                if "mp3" not in tag["src"]:
                                    missing_mp3.append(tag["src"])
                                else:
                                    source_list.append(tag["src"][:-4])
                                    missing_mp3.append("ok")
                                break
                        else:
                            print("No src attribute in this tag:", tag)
            

        # Go down the lists and see if any of the src attributes are out of sequence.
        # If they are, write the line number and the src attribute to a file.
        # print(line_numbers)
        # print(source_list)
        with open(file + "_out_of_sequence.txt", "w") as f:
            # The first src attributes is not checked because it is assumed to be correct.
            for i in range(1, len(source_list)):
                # Because the start of the file is not a number, just check the final digit.
                x = ord(source_list[i][-1])
                x = 58 if x == 48 else x    # Treat 0 as 10 for sequencing purposes.
                y = ord(source_list[i - 1][-1])
                # print(source_list[i], chr(x), chr(y))
                
                if x != y + 1:
                    f.write(str(line_numbers[i]) + " " + source_list[i] + "\n")
                    error_count += 1
            
            # Add the missing mp3s to the end of the file.
            f.write("\nMissing mp3s:\n")
            for i in range(len(missing_mp3)):
                if missing_mp3[i] != "ok":
                    f.write(str(line_numbers[i]) + " " + missing_mp3[i] + "\n")
                    error_count += 1

        print(str(error_count), " errors found, written to ", file + "_out_of_sequence.txt")
        print("Done.")

if __name__ == "__main__":
    main()