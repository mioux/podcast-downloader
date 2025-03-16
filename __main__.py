#!/bin/env python3

import os, sys, validators
from pcd import pcd
from pprint import pprint
import argparse

config_dir = os.path.join(os.path.expanduser('~'), ".config", "podcast-downloader")
db_file = os.path.join(config_dir, "podcast-downloader.sqlite3")

_pcd = pcd.pcd(db_file=db_file)

exe_name = os.path.basename(sys.argv[0])

def stringToIntDays(dayList = "") -> int:
    if dayList is None:
        return 127

    check_days = dayList.lower().replace(" ", "").split(",")
    download_days = 0
    if "mon" in check_days:
        download_days = download_days + 1
    if "tue" in check_days:
        download_days = download_days + 2
    if "wed" in check_days:
        download_days = download_days + 4
    if "thu" in check_days:
        download_days = download_days + 8
    if "fri" in check_days:
        download_days = download_days + 16
    if "sat" in check_days:
        download_days = download_days + 32
    if "sun" in check_days:
        download_days = download_days + 64

    return download_days

def main_usage():
    print ("Usage: " + exe_name + " <command> [help]")
    print ("       command is one of:")
    print ("           add         : Add a new podcast to scrape")
    print ("           edit        : Edit a podcast")
    print ("           delete      : Delete a podcast")
    print ("           list        : List podcast - id: friendly name")
    print ("           dump-config : Display the raw config file")
    print ("           dump        : Alias for dump-config")
    print ("           web         : Starts web server")
    print ("       see 'help' subcommand for more information")

os.makedirs(config_dir, exist_ok=True)

_pcd.migrate_db()
#Import web after DB migration as it is needed for "app" creation
from web import web

argc = len(sys.argv)

parser = argparse.ArgumentParser(prog=exe_name, description="Simple podcast downloader")
parser.add_argument("command", help="Command", action="store", choices=["download", "add", "edit", "delete", "list", "dump-config", "dump", "web", "help", "user"], default="download", nargs="?")
parser.add_argument("help", help="Show help for command", choices=["help"], nargs="?")
parser.add_argument("--id", action="store", help="Id of podcast (nuremic format)")
parser.add_argument("--uuid", action="store", help="Id of podcast (UUID format)")
parser.add_argument("--name", action="store", help="Name of the podcast")
parser.add_argument("--url", action="store", help="URL of podcast")
parser.add_argument("--destination", action="store", help="Destination of files on hard disk")
parser.add_argument("--min-size", action="store", help="Minimum size of file to download (in MB)", type=int)
parser.add_argument("--max-size", action="store", help="Maximum size of file to download (in MB)", type=int)
parser.add_argument("--min-duration", action="store", help="Minimum duration (in s)", type=int)
parser.add_argument("--max-duration", action="store", help="Maximum duration (in s)", type=int)
parser.add_argument("--published-time-before", action="store", help="Published before (HHmmss format)", type=int, choices=range(0, 240000), metavar="HHmmss")
parser.add_argument("--published-time-after", action="store", help="Published after (HHmmss format)", type=int, choices=range(0, 240000), metavar="HHmmss")
parser.add_argument("--include", action="store", help="Include titles containing (regex)")
parser.add_argument("--exclude", action="store", help="Exclude titles containing (regex)")
parser.add_argument("--days", action="store", help="days of download (empty=all, [mon,tue,wed,thu,fri,sat,sun] )")
parser.add_argument("--enabled", action="store", help="Enable download", choices=["0", "off", "no", "false", "disable", "disabled", "1", "on", "yes", "enabled", "enable", "true"])
parser.add_argument("--set-tags", action="store", help="Set tags after downloading", choices=["0", "off", "no", "false", "disable", "disabled", "1", "on", "yes", "enabled", "enable", "true"])
parser.add_argument("--port", action="store", help="Port to listen on. Admin privileges needed for ports < 1024", type=int, choices=range(1, 65535), default=8000, metavar="[1,65534]")
parser.add_argument("--listen", action="store", help="Listen on IP", default="127.0.0.1")
parser.add_argument("--debug", action="store", help="Debug web server", choices=["0", "off", "no", "false", "1", "on", "yes", "debug", "true"])
parser.add_argument("--username", action="store", help="Username to create/modify")
parser.add_argument("--password", action="store", help="password to set tu user (can be ommited)")
parser.add_argument("--delete", action="store_true", help="Delete user")

args = parser.parse_args()

if args.command == "download":
    if args.help == "help":
        _pcd.add_usage()
    else:
        _pcd.dl(dl_url=args.uuid, dl_id=args.id)

    sys.exit(0)

