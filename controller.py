"""
ALJ 08/18/2019 -> 
    1. Fetch books a user wants to read via Goodreads API
    2. Run Photon web crawler on AudioBook Bay per titles user wants to read
    3. Match urls of audiobooks to titles 
    4. Present user with links to audiobooks that available for download per "want to read" (via output console and a textfile generated with identical output)

    Photon Library/Documentation: https://github.com/s0md3v/Photon?utm_source=mybridge&utm_medium=blog&utm_campaign=read_more
"""

from api_fetch_goodreads import *
from xml_parser import *
import subprocess
import os
import json

#global variables
PHOTON_FILE_LOCATION =  '...your/path/to/photon/cloned/directory...Photon/photon.py'
API_KEY = "YOUR_API_KEY_FOR_GOODREADS"
PHOTON_OUTPUT_LOCATION = 'FOLDER/FOR/YOUR/PHOTON/OUTPUT'

#available shelves are: read, currently-reading, to-read (and other custom shelves per user)
shelf = "to-read"
url = "https://www.goodreads.com/review/list/86865482.xml"
total_to_return = 120
parameters = {"key": API_KEY,"v":"2","shelf":shelf, "per_page": 120}

#create a dict from the Goodreads API call response
root = ElementTree.XML(api_fetch_goodreads(url, parameters))
xmldict = XmlDictConfig(root)
#empty list that will hold the books user wants to read
to_read_list = []

#populate the list with the book titles that the user wants to read
for book in xmldict["reviews"]["review"]:
    to_read_list.append((book["book"]["title"]))

for z in range (0, len(to_read_list)):
    book_as_param = to_read_list[z].replace(' ', '+')
    book_as_dir = to_read_list[z].replace(' ', '')

    #see if the file has been created yet, if not, create it
    try:
        test = open("books_crawled.txt", 'r')
        test.close()
    except FileNotFoundError as e:
        print("creating .txt file...")
        test = open("books_crawled.txt", "x")
        test.close()
    print("Determining if there is a need to run Photon crawler for " + to_read_list[z] + "..." + '\n')
    #check if we have already crawled for a given book
    f = open("books_crawled.txt", 'r').read()
    if book_as_dir in f:
        print("...this book has already been crawled, moving on...\n")
    else:
        #form the command to get relevant URL's per the book we are concerned about
        url_to_crawl = 'http://audiobookbay.nl/?s=' + book_as_param
        levels = '1'
        where_to_place_output = PHOTON_OUTPUT_LOCATION + book_as_dir

        command = ['python', PHOTON_FILE_LOCATION, 
                    '-u', url_to_crawl, 
                    '-l', levels, 
                    '-o', where_to_place_output, 
                    '--only-urls', 
                    '--export=json']
        #run Photon and print command line output
        try:
            print(subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE).stdout.decode('utf-8'))
        except UnicodeDecodeError as e:
            print("Unicode error, cannot print output. Crawler ran successfully...\n")
        #update list of books we have already crawled
        f = open("books_crawled.txt", 'a')
        f.write(book_as_dir)
        f.write('\n')
        f.close()

#remove the existing output file
try:
    os.remove("output.txt")
except OSError:
    pass

#now we need to check the URL's that Photon extracted from AudioBook Bay and see if there is a match per book
for n in range (0, len(to_read_list)):
    book_as_dir = to_read_list[n].replace(' ', '')
    with open(os.path.join(PHOTON_OUTPUT_LOCATION, book_as_dir, 'exported.json')) as json_file:
        data = json.load(json_file)

    book_split = to_read_list[n].split()
    flag_dict = {}
    #check internal url links
    for x in range(0, len(data['internal'])):
        #form a dict that holds whether each word is contained in the url or not
        for y in range (0, len(book_split)):
            if book_split[y] in data['internal'][x]:
                flag_dict.update({book_split[y] : True})
            else:
                flag_dict.update({book_split[y] : False})
        #check if this url is a match
        if all(value == True for value in flag_dict.values()):
            print("  %20s                                 %s" % (to_read_list[n], data['internal'][x]))
            #update output file
            f = open("output.txt", 'a')
            f.write("  %20s %s" % (to_read_list[n], data['internal'][x]))
            f.write('\n')
            f.close()
    #check external urls links
    for x in range(0, len(data['external'])):
        #form a dict that holds whether each word is contained in the url or not
        for y in range (0, len(book_split)):
            if book_split[y] in data['external'][x]:
                flag_dict.update({book_split[y] : True})
            else:
                flag_dict.update({book_split[y] : False})
        #check if this url is a match
        if all(value == True for value in flag_dict.values()):
            print("  %20s                                %s" % (to_read_list[n], data['external'][x]))
            #update output file
            f = open("output.txt", 'a')
            f.write("  %20s %s" % (to_read_list[n], data['internal'][x]))
            f.write('\n')
            f.close()
