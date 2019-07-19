import os
import sys
import time
import http
import math
import json
import shutil
import requests
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

def query_repo_info(repo):
    name = repo.name
    description = repo.description
    stars = repo.stargazers_count
    url = repo.url
    topics = repo.get_topics()
    return topics

def safe_query_github(githubAPI, method, *args):
    while(True):
        try:
            result = method(*args)
            return result
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
        min_stars = int(config['CONFIGURATION']['min_stars'])
        max_stars = int(config['CONFIGURATION']['max_stars'])
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

    # Search for relevant repositories (query syntax: https://help.github.com/en/articles/searching-for-repositories)
    log_all(f"Searching for repos with stars from {min_stars} to {max_stars} and the following keywords: {keywords}")
    query = f"{' OR '.join(keywords)}+stars:{min_stars}..{max_stars}"
    query_results = safe_query_github(githubAPI, githubAPI.search_repositories, query, 'stars', 'desc')
    repos = []
    for repo in query_results:
        topics = safe_query_github(githubAPI, query_repo_info, repo)
        if(repo.stargazers_count < min_stars or repo.stargazers_count > max_stars):
            continue
        log_file(f"Found repo '{repo.name}' with {repo.stargazers_count} stars ('{repo.url}')")
        repos.append(repo)
    log_all(f"Found {len(repos)} different repos")

    # Search for contributors in repos
    map_authors = {} # To Remove duplicate authors
    i = 0
    while(i < len(repos)):
        try:
            repo = repos[i]
            log_all(f"Searching for contributors on repo '{repo.name}'... [{i+1}/{len(repos)}]")
            commits = repo.get_commits(since=(datetime.now() - relativedelta(months=months_for_commits)))
            for commit in commits:
                try:
                    author = commit.author
                    if(author.login != None and author.email != None and author.name != None):
                        contributions = 0 if map_authors.get(author.email, None) == None else map_authors[author.email]['contributions'] + 1
                        contributor = {}
                        contributor['address'] = author.email
                        contributor['name'] = author.name
                        contributor['login'] = author.login
                        contributor['repo_name'] = repo.name
                        contributor['repo_url'] = repo.url
                        contributor['repo_stars'] = repo.stargazers_count
                        contributor['contributions'] = contributions
                        map_authors[author.email] = contributor
                        log_file(f"Update contributor {author.name} with {contributions} contributions")
                except AttributeError:
                    pass
            i = i + 1
        except RateLimitExceededException:
            wait_github_rate_recharge(githubAPI)
            continue
        except (requests.exceptions.ReadTimeout, http.client.RemoteDisconnected):
            log_all(f"Http request limit timed out, creating a new session", LogLevel.ERROR)
            githubAPI = Github(github_api_token)
            continue

    # Write contributors to output file
    log_all(f"Writing contributors to file...")
    output_data = {'contributors': []}
    for key in map_authors:
        if(map_authors[key]['contributions'] >= min_contributions):
            output_data['contributors'].append(map_authors[key])
        else:
            log_file(f"Skipping contributor '{map_authors[key]['name']}', he only has {map_authors[key]['contributions']} contributions")
    with open(OUTPUT_FILE_PATH, 'w') as f:
        json.dump(output_data, f, sort_keys=True, indent=4)