if args.command == "add":
    if args.help == "help":
        _pcd.add_usage()
    else:
        url = args.url if args.url is not None and validators.url(args.url) == True else None
        download_days = 127

        if args.days != "":
            download_days = stringToIntDays(args.days)

        if args.enabled is not None:
            enabled = (args.enabled in ["1", "on", "yes", "enabled", "enable", "true"])
        if args.set_tags is not None:
            set_tags = (args.set_tags in ["1", "on", "yes", "enabled", "enable", "true"])

        _pcd.add(url = args.url, name = args.name, min_size = args.min_size, max_size = args.max_size, destination = args.destination,
                 min_duration = args.min_duration, max_duration = args.max_duration, published_time_before = args.published_time_before,
                 published_time_after = args.published_time_after, include = args.include, exclude = args.exclude, download_days = download_days,
                 set_tags = set_tags, enabled = enabled)

elif args.command == "delete":
    if args.help == "help":
        _pcd.delete_usage()
    else:
        _pcd.delete(args.id)

elif args.command == "edit":
    url = args.url if args.url is not None and validators.url(args.url) == True else None
    download_days = None

    if args.days != "":
        download_days = stringToIntDays(args.days)

    edit_uuid = args.id if args.id is not None else args.url_id

    if args.enabled is not None:
        enabled = (args.enabled in ["1", "on", "yes", "enabled", "enable", "true"])
    if args.set_tags is not None:
        set_tags = (args.set_tags in ["1", "on", "yes", "enabled", "enable", "true"])

    if edit_uuid is None:
        _pcd.edit_usage()
    else:
        changed = False
        if url is not None:
            changed = _pcd.edit(edit_uuid, "url", url) or changed
        if args.name is not None:
            changed = _pcd.edit(edit_uuid, "name", args.name) or changed
        if args.min_size is not None:
            changed = _pcd.edit(edit_uuid, "min_size", args.min_size) or changed
        if args.max_size is not None:
            changed = _pcd.edit(edit_uuid, "max_size", args.max_size) or changed
        if args.min_duration is not None:
            changed = _pcd.edit(edit_uuid, "min_duration", args.min_duration) or changed
        if args.max_duration is not None:
            changed = _pcd.edit(edit_uuid, "max_duration", args.max_duration) or changed
        if args.published_time_before is not None:
            changed = _pcd.edit(edit_uuid, "published_time_before", args.published_time_before) or changed
        if args.published_time_after is not None:
            changed = _pcd.edit(edit_uuid, "published_time_after", args.published_time_after) or changed
        if args.destination is not None:
            changed = _pcd.edit(edit_uuid, "destination", args.destination) or changed
        if args.enabled is not None:
            changed = _pcd.edit(edit_uuid, "enabled", enabled) or changed
        if args.include is not None:
            changed = _pcd.edit(edit_uuid, "include", args.include) or changed
        if args.exclude is not None:
            changed = _pcd.edit(edit_uuid, "exclude", args.exclude) or changed
        if download_days is not None:
            changed = _pcd.edit(edit_uuid, "download_days", download_days) or changed
        if download_days is not None:
            changed = _pcd.edit(edit_uuid, "set_tags", set_tags) or changed

        if changed == True:
            print (edit_uuid + " edited successfully")
        else:
            print (edit_uuid + " : no changes were made")

elif args.command == "list":
    if args.help == "help":
        print ("Usage: " + exe_name + " list")
    else:
        data = _pcd.podcast_list()
        for line in data:
            print(line["pc_detail"])
elif args.command == "dump-config" or args.command == "dump" :
    if args.help == "help":
        print ("Usage: " + exe_name + " " + args.command)
    else:
        data = _pcd.config_dump()

        js_data = { }

        for line in data:
            headers = line.keys()
            js_data[line["uuid"]] = { }
            for h in headers:
                if h != "uuid" and h[-6:] != "_cache":
                    js_data[line["uuid"]][h] = line[h]
        pprint(js_data)

elif args.command == "web":
    if args.help == "help":
        web.web_usage()
    else:
        debug=False
        if args.debug is not None:
            if args.debug == "1" or args.debug == "on" or args.debug == "yes" or args.debug == "true" or args.debug == "debug":
                debug = True

        web.start_web_werver(args.port, args.listen, debug, db_file)

elif args.command == "user":
    if args.help == "help" or args.password is not None and args.delete == True or args.username is None:
        _pcd.user_usage()
    else:
        if args.delete == True:
            _pcd.user_del(args.username)
        else:
            _pcd.user_add(args.username, args.password)

else:
    main_usage()
    if args.command == "help":
        sys.exit(0)
    else:
        sys.exit(1)
