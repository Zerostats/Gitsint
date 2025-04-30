import requests
from termcolor import colored
import httpx
import trio


import os
from argparse import ArgumentParser
import csv
from datetime import datetime
import time
import importlib
import pkgutil
import json
import subprocess

from gitsint.instruments import TrioProgress
from importlib.metadata import version, PackageNotFoundError

DEBUG        = True
OUTPUT_PATH  = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output"))
json_data = []
username_FORMAT = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

try:
    __version__ = version("gitsint")
except PackageNotFoundError:
    __version__ = "dev"  # fallback for development or when not installed

def import_submodules(package, recursive=True):
    """Get all the Gitint submodules"""
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def get_functions(modules,args=None):
    """Transform the modules objects to functions"""
    functions = []

    for module in modules:
        if len(module.split(".")) > 3 :
            modu = modules[module]
            site = module.split(".")[-1]
            functions.append(modu.__dict__[site])
    return functions



def check_update():
    """Check and update gitsint if not the latest version on PyPI."""
    try:
        response = httpx.get("https://pypi.org/pypi/gitsint/json", timeout=5)
        response.raise_for_status()
        latest_version = response.json().get("info", {}).get("version", "")

        if latest_version and latest_version != __version__:
            print(f"A new version of gitsint is available: {latest_version} (current: {__version__})")
            print("Updating...")

            pip_cmd = ["pip", "install", "--upgrade", "gitsint"]
            process = subprocess.run(pip_cmd, capture_output=True, text=True)

            if process.returncode == 0:
                print("✅ gitsint has been updated successfully.")
                print("Please restart the tool.")
                exit(0)
            else:
                print("❌ Update failed.")
                print("Error output:\n", process.stderr)
        else:
            print("✅ gitsint is up to date.")
    except httpx.RequestError as e:
        print(f"⚠️ Failed to check for updates (network issue): {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error during update check: {e}")


def credit(args):
    """Print Credit"""
    #TODO
    if(args.cli):
        return
    def print_fancy_credits():
        print('===============================')
        print('        Gitsint Credits        ')
        print('===============================')
        print('\033[94mGithub: https://github.com/zerostats/gitsint\033[0m')
        print('\033[94mThis tool is made for educational purposes only.\033[0m')
        print('\033[94mDo not use it for illegal purposes.\033[0m')
        print('===============================')

    print_fancy_credits()
    
def fetch_user(username: str,args) -> str:
    """Check if the input is a valid username address

    Keyword Arguments:
    username       -- String to be tested

    Return Value:
    User     -- True if string is an username, False otherwise
    """
    headers = {}
    if args.token:
        headers['Authorization'] = f"Bearer {args.token[0]}"
    url = f"https://api.github.com/users/{username}"
    r = requests.get(url.format(username), headers=headers)
    res = r.json()
    if 'message' in res:
        if res['message'] == "Not Found":   # Just to be double sure
            res= "Error: User not found"
        elif res['message'].startswith("API rate limit exceeded"):
            res = "Error: API rate limit exceeded, please try again later or give a --token argument"
        elif res['message'].startswith("Bad credentials"):
            res = "Error: Bad credentials, please check your --token argument"
    return res




def print_result(data,args,user,start_time,functions):
    def print_color(text,color,args):
        if args.nocolor == False:
            return(colored(text,color))
        else:
            return(text)

    if args.noclear==False:
        print("\033[H\033[J")
    else:
        print("\n")

    description = print_color("[+] username used","green",args) + "," + print_color(" [x] Rate limit","yellow",args) + ","  + print_color(" [~] User information","cyan",args) + "," + print_color(" [!] Error","red",args)
    print("\n" + description)
        
    for results in data:
        
        ratelimit = results["rateLimit"]
        domain = results["domain"]
        rdata = results["data"]
        others = results["others"]
        exists = results["exists"]
        

        websiteprint = ""
            
        # Check if the method is userprofile
        if ratelimit and args.onlyused == False:
            websiteprint = print_color("[x] " + domain, "yellow",args)
            print(websiteprint)
        elif "error" in results.keys() and results["error"]:
            toprint = ""
            if others is not None and "Message" in str(others.keys()):
                toprint = " Error message: " + others["errorMessage"]
            websiteprint = print_color("[!] " + domain + toprint, "red",args)
            print(websiteprint)
        elif exists == False and "Message" in str(others.keys()):
            websiteprint = print_color("[-] " + domain, "magenta",args) + " " + others["Message"] + "\n"
            print(websiteprint)
        elif rdata is not None and exists == True and others is None:
            print("")
            websiteprint = print_color("[~] " + domain, "cyan",args)
            print(websiteprint)
            # print(f"{key.capitalize()}: " + print_color(value, "cyan", args))
            if isinstance(rdata, str):
                rdata = json.loads(rdata)
                
            toprint = ""
            #print("Data: " + str(rdata))
            #print(type(rdata))

                
            print_json(rdata,args)

            

    
    print(str(len(functions)) + " modules checked in " +
          str(round(time.time() - start_time, 2)) + " seconds\n")


def print_api(data,output_file=None):

    for module_data in data:

        
        json_data.append({
            "module_name": module_data["name"],
            "data": module_data
        })
    if output_file is not None:
        return json.dumps(json_data, indent=4)
    else:
        print(json.dumps(json_data, indent=4))
    #print(json.dumps(json_data, indent=4))
    #print(json.dumps(data[0], indent=4))


