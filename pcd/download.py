#!/bin/env python3

import feedparser, os, sqlite3, requests, pathlib, datefinder, datetime, time, re, sys, io
from PIL import Image
from urllib.request import urlopen

config_dir = os.path.join(os.path.expanduser('~'), ".config", "podcast-downloader")
db_file = os.path.join(config_dir, "podcast-downloader.sqlite3")

def dl_usage(self):

    print ("Usage: podcast-downloader web [--id|uuid=<id|uuid>] [--url=<url of file>]")
    print ("    Without parameters, same as ./podcast-downloader without arguments")
    print ("    --id|uuid=<id|uuid>: Download only for <id> or <uuid>. Both are interchangeable (--id can be used with uuid value and --uuid can be used wit id value)")
    print ("    --url=<url>        : Download only the file identified by the url (mostly used with the history tab)")
    print ("                         WARNING: Forcing with URL don't apply regex filters")
    print ("                         WARNING: URL MUST be available in current RSS feed. If your broadcaster removes the link from the feed, the podcast-downloader won't download it. You can still get the link in \"downloaded\" table")


def get_image(url):
    print("Fetching image: " + url)
    r = requests.get(url, timeout=60)
    i = Image.open(io.BytesIO(r.content))
    return i

def get_extension(path):
    extension = pathlib.Path(path).suffix
    http_params_position = extension.find('?')
    if (http_params_position == -1):
        return extension
    return extension[:http_params_position]

def format_filename(filename, remove_special_chars=True, replace_slashes=True):

    filename = re.sub(r'[/\\:#?<>|]', '_', filename)
    filename = filename.replace("\"", "''")

    return filename

def get_file_name(href, destination, date_prefix, title):
    file_extension = get_extension(href)
    return os.path.join(destination, date_prefix + format_filename(title) + file_extension)

