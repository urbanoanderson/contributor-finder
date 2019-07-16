# About

Python script to search for contributors of public repos on Github with certain keywords

# Dependencies

- [Python 3](https://www.python.org/)
- [PyGithub](https://pygithub.readthedocs.io)
- [Dateutil lib](https://dateutil.readthedocs.io/en/stable/)

# To Install

On linux using pip:

```
$   sudo apt-get update
$   sudo apt-get install python3-pip
$   pip3 install PyGithub
$   pip3 install python-dateutil
```

# To Run

1. Create a file named `settings.ini` on root folder with your configuration such as the following:

```
[CONFIGURATION]
github_api_token = your_github_api_token_here
keywords = python, script, study, email
min_stars = 50
max_stars = 999999
min_contributions = 10
months_for_commits = 1
clear_old_data = True
```

The possible configurations are:
- `github_api_token`: your github api token
- `keywords`: keywords for the repository search (you can use up to 5)
- `min_stars`: minimum number of stars a repository must have
- `max_stars`: maximum amount of stars a repository can have
- `min_contributions`: minimum amount of contributions a user must have done in found repos to be included
- `months_for_commits` = search for contributions on commits in previous N months
- `clear_old_data` = if set to True, deletes the old output data before running the script

2. Run "python3 contributor_finder.py"

3. An output folder with a file named `contributors.json` and a log file will be created once the script finishes. Here is an example:

```
{
    "contributors": [
        {
            "address": "john@gmail.com",
            "name": "John Snow",
            "login": "contjohn",
            "repo_name": "superrepo",
            "repo_url": "https://github.com/contjohn/superrepo.git",
            "repo_stars": 234,
            "contributions": 50
        },
        {
            "address": "peter@gmail.com",
            "name": "Peter Parker",
            "login": "peterpk",
            "repo_name": "spider",
            "repo_url": "https://github.com/peterpk/spider.git",
            "repo_stars": 125
            "contributions": 50
        }
    ]
}
```