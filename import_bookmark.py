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
        def load_bookmark(folder):
            bookmarks = []
            number = 0
            children = folder.get("children")
            if children:
                for child in children:
                    if child["type"] == "folder":
                        children, children_num = load_bookmark(child)
                        bookmarks.append({"name": child["name"], "children": children})
                        number += children_num
                    else:
                        bookmark = {"name": child["name"], "url": child["url"], "time": parse_chrome_time(child["date_added"])}
                        bookmarks.append(bookmark)
                        number += 1
            return bookmarks, number

        root = raw["roots"]
        bookmark_bar = root.get("bookmark_bar")
        if bookmark_bar:
            self.bookmarks, self.number = load_bookmark(bookmark_bar)
        others = root.get("other")
        if others:
            new_bookmarks, new_number = load_bookmark(others)
            self.bookmarks = self.bookmarks + new_bookmarks
            self.number = self.number + new_number


    def save_to_safari(self, raw):
        def save_bookmark(children):
            bookmarks = []
            for child in children:
                if "children" in child:
                    directory = {"WebBookmarkType": "WebBookmarkTypeList", "Title": child["name"], "Children": save_bookmark(child["children"])}
                    bookmarks.append(directory)
                else:
                    bookmark = {"WebBookmarkType": "WebBookmarkTypeLeaf", "URIDictionary": {"title": child["name"]}, "URLString": child["url"]}
                    bookmarks.append(bookmark)
            return bookmarks

        if self.number is 0:
            print "[Error]No bookmark to be imported"
            return

        found = False
        for children in raw["Children"]:
            if children.get('Title') == "BookmarksBar":
                children["Children"] = save_bookmark(self.bookmarks)
                found = True
        if not found:
            print "[Error]Cannot find bookmark folder of Safari"

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
    print "Done! %i bookmarks have been imported" % bookmark_manager.get_number()


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-packages"))
    main()
