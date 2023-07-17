#!/bin/env python3

import os, ctypes, sys, validators
from flask import Flask, render_template, redirect, session, request
from pcd import pcd
import uuid

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def is_admin():
    try:
        check_admin = (os.getuid() == 0)
    except AttributeError:
        check_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return check_admin

def web_usage():
    exe_name = os.path.basename(sys.argv[0])

    print ("Usage: " + exe_name + " web [--port=<port>] [--listen=<ip or URL to listen>] --debug=[1|ON|YES|TRUE]")
    print ("    Starts web server on port 8000")
    print ("    --port=<port>                 : Set port to listen on")
    print ("    --listen=<ip or URL to listen>: Set IP/URL to listen on (not validated, be sure of your value)")
    print ("    --debug=[1|ON|YES|TRUE]       : ")

def start_web_werver(port, listen, debug, config_file, db_file):

    _pcd = pcd.pcd(config_file, db_file)
    _pcd.migrate_db()

    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError("Port is invalid")
        if port < 1024 and is_admin() == False:
            raise ValueError("Try to use privileged port without administrative rights")
    except Exception as ex:
        port = 8000
        print(ex.args, file=sys.stderr)
        print("Port set to 8000", file=sys.stderr)

    try:
        app.run(host=listen, port=port, debug=debug)
    except Exception as ex:
        print(ex.args, file=sys.stderr)
        print("Cannot start webapp server", file=sys.stderr)

def init_pcd():
    config_dir = os.path.join(os.environ["HOME"], ".config", "podcast-downloader")
    config_file = os.path.join(config_dir, "podcast-downloader.cfg") # Not used, for compatibility with very early version
    db_file = os.path.join(config_dir, "podcast-downloader.sqlite3")

    return pcd.pcd(config_file, db_file)


template_folder = os.path.join(os.path.dirname(__file__), "templates")
template_folder = os.path.realpath(template_folder)

static_folder = os.path.join(os.path.dirname(__file__), "statics")
static_folder = os.path.realpath(static_folder)


app = Flask("Podcast downloader webapp control",
                template_folder=template_folder,
                static_folder=static_folder)

@app.route('/')
def index():
    return redirect("/list", code=302)

@app.route('/delete/<string:delete_id>', methods = ['GET', 'POST'])
def delete(delete_id):

    _pcd = init_pcd()
    podcast = _pcd.web_podcast_detail(delete_id)

    if request.method == "POST":
        delete_id = request.form["delete_id"]
        _pcd.delete(delete_id)
        return redirect("/list", code=302)

    if podcast is None:
        return redirect("/list", code=302)

    return render_template('delete.html', name=podcast["name"], delete_id=podcast["id"])

@app.route('/edit/<string:edit_id>', methods=['GET', 'POST'])
def edit(edit_id):

    data = None
    is_new = 0
    found = 1

    _pcd = init_pcd()

    if edit_id == "new":
        is_new = 1
        edit_id = ""

    if request.method == "POST":
        data = request.form

        valid = True

        id = data["id"]
        url = data["url"]
        name = data["name"]
        min_size = int(data["min_size"]) if data["min_size"].isdecimal() else 0
        max_size = int(data["max_size"]) if data["max_size"].isdecimal() else 0
        min_duration = int(data["min_duration"]) if data["min_duration"].isdecimal() else 0
        max_duration = int(data["max_duration"]) if data["max_duration"].isdecimal() else 0
        published_time_before = data["published_time_before"]
        published_time_after = data["published_time_after"]
        edit_id = data["id"]
        destination = data["destination"]
        enabled = False
        if "enabled" in data:
            enabled = data["enabled"].lower() == "on"

        if validators.url(url) == False:
            valid = False

        published_time_before_int = 240000
        if (published_time_before != ""): published_time_before_int = int(published_time_before.split(':')[0]) * 10000 + int(published_time_before.split(':')[1]) * 100 + int(published_time_before.split(':')[2])
        published_time_after_int = 0
        if (published_time_after != ""): published_time_after_int = published_time_after_int = int(published_time_after.split(':')[0]) * 10000 + int(published_time_after.split(':')[1]) * 100 + int(published_time_after.split(':')[2])

        # podcast-downloader uses 240000 as "no published_time_before", but time input is 00:00:00 to 23:29:29, so 00:00:00 becomes 240000
        if published_time_before_int == 0: published_time_before_int = 240000

        if  published_time_before_int < 0 or published_time_after_int > 240000:
            valid = False

        if min_size < 0 or max_size < 0:
            valid = False

        if min_duration < 0 or max_duration < 0:
            valid = False

        if valid == True and is_new == 1:
            _pcd.add(url=url, name=name, min_size=min_size,
                     max_size=max_size, min_duration=min_duration, max_duration=max_duration,
                     published_time_before=published_time_before_int, published_time_after=published_time_after_int, destination=destination,
                     enabled=enabled)
            return redirect("/list", code=302)
        elif valid == True:
            _pcd.edit(uuid=id, key="name", value=name, flask_update=True)
            _pcd.edit(uuid=id, key="url", value=url, flask_update=True)
            _pcd.edit(uuid=id, key="min_size", value=min_size, flask_update=True)
            _pcd.edit(uuid=id, key="max_size", value=max_size, flask_update=True)
            _pcd.edit(uuid=id, key="min_duration", value=min_duration, flask_update=True)
            _pcd.edit(uuid=id, key="max_duration", value=max_duration, flask_update=True)
            _pcd.edit(uuid=id, key="published_time_before", value=published_time_before_int, flask_update=True)
            _pcd.edit(uuid=id, key="published_time_after", value=published_time_after_int, flask_update=True)
            _pcd.edit(uuid=id, key="destination", value=destination, flask_update=True)
            _pcd.edit(uuid=id, key="enabled", value=enabled, flask_update=True)
            return redirect("/list", code=302)

    else:
        data = None

        if is_new == 0:
            data = _pcd.web_podcast_detail(edit_id)

        if data is None:
            found = 0

    published_time_before_time = ""
    published_time_after_time = ""

    if data is not None and "published_time_before" in data:
        published_time_before_time = "000000{0}".format( data["published_time_before"] )[-6:]
        published_time_before_time = published_time_before_time[:2] + ":" + published_time_before_time[2:4] + ":" + published_time_before_time[-2:]
        # podcast-downloader uses 240000 as "no published_time_before", but time input is 00:00:00 to 23:29:29, so 240000 becomes 00:00:00
        if published_time_before_time == "24:00:00": published_time_before_time = "00:00:00"
    if data is not None and "published_time_after" in data:
        published_time_after_time = "000000{0}".format(data["published_time_after"])[-6:]
        published_time_after_time = published_time_after_time[:2] + ":" + published_time_after_time[2:4] + ":" + published_time_after_time[-2:]
        if published_time_after_time == "24:00:00": published_time_after_time = "00:00:00"

    return render_template('edit.html', found=found, podcast=data, is_new=is_new, edit_id=edit_id, published_time_before_time=published_time_before_time, published_time_after_time=published_time_after_time)

@app.route('/list')
def list():
    _pcd = init_pcd()
    podcast_list = _pcd.web_list()
    return render_template('list.html', podcast_list=podcast_list)

@app.route('/history')
def history():
    _pcd = init_pcd()
    history = _pcd.web_history()
    return render_template('history.html', history=history)

@app.route('/download')
def download():
    _pcd = init_pcd()
    _pcd.dl()
    return render_template('download.html')