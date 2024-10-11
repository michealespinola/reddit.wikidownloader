# reddit.wikidownloader

A **P**ython **R**eddit **A**PI **W**rapper (PRAW) script to download all of the accessible wiki pages of multiple Reddit subreddits.

1. Authentication credentials are not hardcoded in the script. Reddit site auth is done in a standard '[praw.ini](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html)' file. You will need to create and use this. Everything else is provided via command line parameters.
1. This will dump all accessible wiki pages into corresponding markdown language files. It will keep the hierarchy of nested document names.
1. Special files can be designated to preserve original formatting. There are (6) that are preserved by default:

    1. `automoderator-schedule` (yaml: automoderator schedule)
    1. `config/automoderator` (yaml: automoderator config)
    1. `config/stylesheet` (css: HTML stylesheet for the subreddit)
    1. `usernotes` (json: Reddit Toolbox usernotes)
    1. `tbsettings` (json: Reddit Toolbox settings)
    1. `toolbox` (json: Reddit Toolbox settings)

## Prerequisites

### Required Modules (that are likely not a part of your default python install)

* `praw`
* `html2text`

#### Other Modules Used (that should be installed by default or with the above Required Prerequisites)

* `argparse`
* `configparser`
* `os`
* `prawcore`
* `time`

#### Install modules with PIP (**P**IP **I**nstalls **P**ackages)

1. [Make sure `pip` is installed](https://pip.pypa.io/en/stable/installation/)
1. [Install `praw`](https://pypi.org/project/praw/)
1. [Install `html2txt`](https://pypi.org/project/html2text/)

#### Commands To Do It All For You

    curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    pip install argparse
    pip install configparser
    pip install html2text
    pip install os
    pip install praw
    pip install prawcore
    pip install time

## Example Command Syntax

### Example #1 (manually specify subreddits)

    python3 reddit.wikidownloader.py <subreddit1>,<subreddit2>,... <praw-site> <optional-2FA>

This will download wiki pages from manually supplied comma-delimited subreddit names.

### Example #2 (dynamically acquire account-joined subreddits)

    python3 reddit.wikidownloader.py *JOINED* <praw-site> <optional-2FA>

This will download wiki pages from dynamically acquired subreddit names based on the account used to authenticate the Reddit site. All subreddits that the account has joined will be processed.

**Note**: Hundreds of joined subreddits can potentially take hours to download depending on the contents of those subreddit wikis.

## Example Command Output For /r/DataHoarder

    # python reddit.wikidownloader.py datahoarder <praw-site> <optional-2FA>

    Scanning subreddits: datahoarder

    Subreddits queued: 1
        API ratelimit: 95 requests per minute

    Saved: wikis/datahoarder/backups.md
    Saved: wikis/datahoarder/ceph.md
    Saved: wikis/datahoarder/cloud.md
    Saved: wikis/datahoarder/config/description.md
    Saved: wikis/datahoarder/config/sidebar.md
    Saved: wikis/datahoarder/config/stylesheet.css
    Saved: wikis/datahoarder/config/submit_text.md
    Saved: wikis/datahoarder/config/welcome_message.md
    Saved: wikis/datahoarder/guides.md
    Saved: wikis/datahoarder/hardware.md
    Saved: wikis/datahoarder/index.md
    Saved: wikis/datahoarder/index/faq.md
    Saved: wikis/datahoarder/index/rules.md
    Saved: wikis/datahoarder/moderatelyhelpfulbot.md
    Saved: wikis/datahoarder/raidvszfs.md
    Saved: wikis/datahoarder/removalreasons.md
    Saved: wikis/datahoarder/repost_sleuth_config.md
    Saved: wikis/datahoarder/software.md
    Saved: wikis/datahoarder/sources.md
    Saved: wikis/datahoarder/sources/essentials.md
    Saved: wikis/datahoarder/zfs.md

    SUMMARY:

                 Runtime : 8 seconds (00:00:08)
       Applied ratelimit : 95 requests per minute
    Subreddits processed : 1 (this run)
        Wikis downloaded : 1
          Markdown files : 20
             Other files : 1
             Total files : 21
            Average rate : 2.68 files per second
            Size on disk : 145.23 KB

    Archived 'wikis' directory to 'wikis_2024-10-11T13-46-10'

## Example Saved Content For /r/DataHoarder

    # tree -a wikis_2024-10-11T13-46-10
    wikis_2024-10-11T13-46-10
    └── datahoarder
        ├── backups.md
        ├── ceph.md
        ├── cloud.md
        ├── config
        │   ├── description.md
        │   ├── sidebar.md
        │   ├── stylesheet.css
        │   ├── submit_text.md
        │   └── welcome_message.md
        ├── guides.md
        ├── hardware.md
        ├── index
        │   ├── faq.md
        │   └── rules.md
        ├── index.md
        ├── moderatelyhelpfulbot.md
        ├── raidvszfs.md
        ├── removalreasons.md
        ├── repost_sleuth_config.md
        ├── software.md
        ├── sources
        │   └── essentials.md
        ├── sources.md
        └── zfs.md

    5 directories, 21 files

## Common Errors

* `Error: PRAW (invalid_grant error processing request)`  
  > This most likely means that you miss-entered your 2FA code. However, you should also verify your credentials in the `praw.ini` file.

* `Error: /r/<subreddit>/wiki, (HTTP 403: Forbidden)`  
  > This most likely means that the subreddit's wiki is disabled. It's possible that you might be banned from that subreddit's wiki.

* `Error: /r/<subreddit>/wiki, (HTTP 429: Too Many Requests)`  
  > This means that you exceeded the rate limit of your connection to Reddit's API. The script exits to prevent you from being banned. Try lowering the hardcoded `REQUESTS_PER_MINUTE` script variable, or stop using Reddit with the same account until the script is finished.

* `Error: '<name>' site section does not exist in praw.ini, exiting...`  
  > This means that the `praw.ini` file is not properly set up. Look at the '[example-praw.ini](https://github.com/michealespinola/reddit.wikidownloader/blob/main/example-praw.ini)' file for required fields and formatting examples.

* `FileNotFoundError: [Errno 2] No such file or directory: 'wikis/<subreddit>/config/automoderator.yaml'`  
  > This most likely means that you are running an older version of the script that did not properly automatically create subdirectories in certain operating system environments. **This has been fixed**.
