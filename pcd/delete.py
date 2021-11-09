#!/bin/env python3
import sys, os

argc = len(sys.argv)
exe_name = os.path.basename(sys.argv[0])

def delete_usage():
    print ("Usage: " + exe_name + " delete --id=<uuid>")
    print ("       --id=<uuid> : ID of podcast to delete")

def delete(config):
    if argc == 2 or sys.argv[2].lower() == "help":
        delete_usage()
    else:
        id = ""
        for i in range(2, argc):
            if sys.argv[i][0:5] == "--id=":
                id = sys.argv[i][5:]

        if id == "":
            delete_usage()
        else:
            del config[id]
            print (id + " deleted successfully")

