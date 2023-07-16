#!/bin/env python3

import os, sys, validators
from pcd import pcd
from pprint import pprint
from web import web

config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-downloader")
config_file = os.path.join(config_dir, "podcast-downloader.cfg") # Not used, for compatibility with very early version
db_file = os.path.join(config_dir, "podcast-downloader.sqlite3")

_pcd = pcd.pcd(config_file=config_file, db_file=db_file)

exe_name = os.path.basename(sys.argv[0])

def main_usage():
    print ("Usage: " + exe_name + " <command> [help]")
    print ("       command is one of:")
    print ("           add         : Add a new podcast to scrape")
    print ("           edit        : Edit a podcast")
    print ("           delete      : Delete a podcast")
    print ("           list        : List podcast - id: friendly name")
    print ("           dump-config : Display the raw config file")
    print ("           web         : Starts web server")
    print ("       see 'help' subcommand for more information")

os.makedirs(config_dir, exist_ok=True)

_pcd.migrate_db()

argc = len(sys.argv)

if len(sys.argv) == 1:
    _pcd.dl()
    sys.exit(0)

if sys.argv[1].lower() == "add":
    if argc == 2 or sys.argv[2].lower() == "help":
        _pcd.add_usage()
    else:
        url = None
        name = None
        min_size = None
        max_size = None
        destination = None
        min_duration = None
        max_duration = None
        published_time_after = None
        published_time_before = None

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

        _pcd.add(url = url, name = name, min_size = min_size, max_size = max_size, destination = destination, min_duration = min_duration, max_duration = max_duration, published_time_before = published_time_before, published_time_after = published_time_after)

elif sys.argv[1].lower() == "delete":
    if argc == 2 or sys.argv[2].lower() == "help":
        _pcd.delete_usage()
    else:
        id = ""
        for i in range(2, argc):
            if sys.argv[i][0:5] == "--id=":
                id = sys.argv[i][5:]

        if id == "":
            _pcd.delete_usage()
        else:
            _pcd.delete(id)
elif sys.argv[1].lower() == "edit":
    url = None
    name = None
    min_size = None
    max_size = None
    min_duration = None
    max_duration = None
    published_time_before = None
    published_time_after = None
    edit_uuid = None
    destination = None
    enabled = None
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
        if sys.argv[i][0:10] == "--enabled=":
            enabled = sys.argv[i][10:] != "0" and sys.argv[i][10:] != ""

    if edit_uuid is None:
        _pcd.edit_usage()
    else:
        changed = False
        if url is not None:
            changed = _pcd.edit(edit_uuid, "url", url) or changed
        if name is not None:
            changed = _pcd.edit(edit_uuid, "name", name) or changed
        if min_size is not None:
            changed = _pcd.edit(edit_uuid, "min_size", int(min_size)) or changed
        if max_size is not None:
            changed = _pcd.edit(edit_uuid, "max_size", int(max_size)) or changed
        if min_duration is not None:
            changed = _pcd.edit(edit_uuid, "min_duration", int(min_duration)) or changed
        if max_duration is not None:
            changed = _pcd.edit(edit_uuid, "max_duration", int(max_duration)) or changed
        if published_time_before is not None:
            changed = _pcd.edit(edit_uuid, "published_time_before", int(published_time_before)) or changed
        if published_time_after is not None:
            changed = _pcd.edit(edit_uuid, "published_time_after", int(published_time_after)) or changed
        if destination is not None:
            changed = _pcd.edit(edit_uuid, "destination", destination) or changed
        if enabled is not None:
            changed = _pcd.edit(edit_uuid, "enabled", enabled) or changed

        if changed == True:
            print (edit_uuid + " edited successfully")
        else:
            print (edit_uuid + " : no changes were made")

elif sys.argv[1].lower() == "list":
    if argc == 3 and sys.argv[2].lower() == "help":
        print ("Usage: " + exe_name + " list")
    else:
        data = _pcd.podcast_list()
        for line in data:
            print(line["pc_detail"])
elif sys.argv[1].lower() == "dump-config":
    if argc == 3 and sys.argv[2].lower() == "help":
        print ("Usage: " + exe_name + " dump-config")
    else:
        data = _pcd.config_dump()

        js_data = { }

        for line in data:
            headers = line.keys()
            js_data[line["uuid"]] = { }
            for h in headers:
                if h != "uuid":
                    js_data[line["uuid"]][h] = line[h]
        pprint(js_data)

elif sys.argv[1].lower() == "web":
    if argc > 2 and sys.argv[2].lower() == "help":
        web.web_usage()
    else:
        port="8000"
        listen="127.0.0.1"
        debug=False
        for i in range(2, argc):
            if sys.argv[i][0:7] == "--port=":
                port = sys.argv[i][7:]
            if sys.argv[i][0:9] == "--listen=":
                listen = sys.argv[i][9:]
            if sys.argv[i][0:8] == "--debug=":
                debug_str = sys.argv[i][8:]
                if debug_str == "1" or debug_str.lower() == "on" or debug_str.lower() == "yes" or debug_str.lower() == "true":
                    debug = True

        web.start_web_werver(port, listen, debug, config_file, db_file)

else:
    main_usage()
    if sys.argv[1].lower() == "help":
        sys.exit(0)
    else:
        sys.exit(1)
