import json
import os


def read_md_file(file_path):
    """
    读取指定路径下的 .md 文件并返回其内容。

    参数:
    file_path (str): .md 文件的完整路径

    返回:
    str: 文件内容，如果文件不存在或读取失败则返回 None
    """
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} does not exist.")
        return None

    if not file_path.endswith('.md'):
        print(f"Error: {file_path} is not an .md file.")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)
            self.github_token = config.get('github_token')
            self.notification_settings = config.get('notification_settings')
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # Default to 24 hours

    import os

    # 示例使用
    file_path = "/path/to/your/file.md"
    content = read_md_file(file_path)
    if content:
        print("File Content:")
        print(content)

