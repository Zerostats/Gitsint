
from gitsint import *
from bs4 import BeautifulSoup
import json

async def extract_usernames(url, client, out):
    friends = []
    response = await client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    

    name = None
    username = None
    
    for user in soup.find_all("span", {"class": ["Link--primary", "Link--secondary"]}):
        if "Link--primary" in user["class"]:
            name = user.text.strip()
        elif "Link--secondary" in user["class"]:

            username = user.text.strip()
            link = f"https://github.com/{username}"
            friends.append({"name": name, "username": username, "link": link})


    return friends

async def extract_all_usernames(url,client,out):
    usernames = []
    page_num = 1
    while True:
        page_url = f"{url}&page={page_num}"
        
        extracted_usernames = await extract_usernames(page_url,client,out)
        if len(extracted_usernames) == 0:
            break
        usernames.extend(extracted_usernames)
        page_num += 1
    return usernames


async def track(user,client,out):
    followers_url = f"https://github.com/{user}?tab=followers"
    following_url = f"https://github.com/{user}?tab=following"

    followers_usernames = await extract_all_usernames(followers_url,client,out)
    following_usernames = await extract_all_usernames(following_url,client,out)

    
    common_usernames =  [user for user in followers_usernames if user in following_usernames]
    
    

    return json.dumps(common_usernames)

async def friends(user, client, out, args):
    
    name = "friends"
    domain = "friends"
    method="bs4"
    frequent_rate_limit=True
    
    username = user['login']

    try:

        # TODO if repo > 100
        usernames = await track(username,client,out)
             
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True,
                    "data": usernames,
                    "others": None,

                    })

    except Exception as e:
        print(e)
        
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False,
                    "data": None,
                    "others": None,

                    })