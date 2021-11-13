#!/bin/env python3
import sys, os, validators

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def edit_usage():
    print ("Usage: " + exe_name + " edit --id=<uuid> [--url=<url>] [--name=<name>] [--min-size=<size-in-MB>] [--destination=<folder>]")
    print ("       --id=<uuid>            : ID of podcast to edit")
    print ("       --url=<url>            : New URL of podcast")
    print ("       --name=<name>          : New friendly name")
    print ("       --min-size=<size-in-MB>: New minimum size")
    print ("       --max-size=<size-in-MB>: New maximum size")
    print ("       --destination=<folder> : Destination folder")

def edit(config):
    if argc == 2 or sys.argv[2].lower() == "help":
        edit_usage()
    else:
        url = ""
        name = ""
        min_size = ""
        max_size = ""
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
            if destination != None:
                config[edit_uuid]["destination"] = destination
                changed = True
            if changed == True:
                print (edit_uuid + " edited successfully")
            else:
                print (edit_uuid + " : no changes were made")
