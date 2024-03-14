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





logging.basicConfig(filename='gitmailharvester.log',
                    filemode='a',  # Append mode
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

colors = {
    'bold': '\033[01m',
    'reset': '\033[0m',
    'red': '\033[31m',
    'green': '\033[32m',
    'cyan': '\033[36m',
    'low_green': '\033[96m',
    'low_blue': '\033[94m',
    'purple': "\033[95m"
}

random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
def pop_err(text):
    logging.error(text)
    exit()

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
    parser = argparse.ArgumentParser(prog='tool', description='Description : Tool for extracting e-mail addresses from commits in a GitHub account.', formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-H', '--host', choices=['github', 'gitlab'], required=True, help='Host service (github/gitlab)')
    parser.add_argument('-u', '--username', help='Username for the host service')
    parser.add_argument('-o', '--organisation', help='Organisation for the host service')
    parser.add_argument('-oA', '--outputAs', choices=['json', 'csv', 'txt'], help='Output file format')
    parser.add_argument('-oF', '--outputFile', required=True, help='Output file name (with extension)')
    parser.add_argument('-ghT','--github-token', help='GitHub personal access token')
    parser.add_argument('-glT','--gitlab-token', help='GitLab personal access token')
    args = parser.parse_args()

    # Determine if we're looking for a user's or an organisation's repositories
    entity_type = 'user' if args.username else 'org'
    name = args.username or args.organisation
    token = args.github_token if args.host == 'github' else args.gitlab_token
    
    # Get the repos and commits
    repos = get_repos(args.host, name, entity_type,token)
    commiters = []
    for repo in repos:
        commiters.extend(get_commits(args.host, name, repo,token))

    # Eliminate duplicates
    unique_commiters = deduplicate_commiters(commiters)
    if unique_commiters:
       pop_valid("Writing the collected data to file")
       #print(unique_commiters)
    else:
       pop_err("No data to write to the file.")

    # Output results to the specified file format
    if args.outputAs == 'csv':
        write_to_csv(unique_commiters, args.outputFile)
    elif args.outputAs == 'json':
        write_to_json(unique_commiters, args.outputFile)
    elif args.outputAs == 'txt':
        write_to_txt(unique_commiters, args.outputFile)
    else:
        # Print to console
        for commiter in unique_commiters:
            print(f"Data has been written to {args.outputFile}")

    pop_valid("Data correctly writen to output file ");

if __name__ == '__main__':
    print("[+]======================================================")
    print("[+]   Gitmail Harvester v1.0 by @bl4ckarch and @gr0bot    ")
    print("[+]======================================================")
    main()