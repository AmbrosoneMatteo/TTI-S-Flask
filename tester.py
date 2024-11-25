import requests
from concurrent.futures import ThreadPoolExecutor

"""
To use this script disable the login required in the routes image

This script is intended to test how many TTI requests the server can manage
before the GPU runs out of memory
"""

myobj = {'text': 'stable diffusion'}
url = [('http://localhost:5000/image-generation', myobj)]*10

def post_url(args):
    return requests.post(args[0], data=args[1])


with ThreadPoolExecutor(max_workers=10) as pool:
    response_list = list(pool.map(post_url,url))

for response in response_list:
    print(response)