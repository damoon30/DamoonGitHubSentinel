# src/llm.py

import os
from logger import LOG
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_openai import OpenAI


class LLM:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])
        self.llm = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])
        LOG.add("daily_progress/llm_logs.log", rotation="1 MB", level="DEBUG")

    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"以下是项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；:\n\n{markdown_content}, 最后以中文的形式输出"

        if dry_run:
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        LOG.info(f"Starting report generation using GPT model. prompt={prompt}")

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            LOG.debug("GPT response: {}", response)
            return response.choices[0].message.content
        except Exception as e:
            LOG.error("An error occurred while generating the report: {}", e)
            raise

    def generate_daily_report_with_langchain(self, markdown_content):
        try:
            # 初始化总结模型
            summary_template = PromptTemplate(
                input_variables=["markdown_content"],
                template="""Initial Task: You need to create a brief report based on the provided project progress 
                information. Analyze the Progress: First, carefully read all the latest updates on the project and 
                understand the specific changes for each feature. Categorize and Organize: New Features: Group all 
                newly added modules or features into one category. Major Improvements: Identify and organize the 
                parts where significant optimizations or enhancements were made to existing features. Bug Fixes: 
                Identify and summarize the defects or issues that have been fixed. Merge Similar Items: For similar 
                or related features, try to combine them to ensure the report is concise and clear. Generate the 
                Report: Write the report following this structure: New Features: List all the newly added features. 
                Major Improvements: Summarize the significant enhancements or optimizations made to existing 
                features. Bug Fixes: Outline the issues or defects that have been resolved. Review the Report: Ensure 
                that the report covers all the important information and that the content is accurate. Here is the 
                content: {markdown_content}"""

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
