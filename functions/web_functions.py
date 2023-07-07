import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

def browse_web(url):
    MAX_PAGE_SIZE = 128 * 1024  # You say limitations, I say.... well, fine. Limitations.

    parsed_url = urlparse(url)
    robots_url = urljoin(url, '/robots.txt')  # Start the parsing party.

    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    if not rp.can_fetch('*', parsed_url):  # If the robots.txt disapproves, walk away. Trust me, you don't want to get into a fight with a robot.
        return 'Error: does not allow web scraping: ' + url

    response = requests.get(url)
    content = response.content[:MAX_PAGE_SIZE]  # Enough is as good as a feast. Limit the buffet, will ya?

    soup = BeautifulSoup(content, 'html.parser')  # Alphabet soup? Nah, BeautifulSoup!

    text_content = soup.get_text()  # Now this is my kinda soup, data soup!

    MAX_TEXT_LENGTH = 10000  # Even superheroes have their limits.

    trimmed_content = text_content[:MAX_TEXT_LENGTH]  # Snippity snip!

    return trimmed_content.strip()  # Trim the fat, and return the content.