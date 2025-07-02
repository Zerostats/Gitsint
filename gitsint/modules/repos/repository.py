import argparse
import concurrent.futures
import json
import os
from collections import Counter
import logging
from typing import Tuple, List, Dict
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
from pathlib import Path          # ✅ nouvel import

from gitsint import *
from gitsint.utils import gitleaks

logger = logging.getLogger(__name__)
# Get the directory of the current script file
current_dir = os.path.dirname(__file__)

# Navigate from the current directory to the root of your project
root_dir = os.path.abspath(os.path.join(current_dir, "../../.."))


async def fetch_repository(user, client, out, args):
    username = user["login"]
    headers = {}
    repos = []
    page = 1

    # Correction : vérification plus robuste pour le token
    if "token" in args and args["token"] is not None and isinstance(args["token"], (list, tuple)) and len(args["token"]) > 0:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {args['token'][0]}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    if "private" in args and args["private"] is True:
        base_url = "https://api.github.com/user/repos?per_page=100"
    else:
        base_url = f"https://api.github.com/users/{username}/repos?per_page=100"

    while True:
        url = f"{base_url}&page={page}"
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            break
        page_data = response.json()
        if not page_data:
            break
        repos.extend(page_data)
        page += 1

    return repos

def clone_and_collect_data(
    repo: dict,
    username: str,
    args: dict,
    results_folder: str,
    out: list,
) -> Tuple[dict | None, List[Dict[str, str]]]:
    if repo is None:
        print("Error: repo is None!")
        return None, []

    if not isinstance(repo, dict):
        print(f"Error: repo is not a dict, it's {type(repo)}")
        return None, []

    repo_name = repo.get('name', 'Unknown')
    print(f"Processing repo: {repo_name}")

    required_keys = ['name', 'clone_url', 'full_name']
    for key in required_keys:
        if key not in repo:
            print(f"Error: repo missing key {key}")
            return None, []

    try:
        repo_path = Path(results_folder) / repo_name
        print(f"Repo path: {repo_path}")

        try:
            if repo_path.exists():
                repo_obj = Repo(repo_path)
            else:
                clone_kwargs = {}
                token = None
                token_value = args.get("token")
                if token_value is not None:
                    if isinstance(token_value, (list, tuple)) and len(token_value) > 0:
                        token = token_value[0]
                    else:
                        token = token_value

                if token:
                    clone_kwargs["env"] = {"GIT_ASKPASS": "echo", "GIT_PASSWORD": token}

                clone_url = repo.get('clone_url')
                if clone_url is None:
                    print("Error: clone_url is None")
                    return None, []

                try:
                    repo_obj = Repo.clone_from(clone_url, repo_path, **clone_kwargs)
                    print(f"Cloned repo to {repo_path}")
                except Exception as e:
                    print(f"Error cloning repo: {e}")
                    return None, []

            if not hasattr(repo_obj, 'head') or not repo_obj.head.is_valid():
                logger.warning("Dépôt %s sans commit", repo.get("full_name", "unknown"))
                return None, []

            print("Extracting commits...")
            authors, messages = _extract_commits(repo_obj)
            print(f"Extracted {len(authors)} authors and {len(messages)} messages")

            if not isinstance(authors, list):
                print(f"Error: authors is not a list, it's {type(authors)}")
                authors = []

            valid_authors = []
            for a in authors:
                if a is None:
                    print("Warning: found None in authors list")
                    continue
                if not isinstance(a, dict):
                    print(f"Warning: author is not a dict: {a}")
                    continue
                valid_authors.append(a)
            authors = valid_authors

            try:
                response_data = {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "authors": json.dumps(authors),
                    "emails": json.dumps(
                        [a.get("email", "unknown@example.com") for a in authors]
                        if authors else []
                    ),
                    "messages": json.dumps(messages),
                }
                print("Response data constructed successfully")
                return response_data, authors
            except Exception as e:
                print(f"Error constructing response data: {e}")
                return None, []

        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            logger.error("Clone failed for %s: %s", repo.get("full_name", "unknown"), e, exc_info=True)
            return None, []

    except Exception as e:
        print(f"Unexpected error in clone_and_collect_data: {e}")
        import traceback
        traceback.print_exc()
        return None, []



