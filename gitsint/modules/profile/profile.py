from argparse import Namespace
from gitsint import *


async def profile(user, client, out,args):
    name = "aprofile"
    domain = "Github Profile"
    method="api"
    frequent_rate_limit=True

    # Namespace from gitsint or from kwargs 
    if isinstance(args,Namespace):
        args = vars(args)
        
    try:
        username = user["login"]
        url = f"https://api.github.com/users/{username}"
        headers = {}
        if "token" in args and args['token'] != None:
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': "Bearer {}".format(''.join(args['token'])),
                'X-GitHub-Api-Version' : '2022-11-28',
            }
            url = f"https://api.github.com/user"
        r = await client.get(url, headers=headers)
        res = r.json()
        if 'message' in res:
            if res['message'] == "Not Found":   
                out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                "rateLimit": False,
                "exists": False,
                "error": False,
                "others": {"Message": "Not Found","errorMessage" : "Not Found"},
                "data": None})
            elif res['message'].startswith("API rate limit exceeded"):
                out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                "rateLimit": True,
                "exists": False,
                "error": True,
                "others": {"Message": "API rate limit exceeded","errorMessage" : "API rate limit exceeded"},
                "data": None})
            elif res['message'].startswith("Bad credentials"):
                out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                "rateLimit": False,
                "error": True,
                "exists": False,
                "others": {"Message": "Bad credentials","errorMessage" : "Bad credentials"},
                "data": None})
        else: 
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True,
                    "data": res,
                    "others": None})
        
    except Exception as e:
        # Handle the exception here
        print(f"An error occurred: {e}")
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                "rateLimit": False,
                "exists": False,
                "error": True,
                "others": {"Message": "An error occurred","errorMessage" : str(e)},
                "data": None})
        

