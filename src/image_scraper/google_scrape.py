from bs4 import BeautifulSoup
import requests
import re
import urllib.request
# html = urlopen("http://www.google.com/")
import os
import argparse
import sys
import json
import csv

# adapted from https://gist.github.com/genekogan/ebd77196e4bf0705db51f86431099e57

# changed to accommodate python 3 (instead of 2)
# cleaned up
# create directory if not exist


def get_soup(url,header):
    return BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url,headers=header)),'html.parser')


def main(args):
    parser = argparse.ArgumentParser(description='Scrape Google images')
    # parser.add_argument('-s', '--search', default='eye', type=str, help='search term')
    parser.add_argument('-i', 'search_file', default=os.path.join(os.getcwd(), 'additional', 'search_file.csv'), type=str, help='image search term file')
    parser.add_argument('-n', '--num_images', default=10, type=int, help='number of images to save')
    parser.add_argument('-d', '--directory', default=os.path.join(os.getcwd(), 'images'), type=str, help='save directory')

    args = parser.parse_args()
    # query = args.search
    query = args.search_file
    max_images = args.num_images
    save_directory = args.directory

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    if not os.path.isfile(query):
        raise ValueError('Image search term file does not exist. Please specify an existing file.')
    else:
        with open(query, 'rb') as csvfile:
            queryreader = csv.DictReader(csvfile)
            for row in queryreader:
                img_class = row['class']
                img_phrase = row['search']
                row_search = img_phrase.split()
                row_search = '_'.join(row_search)
                img_phrase = img_phrase.split()
                img_phrase = '+'.join(img_phrase)
                url = "https://www.google.co.in/search?q="+img_phrase+"&source=lnms&tbm=isch"
                header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
                soup = get_soup(url, header)

                class_save_dir = os.path.join(save_directory, 'img', img_class)

                if not os.path.isdir(class_save_dir):
                    os.makedirs(class_save_dir)

                img_links = []

                for a in soup.find_all("div", {"class":"rg_meta"}):
                    img_link = json.loads(a.text)["ou"]
                    img_format = json.loads(a.text)["ity"]
                    img_links.append((img_link, img_format))

                for i, (img_link, img_format) in enumerate(img_links[0:max_images]):
                    try:
                        # req = urllib.request.Request(img_link, headers={'User-Agent': header})

                        with urllib.request.urlopen(img_link) as response:
                            raw_img = response.read()

                        if len(img_format) == 0:
                            f = open(os.path.join(class_save_dir, row_search + "_" + str(i) + ".jpg"), 'wb')
                        else :
                            f = open(os.path.join(class_save_dir, row_search + "_" + str(i) + "." + img_format), 'wb')

                        f.write(raw_img)
                        f.close()

                    except Exception as e:
                        print("could not load : {}".format(img_link))
                        print(e)


if __name__ == '__main__':
    from sys import argv
    try:
        main(argv)
    except KeyboardInterrupt:
        pass
    sys.exit()