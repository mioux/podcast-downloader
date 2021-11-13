# podcast-downloader

podcast-downloader is a simple script to download podcast files to a custom directory. Files are renamed like `YYYYMMDD_HHMMSS - Podcast title.ext`

## How to configure

First add a new podcast to follow :

    podcast-downloader add --url="http://example.com/rss.xml" --name="My awesome podcast"

This command will create your config file like this (on a single line)

    {
        '065b203b-2033-4b02-b1b8-831361f4bfac': {
            'url': 'http://example.com/rss.xml',
            'name': 'My awesome podcast',
            'min_size': 0,
            'destination': ''
        }
    }

You can check with `podcast-downloader dump-config`

Add as many podcasts as you want.

Start the downloads by starting the program without arguments. `podcast-downloader`

## Needed dependencies

You need these packages to have this script work. Install it either via your distribution packages or pip:

- requests
- datefinder
- validators
- feedparser

Example for Fedora 35:

    sudo dnf install python3-requests python3-validators python3-feedparser
    pip install datefinder

Example for Debian 11:

    sudo apt install python3-requests python3-validators python3-feedparser
    pip install datefinder

All can be installed via pip:

    pip install datefinder requests validators feedparser

## Help

### Global help

    Usage: podcast-downloader <command> [help]
           command is one of:
               add         : Add a new podcast to scrape
               edit        : Edit a podcast
               delete      : Delete a podcast
               list        : List podcast - id: friendly name
               dump-config : Display the raw config file
           see 'help' subcommand for more information

### Add help

    Usage: podcast-downloader add --url=<url> --name=<name> [--min-size=<size-in-MB>] [--destination=<folder>]
        --url=<url>            : URL of podcast
        --name=<name>          : Friendly name
        --min-size=<size-in-MB>: Don't download file if size is less than this
        --max-size=<size-in-MB>: Don't download file if size is more than this
        --destination=<folder> : Destination folder

### Edit help

    Usage: podcast-downloader add --url=<url> --name=<name> [--min-size=<size-in-MB>] [--destination=<folder>]
        --id=<uuid>            : ID of podcast to edit
        --url=<url>            : New URL of podcast
        --name=<name>          : New friendly name
        --min-size=<size-in-MB>: New minimum size
        --max-size=<size-in-MB>: New maximum size
        --destination=<folder> : Destination folder

### Delete help

    Usage: podcast-downloader delete --id=<uuid>
        --id=<uuid> : ID of podcast to delete

### List help

    Usage: podcast-downloader list

### Dump-conffig help

    Usage: podcast-downloader dump-config