def dl(self, dl_episodes = True, dl_id = None, dl_url = None):
    print("Start downloading process")

    con = sqlite3.connect(self.db_file)
    curs = con.cursor()

    curs.execute("""SELECT uuid, url, name, min_size, max_size,
                            destination, min_duration, max_duration, published_time_before, published_time_after,
                            include, exclude, download_days, image, description
                 FROM podcast WHERE :dl_id IS NULL AND enabled = 1 OR CAST(:dl_id_str AS VARCHAR(36)) IN (CAST(id AS VARCHAR(36)), uuid)""", {'dl_id': dl_id, 'dl_id_str': str(dl_id)})

    data = curs.fetchall()

    for line in data:
        uuid = "" if line[0] is None else line[0]
        url = "" if line[1] is None else line[1]
        name = "" if line[2] is None else line[2]
        min_size = 0 if line[3] is None else line[3]
        max_size = 0 if line[4] is None else line[4]
        destination = "" if line[5] is None else line[5]
        min_duration = 0 if line[6] is None else line[6]
        max_duration = 0 if line[7] is None else line[7]
        published_time_before = 240000 if line[8] is None else line[8]
        published_time_after = 0 if line[9] is None else line[9] # 000000
        include = "" if line[10] is None else line[10]
        exclude = "" if line[11] is None else line[11]
        download_days = 127 if line[12] is None else line[12]
        last_image = "" if line[13] is None else line[13]
        description = "" if line[14] is None else line[14]

        if published_time_before == 0: published_time_before = 240000

        if destination == "":
            destination = os.path.join(config_dir, format_filename(name))

        rss = feedparser.parse(url)

        print("Checking {name} ({uuid})".format(name=name, uuid=uuid))

        if rss["feed"]["image"] is not None:
            image = rss["feed"]["image"]["href"]
        else:
            image = ""

        image_data = None

        if image != last_image and image != "":
            try:
                image_data = get_image(image)
                image_data.thumbnail([sys.maxsize, 128], Image.LANCZOS)

                byteIO = io.BytesIO()
                image_data.save(byteIO, format='PNG')
                image_data = byteIO.getvalue()

            except Exception as exp:
                print("Cannot download image", file=sys.stderr)
                iamge_data = None

            curs.execute("UPDATE podcast SET image = :image, image_cache = :image_data WHERE uuid = :uuid", {'image': image, 'image_data': image_data, 'uuid': uuid})
            con.commit()

        if description != rss["feed"]["description"]:
            description = rss["feed"]["description"]

            curs.execute("UPDATE podcast SET description = :description WHERE uuid = :uuid", {'description': description, 'uuid': uuid})
            con.commit()

        for entry in rss.entries:
            title = entry["title"]

            do_download = dl_episodes

            if dl_url is None:
                if include != "":
                    try:
                        if re.search(include, title, re.IGNORECASE) is None:
                            do_download = False
                    except Exception as exp:
                        print("Invalid \"include\" regular expression: ", file=sys.stderr)
                        if hasattr(exp, "message"):
                            print(exp.message, file=sys.stderr)
                        else:
                            print(exp)

                if exclude != "":
                    try:
                        if re.search(exclude, title, re.IGNORECASE) is not None:
                            do_download = False
                    except Exception as exp:
                        print("Invalid \"include\" regular expression: ", file=sys.stderr)
                        if hasattr(exp, "message"):
                            print(exp.message, file=sys.stderr)
                        else:
                            print(exp)

            date_prefix = ""
            date_published = datetime.datetime.now()
            if "published" in entry:
                date_list = datefinder.find_dates(entry["published"])
                for cur_date in date_list:
                    date_prefix = cur_date.strftime("%Y%m%d_%H%M%S - ")
                    date_published = cur_date

                    # This turns Monday in 1, Tuesday in 2, Wednesday in 4, Thursday in 8....
                    bitday = pow(2, cur_date.weekday())
                    if bitday & download_days != bitday:
                        do_download = False

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

            description = ""
            if "description" in entry:
                description = entry["description"]

            extrenal_link = ""
            if "link" in entry:
                extrenal_link = entry["link"]

            for link in entry["links"]:
                if link["type"][0:5].lower() != "text/":
                    href = link["href"]
                    if dl_url is not None and dl_url != href:
                        do_download = False

                    if "length" in link:
                        length = float(link["length"]) / 1024 / 1024
                        if length < min_size or (length > max_size and max_size != 0):
                            do_download = False

                    con = sqlite3.connect(db_file)
                    curs = con.cursor()
                    curs.execute("SELECT count(*) FROM downloaded WHERE uuid = :uuid AND url = :href", {'uuid': uuid, 'href': href})

                    if curs.fetchone()[0] == 0 or dl_url is not None:
                        if do_download == True:
                            file_dest = get_file_name(href, destination, date_prefix, title)
                            print("Downloading: " + file_dest)
                            file_content = requests.get(href)
                            os.makedirs(destination, exist_ok=True)
                            with open(file_dest, 'wb') as fd:
                                fd.write(file_content.content)

                        if do_download == True or dl_url is None:

                            try:
                                image = entry["image"]["href"]
                                image_data = get_image(image)
                                image_data.thumbnail([sys.maxsize, 128], Image.LANCZOS)

                                byteIO = io.BytesIO()
                                image_data.save(byteIO, format='PNG')
                                image_data = byteIO.getvalue()
                            except Exception as exp:
                                print("Cannot download image", file=sys.stderr)

                            curs.execute("""INSERT INTO downloaded (uuid, url, name, dl_time, publish_time, description, external_link, image, image_cache)
                                         SELECT :uuid, :href, :title, current_timestamp, :date_published, :description, :extrenal_link, :image, :image_data
                                         WHERE NOT EXISTS (SELECT 1 FROM downloaded WHERE uuid = :uuid and url = :href)""",
                                         {'uuid': uuid, 'href': href, 'title': title, 'date_published': date_published, 'description': description,
                                          'extrenal_link': extrenal_link, 'image': image, 'image_data': image_data})

                            con.commit()

    print("Downloading done")

def get_file(self, id:int):
    con = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    curs = con.cursor()

    curs.execute("""SELECT h.url AS href, p.destination, COALESCE(h.publish_time, h.dl_time) AS publish_time, h.name, p.name AS podcast_name
                 FROM podcast p
                 INNER JOIN downloaded h ON h.uuid = p.uuid
                 WHERE h.id = :id""", {'id': id})

    data = curs.fetchone()
    if data is not None:
        destination = data[1]
        if destination == "":
            destination = os.path.join(config_dir, format_filename(data[4]))

        published_time = datetime.datetime.strptime(data[2], "%Y-%m-%d %H:%M:%S%z")

        file = get_file_name(data[0], destination, published_time.strftime("%Y%m%d_%H%M%S - "), data[3])
        url = data[0]
        return file, url
    else:
        return None
