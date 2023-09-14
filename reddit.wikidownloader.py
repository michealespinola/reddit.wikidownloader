# Reddit Wiki Downloader
#
# Description: Download specific or all joined subreddit wiki documents
# Version: 3.0.0
# Author: @michealespinola https://github.com/michealespinola/reddit.wikidownloader
# Date: September 14, 2023

import argparse
import configparser
import html2text
import os
import praw
import prawcore
import time

start_time = time.time()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("subreddits_list",                help="Comma-separated list of subreddit names")
parser.add_argument("praw_site_name",                 help="Name of the Reddit site as specified in praw.ini")
parser.add_argument("twoFA", nargs="?", default=None, help="Optional two-factor authentication code")
args = parser.parse_args()

subreddits_list = args.subreddits_list.split(',')
praw_site_name = args.praw_site_name

if not os.path.exists('praw.ini'):
    print(f"\nError: 'praw.ini' is missing, exiting...\n")
    exit(1)
else:
    # Initialize a configparser object and read the praw.ini file
    config = configparser.ConfigParser()
    config.read('praw.ini')
    if not config.has_section(praw_site_name):
        print(f"\nError: '{praw_site_name}' site section does not exist in praw.ini, exiting...\n")
        exit(1)

# Reddit API rate limits max: 10 for non-OAuth clients
# Reddit API rate limits max: 100 for OAuth clients
REQUESTS_PER_MINUTE = 90

def login():
    # Connect to Reddit API using praw.ini file
    reddit = praw.Reddit(praw_site_name)
    # Modify the password if the twoFA is provided
    if args.twoFA:
        modified_password = "{}:{}{}".format(reddit.config.password, args.twoFA, '')
        reddit = praw.Reddit(
            client_id=reddit.config.client_id,
            client_secret=reddit.config.client_secret,
            username=reddit.config.username,
            password=modified_password,
            user_agent=reddit.config.user_agent
        )
    return reddit

def get_subreddits(reddit):
    try:
        if args.subreddits_list.upper() == "*JOINED*":
            # Retrieve the list of subscribed subreddits
            subreddit_names = [subreddit.display_name for subreddit in reddit.user.subreddits(limit=None)]
        else:
            # Manually specified subreddit names
            subreddit_names = args.subreddits_list.split(',')

        sorted_subreddit_names = sorted(subreddit_names, key=str.lower)  # Sort the subreddit names case-insensitively
        return ','.join(sorted_subreddit_names)

    except prawcore.exceptions.OAuthException as error:
        print("\r\033[K", end="", flush=True)
        print(f"Error: PRAW ({error})")
        print(f"OAUTH: Authorization failed, exiting...\n")
        exit(1)

def save_wiki_pages(sorted_subreddit_names, reddit):

    # Initialize a timestamp for the start of the current minute and a counter for requests made in the current minute
    current_minute_start = time.time()
    requests_in_current_minute = 0

    for subreddit_name in sorted_subreddit_names:
        try:
            subreddit = reddit.subreddit(subreddit_name)

            # Create a directory to save the wiki pages
            output_directory = os.path.join('wikis', subreddit_name)
            os.makedirs(output_directory, exist_ok=True)  # Create directory if it doesn't exist

            # Define the dictionary of wiki pages to exclude from conversion
            excluded_wiki_pages = {
                "config/automoderator": "yaml",  # YAML automoderator config
                "config/stylesheet": "html",     # HTML subreddit stylesheet
                "usernotes": "json",             # JSON Toolbox per-user notes
            }

            # Fetch all wiki pages
            wiki_pages = subreddit.wiki
            requests_in_current_minute += 1

            for page in wiki_pages:
                # Check if the current minute has elapsed since the last request
                current_time = time.time()
                elapsed_seconds = current_time - current_minute_start

                if elapsed_seconds >= 60:
                    # Reset the counter and timestamp for the new minute
                    current_minute_start = current_time
                    requests_in_current_minute = 0

                # Check if we have made 60 requests in the current minute
                if requests_in_current_minute >= REQUESTS_PER_MINUTE:
                    # Calculate the remaining time in the current minute
                    remaining_time = 60 - elapsed_seconds
                    # Format the remaining_time to display with no decimal places
                    remaining_time_formatted = "{:.0f}".format(remaining_time)
                    print(f"PAUSE: Reached {REQUESTS_PER_MINUTE} API requests per minute (wait {remaining_time_formatted}s)", end="", flush=True)
                    time.sleep(1)

                    for i in range(int(remaining_time), 0, -1):
                        print("\r\033[K", end="", flush=True)
                        print(f"PAUSE: Reached {REQUESTS_PER_MINUTE} API requests per minute (wait {i}s)", end="", flush=True)
                        time.sleep(1)

                    current_minute_start = time.time()
                    requests_in_current_minute = 0
                    print("\r\033[K", end="", flush=True)

                # Check if the page is excluded from conversion
                if page.name in excluded_wiki_pages:
                    # Save the wiki page without conversion
                    output_path = os.path.join(output_directory, page.name + '.' + excluded_wiki_pages[page.name])

                    # Create the full directory path if it doesn't exist
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(page.content_md)

                    print(f'Saved: {output_path}')
                else:
                    # Check if the page has HTML content
                    if page.content_html:
                        # Convert content to markdown format using html2text
                        content_md = html2text.html2text(page.content_html)
                    else:
                        # Skip conversion if the page has no HTML content
                        continue

                    # Check if the page is a nested page
                    if '/' in page.name:
                        # Create subfolders if needed
                        subfolder = os.path.join(output_directory, os.path.dirname(page.name))
                        os.makedirs(subfolder, exist_ok=True)
                        output_path = os.path.join(subfolder, os.path.basename(page.name) + '.md')
                    else:
                        output_path = os.path.join(output_directory, page.name + '.md')

                    # Create the full directory path if it doesn't exist
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Save the wiki page as a markdown document
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content_md)

                    print(f'Saved: {output_path}')

                # Increment the counter for requests in the current minute
                requests_in_current_minute += 1

        except prawcore.exceptions.Forbidden as error:
            print(f"Error: /r/{subreddit_name}/wiki, (HTTP 403: Forbidden)")
            requests_in_current_minute += 1

        except prawcore.exceptions.TooManyRequests as error:
            print(f"Error: /r/{subreddit_name}/wiki, (HTTP 429: Too Many Requests)")
            print(f"LIMIT: Per minute rate limit exceeded, exiting...\n")
            exit(1)

        except Exception as error:
            print(f"Error: {error}")

# Run it
print(f"\nAuthenticating...", end="", flush=True)
reddit = login()
print("\r\033[K", end="", flush=True)

print(f"Loading subreddits...", end="", flush=True)
subreddits = get_subreddits(reddit)
print("\r\033[K", end="", flush=True)

print(f"Scanning Subreddits: {subreddits}")
print(f"API ratelimit: {REQUESTS_PER_MINUTE} requests per minute\n")
# exit()
save_wiki_pages(subreddits.split(','), reddit)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Script took {elapsed_time:.2f} seconds to run.")
