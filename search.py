from datetime import datetime
from dateutil.relativedelta import relativedelta

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

def search_contributors(cfg, repo):
    commits = repo.get_commits(since=(datetime.now() - relativedelta(months=cfg.MONTHS_FOR_COMMITS)))
    authors = {}  
    for commit in commits:
        author = commit.author
        if(author in authors):
            authors[author] = authors[author] + 1
        else:
            authors[author] = 1

    return authors