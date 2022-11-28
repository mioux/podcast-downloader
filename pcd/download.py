#!/bin/env python3

#from urllib import request
import feedparser, os, sqlite3, requests, pathlib, datefinder, datetime, time

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
        max_size = config[key].get("max_size", 0)
        destination = config[key].get("destination", "")
        min_duration = config[key].get("min_duration", 0)
        max_duration = config[key].get("max_duration", 0)
        published_time_before = config[key].get("published_time_before", 240000)
        published_time_after = config[key].get("published_time_after", 0) # 000000

        if destination == "":
            destination = os.path.join(config_dir, format_filename(config[key]["name"]))

        rss = feedparser.parse(url)

        for entry in rss.entries:
            title = entry["title"]

            do_download = True

            date_prefix = ""
            if "published" in entry:
                date_list = datefinder.find_dates(entry["published"])
                for cur_date in date_list:
                    date_prefix = cur_date.strftime("%Y%m%d_%H%M%S - ")

                published_time = int(cur_date.strftime("%H%M%S"))
                if published_time > published_time_before or published_time < published_time_after:
                    do_download = False

            duration = 0
            if "itunes_duration" in entry:
                timestr = entry["itunes_duration"]
                ftr = [3600,60,1]
                duration = sum([a*b for a,b in zip(ftr, map(int,timestr.split(':')))])
                if duration < min_duration or (duration > max_duration and max_duration != 0):
                    do_download = False

            for link in entry["links"]:
                if link["type"][0:5].lower() != "text/":
                    href = link["href"]

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
