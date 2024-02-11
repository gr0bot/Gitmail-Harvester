#!/usr/bin/python3

import sys
import random
import string
import argparse
import requests
import re
import json

# =========== GLOBALS =============

bold='\033[01m'; reset='\033[0m'; red='\033[31m'; yellow='\033[32m'; green='\033[36m'; lowgreen='\033[96m'; lowblue='\033[94m'; cyan='\033[92m'; purple="\033[95m"; purple="\033[95m"
random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
#q = Queue()
def pop_err(text):
    print("{}{}{} {}".format(red, "[!]", reset, text))
    exit()
def pop_dbg(text):
    print("{}{}{} {}".format(cyan, "[i]", reset, text))
def pop_info(text):
    print("{}{}{} {}".format(cyan, "[*]", reset, text))
def pop_valid(text):
    print("{}{}{} {}".format(green, "[+]", reset, text))
def log_to_file(line):
    f = open(f'./{output_name}.txt', 'a')
    f.write(line); f.write("\n")
    f.close()

# =========== ARGS =============

example_text='''Examples :
    command    # description
    '''
parser = argparse.ArgumentParser(prog='tool', description='Description : Tool for extracting e-mail addresses from commits in a GitHub account.', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-u", "--url", help="URL of the repo", required=True)
args = parser.parse_args()
if not len(sys.argv) > 1:
    parser.print_help()
    exit()

# =========== FUNCTIONS =============



# =========== MAIN =============

url_repo = 'https://api.github.com/users/' + args.url + '/repos'
# Recuperer les repo
r1 = requests.get(url_repo)
if r1.status_code == 200:
    r1_json = r1.json()
    repos_lst = [e['name'] for e in r1_json]

    email_lst = []
    # Recuperer les commits
    for i in range(len(r1_json)):
        r2 = requests.get('https://api.github.com/repos/' + args.url + '/' + repos_lst[i] + '/commits')
        if r2.status_code == 200:
            r2_json = r2.json()
            # Recuperer les email
            #for y in r2_json:
            #    email_lst.append(r2_json[y]["commit"]["author"]["email"])
            for y in r2_json:
                email = y["commit"]["author"]["email"]
                email_lst.append(email)
    print(email_lst)
else:
    print("Impossible de récupérer les repos.")
