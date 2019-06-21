from config import Configuration
import os
import sys
import shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv
import github
import time

def search_contributors(cfg, repo):
    commits = repo.get_commits(since=(datetime.now() - relativedelta(months=cfg.MONTHS_FOR_COMMITS)))

    # Remove duplicate authors
    map_contributions = {}
    distinct_authors = []
    icon = ["\\", "|", "/", "-"]
    i = 0
    for commit in commits:
        try:
            author = commit.author
            #print(f"Commit author: [login:{author.login}, email:{author.email}, name:{author.name}]")
            if(author.login != None and author.email != None and author.name != None):
                if(author.email in map_contributions):
                    map_contributions[author.email] = map_contributions[author.email] + 1
                else:
                    map_contributions[author.email] = 1
                    distinct_authors.append(author)
        except AttributeError:
            pass
        i = i + 1
        print(f"\r{icon[i%4]}", end = '')
    print('\r     \r', end = '')

    # Remove authors with too little contributions
    selected_authors = [author for author in distinct_authors if map_contributions[author.email] >= cfg.MIN_CONTRIBUTIONS]

    return selected_authors, map_contributions

def write_contributors(repo, contributors, map_contributions):
    f = open(f"repos/{repo.name}/contributors.csv", "w")
    f.write("login, name, email, contribution count\n")
    i = 0
    for author in contributors:
        login = author.login
        name = author.name
        email = author.email
        contribution_count = map_contributions[email]
        f.write(f'{login}, {name}, {email}, {contribution_count}\n')
        i = i+1
        print("\rCompletion {:.2f}%".format(100.0*(float(i)/float(len(contributors)))), end = '')
    print('')
    f.close()
    
if __name__ == '__main__':
    # Load API token and settings
    cfg = Configuration('config.ini')

    # Load repos saved at repos.csv
    with open('repos/repos.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        contributor_count = 0
        processed_repos_count = 0
        for row in csv_reader:
            # Only search contributors of repos that weren't searched before
            repo_name = row[1].strip()
            if line_count != 0 and (not os.path.isfile(f'./repos/{repo_name}/contributors.csv')):
                contributors = None
                while(contributors == None):
                    try:
                        print(f"Reading CSV line {line_count}: '{repo_name}' ...")
                        cur_rate = cfg.githubAPI.rate_limiting
                        print(f"Github API status: {cur_rate[0]} requests remaining, the limit is {cur_rate[1]} per hour")
                        repo = cfg.githubAPI.get_repo(int(row[0]))
                        print(f"Searching contributors of repo '{repo_name}'")
                        contributors, map_contributions = search_contributors(cfg, repo)
                        contributor_count = contributor_count + len(contributors)
                        print(f"Writing {len(contributors)} contributors of '{repo_name}' to CSV...")
                        write_contributors(repo, contributors, map_contributions)
                        processed_repos_count = processed_repos_count + 1
                    except KeyboardInterrupt:
                        print('Exiting...')
                        exit()
                    except github.RateLimitExceededException:
                        minutes_to_wait = 15
                        print(f'You have exceeded your Github API rate limit for requests. Trying again in {minutes_to_wait} minutes...')
                        time.sleep(60*minutes_to_wait)
                        pass
                    except:
                        print('Unexpected error. Trying again...')
                        pass
            line_count += 1
        print(f'Done. Selected {contributor_count} contributors in {processed_repos_count} repos.')
