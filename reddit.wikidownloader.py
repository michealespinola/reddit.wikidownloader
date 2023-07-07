import praw
import argparse
import os
import html2text
import prawcore
import time

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("subreddits_list", help="Comma-separated list of subreddit names")
parser.add_argument("reddit_instance_name", help="Name of the Reddit instance (PRAW) as specified in praw.ini")
parser.add_argument("twoFA", nargs="?", default=None, help="Optional two-factor authentication code")
args = parser.parse_args()

subreddits_list = args.subreddits_list.split(',')
reddit_instance_name = args.reddit_instance_name

def login():
    # Connect to Reddit API using praw.ini file
    reddit = praw.Reddit(reddit_instance_name)

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
    if args.subreddits_list.upper() == "*JOINED*":
        # Retrieve the list of subscribed subreddits
        subreddit_names = [subreddit.display_name for subreddit in reddit.user.subreddits(limit=None)]
    else:
        # Manually specified subreddit names
        subreddit_names = args.subreddits_list.split(',')

    sorted_subreddit_names = sorted(subreddit_names, key=str.lower)  # Sort the subreddit names case-insensitively
    return ','.join(sorted_subreddit_names)

def save_wiki_pages(sorted_subreddit_names, reddit):

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

            for page in wiki_pages:
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

        except prawcore.exceptions.Forbidden as error:
            print(f"Error: /r/{subreddit_name}/wiki, {error}")

#       time.sleep(1)  # Pause for 1 second


# Run it
reddit = login()
subreddits = get_subreddits(reddit)

print("Scanning Subreddits:")
print(subreddits)

save_wiki_pages(subreddits.split(','), reddit)
