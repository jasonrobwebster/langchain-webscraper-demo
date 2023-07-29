import argparse
import requests
import os
from urllib.parse import urlparse
from collections import defaultdict
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument("--site", type=str, required=True)
parser.add_argument("--depth", type=int, default=3)


def get_request_and_save(root: str):
    url = root
    parsedUrl = url.replace("https://", "").replace("/", "-").replace(".", "_")
    print(url, parsedUrl)
    request = requests.get(url)
    if not os.path.exists("./scrape"):
        os.mkdir("./scrape")
    with open("./scrape/" + parsedUrl + ".html", "wb") as f:
        # soup = BeautifulSoup(request.content, features="lxml")
        f.write(request.content)
    return request


def scrape_links(
    scheme: str,
    origin: str,
    path: str,
    depth=3,
    visited_sites: dict = defaultdict(lambda: False),
):
    if depth <= 0:
        return
    if visited_sites[path]:
        return
    visited_sites[path] = True
    request = get_request_and_save(scheme + "://" + origin + path)
    soup = BeautifulSoup(request.content, "html.parser")
    links = soup.find_all("a")
    for link in links:
        href = urlparse(link.get("href"))
        if (href.netloc != origin and href.netloc != "") or (
            href.scheme != "" and href.scheme != "https"
        ):
            continue
        scrape_links(
            href.scheme or "https",
            href.netloc or origin,
            href.path,
            depth=depth - 1,
            visited_sites=visited_sites,
        )


if __name__ == "__main__":
    args = parser.parse_args()
    url = urlparse(args.site)
    scrape_links(url.scheme, url.netloc, url.path, depth=args.depth)
