# 🔍 Gitsint OSINT — Extract usernames, names, emails & secrets from GitHub


🕵️‍♂️ Feel free to open issues, submit PRs, or suggest modules! Contributions are very welcome.


📧 For any professional / personal inquiries or collaborations, reach out to me at: 📧 Contact: Zerostats via [GitHub Discussions](https://github.com/Zerostats/Gitsint/discussions) or `43150869+Zerostats@users.noreply.github.com`


![](https://files.catbox.moe/w30lsv.png)

![PyPI](https://img.shields.io/pypi/v/gitsint) ![PyPI - Week](https://img.shields.io/pypi/dw/gitsint) ![PyPI - Downloads](https://static.pepy.tech/badge/gitsint) ![PyPI - License](https://img.shields.io/pypi/l/gitsint) [![Try it on telegram](https://img.shields.io/badge/Try%20me%20on%20Telegram-2CA5E0?style=flat-squeare&logo=telegram&logoColor=white)](http://t.me/gitsint_bot)

# **Telegram bot**

For a quick demo, you can try the bot on [telegram](http://t.me/gitsint_bot).


Here are the commands you can use with the bot:

## Telegram bot commands  

Atm the bot is down, will be fixed.

- `help` - Display help message
- `register $TOKEN` - Register your GitHub token
- `gitsint $USERNAME` - Search for a GitHub user

> `⚠️ To prevent abuse, the bot is rate-limited to 1 request per minute.`<br>
> `⭐ You can use your own token and star this repo to bypass this limitation.`


Here’s an updated version of your **📃 Summary** section that includes the new `--gitleaks` capability and reflects the current state of your tool:

---

## 🚀 Why Use Gitsint?

- 🕵️ Audit your own or others' public GitHub footprint
- 🔐 Find exposed secrets in commits and repos
- 🧩 Map email addresses to usernames
- 📊 Use in OSINT, red teaming, or compliance workflows

## 📃 **Summary**

*Efficiently extract usernames, names, emails, and even secrets from a GitHub account.*

**Gitsint** is a GitHub OSINT tool that automates the process of extracting public and private data from GitHub profiles, repositories, and commits.

### 🔍 Features

+ 🧠 Retrieves data from profiles, repositories, and commit history  
+ 🔒 Scans cloned repositories with [Gitleaks](https://github.com/gitleaks/gitleaks) to uncover secrets, tokens, emails, and credentials  
+ 🦻 Does **not alert** the target (read-only, non-intrusive)  
+ ⚙️ Supports CLI and library usage  
+ 📦 Exports results as **CSV** or **JSON**  
+ 🔁 Can **clone and scan** all user/org repositories (public/private/forked) 
+ 🧪 Compatible with **Python 3.10+**  
+ 💻 Cross-platform: works on **Linux, macOS, and Windows**



## 🛠️ Installation

### 🐍 With PyPI

```pip3 install gitsint```

### 🚀 With Github

```bash
git clone https://github.com/zerostats/gitsint.git
cd gitsint/
pip install -e .
```

### 🐳 With Docker


```bash
docker build . -t my-gitsint-image
docker run my-gitsint-image gitsint username
```

## Quick Start

Gitsint can be run from the CLI and rapidly embedded within existing python applications.

### Help

```console	
usage: gitsint [-h] [--size SIZE] [--token TOKEN [TOKEN ...]] [--fork] [--private]
               [--only-used] [--no-color] [--no-clear] [-C] [-J] [-T TIMEOUT]
               [--cli] [--clean] [--output OUTPUT] [--version] [--debug]
               [--check-update] [--gitleaks]
               USERNAME [USERNAME ...]

positional arguments:
  USERNAME              Target Username

options:
  -h, --help            Show this help message and exit
  --size SIZE           Set max repo size in KB (default: 50000)
  --token TOKEN [TOKEN ...]
                        API token (required for private or org access)
  --fork                Include forked repositories
  --private             Include private repositories
  --only-used           Display only the platforms used by the target
  --no-color            Disable colored terminal output
  --no-clear            Prevent terminal clearing before display
  -C, --csv             Save results to CSV
  -J, --json            Save results to JSON
  -T, --timeout TIMEOUT Set max timeout (default: 10 seconds)
  --cli                 Output raw JSON result to console
  --clean               Clean and reset previous result set
  --output OUTPUT       Set custom output folder (default: ./output)
  --version             Show version and exit
  --debug               Enable debug logging
  --check-update        Check for latest version on PyPI and auto-update
  --gitleaks            Run https://github.com/gitleaks/gitleaks to detect secrets in all cloned repositories


```


### 📚 CLI Example

```console
# Basic public scan
gitsint exemple

# Scan including forks
gitsint exemple --fork

# Limit by max repo size (in KB)
gitsint exemple --size 5000

# Use GitHub token (required for --private)
gitsint exemple --token $TOKEN

# Scan own private repos
gitsint yourname --token $TOKEN --private

# Save output to a specific folder
gitsint exemple --output ./my-results

# Export to JSON + CSV
gitsint exemple --csv --json

# Run Gitleaks scan on all cloned repos
gitsint exemple --token $TOKEN --private --gitleaks

# Check for Gitsint updates
gitsint exemple --check-update


```

### 📈 Python Example

Gitsint can be imported as a module to run targeted scans in your own scripts:


```python
import trio
import httpx

from gitsint.modules.profile.friends import friends


async def main():
    username = "exemple"
    out = []
    client = httpx.AsyncClient()

    await friends({'login':username}, client, out, [])

    print(out)

    await client.aclose()

trio.run(main)
```

## Module Output

For each module, data is returned in a standard dictionary with the following json-equivalent format :

```json
{
  "name": "module_name",
  "rateLimit": false,
  "exists": true,
  "data": "[{...}]",
  "others": null
}
```
- name : The name of the module ( friends, profile, repository.. )
- rateLitmit : Lets you know if you've been rate-limited.
- exists : If an account exists for the email on that service.
- data : The data returned by the module.
- others : Any extra info.


Rate limited? Use a token.


## 🧪 Development

Want to contribute or test modules locally? Here's how to get started.

### 🔧 Poetry-based Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/zerostats/gitsint.git
cd gitsint

# Install poetry if you haven't
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell

# Run the CLI
poetry run gitsint username
```

### 🔍 Useful Dev Commands

```bash
poetry run black gitsint/         # Format code
poetry run isort gitsint/         # Sort imports
```

### 💡 Dev Notes

* Modules live in gitsint/modules/ and are fully async
* Use out.append({...}) to return module results
* Optional flags (--token, --gitleaks, etc.) are available in the args object



## TODO

[ ] - Add confidence




## Thank you to :

- [Megadose](https://github.com/megadose) ( for the base template )



## 📝 License

[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.fr.html)

Built for educational purposes only.

## Modules
| Name       | Method            | Frequent Rate Limit |
| ---------- | ----------------- | ------------------- |
| friends    | bs4               | ✔                   |
| profile    | api               | ✘                   |
| repository | api               | ✘                   |
