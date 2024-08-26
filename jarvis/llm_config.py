from openai import OpenAI
import os
from langchain.chat_models import ChatOpenAI

llm = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_API_BASE'])

chat_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.8)
