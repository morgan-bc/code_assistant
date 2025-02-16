import os
from copy import deepcopy
from openai import OpenAI
from openai import AzureOpenAI


def chat_complete(messages, llm_config={}, gen_args={}):
    client = OpenAI(**llm_config)
    response = client.chat.completions.create(
        messages=messages,
        **gen_args
    )
    return response.choices[0].message.content

    
def azure_chat_complete(messages, llm_config={}, gen_args={}):
    client = AzureOpenAI(**llm_config)
    response = client.chat.completions.create(
        messages=messages,
        **gen_args
    )
    return response.choices[0].message.content