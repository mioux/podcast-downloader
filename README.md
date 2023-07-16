# podcast-downloader

podcast-downloader is a simple script to download podcast files to a custom directory. Files are renamed like `YYYYMMDD_HHMMSS - Podcast title.ext`

## How to configure

First add a new podcast to follow :

    podcast-downloader add --url="http://example.com/rss.xml" --name="My awesome podcast"

This command will create your config and database file in ~/.config/podcast-downloader/podcast-downloader.sqlite3. I have removed the `podcast-downloader.cfg` to have only one file to manage. The database has no password, so you can access it with any compatible client.

You can check with `podcast-downloader dump-config`

Add as many podcasts as you want.

Start the downloads by starting the program without arguments. `podcast-downloader`

## Needed dependencies

You need these packages to have this script work. Install it either via your distribution packages or pip:

- requests
- datefinder
- validators
- feedparser
- Flask

Example for Fedora 35:

    sudo dnf install python3-requests python3-validators python3-feedparser python3-flask
    pip install datefinder

Example for Debian 11:

    sudo apt install python3-requests python3-validators python3-feedparser python3-flask
    pip install datefinder

All can be installed via pip:

    pip install datefinder requests validators feedparser Flask
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
               web         : Starts web server (default port : 8000)
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
        --destination=<folder>

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
        --enabled=<enabled>                     : If value is not 0 or empty, then enable podcast

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
