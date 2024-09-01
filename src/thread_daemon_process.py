import asyncio

import daemon
import threading
import time

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from scheduler_hacker_news import SchedulerHackerNews
from logger import LOG


def run_scheduler(scheduler):
    scheduler.start()


def main():
    config = Config()
    notifier = Notifier(config.notification_settings)
    llm = LLM(config.llm_config)
    report_generator = ReportGenerator(llm)

    scheduler = SchedulerHackerNews(
        notifier=notifier,
        report_generator=report_generator,
        interval=1000
    )

    scheduler_thread = threading.Thread(target=run_scheduler, args=(scheduler,))
    scheduler_thread.daemon = True
    scheduler_thread.start()

    LOG.info("Scheduler thread started.")

    # Use python-daemon to properly daemonize the process
    # with daemon.DaemonContext():
    #     try:
    #         while True:
    #             print(f"主线程运行")
    #             time.sleep(5)
    #     except KeyboardInterrupt:
    #         LOG.info("Daemon process stopped.")

    # 主线程的任务
    try:
        for i in range(1000):
            print(f"主线程运行: {i}")
            time.sleep(10)  # 每 1 秒打印一次
    except KeyboardInterrupt:
        print("主线程被中断")

    print("主线程结束，守护线程也将结束。")


if __name__ == '__main__':
    main()

# nohup python3 src/daemon_process.py > logs/daemon_process.log 2>&1 &
