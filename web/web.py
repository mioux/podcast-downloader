#!/bin/env python3

import os, ctypes, sys, validators, base64, requests, feedparser, json
from flask import Flask, render_template, redirect, session, request, Response
from pcd import pcd
from urllib.parse import unquote


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
    config_dir = os.path.join(os.path.expanduser('~'), ".config", "podcast-downloader")
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
        include = data["include"]
        exclude = data["exclude"]
        download_days = data["total_days_value"]
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
                     enabled=enabled, include=include, exclude=exclude, download_days = download_days)
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
            _pcd.edit(uuid=id, key="include", value=include, flask_update=True)
            _pcd.edit(uuid=id, key="exclude", value=exclude, flask_update=True)
            _pcd.edit(uuid=id, key="download_days", value=download_days, flask_update=True)
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

    has_mon = True
    has_tue = True
    has_wed = True
    has_thu = True
    has_fri = True
    has_sat = True
    has_sun = True
    total_days_value = 127

    if data is not None and "download_days" in data:
        if data["download_days"] is not None:
            total_days_value = 0
            has_mon = False
            has_tue = False
            has_wed = False
            has_thu = False
            has_fri = False
            has_sat = False
            has_sun = False

            if data["download_days"] & 1:
                total_days_value = total_days_value + 1
                has_mon = True

            if data["download_days"] & 2:
                total_days_value = total_days_value + 2
                has_tue = True

            if data["download_days"] & 4:
                total_days_value = total_days_value + 4
                has_wed = True


            if data["download_days"] & 8:
                total_days_value = total_days_value + 8
                has_thu = True


            if data["download_days"] & 16:
                total_days_value = total_days_value + 16
                has_fri = True


            if data["download_days"] & 32:
                total_days_value = total_days_value + 32
                has_sat = True


            if data["download_days"] & 64:
                total_days_value = total_days_value + 64
                has_sun = True

    return render_template('edit.html',
                           found=found,
                           podcast=data,
                           is_new=is_new,
                           edit_id=edit_id,
                           published_time_before_time=published_time_before_time,
                           published_time_after_time=published_time_after_time,
                           has_mon = has_mon,
                           has_tue = has_tue,
                           has_wed = has_wed,
                           has_thu = has_thu,
                           has_fri = has_fri,
                           has_sat = has_sat,
                           has_sun = has_sun,
                           total_days_value = total_days_value)

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

@app.route('/downloadItem/<int:dl_id>/<string:dl_url>')
def downloadItem(dl_id, dl_url):
    _pcd = init_pcd()
    _pcd.dl(dl_id=dl_id, dl_url=base64.b32decode(dl_url).decode("ascii") if dl_url is not None else None)
    return render_template('download.html')

@app.route('/downloadPodcast/<int:dl_id>')
def downloadPodcast(dl_id):
    return downloadItem(dl_id, None)

@app.route('/download')
def download():
    return downloadItem(None, None)


@app.route('/proxy/<string:url_to_call>')
def proxy(url_to_call):
    url_to_call = unquote(url_to_call) # Need to decrypt double encoded URL
    content = requests.get(url_to_call)

    try:
        checkfeed = feedparser.parse(content.text)
        if hasattr(checkfeed, 'feed') == False:
            raise "Not a RSS"
        elif checkfeed["feed"]["title"] is None or checkfeed["feed"]["title"] == "":
            raise "Not a RSS"

    except:
        # Not an RSS, check if json
        try:
            json.loads(content.text)
        except:
            # Not a json : stop here as we are waiting only for json or rss in proxy
            # This reduces the array of attack if the website is worldwide accessible
            # and someone tries to use it as a HTTPx proxy
            raise "Invalid data! Use only for RSS or json api!"

    resp = Response(content)
    resp.headers["Access-Control-Allow-Origin"] = "Same-Origin"

    return content.text

@app.template_filter('b64encode')
def b64encode(input):
    """Custom filter"""
    return base64.b64encode(input).decode("ascii") if input is not None else ""

@app.template_filter('str32encode')
def str32encode(input):
    data = bytes(input, 'utf-8')
    return base64.b32encode(data).decode("ascii") if input is not None else ""
