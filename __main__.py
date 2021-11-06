#!/bin/env python3

from genericpath import exists
import os, json, sqlite3, sys, pcd

config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-dowloader")
config_file = os.path.join(config_dir, "podcast-dowloader.cfg")
db_file = os.path.join(config_dir, "podcast-dowloader.sqlite3")

exe_name = os.path.basename(sys.argv[0])

def main_usage():
    print ("Usage: " + exe_name + " <command> [help]")
    print ("       command is one of:")
    print ("           add         : Add a new podcast to scrape")
    print ("           edit        : Edit a podcast")
    print ("           delete      : Delete a podcast")
    print ("           list        : List podcast - id: friendly name")
    print ("           dump-config : Display the raw config file")
    print ("       see 'help' subcommand for more information")

os.makedirs(config_dir, exist_ok=True)

if exists(config_file):
    config_data = open(config_file, mode="r")
    config = json.loads(config_data.read())
    config_data.close()
else:
    config = json.loads("{ }")

con = sqlite3.connect(db_file)
curs = con.cursor()

curs.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='downloaded'")

if curs.fetchone()[0] == 0:
    curs.execute("CREATE TABLE downloaded (id INTEGER PRIMARY KEY AUTOINCREMENT, uuid CHAR(36), url VARCHAR(1024));")

argc = len(sys.argv)

if len(sys.argv) == 1:
    pcd.download.dl(config)
    sys.exit(0)

if sys.argv[1].lower() == "add":
    pcd.add.add(config)
elif sys.argv[1].lower() == "delete":
    pcd.delete.delete(config)
elif sys.argv[1].lower() == "edit":
    pcd.edit.edit(config)
elif sys.argv[1].lower() == "list":
    for key in config:
        print(key + ": " + config[key]["name"])
elif sys.argv[1].lower() == "dump-config":
    print (config)
else:
    main_usage()
    if sys.argv[1].lower() == "help":
        sys.exit(0)
    else:
        sys.exit(1)

with open(config_file, 'w') as config_save:
    json.dump(config, config_save)
