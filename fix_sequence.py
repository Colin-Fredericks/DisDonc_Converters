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

    # If either of them has "No audio" in it, remove all instances.
    correct_list = [x for x in audio_list1 if "No audio" not in x["src"]]
    busted_list = [x for x in audio_list2 if "No audio" not in x["src"]]

    # If the lists are the same size,
    if len(correct_list) == len(busted_list):
        # Go through the lists and replace the src attributes in the second list.
        for i in range(len(correct_list)):
            # Strip whitespace and fix misdirected links while we're at it.
            correct_list[i]["src"] = correct_list[i]["src"].strip()
            correct_list[i]["src"] = correct_list[i]["src"].replace("../../", "../")
            if ".mp3" not in correct_list[i]["src"]:
                correct_list[i]["src"] += ".mp3"
            busted_list[i]["src"] = correct_list[i]["src"]
        # Then replace those audio tags in the file.
        with open(file2, "r") as f:
            soup = bs.BeautifulSoup(f, "html.parser")
            audio_tags = soup.find_all("audio")
            for i in range(len(audio_tags)):
                audio_tags[i].replace_with(busted_list[i])
        # Write the file.
        with open(file2[:-5] + "_fixed.html", "w") as f:
            f.write(str(soup))
        print("Fixed file created: " + file2[:-5] + "_fixed.html")
    else:
        print("There are different numbers of audio tags in these files.")
        print(len(correct_list), len(busted_list))
        all_tags = []
        # Pad out the shorter list with blank audio tags to make them the same size.
        if len(correct_list) > len(busted_list):
            for i in range(len(correct_list) - len(busted_list)):
                busted_list.append(bs.BeautifulSoup("<audio src='none'></audio>", "html.parser"))
        else:
            for i in range(len(busted_list) - len(correct_list)):
                correct_list.append(bs.BeautifulSoup("<audio src='none'></audio>", "html.parser"))

        # Make a CSV log file with the audio src attributes from both files.
        with open(file1[:-5] + "_log.csv", "w") as f:
            for i in range(len(correct_list)):
                print(correct_list[i], busted_list[i])
                f.write(str(correct_list[i]) + "," + str(busted_list[i]) + "\n")
        print("Log file created: " + file1[:-5] + "_log.csv")


if __name__ == "__main__":
    main()
