#!/bin/env python3

from genericpath import exists
import os, json, sqlite3, sys

def migrate_db(self):
    con = sqlite3.connect(self.db_file)
    curs = con.cursor()

    curs.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='config'")

    if curs.fetchone()[0] == 0:
        curs.execute("CREATE TABLE config (configname CHAR(20) PRIMARY KEY, configvalue VARCHAR(1024));")
        curs.execute("INSERT INTO config (configname, configvalue) VALUES ('DB_VERSION', '0')")
        con.commit()

    curs.execute("SELECT configvalue FROM config WHERE configname = 'DB_VERSION'")
    version = curs.fetchone()[0]

    if version == '0':
        curs.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='downloaded';")

        if curs.fetchone()[0] == 0:
            curs.execute("CREATE TABLE downloaded (id INTEGER PRIMARY KEY AUTOINCREMENT, uuid CHAR(36), url VARCHAR(1024));")
        curs.execute("UPDATE config SET configvalue = '1' WHERE configname = 'DB_VERSION';")

        con.commit()
        version = '1'

    if version == '1':
        curs.execute("""
          CREATE TABLE podcast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid CHAR(36),
            name VARCHAR(1024),
            url VARHCAR(1024),
            min_size INT,
            max_size INT,
            destination VARCHAR(1024),
            min_duration INT,
            max_duration INT,
            published_time_before INT,
            published_time_after INT,
            enabled BIT
          );""")
        
        # Please, do not add foreign key between id/uuid in podcast and id/uuid in downloaded. If you remove a podcast, the download history is kept.
        # I may add it later, as the history has no interest but if you want to re-add an existing podcast. As the id/uuid will not be the same on second addition, a manual update will be needed in database file.
        # If you plan to add it, please don't add it here, create a new version of database and create it as a normal database upgrade process, so existings DB will be correctly updated.

        curs.execute("UPDATE config SET configvalue = '2' WHERE configname = 'DB_VERSION';")
    
        con.commit()

        if exists(self.config_file):
            config_data = open(self.config_file, mode="r")
            config = json.loads(config_data.read())
            config_data.close()
        else:
            config = json.loads("{ }")

        for key in config:
            url = config[key].get("url", "")
            name = config[key].get("name", "")
            min_size = config[key].get("min_size", None)
            max_size = config[key].get("max_size", None)
            destination = config[key].get("destination", None)
            min_duration = config[key].get("min_duration", None)
            max_duration = config[key].get("max_duration", None)
            published_time_before = config[key].get("published_time_before", None)
            published_time_after = config[key].get("published_time_after", None)

            if min_size == 0 : min_size = None
            if max_size == 0 : max_size = None
            if min_duration == 0 : min_duration = None
            if max_duration == 0 : max_duration = None
            if published_time_before == 240000 : published_time_before = None
            if published_time_after == 0 : published_time_after = None

            self.add(url = url, name = name, min_size = min_size, max_size = max_size, destination = destination, min_duration = min_duration, max_duration = max_duration, published_time_before = published_time_before, published_time_after = published_time_after, add_uuid = key)
            version = '2'

    con.close()

def get_data(db_file, query):
    con = sqlite3.connect(db_file)
    con.row_factory = sqlite3.Row
    curs = con.cursor()

    curs.execute(query)

    data = curs.fetchall()
    curs.close()
    con.commit()
    con.close()
    return data

def podcast_list(self):
    return get_data(self.db_file, "SELECT id || ' (' || uuid || '): ' || name || CASE enabled WHEN 1 THEN '' ELSE ' (disabled)' END AS pc_detail FROM podcast")

def config_dump(self):
    return get_data(self.db_file, "SELECT * FROM podcast")
    