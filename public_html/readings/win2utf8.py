# Converts files from Windows encoding to UTF-8

import sys
import glob

def convert_file(filename):
    print("Converting %s" % filename)
    with open(filename, 'rb') as f:
        data = f.read()
    with open(filename, 'wb') as f:
        f.write(data.decode('cp1252').encode('utf-8'))

# Take in a list of files to convert
if len(sys.argv) > 1:
    # Use glob to expand wildcards
    files = []
    for arg in sys.argv[1:]:
        files.extend(glob.glob(arg))

    for filename in files:
        convert_file(filename)
