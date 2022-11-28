#!/bin/env python3
import sys, os, validators

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def edit_usage():
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

def edit(config):
    if argc == 2 or sys.argv[2].lower() == "help":
        edit_usage()
    else:
        url = ""
        name = ""
        min_size = ""
        max_size = ""
        min_duration = ""
        max_duration = ""
        published_time_before = ""
        published_time_after = ""
        edit_uuid = ""
        destination = None
        for i in range(2, argc):
            if sys.argv[i][0:5] == "--id=":
                edit_uuid = sys.argv[i][5:]
            if sys.argv[i][0:6] == "--url=" and validators.url(sys.argv[i][6:]) == True:
                url = sys.argv[i][6:]
            if sys.argv[i][0:7] == "--name=":
                name = sys.argv[i][7:]
            if sys.argv[i][0:11] == "--min-size=":
                min_size = int(sys.argv[i][11:])
            if sys.argv[i][0:11] == "--max-size=":
                max_size = int(sys.argv[i][11:])
            if sys.argv[i][0:14] == "--destination=":
                destination = sys.argv[i][14:]
            if sys.argv[i][0:15] == "--min-duration=":
                min_duration = sys.argv[i][15:]
            if sys.argv[i][0:15] == "--max-duration=":
                max_duration = sys.argv[i][15:]
            if sys.argv[i][0:24] == "--published-time-before=":
                published_time_before = int(sys.argv[i][24:])
                if published_time_before > 240000:
                    published_time_before = 240000
                if published_time_before < 0:
                    published_time_before = 0
            if sys.argv[i][0:23] == "--published-time-after=":
                published_time_after = int(sys.argv[i][23:])
                if published_time_after > 240000:
                    published_time_after = 240000
                if published_time_after < 0:
                    published_time_after = 0

        if edit_uuid == "":
            edit_usage()
        else:
            changed = False
            if url != "":
                config[edit_uuid]["url"] = url
                changed = True
            if name != "":
                config[edit_uuid]["name"] = name
                changed = True
            if min_size != "":
                config[edit_uuid]["min_size"] = int(min_size)
                changed = True
            if max_size != "":
                config[edit_uuid]["max_size"] = int(max_size)
                changed = True
            if min_duration != "":
                config[edit_uuid]["min_duration"] = int(min_duration)
                changed = True
            if max_duration != "":
                config[edit_uuid]["max_duration"] = int(max_duration)
                changed = True
            if published_time_before != "":
                config[edit_uuid]["published_time_before"] = int(published_time_before)
                changed = True
            if published_time_after != "":
                config[edit_uuid]["published_time_after"] = int(published_time_after)
                changed = True
            if destination != None:
                config[edit_uuid]["destination"] = destination
                changed = True
            if changed == True:
                print (edit_uuid + " edited successfully")
            else:
                print (edit_uuid + " : no changes were made")
