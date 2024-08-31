# src/scheduler.py

import time
from datetime import date

from hacker_news_client import crawl_news
from report_generator import ReportGenerator
from llm import LLM
from notifier import Notifier


class SchedulerHackerNews:
    def __init__(self, notifier, report_generator: ReportGenerator, interval=86400):
        self.notifier = notifier
        self.report_generator = report_generator
        self.interval = interval

    def start(self):
        self.run()

    def run(self):
        # 爬取信息
        new_list = crawl_news(url='https://news.ycombinator.com/')
        # 整理成报告
        content = self.report_generator.generate_hacker_news(new_list)

        # 发送邮件
        title = f"今日HackerNews新闻_{date.today()}"
        self.notifier.notify(title, content)
        print("----------finish----------")


if __name__ == '__main__':
    # notifier = Notifier()
    # llm = LLM()
    # report_generator = ReportGenerator(llm)
    # scheduler = SchedulerHackerNews(notifier, report_generator)
    # scheduler.start()
    pass
