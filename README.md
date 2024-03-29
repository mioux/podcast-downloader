# podcast-downloader

podcast-downloader is a simple script to download podcast files to a custom directory. Files are renamed like `YYYYMMDD_HHMMSS - Podcast title.ext`

## How to configure

First add a new podcast to follow :

    podcast-downloader add --url="http://example.com/rss.xml" --name="My awesome podcast"

This command will create your config and database file in ~/.config/podcast-downloader/podcast-downloader.sqlite3. I have removed the `podcast-downloader.cfg` to have only one file to manage. The database has no password, so you can access it with any compatible client.

You can check with `podcast-downloader dump-config`

Add as many podcasts as you want.

Start the downloads by starting the program without arguments. `podcast-downloader`

Beware of running web server through `podcast-downloader web` instead of flask, or at least, start `podcast-downloader` without arguments after an upgrade, to ensure database is correctly updated

You can configure the app through the web server. It uses internal python's web server AND MUST NOT BE SET AS WORLDWIDE ACCESSIBLE ! There is no security set, no password protection, and it should easily used to download mallicious files on your computer.

There is a `podcast-downlader-web.bat` and a `podcast-downlader-web.sh` as helper to start web server

## Needed dependencies

You need these packages to have this script work. Install it either via your distribution packages or pip:

- requests
- datefinder
- validators
- feedparser
- Flask
- regex
- dateutil
- Pillow

Example for Fedora 35:

    sudo dnf install python3-requests python3-validators python3-feedparser python3-flask python3-regex python3-dateutil python3-willow
    pip install datefinder

Example for Debian 11:

    sudo apt install python3-requests python3-validators python3-feedparser python3-flask python3-regex python3-dateutil python3-willow
    pip install datefinder

All can be installed via pip:

    pip install datefinder requests validators feedparser Flask regex dateutil Pillow
    #or
    pip install -r requirements.txt

## Help

All --id= paramteres can be either "id" or "uuid". UUID may disapear sometime. It was a "simple" way to create a unique ID for configuration file. Sqlite has an autoincrement which ensure id is unique.

### Global help

    Usage: podcast-downloader <command> [help]
           command is one of:
               add         : Add a new podcast to scrape
               edit        : Edit a podcast
               delete      : Delete a podcast
               list        : List podcast - id: friendly name
               dump-config : Display configuration json style
               dump        : Alias for dump-config
               web         : Starts web server (default port : 8000)
               download    : Download files
           see 'help' subcommand for more information

### Add help

    Usage: podcast-downloader add --url=<url> --name=<name> [--min-size=<size-in-MB>] [--destination=<folder>] [--min-duration=<duration-in-seconds>] [--max-duration=<duration-in-seconds>] [--published-time-before=<time-in-HHMMSS>] [--published-time-after=<time-in-HHMMSS>]
        --url=<url>                             : URL of podcast
        --name=<name>                           : Friendly name
        --min-size=<size-in-MB>                 : Don't download file if size is less than this
        --max-size=<size-in-MB>                 : Don't download file if size is more than this
        --min-duration=<duration-in-seconds>    : Don't download file if duration is shorter than this
        --max-duration=<duration-in-seconds>    : Don't download file if duration is longer than this
        --published-time-before=<time-in-HHMMSS>: Download file if publication time is before time (Format is 24 hour "HHMMSS" only.)
        --published-time-after=<time-in-HHMMSS> : Download file if publication time is after time (Format is 24 hour "HHMMSS" only.)
        --destination=<folder>                  : Destination folder
        --include=<regular expression>          : Include podcasts whose title matches the regular expression. This uses case insensitive search.
        --exclude=<regular expression>          : Exclude podcasts whose title matches the regular expression. This uses case insensitive search.
        --days=<mon,tue,wed,thu,fri,sat,sun>    : Download only on these days (default is all).

### Edit help

    Usage: podcast-downloader edit --id=<id|uuid> [--url=<url>] [--name=<name>] [--min-size=<size-in-MB>] [--destination=<folder>] [--min-duration=<duration-in-seconds>] [--max-duration=<duration-in-seconds>] [--enabled=<enabled>]
        --id=<id|uuid>                          : ID of podcast to edit
        --url=<url>                             : URL of podcast
        --name=<name>                           : Friendly name
        --min-size=<size-in-MB>                 : Don't download file if size is less than this
        --max-size=<size-in-MB>                 : Don't download file if size is more than this
        --min-duration=<duration-in-seconds>    : Don't download file if duration is shorter than this
        --max-duration=<duration-in-seconds>    : Don't download file if duration is longer than this
        --published-time-before=<time-in-HHMMSS>: Download file if publication time is before time (Format is 24 hour "HHMMSS" only.)
        --published-time-after=<time-in-HHMMSS> : Download file if publication time is after time (Format is 24 hour "HHMMSS" only.)
        --destination=<folder>                  : Destination folder
        --include=<regular expression>          : Include podcasts whose title matches the regular expression. This uses case insensitive search.
        --exclude=<regular expression>          : Exclude podcasts whose title matches the regular expression. This uses case insensitive search.
        --enabled=<enabled>                     : If value is not 0 or empty, then enable podcast
        --days=<mon,tue,wed,thu,fri,sat,sun>    : Download only on these days.

### Delete help

    Usage: podcast-downloader delete --id=<id|uuid>
        --id=<id|uuid> : ID of podcast to delete

### List help

    Usage: podcast-downloader list

### Dump-config help

    Usage: podcast-downloader dump-config

### Web help

    Usage: podcast-downloader web [--port=<port>] [--listen=<ip or URL to listen>] --debug=[1|ON|YES|TRUE]
        Starts web server on port 8000
        --port=<port>                 : Set port to listen on
        --listen=<ip or URL to listen>: Set IP/URL to listen on (not validated, be sure of your value)
        --debug=[1|ON|YES|TRUE]

### Download help

    Usage: podcast-downloader web [--id|uuid=<id|uuid>] [--url=<url of file>]
        Without parameters, same as ./podcast-downloader without arguments
        --id|uuid=<id|uuid>: Download only for <id> or <uuid>. Both are interchangeable (--id can be used with uuid value and --uuid can be used wit id value)
        --url=<url>        : Download only the file identified by the url (mostly used with the history tab)
                             WARNING: Forcing with URL don't apply regex filters
                             WARNING: URL MUST be available in current RSS feed. If your broadcaster removes the link from the feed, the podcast-downloader won't download it. You can still get the link in "downloaded" table