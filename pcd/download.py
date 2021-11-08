#!/bin/env python3

#from urllib import request
import feedparser, os, sqlite3, requests, pathlib, datefinder

config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-dowloader")
db_file = os.path.join(config_dir, "podcast-dowloader.sqlite3")

def format_filename(filename):
    return filename.replace("/", "_").replace(":", "_").replace("\\", "_").replace("*", "_").replace("?", "_")

def dl(config):
    for key in config:
        rss = feedparser.parse(config[key]["url"])
        dl_path = os.path.join(config_dir, format_filename(config[key]["name"]))
        if config[key]["destination"] != "":
            dl_path = config[key]["destination"]
        for entry in rss.entries:
            title = entry["title"]
            date_prefix = ""
            if "published" in entry:
                date_list = datefinder.find_dates(entry["published"])
                for cur_date in date_list:
                    date_prefix = cur_date.strftime("%Y%m%d_%H%M%S - ")
            for link in entry["links"]:
                if link["type"][0:5].lower() != "text/":
                    href = link["href"]

                    do_download = True
                    if "length" in link:
                        length = float(link["length"]) / 1024 / 1024
                        if length < config[key]["min_size"]:
                            do_download = False

                    con = sqlite3.connect(db_file)
                    curs = con.cursor()
                    curs.execute("SELECT count(*) FROM downloaded WHERE uuid = ? AND url = ?", (key, href))

                    if curs.fetchone()[0] == 0 and do_download == True:
                        file_dest = os.path.join(dl_path, date_prefix + format_filename(title) + pathlib.Path(href).suffix)
                        print("Downloading: " + file_dest)
                        file_content = requests.get(href)
                        os.makedirs(dl_path, exist_ok=True)
                        with open(file_dest, 'wb') as fd:
                            fd.write(file_content.content)
                        
                        curs.execute("INSERT INTO downloaded (uuid, url) VALUES (?, ?)", (key, href))
                        con.commit()
                    
            