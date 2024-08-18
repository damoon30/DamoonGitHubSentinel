# src/command_handler.py

import argparse
import os

from logger import LOG
from config import read_md_file
from datetime import datetime, date, timedelta

class CommandHandler:
    def __init__(self, github_client, subscription_manager, report_generator):
        self.github_client = github_client
        self.subscription_manager = subscription_manager
        self.report_generator = report_generator
        self.parser = self.create_parser()

    def create_parser(self):
        parser = argparse.ArgumentParser(
            description='GitHub Sentinel Command Line Interface',
            formatter_class=argparse.RawTextHelpFormatter
        )
        subparsers = parser.add_subparsers(title='Commands', dest='command')

        parser_add = subparsers.add_parser('add', help='Add a subscription')
        parser_add.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
        parser_add.set_defaults(func=self.add_subscription)

        parser_remove = subparsers.add_parser('remove', help='Remove a subscription')
        parser_remove.add_argument('repo', type=str, help='The repository to unsubscribe from (e.g., owner/repo)')
        parser_remove.set_defaults(func=self.remove_subscription)

        parser_list = subparsers.add_parser('list', help='List all subscriptions')
        parser_list.set_defaults(func=self.list_subscriptions)

        parser_export = subparsers.add_parser('export', help='Export daily progress')
        parser_export.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export.set_defaults(func=self.export_daily_progress)

        parser_export_range = subparsers.add_parser('export-range', help='Export progress over a range of dates')
        parser_export_range.add_argument('repo', type=str, help='The repository to export progress from (e.g., owner/repo)')
        parser_export_range.add_argument('days', type=int, help='The number of days to export progress for')
        parser_export_range.set_defaults(func=self.export_progress_by_date_range)

        parser_generate = subparsers.add_parser('generate', help='Generate daily report from markdown file')
        parser_generate.add_argument('repo', type=str, help='The repository to subscribe to (e.g., owner/repo)')
        parser_generate.add_argument('date', type=str, help='file name for md report')
        parser_generate.set_defaults(func=self.generate_daily_report)

        parser_help = subparsers.add_parser('help', help='Show help message')
        parser_help.set_defaults(func=self.print_help)

        return parser

    def add_subscription(self, args):
        self.subscription_manager.add_subscription(args.repo)
        print(f"Added subscription for repository: {args.repo}")
        LOG.info("Added subscription for repository:" + args.repo)

    def remove_subscription(self, args):
        self.subscription_manager.remove_subscription(args.repo)
        print(f"Removed subscription for repository: {args.repo}")

    def list_subscriptions(self, args):
        subscriptions = self.subscription_manager.list_subscriptions()
        print("Current subscriptions:")
        for sub in subscriptions:
            print(f"  - {sub}")

    def export_daily_progress(self, args):
        self.github_client.export_daily_progress(args.repo)
        print(f"Exported daily progress for repository: {args.repo}")

    def export_progress_by_date_range(self, args):
        self.github_client.export_progress_by_date_range(args.repo, days=args.days)
        print(f"Exported progress for the last {args.days} days for repository: {args.repo}")

    def generate_daily_report(self, args):
        # 根据
        # today = datetime.now().date().isoformat()
        # updates = self.github_client.fetch_updates(args.repo, since=today)
        # print(updates)
        # 获取repo下载的文件地址
        repo_dir = os.path.join('daily_progress', args.repo.replace("/", "_"))
        file_path = os.path.join(repo_dir, f'{args.date}.md')

        self.report_generator.generate_daily_report(file_path)
        print(f"Generated daily report from file: {args.repo}")

    def print_help(self, args=None):
        self.parser.print_help()
