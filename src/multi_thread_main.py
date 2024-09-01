from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager

executor = ThreadPoolExecutor(max_workers=3)


def main():
    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.notification_settings)
    llm = LLM(config.llm_config)
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)

    print("-----tasking----")
    all_tasks = [
        executor.submit(lambda cpx: run_on_thread_task(*cpx),
                        (github_client, notifier, subscription_manager, report_generator, 1)),
        executor.submit(lambda cpx: run_on_thread_task(*cpx),
                        (github_client, notifier, subscription_manager, report_generator, 7)),
        executor.submit(lambda cpx: run_on_thread_task(*cpx),
                        (github_client, notifier, subscription_manager, report_generator, 14)),
    ]
    for future in as_completed(all_tasks):
        print("----start---")
        result = future.result()
        print(f"----end---{result}")
        print(result)


def run_on_thread_task(github_client: GitHubClient,
                       notifier: Notifier,
                       subscription_manager: SubscriptionManager,
                       report_generator: ReportGenerator,
                       days: int):
    """
    多线程执行任务，但是多线程还是会等待任务执行完成后
    :param config:
    :param github_client:
    :param notifier:
    :param llm:
    :param subscription_manager:
    :param report_generator:
    :param days:
    :return:
    """
    print(days)
    for repo in subscription_manager.list_subscriptions():
        try:
            # 导出更新
            file_path = github_client.export_progress_by_date_range(repo=repo, days=days)
            print(f"update----{file_path}---")
            # 目录下生成日报的翻译
            report, report_file_path = report_generator.generate_report_by_date_range(markdown_file_path=file_path)

            subject = repo + "总结"
            notifier.notify(subject, report)
        except Exception as exp:
            print({exp})
    return "ok"


if __name__ == '__main__':
    main()