def _extract_commits(repo_obj: Repo) -> Tuple[List[dict], List[str]]:
    authors = []
    messages = []
    try:
        for commit in repo_obj.iter_commits(all=True):
            try:
                author_name = commit.author.name if commit.author and commit.author.name else "Unknown"
                author_email = commit.author.email if commit.author and commit.author.email else "unknown@example.com"
                author = {"name": author_name, "email": author_email}
            except AttributeError:
                author = {"name": "Unknown", "email": "unknown@example.com"}

            if author not in authors:
                authors.append(author)

            message = commit.message.strip() if commit.message else ""
            messages.append(message)
    except Exception as e:
        print(f"Error extracting commits: {e}")

    return authors, messages



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
        if "message" in repos:
            message = repos["message"]
            if message == "Not Found":
                out.append(
                    {
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "error": False,
                        "others": {"Message": "Not Found", "errorMessage": "Not Found"},
                        "data": None,
                    }
                )
            elif message.startswith("API rate limit exceeded"):
                out.append(
                    {
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True,
                        "exists": False,
                        "error": True,
                        "others": {
                            "Message": "API rate limit exceeded",
                            "errorMessage": "API rate limit exceeded",
                        },
                        "data": None,
                    }
                )
            elif message.startswith("Bad credentials"):
                out.append(
                    {
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "error": True,
                        "exists": False,
                        "others": {
                            "Message": "Bad credentials",
                            "errorMessage": "Bad credentials",
                        },
                        "data": None,
                    }
                )
        else:
            RESULTS_FOLDER = (
                os.path.join(args["output"], username)
                if "output" in args and args["output"]
                else os.path.join(root_dir, f"results/{username}")
            )
            os.makedirs(RESULTS_FOLDER, exist_ok=True)

            if "fork" in args and not args["fork"]:
                repos = [repo for repo in repos if not repo["fork"]]
            if "size" in args and int(args["size"]) > 0:
                repos = [
                    repo for repo in repos if 0 < int(repo["size"]) < int(args["size"])
                ]
            else:
                repos = [repo for repo in repos if 0 < int(repo["size"]) < 500000]
            if len(repos) < 1:
                out.append(
                    {
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "others": {
                            "Message": "No repositories found for this user.",
                            "errorMessage": "No repositories found for this user.",
                        },
                        "data": None,
                    }
                )
                return

            _repos = []
            _authors = []

            with concurrent.futures.ThreadPoolExecutor() as executor:

                future_to_repo = {
                        executor.submit(
                        clone_and_collect_data,
                        repo,

                        username,
                        args,
                        RESULTS_FOLDER,
                        out,            # ⬅️ dernier param.
                    ): repo
                    for repo in repos
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
                        out.append(
                            {
                                "name": name,
                                "domain": domain,
                                "method": method,
                                "frequent_rate_limit": frequent_rate_limit,
                                "rateLimit": False,
                                "exists": True,
                                "others": {
                                    "Message": "Error processing repository.",
                                    "errorMessage": str(exc),
                                },
                                "data": None,
                            }
                        )

            if not _authors:
                out.append(
                    {
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "others": {
                            "Message": "No authors or emails found for this user.",
                            "errorMessage": "No authors or emails found for this user.",
                        },
                        "data": json.dumps(_repos),
                    }
                )
            else:
                # Remove duplicate authors
                authors = []
                for _auth in _authors:
                    if _auth not in authors:
                        authors.append(_auth)

                out.append(
                    {
                        "name": "repository",
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True,
                        "others": None,
                        "data": json.dumps(_repos),
                    }
                )

                out.append(
                    {
                        "name": "repository",
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True,
                        "others": None,
                        "data": json.dumps(authors),
                    }
                )
    except Exception as e:
        print(e, "Error")
        out.append(
            {
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False,
                "data": None,
                "others": {"Message": "An error occurred.", "errorMessage": str(e)},
            }
        )
