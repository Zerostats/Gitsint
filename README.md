# **Gitsint OSINT - Github user to usernames, names and emails.**

🕵️ Hi there! Feel free to submit issues or PR !

📧 For any professional / personal inquiries or collaborations, reach out to me at: 43150869+Zerostats@users.noreply.github.com

![](https://files.catbox.moe/w30lsv.png)

![PyPI](https://img.shields.io/pypi/v/gitsint) ![PyPI - Week](https://img.shields.io/pypi/dw/gitsint) ![PyPI - Downloads](https://static.pepy.tech/badge/gitsint) ![PyPI - License](https://img.shields.io/pypi/l/gitsint) [![Try it on telegram](https://img.shields.io/badge/Try%20me%20on%20Telegram-2CA5E0?style=flat-squeare&logo=telegram&logoColor=white)](http://t.me/gitsint_bot)

# **Telegram bot**

For a quick demo, you can try the bot on [telegram](http://t.me/gitsint_bot).


Here are the commands you can use with the bot:

# Telegram bot commands

- `help` - Display help message
- `register $TOKEN` - Register your GitHub token
- `gitsint $USERNAME` - Search for a GitHub user

> `⚠️ To prevent abuse, the bot is rate-limited to 1 request per minute.`<br>
> `⭐ You can use your own token and star this repo to bypass this limitation.`



## 📃 **Summary**

*Efficiently finding name, emails and usernames from a github user.*

Gitsint is a Github osint tool. It gather all available informations from a github user.

+ Retrieves information using github profiles, repositories and commits .
+ Does not alert the target.
+ Runs on [Python 3](https://www.python.org/downloads/release/python-370/).
+ Works on Windows, Linux, Mac OS X.
+ Can be used as a library or a CLI tool.


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
               [--only-used] [--no-color] [--no-clear] [-C] [-J] [-T TIMEOUT] [--cli]
               [--clean]
               USERNAME [USERNAME ...]

positional arguments:
  USERNAME              Target Username

options:
  -h, --help            show this help message and exit
  --size SIZE           Set max size value (default 50000)
  --token TOKEN [TOKEN ...]
                        API token
  --fork                Include forked repositories
  --private             Include private repositories
  --only-used           Displays only the sites used by the target username address.
  --no-color            Don't color terminal output
  --no-clear            Do not clear the terminal to display the results
  -C, --csv             Create a CSV with the results
  -J, --json            Create a JSON with the results
  -T TIMEOUT, --timeout TIMEOUT
                        Set max timeout value (default 10)
  --cli                 Print the response in JSON format
```


### 📚 CLI Example

```console
# By size + fork
gitsint exemple --size 5000 --fork

# Using a token
gistsint exemple --token $TOKEN

# Private footprints /!\ have to match own username
gitsint exemple --token $TOKEN --private


```

### 📈 Python Example

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


## TODO

[ ] - Add confidence
[ ] - Implement git SDK




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
