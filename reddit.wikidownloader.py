# Reddit Wiki Downloader
#
# Description: Download specific or all joined subreddit wiki documents
# Version: 3.2.1
# Author: @michealespinola https://github.com/michealespinola/reddit.wikidownloader
# Date: March 16, 2024

import argparse
import configparser
import html2text
import os
import praw
import prawcore
import time
from datetime import datetime

#BEGIN TIME CALCULATION
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
requests_per_minute = 95

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

        # Sort the subreddit names case-insensitively
        sorted_subreddit_names = sorted(subreddit_names, key=str.lower)
        return ','.join(sorted_subreddit_names)

    except prawcore.exceptions.OAuthException as error:
        print("\r\033[K", end="", flush=True)
        print(f"Error: PRAW ({error})")
        print(f"OAUTH: Authorization failed, exiting...\n")
        exit(1)

wikis_directory = os.path.join(os.getcwd(), 'wikis')

def save_wiki_pages(sorted_subreddit_names, reddit):
    # Initialize a timestamp for the start of the current minute and a counter for requests made in the current minute
    current_minute_start = time.time()
    requests_in_current_minute = 0

    for subreddit_name in sorted_subreddit_names:
        try:
            subreddit = reddit.subreddit(subreddit_name)

            # Create a directory to save the wiki pages
            output_directory = os.path.join('wikis', subreddit_name)
            # Create directory if it doesn't exist
            os.makedirs(output_directory, exist_ok=True)

            # Define the dictionary of wiki pages to exclude from conversion
            excluded_wiki_pages = {
                "automoderator-schedule": "yaml", # YAML automoderator schedule
                "config/automoderator": "yaml",   # YAML automoderator config
                "config/stylesheet": "css",       # HTML subreddit stylesheet
                "usernotes": "json",              # JSON Toolbox per-user notes
                "tbsettings": "json",             # JSON Toolbox settings
                "toolbox": "json",                # JSON Toolbox settings
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
                if requests_in_current_minute >= requests_per_minute:
                    # Calculate the remaining time in the current minute
                    remaining_time = 60 - elapsed_seconds
                    # Format the remaining_time to display with no decimal places
                    remaining_time_formatted = "{:.0f}".format(remaining_time)
                    print(f"PAUSE: Reached {requests_per_minute} API requests per minute (wait {remaining_time_formatted}s)", end="", flush=True)
                    time.sleep(1)

                    for i in range(int(remaining_time), 0, -1):
                        print("\r\033[K", end="", flush=True)
                        print(f"PAUSE: Reached {requests_per_minute} API requests per minute (wait {i}s)", end="", flush=True)
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

        #CATCH EXCEPTIONS
        except prawcore.exceptions.Forbidden as error:
            print(f"Error: /r/{subreddit_name}/wiki (HTTP 403: Forbidden)")
            requests_in_current_minute += 1
        except prawcore.exceptions.TooManyRequests as error:
            print(f"Error: /r/{subreddit_name}/wiki (HTTP 429: Too Many Requests)")
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
num_subreddits = len(subreddits.split(','))
print("\r\033[K", end="", flush=True)

print(f"Scanning subreddits: {subreddits}\n")
print(f"Subreddits queued: {num_subreddits}")
print(f"    API ratelimit: {requests_per_minute} requests per minute\n")
save_wiki_pages(subreddits.split(','), reddit)

#CLEANUP EMPTY/INACCESSIBLE SUBREDDITS
if os.path.exists(wikis_directory):
    for root, dirs, files in os.walk(wikis_directory, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # Check if the directory starts with or is a subdirectory of wikis_directory
            if dir_path.startswith(wikis_directory):
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

# Count directories and .md files in the 'wikis' directory
if os.path.exists('wikis'):
    directory_count = sum(os.path.isdir(os.path.join('wikis', d)) for d in os.listdir('wikis'))

    # Function to count files in a directory and its subdirectories recursively
    def count_files_in_directory(directory):
        file_count = 0
        for root, _, files in os.walk(directory):
            file_count += len(files)
        return file_count

    # Function to count ".md" files in a directory and its subdirectories recursively
    def count_md_files_in_directory(directory):
        md_file_count = 0
        for root, _, files in os.walk(directory):
            md_file_count += sum(f.endswith('.md') for f in files)
        return md_file_count

    # Calculate the total count of all files saved
    total_file_count = count_files_in_directory('wikis')
    # Calculate the total count of ".md" files
    md_file_count = count_md_files_in_directory('wikis')
    # Calculate the total count of "other" files
    other_file_count = total_file_count - md_file_count

# Function to calculate the total size of all files in a directory and its subdirectories recursively
def calculate_total_size(directory):
    total_size = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size

# Calculate the total size of all files in the 'wikis' directory
if os.path.exists('wikis'):
    total_size_bytes = calculate_total_size('wikis')
    # Function to convert bytes to a human-readable format
    def convert_bytes_to_human_readable(bytes):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        i = 0
        while bytes >= 1024 and i < len(suffixes)-1:
            bytes /= 1024.0
            i += 1
        return f"{bytes:.2f} {suffixes[i]}"
    total_size_readable = convert_bytes_to_human_readable(total_size_bytes)

#CALCULATE RUNTIME
end_time = time.time()
elapsed_time = end_time - start_time
rounded_elapsed_time = int(elapsed_time) + (elapsed_time > int(elapsed_time))
# Calculate hours, minutes, and seconds
std_hours = rounded_elapsed_time // 3600
std_minutes = (rounded_elapsed_time % 3600) // 60
std_seconds = rounded_elapsed_time % 60

# Calculate average files downloaded per minute
if elapsed_time < 60:
    average_files_per_second = total_file_count / elapsed_time
    average_files = f"{average_files_per_second:.2f} files per second"
else:
    elapsed_time_minutes = elapsed_time / 60
    average_files_per_minute = total_file_count / elapsed_time_minutes
    average_files = f"{average_files_per_minute:.2f} files per minute"

# PRINT SUMMARY
print(f"\nSUMMARY:\n")
print(f"             Runtime : {rounded_elapsed_time} seconds ({std_hours:02}:{std_minutes:02}:{std_seconds:02})")
print(f"   Applied ratelimit : {requests_per_minute} requests per minute")
print(f"Subreddits processed : {num_subreddits} (this run)")
print(f"    Wikis downloaded : {directory_count}")
print(f"      Markdown files : {md_file_count}")
print(f"         Other files : {other_file_count}")
print(f"         Total files : {total_file_count}")
print(f"        Average rate : {average_files}")
print(f"        Size on disk : {total_size_readable}\n")

if os.path.exists('wikis'):
    timestamp = datetime.now().isoformat(timespec='seconds').replace(':', '-')
    new_directory_name = f"wikis_{timestamp}"
    os.rename('wikis', new_directory_name)
    print(f"Archived 'wikis' directory to '{new_directory_name}'\n")
