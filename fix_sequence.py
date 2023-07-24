#! /usr/bin/env python3

##############################
# Matches up the sequence of audio tags from one file to another.
# Fixes the sequence of the second file to match the first.
##############################


import csv
import argparse
import bs4 as bs


def main():
    # Get the two files to be processed.
    parser = argparse.ArgumentParser(
        description="Matches up the sequence of audio tags from one file to another. Fixes the sequence of the second file to match the first."
    )
    parser.add_argument(
        "file1", help="The file with the correct sequence of audio tags."
    )
    parser.add_argument("file2", help="The file with the wrong sequence.")

    args = parser.parse_args()
    file1 = args.file1
    file2 = args.file2

    # Get the lists of audio elements from both files.
    audio_list1 = []
    audio_list2 = []

    with open(file1, "r") as f:
        soup = bs.BeautifulSoup(f, "html.parser")
        audio_tags = soup.find_all("audio")
        for tag in audio_tags:
            audio_list1.append(tag)

    with open(file2, "r") as f:
        soup = bs.BeautifulSoup(f, "html.parser")
        audio_tags = soup.find_all("audio")
        for tag in audio_tags:
            audio_list2.append(tag)

    # If the lists are the same size,
    if len(audio_list1) == len(audio_list2):
        # Go through the lists and replace the src attributes in the second list.
        for i in range(len(audio_list1)):
            # Strip whitespace and fix misdirected links while we're at it.
            audio_list1[i]["src"] = audio_list1[i]["src"].strip()
            audio_list1[i]["src"] = audio_list1[i]["src"].replace("../../", "../")
            if ".mp3" not in audio_list1[i]["src"]:
                audio_list1[i]["src"] += ".mp3"
            audio_list2[i]["src"] = audio_list1[i]["src"]
        # Then replace those audio tags in the file.
        with open(file2, "r") as f:
            soup = bs.BeautifulSoup(f, "html.parser")
            audio_tags = soup.find_all("audio")
            for i in range(len(audio_tags)):
                audio_tags[i].replace_with(audio_list2[i])
        # Write the file.
        with open(file2[:-5] + "_fixed.html", "w") as f:
            f.write(str(soup))
        print("Fixed file created: " + file2[:-5] + "_fixed.html")
    else:
        print("There are different numbers of audio tags in these files.")
        all_tags = []
        # Pad out the shorter list with blank entries to make them the same size.
        if len(audio_list1) > len(audio_list2):
            for i in range(len(audio_list1) - len(audio_list2)):
                audio_list2.append("")
        else:
            for i in range(len(audio_list2) - len(audio_list1)):
                audio_list1.append("")

        # Make a CSV log file with the audio src attributes from both files.
        with open(file1[:-5] + "_log.csv", "w") as f:
            for i in range(len(audio_list1)):
                f.write(audio_list1[i]["src"] + "," + audio_list2[i]["src"] + "\n")
        print("Log file created: " + file1[:-5] + "_log.csv")


if __name__ == "__main__":
    main()
