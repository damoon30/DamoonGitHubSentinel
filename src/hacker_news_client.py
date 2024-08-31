import requests
from bs4 import BeautifulSoup
from logger import LOG


def crawl_news(url: str) -> list:
    LOG.info('Crawling')
    response = requests.get(url)

    content = []
    # 检查响应状态
    if response.status_code == 200:
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找热点新闻
        stories = soup.find_all('tr', class_='athing')
        # 输出热点信息
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                print(f'Title: {title}')
                print(f'Link: {link}')
                print('---')
                content.append((title, link))
    else:
        LOG.info('Crawling error')

    LOG.info('Crawling end')

    return content

class HackerNews:
    def __init__(self):
        LOG.info('Initializing HackerNews')


if __name__ == '__main__':
    crawl_news(url='https://news.ycombinator.com/''')