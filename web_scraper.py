import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from ast import literal_eval

# Courtesy to the BeautifulSoup team for their wonderful library.
def browse_web(url):
    # You say limitations, I say.... well, fine. Limitations.
    MAX_PAGE_SIZE = 128 * 1024

    # Begin the parsing party, urlparse you're up!
    parsed_url = urlparse(url)
    robots_url = urljoin(url, '/robots.txt')

    # Reveal the secrets of the robots.txt, oh mighty RobotFileParser
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    # If the robots.txt disapproves, walk away. It's a trap!
    if not rp.can_fetch('*', url):
        return 'Error: The website does not allow web scraping.'

    response = requests.get(url)
    # Enough is as good as a feast. Limit the buffet, will ya?
    content = response.content[:MAX_PAGE_SIZE]

    # Roll out the 'soup', let's get parsing!
    soup = BeautifulSoup(content, 'html.parser')

    # Extracting content from soup sure beats the diet.
    text_content = soup.get_text()

    # Real heroes know their limits, unlike the guy who ate the Infinity Stone.
    MAX_TEXT_LENGTH = 10000

    # Speech too long? A little snip-snip should do.
    trimmed_content = text_content[:MAX_TEXT_LENGTH]

    return trimmed_content
