#!/bin/env python3
import sys, os, uuid, validators

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def add_usage():
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

def add(config):
    if argc == 2 or sys.argv[2].lower() == "help":
        add_usage()
    else:
        url = ""
        name = ""
        min_size = 0
        max_size = 0
        min_duration = 0
        max_duration = 0
        published_time_before = 240000
        published_time_after = 0
        add_uuid = str(uuid.uuid4())
        destination = ""
        for i in range(2, argc):
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
                min_duration = int(sys.argv[i][15:])
            if sys.argv[i][0:15] == "--max-duration=":
                max_duration = int(sys.argv[i][15:])
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

        if url == "" or name == "":
            add_usage()
        else:
            config[add_uuid] = { 
                "name": name, 
                "url": url, 
                "min_size": min_size, 
                "max_size": max_size, 
                "destination": destination, 
                "min_duration": min_duration, 
                "max_duration": max_duration, 
                "published_time_before": published_time_before, 
                "published_time_after": published_time_after
            }
            print (add_uuid + " (" + name + ") added successfully")
