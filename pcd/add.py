#!/bin/env python3
import sys, os, uuid, validators, sqlite3

def add_usage(self):
    exe_name = os.path.basename(sys.argv[0])

    print ("Usage: " + exe_name + " add --url=<url> --name=<name> [--min-size=<size-in-MB>] [--destination=<folder>] [--min-duration=<duration-in-seconds>] [--max-duration=<duration-in-seconds>] [--published-time-before=<time-in-HHMMSS>] [--published-time-after=<time-in-HHMMSS>]")
    print ("       --url=<url>                             : URL of podcast")
    print ("       --name=<name>                           : Friendly name")
    print ("       --min-size=<size-in-MB>                 : Don't download file if size is less than this")
    print ("       --max-size=<size-in-MB>                 : Don't download file if size is more than this")
    print ("       --min-duration=<duration-in-seconds>    : Don't download file if duration is shorter than this")
    print ("       --max-duration=<duration-in-seconds>    : Don't download file if duration is longer than this")
    print ("       --published-time-before=<time-in-HHMMSS>: Download file if publication time is before time (Format is 24 hour \"HHMMSS\" only.)")
    print ("       --published-time-after=<time-in-HHMMSS> : Download file if publication time is after time (Format is 24 hour \"HHMMSS\" only.)")
    print ("       --destination=<folder>                  : Destination folder")
    print ("       --include=<regular expression>          : Include podcasts whose title matches the regular expression. This uses case insensitive search.")
    print ("       --exclude=<regular expression>          : Exclude podcasts whose title matches the regular expression. This uses case insensitive search.")
    print ("       --days=<mon,tue,wed,thu,fri,sat,sun>    : Download only on these days (default is all).")

def add(self, url = "", name = "", min_size = None, max_size = None,
        min_duration = None, max_duration = None, published_time_before = None, published_time_after = None, add_uuid = None,
        destination = None, enabled = True, include = "", exclude = "", download_days = 127) -> str:

    if add_uuid is None: add_uuid = str(uuid.uuid4())

    if url == "" or name == "":
        add_usage()
        return ""
    else:
        con = sqlite3.connect(self.db_file)
        curs = con.cursor()

        if enabled == True:
            enabled = 1
        else:
            enabled = 0

        curs.execute("""
            INSERT INTO podcast (
                uuid, name, url, min_size, max_size,
                destination, min_duration, max_duration, published_time_before, published_time_after,
                enabled, include, exclude, download_days
            )
            VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?)""", (
                    add_uuid, name, url, min_size, max_size,
                    destination, min_duration, max_duration, published_time_before, published_time_after,
                    enabled, include, exclude, download_days
                ))

        print (add_uuid + " (" + name + ") added successfully")

        con.commit()
        con.close()

        return add_uuid
