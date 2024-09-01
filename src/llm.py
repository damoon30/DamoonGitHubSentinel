# src/llm.py

import os
from typing import Dict

import requests

from logger import LOG
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

ollama_model_name = "llama3.1"

class LLM:
    def __init__(self, config: Dict):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])
        self.llm = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])
        self.chat = ChatOpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])
        with open("prompt/prompt_github_sentinel.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()
        with open("prompt/prompt_hn.txt", "r", encoding="utf-8") as file:
            self.system_prompt_hn = file.read()
        # 加载ollama的模型参数
        model_name_setting = config.get('use_model_name')
        self.model_name = model_name_setting
        if model_name_setting == ollama_model_name:
            model_map = config.get('model_map')
            print(f"model_map = {model_map}")
            self.open_base_url = model_map.get(model_name_setting).get('open_base_url')
            print(f"model={self.model_name}, open_base_url={self.open_base_url}")

        LOG.add("logs/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content):
        if self.model_name == ollama_model_name:
            return self._generate_daily_report_ollama(self.system_prompt_hn, markdown_content)
        else:

            return self._generate_daily_report_openai(self.system_prompt, markdown_content)

    def _generate_daily_report_openai(self, prompt, markdown_content):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": markdown_content}
                ]
            )
            LOG.debug("GPT response: {}", response)
            return response.choices[0].message.content
        except Exception as e:
            LOG.error("An error occurred while generating the report: {}", e)
            raise

    def _generate_daily_report_ollama(self, prompt, markdown_content):
        LOG.info("使用 Ollama LLaMA 模型开始生成报告。")

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": markdown_content},
        ]

        try:
            payload = {
                "model": self.model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "stream": False
            }
            print(f"param = {payload}")
            response = requests.post(self.open_base_url, json=payload)  # 发送POST请求到Ollama API
            response_data = response.json()

            # 调试输出查看完整的响应结构
            LOG.debug("Ollama response: {}", response_data)

            # 直接从响应数据中获取 content
            message_content = response_data.get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Invalid response structure from Ollama API")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def generate_daily_report_with_langchain(self, markdown_content):
        try:
            # 初始化总结模型
            summary_template = PromptTemplate(
                input_variables=["markdown_content"],
                template=f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}, 最后以中文的形式输出"
            )

            summary_chain = LLMChain(llm=self.llm, prompt=summary_template, output_key="summary", verbose=True)
            # 翻译成 中 文
            translation_template = PromptTemplate(
                input_variables=["summary"],
                template="Translate the following summary into Chinese: {summary}"
            )

            translation_chain = LLMChain(llm=self.llm, prompt=translation_template, output_key="chinese_summary",
                                         verbose=True)
            # 创建顺序链
            chain = SequentialChain(
                chains=[summary_chain, translation_chain],
                input_variables=["markdown_content"],
                output_variables=["chinese_summary"],
                verbose=True
            )
            # 执行链并获取结果
            result = chain.invoke({"markdown_content": markdown_content})
            LOG.info(result)
            return result["chinese_summary"]
        except Exception as e:
            LOG.error("langchain error", e)
            raise

    def generate_report_chat_langchain(self, markdown_content):
        try:
            # 初始化总结模型
            # 创建 ChatPromptTemplate
            template = ChatPromptTemplate([
                ("system",
                 f"You are a helpful AI bot. Your name is Carl. follow the rules to answer {self.system_prompt}"),
                ("human", "{user_input}"),
            ])

            chain = template | self.chat
            response = chain.invoke(markdown_content)
            LOG.info(response)
            return response.content
        except Exception as e:
            LOG.error("langchain error", e)
            raise

    def generate_hn_report_client(self, markdown_content):
        if self.model_name == ollama_model_name:
            return self._generate_daily_report_ollama(self.system_prompt_hn, markdown_content)
        else:
            return self._generate_daily_report_openai(self.system_prompt_hn, markdown_content)
