import gradio as gr

from config import Config
from github_client import GitHubClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG

config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM(config.llm_config)
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)
list_subscriptions = subscription_manager.list_subscriptions()


def export_progress_by_date_range(repo, days):
    LOG.info(f"repo={repo}, days={days}")
    raw_file_path = github_client.export_progress_by_date_range(repo, days)

    LOG.info(f"raw_file_path={raw_file_path}, days={days}")
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path)

    return report, report_file_path


def operate_with_subscription(repo, operation):
    LOG.info(f"repo={repo}, operation={operation}")
    if operation == "add":
        subscription_manager.add_subscription(repo)
    elif operation == "remove":
        subscription_manager.remove_subscription(repo)
    return "ok"


# 函数在点击按钮时更新下拉选项
def refresh_dropdown():
    global list_subscriptions
    LOG.info(f"before_list_subscriptions={list_subscriptions}")
    # 更新选项列表（此处可以根据需要动态生成新选项）
    list_subscriptions = subscription_manager.list_subscriptions()
    LOG.info(f"after_list_subscriptions={list_subscriptions}")
    return update_dropdown()


# 函数用来返回当前选项
def update_dropdown():
    return gr.Dropdown(choices=list_subscriptions)


with gr.Blocks() as demo:
    gr.Markdown("view the Github Sentinel or manage the Github Sentinel using this tab.")
    with gr.Tab("view the Github Sentinel"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    view_input1 = gr.Dropdown(choices=list_subscriptions, label="订阅列表",
                                              info="已订阅GitHub项目", scale=3)
                    update_button = gr.Button("update", scale=0, size="sm")
                view_input2 = gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期",
                                        info="生成项目过去一段时间进展，单位：天")
            with gr.Column():
                view_output1 = gr.Markdown()
                view_output2 = gr.File(label="下载报告")
        view_button = gr.Button("view")
    with gr.Tab("manage the Github Sentinel"):
        with gr.Row():
            with gr.Column():
                project_name = gr.Dropdown(choices=list_subscriptions, label="请输入项目",
                                           info="格式参考：ollama/ollama", allow_custom_value=True)
                operate = gr.Radio(["add", "remove"])
            image_output = gr.Textbox(label="Output")
        image_button = gr.Button("operate")

    view_button.click(export_progress_by_date_range, inputs=[view_input1, view_input2],
                      outputs=[view_output1, view_output2])
    update_button.click(refresh_dropdown, outputs=view_input1)
    image_button.click(operate_with_subscription, inputs=[project_name, operate], outputs=image_output)
    image_button.click(refresh_dropdown, outputs=project_name)

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))
