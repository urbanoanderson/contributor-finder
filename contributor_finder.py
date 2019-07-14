import os
import sys
import time
import math
import json
import shutil
import configparser
from github import Github
from github import RateLimitExceededException
from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta

DATA_FOLDER_PATH = "output"
SETTINGS_FILE_PATH = "settings.ini"
OUTPUT_FILE_PATH = f"{DATA_FOLDER_PATH}/contributors.json"
LOG_FILE_PATH = f"{DATA_FOLDER_PATH}/contributor_finder.log"
MAX_KEYWORDS_ALLOWED = 5

# ----------------------------------------------------------------------------------------
# UTILS
# ----------------------------------------------------------------------------------------

class LogLevel(Enum):
    INFO = 0
    WARNING = 1
    ERROR = 2
    DEBUG = 3

def log_all(message="", level=LogLevel.INFO):
    log_console(message, level)
    log_file(message, level)

def log_console(message="", level=LogLevel.INFO):
    print(f"{datetime.now().time()} {level.name} - {message}")

def log_file(message="", level=LogLevel.INFO):
    with open(LOG_FILE_PATH, "a") as f:
        f.write(f"{datetime.now().time()} {level.name} - {message}\n")

def wait_github_rate_recharge(githubAPI):
    seconds_left = math.ceil(githubAPI.rate_limiting_resettime - time.time())
    seconds_to_wait = max(seconds_left, 5)
    minutes_to_wait = math.ceil(seconds_to_wait/60.0)
    log_all(f'You have exceeded your Github API rate limit for requests. Trying again in {minutes_to_wait} minutes...', LogLevel.ERROR)
    time.sleep(seconds_to_wait)

def github_api_search_repos(githubAPI, query):
    while(True):
        try:
            repos = githubAPI.search_repositories(query, 'stars', 'desc')
            return repos
        except RateLimitExceededException:
            wait_github_rate_recharge(githubAPI)

def github_api_get_commits(githubAPI, repo, since):
    while(True):
        try:
            commits = repo.get_commits(since)
            return repos
        except RateLimitExceededException:
            wait_github_rate_recharge(githubAPI)

def github_api_get_author_from_commit(githubAPI, commit):
    while(True):
        try:
            author = commit.author
            return author
        except RateLimitExceededException:
            wait_github_rate_recharge(githubAPI)

# ----------------------------------------------------------------------------------------
# CONTRIBUTOR FINDER
# ----------------------------------------------------------------------------------------

if __name__ == '__main__':

    # Read settings
    try:
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE_PATH)
        github_api_token = config['CONFIGURATION']['github_api_token']
        keywords = [keyword.strip() for keyword in config['CONFIGURATION']['keywords'].split(',')]
        if(len(keywords) > MAX_KEYWORDS_ALLOWED):
            log_console(f'Github API search only support {MAX_KEYWORDS_ALLOWED} or less keywords. Using the first {MAX_KEYWORDS_ALLOWED}...', LogLevel.WARNING)
            keywords = keywords[:MAX_KEYWORDS_ALLOWED]
        max_repos = int(config['CONFIGURATION']['max_repos'])
        min_stars = int(config['CONFIGURATION']['min_stars'])
        min_contributions = int(config['CONFIGURATION']['min_contributions'])
        months_for_commits = int(config['CONFIGURATION']['months_for_commits'])
        clear_old_data = bool(config['CONFIGURATION']['clear_old_data'])
    except Exception as e:
        log_console(f"'{SETTINGS_FILE_PATH}' not found or invalid. Exiting script...", LogLevel.ERROR)
        exit()

    # Optional clearing of old data
    if(not os.path.isdir(DATA_FOLDER_PATH)):
            os.mkdir(DATA_FOLDER_PATH)

    if(clear_old_data):
        if(os.path.isdir(DATA_FOLDER_PATH)):
            shutil.rmtree(DATA_FOLDER_PATH)
            os.mkdir(DATA_FOLDER_PATH)
        log_all('Old data cleared')

    # Instantiate Github API client
    try:
        log_all("Checking credentials...")
        githubAPI = Github(github_api_token)
        githubAPI.get_user().name #test for valid credentials
        log_all("Credentials successfully validated")
    except:
        log_all('Could not create client for github API. Please check your token. Exiting script...', LogLevel.ERROR)
        exit()

    # Search relevant repositories
    log_all(f"Searching for repos with at least {min_stars} stars and the following keywords: {keywords}")
    # Query syntax: https://help.github.com/en/articles/understanding-the-search-syntax
    #query = ' OR '.join(keywords) + '+in:readme+in:description'
    query = f"{' OR '.join(keywords)}+in:name,description,readme+stars:>={min_stars}"
    repos = []
    for repo in github_api_search_repos(githubAPI, query):
        if(len(repos) >= max_repos):
            break
        if(repo.stargazers_count < min_stars):
            break
        repos.append(repo)
    log_all(f"Found {len(repos)} different repos")

    # Search for contributors in repos
    map_authors = {} # To Remove duplicate authors
    for i in range(len(repos)):
        repo = repos[i]
        log_all(f"Searching for contributors on repo '{repo.name}'... [{i+1}/{len(repos)}]")
        commits = repo.get_commits(since=(datetime.now() - relativedelta(months=months_for_commits)))
        #commits = github_api_get_commits(githubAPI, repo, datetime.now()-relativedelta(months=months_for_commits))
        for commit in commits:
            try:
                author = github_api_get_author_from_commit(githubAPI, commit)
                if(author.login != None and author.email != None and author.name != None):
                    contributions = 0 if map_authors.get(author.email, None) == None else map_authors[author.email][2] + 1
                    map_authors[author.email] = (author, repo, contributions)
            except AttributeError:
                pass

    # Write contributors to output file
    data = {}
    data['contributors'] = []
    for key in map_authors:
        author = map_authors[key][0]
        repo = map_authors[key][1]
        contributions = map_authors[key][2]
        contributor = {}
        contributor['address'] = author.email
        contributor['name'] = author.name
        contributor['login'] = author.login
        contributor['repo_name'] = repo.name
        contributor['repo_stars'] = repo.stargazers_count
        contributor['contributions'] = contributions

        if(contributions >= min_contributions):
            data['contributors'].append(contributor)

    log_all(f"Writing contributors to file...")
    with open(OUTPUT_FILE_PATH, 'w') as f:
        json.dump(data, f)