import unittest
import httpx


from gitsint.modules.profile.friends import friends as gitsint_friends
from gitsint.modules.repos.repository import repository as gitsint_repos 
from gitsint.modules.profile.profile import profile as gitsint_profile


print("ok")
class TestGitsintModules(unittest.TestCase):
    async def test_profile(self):
        
        username = "exemple"
        client = httpx.AsyncClient()

        out = []
        
        await gitsint_repos({'login':username}, client, out, {"size": '50',"fork":False})


        result = await client.aclose()

        

