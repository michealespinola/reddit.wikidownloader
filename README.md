# reddit.wikidownloader
A Python PRAW script to download all of the accessible wiki pages of a Reddit subreddit

1. Nothing is hardcoded in the script. Reddit instance auth is done in a standard [praw.ini](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html) file. Everything else is provided via command line parameters.
1. This will dump all accessible wiki pages into corresponding markdown language files. It will keep the heirarchy of nested document names.
1. Special files can be designated to preserve original formatting. There are (2) that are preserved by default:
   1. `config/stylesheet` (html: stylesheet for the subreddit)
   1. `usernotes` (json: Reddit Toolbox usernotes)

## Example command syntax

    python3 reddit.wikidownloader.py <subreddit1>,<subreddit2>,<subreddit3>,... <praw-instance> <optional-2FA>

## Example command output for /r/DataHoarder

    # python3 reddit.wikidownloader.py datahoarder <praw-instance> <optional-2FA>
    Saved: datahoarder_wiki/backups.md
    Saved: datahoarder_wiki/ceph.md
    Saved: datahoarder_wiki/cloud.md
    Saved: datahoarder_wiki/config/description.md
    Saved: datahoarder_wiki/config/sidebar.md
    Saved: datahoarder_wiki/config/stylesheet.html
    Saved: datahoarder_wiki/config/submit_text.md
    Saved: datahoarder_wiki/config/welcome_message.md
    Saved: datahoarder_wiki/guides.md
    Saved: datahoarder_wiki/hardware.md
    Saved: datahoarder_wiki/index.md
    Saved: datahoarder_wiki/index/faq.md
    Saved: datahoarder_wiki/index/rules.md
    Saved: datahoarder_wiki/moderatelyhelpfulbot.md
    Saved: datahoarder_wiki/raidvszfs.md
    Saved: datahoarder_wiki/removalreasons.md
    Saved: datahoarder_wiki/repost_sleuth_config.md
    Saved: datahoarder_wiki/software.md
    Saved: datahoarder_wiki/sources.md
    Saved: datahoarder_wiki/sources/essentials.md
    Saved: datahoarder_wiki/zfs.md

## Example saved content for /r/DataHoarder

    # tree -a  datahoarder_wiki
    datahoarder_wiki
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
    
    3 directories, 21 files
