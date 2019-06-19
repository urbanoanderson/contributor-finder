from github import Github
import configparser
import os

class Configuration:
    KEYWORDS = None
    MAX_REPOS = None
    MIN_STARS = None
    MIN_CONTRIBUTIONS = None
    MONTHS_FOR_COMMITS = None
    CLEAR_OLD_DATA = None

    githubAPI = None

    def __init__(self):
        self.set_default_values()

        if(not os.path.isdir('repos')):
            os.mkdir('repos')
    
    def set_default_values(self):
        self.KEYWORDS = []
        self.MAX_REPOS = 50
        self.MIN_STARS = 100
        self.MIN_CONTRIBUTIONS = 1
        self.MONTHS_FOR_COMMITS = 12
        self.CLEAR_OLD_DATA = False

    def load_configuration(self, filename):
        # Read API token
        try:
            with open('token.ini', "r") as f:
                token = f.readline()
                self.githubAPI = Github(token)
        except:
            print('Error: github token file not found or invalid. Exiting...')
            exit()

        # Read settings
        try:
            config = configparser.ConfigParser()
            config.read(filename)
            self.KEYWORDS = [keyword.strip() for keyword in config['CONFIGURATION']['keywords'].split(',')]
            if(len(self.KEYWORDS) > 5):
                print('Warning: github API search only support 5 or less keywords. Using the first 5...')
                self.KEYWORDS = self.KEYWORDS[:5]
            self.MAX_REPOS = int(config['CONFIGURATION']['max_repos'])
            self.MIN_STARS = int(config['CONFIGURATION']['min_stars'])
            self.MIN_CONTRIBUTIONS = int(config['CONFIGURATION']['min_contributions'])
            self.MONTHS_FOR_COMMITS = int(config['CONFIGURATION']['months_for_commits'])
            self.CLEAR_OLD_DATA = bool(config['CONFIGURATION']['clear_old_data'])
        except:
            print(f"Warning: '{filename}' not found or invalid, using default values")
            self.set_default_values()