from fake_useragent import UserAgent
from bs4 import BeautifulSoup as Soup
from requests_html import HTMLSession

ua = UserAgent()
s = HTMLSession()

def parse(url, scroll):
    base_url = url

    response = s.get(
        base_url,
        headers={'User-Agent': ua.chrome})

    response.html.render(
        sleep=2,
        scrolldown=scroll
    )

    soup = Soup(response.html.raw_html, 'html.parser')
    info = [item.a['href'] for item in soup.find_all('h3', class_='channel-card__title')]
    print(len(info))
    data = info.pop(0)

    return info

print(parse('https://tlgrm.ru/channels/business', 1))