import praw
import argparse
import os
import html2text

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("subreddit", help="Name of the subreddit")
parser.add_argument("reddit_instance", help="Name of the Reddit instance (PRAW) as specified in praw.ini")
parser.add_argument("twoFA", nargs="?", default=None, help="Optional two-factor authentication code")
args = parser.parse_args()

sub_name = args.subreddit
reddit_instance_name = args.reddit_instance

def save_wiki_pages(sub_name, reddit_instance_name):
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

    subreddit = reddit.subreddit(sub_name)

    # Create a directory to save the wiki pages
    output_directory = sub_name + '_wiki'
    os.makedirs(output_directory, exist_ok=True)

    # Define the dictionary of wiki pages to exclude from conversion
    excluded_wiki_pages = {
        "config/stylesheet": "html",  # HTML subreddit stylesheet
        "usernotes": "json",          # JSON Toolbox per-user notes
    }

    # Fetch all wiki pages
    wiki_pages = subreddit.wiki

    for page in wiki_pages:
        # Check if the page is excluded from conversion
        if page.name in excluded_wiki_pages:
            # Save the wiki page without conversion
            output_extension = excluded_wiki_pages[page.name]
            output_path = os.path.join(output_directory, page.name + '.' + output_extension)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page.content_md)
        else:
            # Check if the page is a nested page
            if '/' in page.name:
                # Create subfolders if needed
                subfolder = os.path.join(output_directory, os.path.dirname(page.name))
                os.makedirs(subfolder, exist_ok=True)
                output_path = os.path.join(subfolder, os.path.basename(page.name) + '.md')
            else:
                output_path = os.path.join(output_directory, page.name + '.md')

            # Convert content to markdown format using html2text
            content_md = html2text.html2text(page.content_html)

            # Save the wiki page as a markdown document
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content_md)

        print(f'Saved: {output_path}')

# Example usage
save_wiki_pages(sub_name, reddit_instance_name)
