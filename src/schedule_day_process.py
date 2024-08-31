import asyncio
import functools

import daemon
import threading
import time

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from scheduler_hacker_news import SchedulerHackerNews
import schedule
import time


def run_scheduler(scheduler):
    scheduler.start()


def main():
    """
    每小时执行一次：schedule.every().hour.do(job)
    每天特定时间执行：schedule.every().day.at("10:30").do(job)
    每周特定时间执行：schedule.every().week.at("monday").do(job)
    :return:
    """
    notifier = Notifier()
    llm = LLM()
    report_generator = ReportGenerator(llm)

    scheduler = SchedulerHackerNews(
        notifier=notifier,
        report_generator=report_generator,
        interval=1000
    )

    job = functools.partial(run_scheduler, scheduler)
    schedule.every().day.at("15:16").do(job)

    # 持续运行调度
    while True:
        schedule.run_pending()  # 运行所有待执行的任务
        time.sleep(1)  # 每秒检查一次
        print("run")

    # print("主线程结束，守护线程也将结束。")


if __name__ == '__main__':
    main()

# nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
