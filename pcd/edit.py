#!/bin/env python3
import sys, os, sqlite3

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def edit_usage(self):
    print ("Usage: " + exe_name + " edit --id=<uuid> [--url=<url>] [--name=<name>] [--min-size=<size-in-MB>] [--destination=<folder>] [--min-duration=<duration-in-seconds>] [--max-duration=<duration-in-seconds>] [--published-time-before=<time-in-HHMMSS>] [--published-time-after=<time-in-HHMMSS>]")
    print ("       --id=<uuid>                             : ID of podcast to edit")
    print ("       --url=<url>                             : URL of podcast")
    print ("       --name=<name>                           : Friendly name")
    print ("       --min-size=<size-in-MB>                 : Don't download file if size is less than this")
    print ("       --max-size=<size-in-MB>                 : Don't download file if size is more than this")
    print ("       --min-duration=<duration-in-seconds>    : Don't download file if duration is shorter than this")
    print ("       --max-duration=<duration-in-seconds>    : Don't download file if duration is longer than this")
    print ("       --published-time-before=<time-in-HHMMSS>: Download file if publication time is before time (Format is 24 hour \"HHMMSS\" only.)")
    print ("       --published-time-after=<time-in-HHMMSS> : Download file if publication time is after time (Format is 24 hour \"HHMMSS\" only.)")
    print ("       --destination=<folder>                  : Destination folder")
    print ("       --enabled=<enabled>                     : If value is not 0 or empty, then enable podcast")
    print ("       --include=<regular expression>          : Include podcasts whose title matches the regular expression. This uses case insensitive search.")
    print ("       --exclude=<regular expression>          : Exclude podcasts whose title matches the regular expression. This uses case insensitive search.")

def edit(self, uuid, key, value, flask_update = False):
    if flask_update == False:
        if argc == 2 or sys.argv[2].lower() == "help":
            edit_usage()
            return 0

    con = sqlite3.connect(self.db_file)
    curs = con.cursor()
    curs.execute("UPDATE podcast SET " + key + " = ? WHERE uuid = ? OR id = ?", (value, uuid, uuid))
    rc = curs.rowcount
    con.commit()
    con.close()

    return rc > 0
