import os
from src.llm import chat_complete
from src.prompt import CodeCommentSuggestion, RelevanceDetectionPrompt

llm_config = {
    "base_url": "https://api-inference.modelscope.cn/v1/",
    "api_key": os.environ.get("MODELSCOPE_API_KEY"),
}
gen_args = {
    "model": "Qwen/Qwen2.5-72B-Instruct",
    "temperature": 0.8,  
}


code = '''
def has_self_loops(allowed_speaker_transitions: Dict) -> bool:
    """
    Returns True if there are self loops in the allowed_speaker_transitions_Dict.
    """
    return any([key in value for key, value in allowed_speaker_transitions.items()])
'''

comment = "Returns True if there are self loops in the allowed_speaker_transitions_Dict."



code = '''
def check_graph_validity(
    allowed_speaker_transitions_dict: Dict,
    agents: List[Agent],
):

'''

comment = '''
    allowed_speaker_transitions_dict: A dictionary of keys and list as values. The keys are the names of the agents, and the values are the names of the agents that the key agent can transition to.
    agents: A list of Agents

'''

user_text = f"""
代码和注释如下
<commnet>
{comment}
</comment>

<code>
```
{code}
```
</code>

请帮我分析注释是否合理，并给出分析和修改建议
"""

messages = [
    {"role": "system", "content": RelevanceDetectionPrompt},
    {"role": "user", "content": user_text}
]

response = chat_complete(messages, llm_config=llm_config, gen_args=gen_args)
print(response)
