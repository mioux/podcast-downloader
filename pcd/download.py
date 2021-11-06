#!/bin/env python3

from urllib import request
import feedparser, os, sys, sqlite3, json, requests, pathlib

config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-dowloader")
db_file = os.path.join(config_dir, "podcast-dowloader.sqlite3")

def dl(config):
    for key in config:
        rss = feedparser.parse(config[key]["url"])
        dl_path = os.path.join(config_dir, config[key]["name"].replace("/", "_").replace(":", "_").replace("\\", "_"))
        for entry in rss.entries:
            title = entry["title"]
            for link in entry["links"]:
                if link["type"][0:5].lower() != "text/":
                    href = link["href"]

                    con = sqlite3.connect(db_file)
                    curs = con.cursor()
                    curs.execute("SELECT count(*) FROM downloaded WHERE uuid = ? AND url = ?", (key, href))

                    if curs.fetchone()[0] == 0:
                        file_dest = os.path.join(dl_path, title.replace("/", "_").replace(":", "_").replace("\\", "_") + pathlib.Path(href).suffix)
                        file_content = requests.get(href)
                        os.makedirs(dl_path, exist_ok=True)
                        print("Downloading: " + file_dest)
                        with open(file_dest, 'wb') as fd:
                            fd.write(file_content.content)
                        
                        curs.execute("INSERT INTO downloaded (uuid, url) VALUES (?, ?)", (key, href))
                    
            