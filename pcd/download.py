#!/bin/env python3

#from urllib import request
import feedparser, os, sqlite3, requests, pathlib, datefinder

config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-downloader")
db_file = os.path.join(config_dir, "podcast-downloader.sqlite3")

def get_extension(path):
    extension = pathlib.Path(path).suffix
    http_params_position = extension.find('?')
    if (http_params_position == -1):
        return extension
    return extension[:http_params_position]


def format_filename(filename):
    return filename.replace("/", "_").replace(":", "_").replace("\\", "_").replace("*", "_").replace("?", "_").replace("\"", "''")

def dl(config):
    for key in config:
        url = config[key].get("url", "")
        name = config[key].get("name", "")
        min_size = config[key].get("min_size", 0)
        destination = config[key].get("destination", "")
        max_size = config[key].get("max_size", 0)

        if destination == "":
            destination = os.path.join(config_dir, format_filename(config[key]["name"]))

        rss = feedparser.parse(url)

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
                        if length < min_size or (length > max_size and max_size != 0):
                            do_download = False

                    con = sqlite3.connect(db_file)
                    curs = con.cursor()
                    curs.execute("SELECT count(*) FROM downloaded WHERE uuid = ? AND url = ?", (key, href))

                    if curs.fetchone()[0] == 0 and do_download == True:
                        file_extension = get_extension(href)
                        file_dest = os.path.join(destination, date_prefix + format_filename(title) + file_extension)
                        print("Downloading: " + file_dest)
                        file_content = requests.get(href)
                        os.makedirs(destination, exist_ok=True)
                        with open(file_dest, 'wb') as fd:
                            fd.write(file_content.content)

                        curs.execute("INSERT INTO downloaded (uuid, url) VALUES (?, ?)", (key, href))
                        con.commit()
