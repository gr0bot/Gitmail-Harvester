#!/usr/bin/env python3
# File name          : gitmailharvester.py
# Author             : bl4ckarch & gr0bot
# Date created       : 6 feb 2024


import sys
import random
import string
import argparse
import requests
import csv
import json
import re
import logging
class CustomColors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RESET = '\033[0m'
    BOLD = '\033[01m'
    PURPLE = '\033[95m'

# Custom formatter with color support
class CustomFormatter(logging.Formatter):
    format_dict = {
        logging.DEBUG: CustomColors.CYAN + "[DEBUG] " + CustomColors.RESET,
        logging.INFO: CustomColors.GREEN + "[INFO] " + CustomColors.RESET,
        logging.WARNING: CustomColors.YELLOW + "[WARNING] " + CustomColors.RESET,
        logging.ERROR: CustomColors.RED + "[ERROR] " + CustomColors.RESET,
        logging.CRITICAL: CustomColors.PURPLE + "[CRITICAL] " + CustomColors.RESET
    }

    def format(self, record):
        log_fmt = self.format_dict.get(record.levelno)
        formatter = logging.Formatter('%(asctime)s ' + log_fmt + '%(message)s', "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
    
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

def pop_err(text):
    logging.error(text)
    sys.exit()

def pop_dbg(text):
    logging.debug(text)

def pop_info(text):
    logging.info(text)

def pop_valid(text):
    logging.info(text)


def make_api_call(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            pop_err("API rate limit exceeded.")
        elif response.status_code == 200:
            return response.json()
        else:
            pop_err(f"Failed to access {url} with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        pop_err(f"Request failed: {e}")
    return None    

def get_repos(service, name, entity_type, token):
    repos = []
    if service == 'github':
        api_url = f'https://api.github.com/users/{name}/repos' if entity_type == 'user' else f'https://api.github.com/orgs/{name}/repos'
        headers = {'Authorization': f'token {token}'} if token else {}
        repos_data = make_api_call(api_url, headers)
        if repos_data is not None:
            for repo in repos_data:
                repos.append(repo['name'])
    elif service == 'gitlab':
        pop_info("Service gitlab not yet functional")
    else:
        pop_info("Service not supported")
    return repos



# Fonction pour récupérer les commits d'un dépôt
def get_commits(service, name, repo_name, token):
    commits = []
    if service == 'github':
        api_url = f'https://api.github.com/repos/{name}/{repo_name}/commits'
        headers = {'Authorization': f'token {token}'} if token else {}
        commits_data = make_api_call(api_url, headers)
        if commits_data is not None:
            for commit in commits_data:
                committer_info = commit['commit']['committer']
                commits.append({'name': committer_info['name'], 'email': committer_info['email']})
    elif service == 'gitlab':
        pop_info("Service gitlab not yet functional")
    else:
        pop_info("Service not supported")
    return commits


# Fonction pour écrire les résultats dans un fichier CSV
def write_to_csv(data, filename):
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:  # for CSV
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Fonction pour écrire les résultats dans un fichier JSON
def write_to_json(data, filename):
    with open(filename, 'a', encoding='utf-8') as jsonfile:  # for JSON
        # file deepcode ignore PT: <please specify a reason of ignoring this>
        json.dump(data, jsonfile, indent=5)

# Fonction pour écrire les résultats dans un fichier texte
def write_to_txt(data, filename):
    with open(filename, 'a') as txtfile:
        for entry in data:
            txtfile.write(f"{entry['name']}: {entry['email']}\n")

def deduplicate_commiters(commiters):
    unique_commiters = {f"{c['email']}": c for c in commiters}.values()
    return list(unique_commiters)


# Fonction principale qui parse les arguments et appelle les autres fonctions
def main():
    

    parser = argparse.ArgumentParser(
        prog='gitmailharvester',
        description='Tool for extracting e-mail addresses from commits in a GitHub or GitLab account.',
        epilog='''
            Examples:
            python Gitmailharvester.py --service github --username john_doe --outputFile johns_emails.csv --outputAs csv --github-token yourtokenhere
            python Gitmailharvester.py --service gitlab --organisation my_org --outputFile org_emails.txt --outputAs txt --gitlab-token yourtokenhere

            Note: Replace 'yourtokenhere' with your actual GitHub or GitLab personal access token.
                ''',
                formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-s', '--service', choices=['github', 'gitlab'], required=True, help='service (either "github" or "gitlab").')
    parser.add_argument('-u', '--username', help='Username for the  service. Used to fetch user repositories.')
    parser.add_argument('-o', '--organisation', help='Organisation name for the  service. Used to fetch organisation repositories.')
    parser.add_argument('-oA', '--outputAs', choices=['json', 'csv', 'txt'], help='Output file format. Choose between "json", "csv", and "txt".')
    parser.add_argument('-oF', '--outputFile', required=True, help='Output file name. Please include the desired extension based on the output format.')
    parser.add_argument('-ghT', '--github-token', help='GitHub personal access token. Required for accessing private repositories or increasing rate limits.')
    parser.add_argument('-glT', '--gitlab-token', help='GitLab personal access token. Required for accessing private repositories or increasing rate limits.')

    args = parser.parse_args()


    # Determine if we're looking for a user's or an organisation's repositories
    entity_type = 'user' if args.username else 'org'
    name = args.username or args.organisation
    token = args.github_token if args.service == 'github' else args.gitlab_token
    
    # Get the repos and commits
    repos = get_repos(args.service, name, entity_type,token)
    commiters = []
    for repo in repos:
        commiters.extend(get_commits(args.service, name, repo,token))

    # Eliminate duplicates
    unique_commiters = deduplicate_commiters(commiters)
    if unique_commiters:
       pop_valid("Writing the collected data to file")
    else:
       pop_err("No data to write to the file.")

    # Output results to the specified file format
    if args.outputAs == 'csv':
        write_to_csv(unique_commiters, args.outputFile)
        pop_valid("Data correctly writen to output file ");
    elif args.outputAs == 'json':
        write_to_json(unique_commiters, args.outputFile)
        pop_valid("Data correctly writen to output file ");
    elif args.outputAs == 'txt':
        write_to_txt(unique_commiters, args.outputFile)
        pop_valid("Data correctly writen to output file ");
    else:
        # Print to console
        for commiter in unique_commiters:
            print(f"name: {commiter['name']} email: {commiter['email']}")   

    

if __name__ == '__main__':
    print("[+]======================================================")
    print("[+]   Gitmail Harvester v1.0 by @bl4ckarch and @gr0bot    ")
    print("[+]======================================================")
    print("\n")
    main()