def print_json(json_obj, args, depth=0):
    """
    Print JSON key-value pairs recursively.

    Args:
    json_obj (dict or list): JSON object or array to print.
    """
    def print_color(text, color, args):
        if args.nocolor == False:
            return colored(text, color)
        else:
            return text

    indent = " " * (depth * 2 + 1) 
    if depth == 0:
        print("")
    elif depth == 1:
        print("")
    # elif depth == 2:
    #     print("2")
    toprint = ""
    
    if isinstance(json_obj, dict):
        
        for key, value in json_obj.items():
            print(f"{indent}{print_color(key.capitalize(), 'cyan', args)}: ", end="")
            if isinstance(value, (dict, list)):
                print()
                print_json(value, args, depth + 1)
            else:
                # Cast in json and find if result is an array
                print(print_color(str(value), 'white', args))
    elif isinstance(json_obj, list):
        for item in json_obj:
            print_json(item, args, depth + 1)



def export_csv(data, args, username):
    """Export result to CSV or JSON"""
    output_dir = args.output if args.output else OUTPUT_PATH

    now = datetime.now()
    timestamp = datetime.timestamp(now)

    if args.csvoutput:
        name_file = f"gitsint_{round(timestamp)}_{username}_results.csv"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_path = os.path.join(output_dir, name_file)

        with open(file_path, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(output_file, fieldnames=data[0].keys())
            fc.writeheader()
            fc.writerows(data)

        print("All results have been exported to " + file_path)

    if args.jsonoutput:
        name_file = f"gitsint_{round(timestamp)}_{username}_results.json"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        file_path = os.path.join(output_dir, name_file)

        with open(file_path, 'w', encoding='utf8') as output_file:
            json.dump(data, output_file, indent=4)

        exit("All results have been exported to " + file_path)

async def launch_module(module,profile, client, out, args):
    data={'profile': 'aprofile', 'friends': 'friends', 'repository': 'repository', 'track': 'track'}
    try:
        await module(profile, client, out, args)
    except Exception as e:
        print(e)
        name=str(module).split('<function ')[1].split(' ')[0]
        out.append({"name": name,"domain":data[name],
                    "rateLimit": False,
                    "error": True,
                    "exists": False,
                    "data": [],
                    "others": None})
        
        
async def maincore():
    parser= ArgumentParser(description=f"gitsint v{__version__}")
    parser.add_argument("username",
                    nargs='+', metavar='USERNAME',
                    help="Target Username")
    # add size
    parser.add_argument("--size", type=int, default=0, required=False, dest="size",
                    help="Set max size value (default 50000)")
    parser.add_argument("--token", nargs='+', metavar='TOKEN', dest="token", help="API token")
    parser.add_argument("--fork", default=False, required=False,action="store_true",dest="fork",
                    help="Include forked repositories")
    parser.add_argument("--private", default=False, required=False,action="store_true",dest="private",
                    help="Include private repositories")
    parser.add_argument("--only-used", default=False, required=False,action="store_true",dest="onlyused",
                    help="Displays only the sites used by the target username address.")
    parser.add_argument("--no-color", default=False, required=False,action="store_true",dest="nocolor",
                    help="Don't color terminal output")
    parser.add_argument("--no-clear", default=False, required=False,action="store_true",dest="noclear",
                    help="Do not clear the terminal to display the results")
    parser.add_argument("-C","--csv", default=False, required=False,action="store_true",dest="csvoutput",
                    help="Create a CSV with the results")
    parser.add_argument("-J","--json", default=False, required=False,action="store_true",dest="jsonoutput",
                    help="Create a JSON with the results")
    parser.add_argument("-T","--timeout", type=int , default=10, required=False,dest="timeout",
                    help="Set max timeout value (default 10)")
    parser.add_argument("--cli", default=False, required=False,action="store_true",dest="cli",
                    help="Print the response in JSON format")
    parser.add_argument("--clean", default=False, required=False,action="store_true",dest="cli",
                    help="Print the response in JSON format")
    parser.add_argument("--output", type=str, required=False, dest="output",
                    help="Specify custom output directory path")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--debug", default=False, required=False,action="store_true",dest="debug",
                    help="Enable debug mode")
    parser.add_argument("--check-update", action="store_true", dest="check_update",
                    help="Force a check for the latest version of gitsint on PyPI", default=False)


    args = parser.parse_args()

    credit(args)
    if args.check_update:
        check_update()
    username=args.username[0]

    user = fetch_user(username,args)
    if "Error" in user:
        print(colored(user, 'red'))
        exit()


    # Import Modules
    modules = import_submodules("gitsint.modules")
    functions = get_functions(modules,args)
    # Get timeout
    timeout=args.timeout
    # Start time
    start_time = time.time()
    # Def the async client
    client = httpx.AsyncClient(timeout=timeout)
    # Launching the modules
    out = []
    

    
    instrument = TrioProgress(len(functions))
    trio.lowlevel.add_instrument(instrument)
    async with trio.open_nursery() as nursery:
        for website in functions:
            nursery.start_soon(launch_module, website, user, client, out, args)
    trio.lowlevel.remove_instrument(instrument)
    
    
    # Sort by modules names
    out = sorted(out, key=lambda i: i['name'])
    # Close the client
    await client.aclose()
    # Print the result
    if args.cli:
        print_api(out)
    else:
        print_result(out,args,user,start_time,functions)
    credit(args)
    
    
    # Export results
    print()
    export_csv(out,args,username)

def main():
    trio.run(maincore)
