# reddit.wikidownloader
A Python PRAW script to download all of the accessible wiki pages of multiple Reddit subreddits.

1. Nothing is hardcoded in the script. Reddit instance auth is done in a standard [praw.ini](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html) file. Everything else is provided via command line parameters.
1. This will dump all accessible wiki pages into corresponding markdown language files. It will keep the heirarchy of nested document names.
1. Special files can be designated to preserve original formatting. There are (2) that are preserved by default:
   1. `config/stylesheet` (html: stylesheet for the subreddit)
   1. `usernotes` (json: Reddit Toolbox usernotes)

## Example command syntax

    python3 reddit.wikidownloader.py <subreddit1>,<subreddit2>,... <praw-instance> <optional-2FA>

## Example command output for /r/DataHoarder

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

## Example saved content for /r/DataHoarder

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

## Common errors

1. `prawcore.exceptions.OAuthException: invalid_grant error processing request`  
*This most likely means that you misentered your 2FA code. You should also verify your credentials in the `praw.ini` file.*
