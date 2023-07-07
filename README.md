# reddit.wikidownloader
A **P**ython **R**eddit **A**PI **W**rapper (PRAW) script to download all of the accessible wiki pages of multiple Reddit subreddits.

1. Nothing is hardcoded in the script. Reddit instance auth is done in a standard [praw.ini](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html) file. Everything else is provided via command line parameters.
1. This will dump all accessible wiki pages into corresponding markdown language files. It will keep the heirarchy of nested document names.
1. Special files can be designated to preserve original formatting. There are (3) that are preserved by default:
   1. `config/automoderator` (yaml: automoderator config)
   1. `config/stylesheet` (html: stylesheet for the subreddit)
   1. `usernotes` (json: Reddit Toolbox usernotes)

## Prerequisites

### Required Modules (that are likely not a part of your default python install)

* `praw`
* `html2text`

#### Other Modules Used (that should be installed by default or with the above Required Prerequisites):

* argparse
* os
* prawcore
* time

#### Install modules with PIP (**P**IP **I**nstalls **P**ackages)

1. [Make sure `pip` is installed](https://pip.pypa.io/en/stable/installation/)
2. [Install `praw`](https://pypi.org/project/praw/)
3. [Install `html2txt`](https://pypi.org/project/html2text/)

#### Commands To Do It All For You

    curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    pip install praw
    pip install html2text

## Example Command Syntax

### Example #1 (manually specifiy subreddits)

    python3 reddit.wikidownloader.py <subreddit1>,<subreddit2>,... <praw-instance> <optional-2FA>

This will download wiki pages from manually supplied subreddit names.

### Example #2 (dynamically aquire account-joined subreddits)

    python3 reddit.wikidownloader.py *JOINED* <praw-instance> <optional-2FA>

This will download wiki pages from dynamically aquired subreddit names based on the account used to authenticate the Reddit instance. All subreddits that the account has joined will be processed.

Note: Hundreds of joined subreddits can potentially take hours to download depending on the contents of those subreddit wikis.

## Example Command Output For /r/DataHoarder

    # python3 reddit.wikidownloader.py datahoarder <praw-instance> <optional-2FA>
    Saved: wikis/datahoarder/backups.md
    Saved: wikis/datahoarder/ceph.md
    Saved: wikis/datahoarder/cloud.md
    Saved: wikis/datahoarder/config/description.md
    Saved: wikis/datahoarder/config/sidebar.md
    Saved: wikis/datahoarder/config/stylesheet.html
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

## Example Saved Content For /r/DataHoarder

    # tree -a wikis
    wikis
    └── datahoarder
        ├── backups.md
        ├── ceph.md
        ├── cloud.md
        ├── config
        │   ├── description.md
        │   ├── sidebar.md
        │   ├── stylesheet.html
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

    4 directories, 21 files

## Common Errors

1. `Error: /r/<subreddit>/wiki, received 403 HTTP response`  
   * *This most likely means that the subreddit's wiki is disabled.*
2. `prawcore.exceptions.OAuthException: invalid_grant error processing request`  
   * *This most likely means that you misentered your 2FA code. You should also verify your credentials in the `praw.ini` file.*
3. `FileNotFoundError: [Errno 2] No such file or directory: 'wikis/<subreddit>/config/automoderator.yaml'`  
   * *This most likely means that you are running an older version of the script that did not properly automatically create subdirectories in certain operating system environments. **This has been fixed**.*
