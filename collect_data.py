from search import *
from config import Configuration
import os
import sys
import shutil

def write_repo_list(repos):
    f = open("repos/repos.csv", "w")
    f.write("name, url, star count, topics\n")

    i = 0
    for repo in repos:
        f.write(f'{repo.name}, {repo.clone_url}, {repo.stargazers_count}, {repo.get_topics()}\n')
        i = i+1
        print("\rCompletion: {:.2f}%".format(100.0*(float(i)/float(len(repos)))), end = '')
    print('')
    
    f.close()

def write_repo_info(repo):
    f = open(f'repos/{repo.name}/info.txt', "w")
    f.write(f"Url: {repo.clone_url}\n")
    f.write(f"Name: {repo.name}\n")
    f.write(f"Description: {repo.description}\n")
    f.write(f"Star Count: {repo.stargazers_count}\n")
    f.write(f"Topics: {repo.get_topics()}\n")

def write_contributors(repo, authors):
    f = open(f"repos/{repo.name}/contributors.csv", "w")
    f.write("username, email, contributions\n")

    i = 0
    for author in authors:
        if(author != None and author.name != None and author.email != None and authors[author] >= cfg.MIN_CONTRIBUTIONS):
            f.write(f'{author.name}, {author.email}, {authors[author]}\n')
        i = i+1
        print("\rCompletion {:.2f}%".format(100.0*(float(i)/float(len(authors)))), end = '')
    print('')

    f.close()
    
if __name__ == '__main__':
    # Load API token and settings
    cfg = Configuration()
    cfg.load_configuration('config.ini')

    # Clear old data (TODO)
    if(cfg.CLEAR_OLD_DATA):
        print('Clearing old data...')
        shutil.rmtree('repos/')
        os.mkdir('repos/')

    # Find repos with certain keywords
    print('Searching repos...')
    repos = search_repos(cfg)
    print(f'Total repos selected: {len(repos)}')
    print(f'Writing repos to CSV...')
    write_repo_list(repos)

    # Find contributors
    print(f'Searching contributors in {len(repos)} repos...')
    for repo in repos:
        if(not os.path.isdir(f'repos/{repo.name}')):
            os.mkdir(f'repos/{repo.name}')
        write_repo_info(repo)
        print(f"Searching contributors of repo '{repo.name}'")
        contributors = search_contributors(cfg, repo)
        print(f"Writing contributors of '{repo.name}' to CSV...")
        write_contributors(repo, contributors)