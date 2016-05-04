# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# FileName:      import_bookmark.py
# Author:        binss
# Create:        2016-05-04 12:20:43
# Description:   No Description
#


from biplist import *
import json
import datetime
import os
import sys
import shutil


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def parse_chrome_time(raw):
    if isinstance(raw, str):
        raw = int(raw)
    if not isinstance(raw, int):
        return None
    dt = hex(raw * 10)[2:17]
    microseconds = int(dt, 16) / 10
    seconds, microseconds = divmod(microseconds, 1000000)
    days, seconds = divmod(seconds, 86400)
    return datetime.datetime(1601, 1, 1) + datetime.timedelta(days, seconds, microseconds)



class BookmarkManager:
    def __init__(self):
        self.bookmarks = []
        self.number = 0

    def load_from_chrome(self, raw):
        def load_bookmark(raw_list):
            bookmarks = []
            number = 0
            for raw_dict in raw_list:
                if "children" in raw_dict and len(raw_dict["children"]):
                    children, children_num = load_bookmark(raw_dict["children"])
                    directory = {"name": raw_dict["name"], "children": children}
                    bookmarks.append(directory)
                    number += children_num
                else:
                    bookmark = {"name": raw_dict["name"], "url": raw_dict["url"], "time": parse_chrome_time(raw_dict["date_added"])}
                    bookmarks.append(bookmark)
                    number += 1
            return bookmarks, number

        raw_list = raw["roots"]["bookmark_bar"]["children"]
        new_bookmarks, new_number = load_bookmark(raw_list)
        self.bookmarks = self.bookmarks + new_bookmarks
        self.number = self.number + new_number


    def save_to_safari(self, origin_raw):
        def save_bookmark(data_list):
            bookmarks = []
            for data_dict in data_list:
                if "children" in data_dict:
                    directory = {"WebBookmarkType": "WebBookmarkTypeList", "Title": data_dict["name"], "Children": save_bookmark(data_dict["children"])}
                    bookmarks.append(directory)
                else:
                    bookmark = {"WebBookmarkType": "WebBookmarkTypeLeaf", "URIDictionary": {"title": data_dict["name"]}, "URLString": data_dict["url"]}
                    bookmarks.append(bookmark)
            return bookmarks

        origin_raw["Children"][1]["Children"] = save_bookmark(self.bookmarks)

    def get_number(self):
        return self.number



def main():
    home_path = os.environ['HOME']

    safari_path = home_path + "/Library/Safari/Bookmarks.plist"
    chrome_path = home_path + "/Library/Application Support/Google/Chrome/Default/Bookmarks"

    if not os.path.exists(safari_path):
        print "[Error]The bookmarks files of safari is not exist! path: " + safari_path
        return

    if not os.path.exists(chrome_path):
        print "[Error]The bookmarks files of chrome is not exist! path: " + chrome_path
        return

    bookmark_manager = BookmarkManager()

    with open(chrome_path, "r") as f:
        chrome_info = json.load(f)
        bookmark_manager.load_from_chrome(chrome_info)

    safari_info = readPlist(safari_path)
    bookmark_manager.save_to_safari(safari_info)
    # create backup
    shutil.copyfile(safari_path, safari_path + ".bak")
    writePlist(safari_info, safari_path)
    print "Done"


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-packages"))
    main()
