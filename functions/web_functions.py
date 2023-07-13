import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser

class WebScraper:
    def __init__(self, max_page_size=128*1024, max_text_length=10000):
        self.max_page_size = max_page_size
        self.max_text_length = max_text_length
        self.session = requests.Session()

    def clean_soup(self, soup):
        for element in soup(['script', 'style', 'head', 'title', 'meta', '[document]']):
            element.extract()
        for element in soup(text=lambda text: isinstance(text, Comment)):
            element.extract()
        return soup

    def get_text_content(self, url):
        try:
            response = self.session.get(url)
            content = response.content[:self.max_page_size]
            soup = BeautifulSoup(content, 'html.parser')
            soup = self.clean_soup(soup)
            text_content = soup.get_text(separator=' ')
            return text_content.strip()
        except requests.exceptions.RequestException as e:
            return 'Error: ' + str(e)

    def parse_links(self, url, soup):
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
        links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a')]
        return links

    def scrape_web(self, url):
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return 'Error: Invalid URL'
        
        robots_url = urljoin(url, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()

        if not rp.can_fetch('*', parsed_url.path):
            return 'Error: does not allow web scraping: ' + url
        
        response = self.get_text_content(url)
        if response.startswith('Error: '):
            return response
        
        soup = BeautifulSoup(response, 'html.parser')
        links = self.parse_links(url, soup)
        return {
            'content': response[:self.max_text_length],
            'links': links,
        }

def browse_web(url):
    scraper = WebScraper()
    output = scraper.scrape_web(url)
    return output