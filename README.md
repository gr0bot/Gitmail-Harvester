# Gitmail-Harvester

Gitmail-Harvester is a powerful Osint/Pentest tool designed to extract email addresses from commit history in GitHub and GitLab repositories. It provides a convenient way to gather email addresses from public and private repositories of users or organizations, offering support for both GitHub and GitLab platforms.

## Features

- Support for both GitHub and GitLab.
- Ability to extract from both user and organization repositories.
- Authentication support to increase rate limits and access private repositories.
- Outputs data in JSON, CSV, or plain text format.
- Deduplication of committer information to avoid repeated entries.
- Customizable output file naming.

## Requirements

- Python 3.x
- Requests library (`pip install requests`)

## Installation

Clone this repository to your local machine using:

```bash
git clone https://github.com/gr0bot/Gitmail-Harvester/
cd Gitmail-Harvester
```
Ensure you have Python 3 installed, and then install the required Python packages:

```bash

pip install -r requirements.txt
```
## Usage

The tool can be executed from the command line with various options to specify the target platform, username or organization, and output format.
Basic Syntax

```bash 
    python3 GitMailharvester.py [OPTIONS]
```

Options

    -s, --service: Required. The hosting service (github or gitlab).
    -u, --username: The username on the service.
    -o, --organisation: The organization name on the  service.
    -oA, --outputAs: The output format (json, csv, txt).
    -oF, --outputFile: Required. The name of the output file (with extension).
    --github-token: The GitHub personal access token for increased rate limits and private repo access.
    --gitlab-token: The GitLab personal access token for increased rate limits and private repo access.

### Examples

Extract all committers from a GitHub user's repositories and output to committers.csv:

```bash

python GitMailharvester.py -s github -u username  -oA csv -oF committers.txt --github-token YOUR_GITHUB_TOKEN 
```

Extract all committers from a GitLab organization's repositories and output to committers.json:

```bash

python GitMailharvester.py -s gitlab -o organisation_name  -oA json -oF committers.json --gitlab-token YOUR_GITLAB_TOKEN
```
### Notes

    Replace YOUR_GITHUB_TOKEN and YOUR_GITLAB_TOKEN with your actual personal access tokens from GitHub and GitLab, respectively.
    The personal access token is necessary for accessing private repositories and avoiding rate limits on API requests.



