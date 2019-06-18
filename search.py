# Useful links
# https://pygithub.readthedocs.io/en/latest/github.html
# https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository
# https://pygithub.readthedocs.io/en/latest/examples/Repository.html
# https://github.com/PyGithub/PyGithub/issues/323
# https://help.github.com/en/articles/understanding-the-search-syntax

# To Install and Run: 
#   sudo apt-get update
#   sudo apt-get install python3-pip
#   pip3 install PyGithub
#   python3 search.py

from github import Github
import configparser

# API and configuration
githubAPI = None
keywords = []
MAX_REPOS = 50
MIN_STARS = 100

def load_configuration():
    try:
        with open("token.ini", "r") as f:
            token = f.readline()
            print(token)
            global githubAPI
            githubAPI = Github(token)
    except IOError:
        print('Error: github token file not found')
        exit()

    #f_token = open("token.ini", "r")
    #token = f_token.readline()
    #githubAPI = Github(token)
    #f_token.close()

    config = configparser.ConfigParser()
    config.read('config.ini')
    
    global keywords
    global MAX_REPOS
    global MIN_STARS

    keywords = [keyword.strip() for keyword in config['CONFIGURATION']['keywords'].split(',')]
    MAX_REPOS = int(config['CONFIGURATION']['max_repos'])
    MIN_STARS = int(config['CONFIGURATION']['min_stars'])

def search_repos():
    query = ' OR '.join(keywords) + '+in:readme+in:description'
    repos = githubAPI.search_repositories(query, 'stars', 'desc')
    print(repos.totalCount)
    selected_repos = []

    f_repos = open("repos.csv", "w")
    f_repos.write("url, star count, topics\n")
 
    i = 0
    for repo in repos:
        url = repo.clone_url
        star_count = repo.stargazers_count
        topics = repo.get_topics()

        if(star_count < MIN_STARS):
            break
        
        selected_repos.append(repo)
        f_repos.write(f'{url}, {star_count}, {topics}\n')

        i = i+1
        if(i >= MAX_REPOS):
            break

    f_repos.close()

    return selected_repos

def search_contributors():
    print("huhu")

if __name__ == '__main__':
    load_configuration()

    print('Searching repos...')
    repos = search_repos()
    print(f'Selected Found {len(repos)} repo(s)')

    exit()

    for repo in repos:
        search_contributors()

    
    