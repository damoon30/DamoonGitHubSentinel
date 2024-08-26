import gradio as gr
from jarvis.llm_config import chat_llm
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryBufferMemory


def predict(message, history):
    history_openai_format = []
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    history_openai_format.append({"role": "user", "content": message})

    print(history_openai_format)

    conversation = ConversationChain(llm=chat_llm, memory=ConversationSummaryBufferMemory(llm=chat_llm))

    response = conversation.invoke(message)
    print(f"response={response}")
    return response["response"]

demo = gr.ChatInterface(predict)

if __name__ == '__main__':
    demo.launch(share=True, server_name="0.0.0.0")
