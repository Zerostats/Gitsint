import argparse
from gitsint import *
from git import Repo
import os
import json
import concurrent.futures
from collections import Counter

# Get the directory of the current script file
current_dir = os.path.dirname(__file__)

# Navigate from the current directory to the root of your project
root_dir = os.path.abspath(os.path.join(current_dir, "../../.."))

async def fetch_repository(user, client, out, args):
    repos = {}

    username = user["login"]
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {}
    if "token" in args and args['token'] is not None:
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': "Bearer {}".format(''.join(args['token'])),
            'X-GitHub-Api-Version': '2022-11-28',
        }
        if "private" in args and args['private'] == True:
            url = f"https://api.github.com/user/repos?per_page=100"

    repos = await client.get(url, headers=headers)
    
    return repos.json()

def clone_and_collect_data(repo, username, args, RESULTS_FOLDER, name, domain, method, frequent_rate_limit, out):
    _repo = {
        "name": repo['name'],
        "description": repo['description'],
        "authors": [],
    }
    try:
        repo_path = os.path.join(RESULTS_FOLDER, repo['name'])
        
        if os.path.exists(repo_path):
            repo = Repo(repo_path)
        else:
            if "token" in args and args["token"] is not None:
                Repo.clone_from(f"https://{args['token'][0]}@github.com/{username}/{repo['name']}.git", repo_path)
            else:
                # Check if repo already exists
                if not os.path.exists(repo_path):
                    Repo.clone_from(repo['clone_url'], repo_path)
        

        repo = Repo(repo_path)
        
        messages = []
        authors = []
        for commit in repo.iter_commits(all=True):
            _author = {"name": commit.author.name, "email": commit.author.email}
            message = str(commit.message).strip()
        
            if _author not in authors:
                authors.append(_author)
            messages.append(message)
        _repo["authors"] = json.dumps(authors)
        _repo["emails"] = json.dumps([author["email"] for author in authors])
        _repo["messages"] = json.dumps(messages)

        return _repo, authors

    except Exception as e:
        print("Error...: "  + str(e))
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": True,
            "others": {"Message": "Clone failed.", "errorMessage": str(e)},
            "data": None,
        })
        return None, []

async def repository(user, client, out, args):
    name = "repository"
    domain = "repository"
    method = "api"
    frequent_rate_limit = True
    username = user["login"]
    authors = []

    if isinstance(args, argparse.Namespace):
        args = vars(args)

    try:
        repos = await fetch_repository(user, client, out, args)
        if 'message' in repos:
            message = repos['message']
            if message == "Not Found":
                out.append({
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": False, "error": False,
                    "others": {"Message": "Not Found", "errorMessage": "Not Found"},
                    "data": None
                })
            elif message.startswith("API rate limit exceeded"):
                out.append({
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": True, "exists": False, "error": True,
                    "others": {"Message": "API rate limit exceeded", "errorMessage": "API rate limit exceeded"},
                    "data": None
                })
            elif message.startswith("Bad credentials"):
                out.append({
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "error": True, "exists": False,
                    "others": {"Message": "Bad credentials", "errorMessage": "Bad credentials"},
                    "data": None
                })
        else:
            RESULTS_FOLDER = os.path.join(args['output'], username) if 'output' in args and args['output'] else os.path.join(root_dir, f"results/{username}")
            os.makedirs(RESULTS_FOLDER, exist_ok=True)

            if "fork" in args and not args['fork']:
                repos = [repo for repo in repos if not repo['fork']]
            if "size" in args and int(args['size']) > 0:
                repos = [repo for repo in repos if 0 < int(repo['size']) < int(args['size'])]
            else:
                repos = [repo for repo in repos if 0 < int(repo['size']) < 500000]
            if len(repos) < 1:
                out.append({
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": False,
                    "others": {"Message": "No repositories found for this user.", "errorMessage": "No repositories found for this user."},
                    "data": None,
                })
                return

            _repos = []
            _authors = []

            with concurrent.futures.ThreadPoolExecutor() as executor:
                
                future_to_repo = {
                    executor.submit(clone_and_collect_data, repo, username, args, RESULTS_FOLDER, name, domain, method, frequent_rate_limit, out): repo for repo in repos
                }
                for future in concurrent.futures.as_completed(future_to_repo):
                    repo = future_to_repo[future]
                    try:
                        repo_data, authors_data = future.result()
                        if repo_data:
                            _repos.append(repo_data)
                        if authors_data:
                            _authors.extend(authors_data)
                    except Exception as exc:
                        print("Exc in future", exc)
                        out.append({
                            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                            "rateLimit": False, "exists": True,
                            "others": {"Message": "Error processing repository.", "errorMessage": str(exc)},
                            "data": None,
                        })

            if not _authors:
                out.append({
                    "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": False,
                    "others": {"Message": "No authors or emails found for this user.", "errorMessage": "No authors or emails found for this user."},
                    "data": json.dumps(_repos),
                })
            else:
                # Remove duplicate authors
                authors = []
                for _auth in _authors:
                    if _auth not in authors:
                        authors.append(_auth)
                
                
                out.append({
                    "name": "repository", "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": True, "others": None,
                    "data": json.dumps(_repos)
                })
                
                out.append({
                    "name": "repository", "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False, "exists": True, "others": None,
                    "data": json.dumps(authors)
                })
    except Exception as e:
        print(e,"Error")
        out.append({
            "name": name, "domain": domain, "method": method, "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False, "exists": False, "data": None,
            "others": {"Message": "An error occurred.", "errorMessage": str(e)}
        })
