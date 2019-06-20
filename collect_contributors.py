from config import Configuration
import os
import sys
import shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv

def search_contributors(cfg, repo):
    commits = None
    while(commits == None):
        try:
            commits = repo.get_commits(since=(datetime.now() - relativedelta(months=cfg.MONTHS_FOR_COMMITS)))
        except:
            print('Error fetching commits. Trying again...')

    # Remove duplicate authors
    map_contributions = {}
    distinct_authors = []
    i = 0
    for commit in commits:
        author = commit.author

        if(author == None or author.email == None):
            i = i + 1
            continue
        elif(author.email in map_contributions):
            map_contributions[author.email] = map_contributions[author.email] + 1
        else:
            map_contributions[author.email] = 1
            distinct_authors.append(author)
        i = i + 1
        print("\rCompletion {:.2f}%".format(100.0*(float(i)/float(commits.totalCount))), end = '')
    print('')

    # Remove authors with too little contributions
    return [author for author in distinct_authors if map_contributions[author.email] >= cfg.MIN_CONTRIBUTIONS]

def write_contributors(repo, authors):
    f = open(f"repos/{repo.name}/contributors.csv", "w")
    f.write("username, email, contributions\n")
    i = 0
    for author in authors:
        f.write(f'{author.name}, {author.email}\n')
        i = i+1
        print("\rCompletion {:.2f}%".format(100.0*(float(i)/float(len(authors)))), end = '')
    print('')
    f.close()
    
if __name__ == '__main__':
    # Load API token and settings
    cfg = Configuration('config.ini')

    # Load repos saved at repos.csv
    print('Loading repos from CSV...')
    repos = []
    with open('repos/repos.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0 and (not os.path.isfile(f'./repos/{row[1].strip()}/contributors.csv')):
                print(f"Loading line {line_count}: '{row[1]}'")
                repos.append(cfg.githubAPI.get_repo(int(row[0])))
            line_count += 1
        print(f'Loaded {line_count-1} repos.')

    # Find contributors
    print(f'Searching contributors in {len(repos)} repos...')
    for repo in repos:
        print(f"Searching contributors of repo '{repo.name}'")
        contributors = search_contributors(cfg, repo)
        print(f"Writing contributors of '{repo.name}' to CSV...")
        write_contributors(repo, contributors)