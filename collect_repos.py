from config import Configuration
import os
import sys
import shutil

def search_repos(cfg):
    query = ' OR '.join(cfg.KEYWORDS) + '+in:readme+in:description'
    repos = cfg.githubAPI.search_repositories(query, 'stars', 'desc')
    selected_repos = [] 
    i = 0
    for repo in repos:
        url = repo.url
        star_count = repo.stargazers_count
        topics = repo.get_topics()
        if(star_count < cfg.MIN_STARS):
            break     
        selected_repos.append(repo)
        i = i+1
        if(i >= cfg.MAX_REPOS):
            break
    return selected_repos

def write_repo_list(repos):
    f = open("repos/repos.csv", "w")
    f.write("id, name, url, star count, topics, description\n")
    i = 0
    for repo in repos:
        if(not os.path.isdir(f'repos/{repo.name}')):
            os.mkdir(f'repos/{repo.name}')
        f.write(f'{repo.id}, {repo.name}, {repo.clone_url}, {repo.stargazers_count}, {repo.get_topics()}, {repo.description}\n')
        i = i+1
        print("\rCompletion: {:.2f}%".format(100.0*(float(i)/float(len(repos)))), end = '')
    print('\r\t\t\t\t\t\r', end = '')   
    f.close()
    
if __name__ == '__main__':
    # Load API token and settings
    cfg = Configuration('config.ini')

    # Clear old data
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
    print('                   \rDone')