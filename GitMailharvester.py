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
#q = Queue()
def pop_err(text):
    raise Exception(f"{colors['red']}[!]{colors['reset']} {text}")
def pop_dbg(text):
    #print("{}{}{} {}".format(cyan, "[i]", reset, text))
    print(f"{colors['low_blue']}[!]{colors['reset']} {text}")
def pop_info(text):
    #print("{}{}{} {}".format(cyan, "[*]", reset, text))
    print(f"{colors['purple']}[*]{colors['reset']} {text}")
def pop_valid(text):
    #print("{}{}{} {}".format(green, "[+]", reset, text))
    print(f"{colors['cyan']}[+]{colors['reset']} {text}")
def log_to_file(line):
    f = open('log.txt', 'a')
    f.write(line); f.write("\n")
    f.close()
    pass

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




# Fonction pour récupérer les dépôts de l'utilisateur ou de l'organisation
def get_repos(service, name, entity_type, token):
    
    repos = []
    headers = {}    
    
    if service == 'github':
        
        api_url = f'https://api.github.com/users/{name}/repos' if entity_type == 'user' else f'https://api.github.com/orgs/{name}/repos'
        headers = {'Authorization': f'token {token}'} if token else {}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 403:
            pop_err("API rate limit exceeded. repos")
            return []
        if response.status_code == 200:
            repos_data = response.json()
            for repo in repos_data:
                repos.append(repo['name'])
    elif service == 'gitlab':
        # Ajoutez la logique pour GitLab ici
        pop_info("Service gitlab not yet functional")
        pass
    else:
        raise pop_info("Service not supported")
    #print(response.json())  # Add this in your get_repos and get_commits functions
    log = response.json()
    formatted_log = json.dumps(log,indent= 5)
    log_to_file(formatted_log)
    return repos



# Fonction pour récupérer les commits d'un dépôt
def get_commits(service, name, repo_name, token):
    commits = []
    headers = {}
    if service == 'github':
        api_url = f'https://api.github.com/repos/{name}/{repo_name}/commits'
        headers = {'Authorization': f'token {token}'} if token else {}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 403:
            pop_err("API rate limit exceeded. commits")
            return []
        if response.status_code == 200:
            commits_data = response.json()
            for commit in commits_data:
                # Supposons que le commit contient un objet 'commit' qui à son tour contient un objet 'committer'
                committer_info = commit['commit']['committer']
                commits.append({'name': committer_info['name'], 'email': committer_info['email']})
    elif service == 'gitlab':
        # Ajoutez la logique pour GitLab ici
        pop_info("Service gitlab not yet functional")
        pass
    else:
        pop_info("Service not yet functional")
        raise ValueError("Service not supported")
   
    return commits



# Fonction pour écrire les résultats dans un fichier CSV
def write_to_csv(data, filename):
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:  # for CSV
        fieldnames = ['name', 'email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

# Fonction pour écrire les résultats dans un fichier JSON
def write_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as jsonfile:  # for JSON
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
    parser.add_argument('-list', '--list', choices=['all'], help='List all commiters')
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
    if args.list == 'all':
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