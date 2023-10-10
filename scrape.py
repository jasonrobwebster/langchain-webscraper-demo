

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
#     "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
# ]


# Faster? Oh yeah alot faster.

import argparse
import os
import logging
import json
import random
import aiohttp
import asyncio
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Argument parser setup
parser = argparse.ArgumentParser()
parser.add_argument("--site", type=str, required=True)
parser.add_argument("--depth", type=int, default=3)

# List of User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    # Add more user-agents if needed
]

def clean_url(url: str) -> str:
    return url.replace("https://", "").replace("/", "-").replace(".", "_")

async def fetch(url: str, session: aiohttp.ClientSession) -> str:
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        async with session.get(url, headers=headers) as response:
            logger.info(f"\nFetching: {url}\n{'='*len(url)}\nUsing User-Agent: {headers['User-Agent']}")
            return await response.text()
    except Exception as e:
        logger.error(f"\nFailed to fetch {url}\nError: {str(e)}")
        return None

async def save_response_content(content: str, path: str):
    with open(path, "w", encoding='utf-8') as f:
        f.write(content)

async def scrape_links(session: aiohttp.ClientSession, scheme: str, origin: str, path: str, depth=3, sitemap=None) -> dict:
    if sitemap is None:
        sitemap = defaultdict(lambda: "")
    
    site_url = f"{scheme}://{origin}{path}"
    cleaned_url = clean_url(site_url)

    if depth < 0 or sitemap[cleaned_url] != "":
        return sitemap

    sitemap[cleaned_url] = site_url
    response_content = await fetch(site_url, session)
    if response_content is None:
        return sitemap

    if not os.path.exists("./scrape"):
        os.mkdir("./scrape")
    await save_response_content(response_content, f"./scrape/{cleaned_url}.html")

    soup = BeautifulSoup(response_content, "html.parser")
    links = soup.find_all("a")

    tasks = []
    for link in links:
        href = urlparse(link.get("href", ""))
        if (href.netloc and href.netloc != origin) or (href.scheme and href.scheme != "https"):
            continue
        tasks.append(scrape_links(session, href.scheme or scheme, href.netloc or origin, href.path, depth=depth-1, sitemap=sitemap))
    
    await asyncio.gather(*tasks)
    return sitemap

async def main(args):
    url = urlparse(args.site)
    logger.info(f"\nScraping initiated for: {args.site}\nDepth: {args.depth}\n")
    
    async with aiohttp.ClientSession() as session:
        sitemap = await scrape_links(session, url.scheme, url.netloc, url.path, depth=args.depth)
    
    with open("./scrape/sitemap.json", "w") as f:
        json.dump(sitemap, f)
    logger.info("\nScraping completed. Sitemap saved to ./scrape/sitemap.json\n")

if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(main(args))







# Working slow. 

# import argparse
# import requests
# import os
# import logging
# import time
# from urllib.parse import urlparse
# from collections import defaultdict
# from bs4 import BeautifulSoup
# import json
# import random

# # Setup logging
# logging.basicConfig(format='%(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Argument parser setup
# parser = argparse.ArgumentParser()
# parser.add_argument("--site", type=str, required=True)
# parser.add_argument("--depth", type=int, default=3)

# # List of User-Agents
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
#     # Add more user-agents if needed
# ]

# def clean_url(url: str) -> str:
#     return url.replace("https://", "").replace("/", "-").replace(".", "_")

# def get_response_and_save(url: str) -> requests.Response:
#     try:
#         headers = {"User-Agent": random.choice(USER_AGENTS)}
#         logger.info(f"\nFetching: {url}\n{'='*len(url)}\nUsing User-Agent: {headers['User-Agent']}")
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         logger.error(f"\nFailed to fetch {url}\nError: {str(e)}")
#         return None

#     if not os.path.exists("./scrape"):
#         os.mkdir("./scrape")
#     parsed_url = clean_url(url)
#     with open(f"./scrape/{parsed_url}.html", "wb") as f:
#         f.write(response.content)
#     return response

# def scrape_links(scheme: str, origin: str, path: str, depth=3, sitemap=None) -> dict:
#     if sitemap is None:
#         sitemap = defaultdict(lambda: "")
    
#     site_url = f"{scheme}://{origin}{path}"
#     cleaned_url = clean_url(site_url)

#     if depth < 0 or sitemap[cleaned_url] != "":
#         return sitemap

#     sitemap[cleaned_url] = site_url
#     response = get_response_and_save(site_url)
#     if response is None:
#         return sitemap

#     soup = BeautifulSoup(response.content, "html.parser")
#     links = soup.find_all("a")

#     for link in links:
#         href = urlparse(link.get("href", ""))
#         if (href.netloc and href.netloc != origin) or (href.scheme and href.scheme != "https"):
#             continue
#         time.sleep(1)  # Respectful crawling by sleeping between requests
#         scrape_links(href.scheme or scheme, href.netloc or origin, href.path, depth=depth-1, sitemap=sitemap)
    
#     return sitemap

# if __name__ == "__main__":
#     args = parser.parse_args()
#     url = urlparse(args.site)
#     logger.info(f"\nScraping initiated for: {args.site}\nDepth: {args.depth}\n")
#     sitemap = scrape_links(url.scheme, url.netloc, url.path, depth=args.depth)
#     with open("./scrape/sitemap.json", "w") as f:
#         json.dump(sitemap, f)
#     logger.info("\nScraping completed. Sitemap saved to ./scrape/sitemap.json\n")
