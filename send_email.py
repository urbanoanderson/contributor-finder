import smtplib
import csv
import configparser
import os

def send_email(sender, contributor, email_subject, email_body):
    email_from = sender[0]
    email_password = sender[1]
    to = [contributor[2]] 
    subject = email_subject 
    body = email_body
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (email_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(email_from, email_password)
        server.sendmail(email_from, to, message.encode("utf8"))
        server.close()
        print('Email sent!')
    except Exception as ex:  
        print(f'Something went wrong while sending email to {contributor[0]}...\n{ex}')

def is_contributor_in_list(contributor, contributors):
    for c in contributors:
        if(c[2] == contributor[2]):
            return True
    return False

if __name__ == '__main__':
    # Read config file for email client
    settings_file = 'email_settings.ini'
    try:
        config = configparser.ConfigParser()
        config.read(settings_file)      
        sender_email = config['CONFIGURATION']['sender_email']
        sender_token = config['CONFIGURATION']['sender_token']
        sender = (sender_email, sender_token)
    except:
        print(f"Warning: '{settings_file}' not found or invalid, using default values")
        exit()

    # Read repos.csv find all repo names
    repos = []
    with open('repos/repos.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if(line_count != 0):
                name = row[1].strip()
                repos.append(name)
            line_count += 1

    # Open each contributors.csv file and aggregate names
    contributors = []
    for repo_name in repos:
        with open(f'repos/{repo_name}/contributors.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if(line_count != 0):
                    login = row[0].strip()
                    name = row[1].strip()
                    email = row[2].strip()
                    contributor = (login, name, email)
                    if(not is_contributor_in_list(contributor, contributors)):
                        contributors.append(contributor)
                line_count += 1

    # Read template
    with open('email_template.txt', 'r') as file:
        template = file.read()
    email_subject = 'Research on blockchain development tools' 

    # Send emails
    for contributor in contributors:
        email_body = template.replace('<CLOGIN>', contributor[0]).replace('<CNAME>', contributor[1]).replace('<CEMAIL>', contributor[2])
        send_email(sender, contributor, email_subject, email_body)