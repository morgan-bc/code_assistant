import os
import numpy as np
from tqdm import tqdm
from pprint import pprint
from suggestions.rules import LengthRule, DuplicateRule, LLMRule
from parsers.python_parser import parse_python_code
from reports import generate_pandas_report


llm_config = {
    "base_url": "https://api-inference.modelscope.cn/v1/",
    "api_key": os.environ.get("MODELSCOPE_API_KEY"),
}

gen_args = {
    "model": "Qwen/Qwen2.5-72B-Instruct",
    "temperature": 0.8,  
}



# code_file = r"D:\Projects\aigc\code_assistant\parsers\python_parser.py"
code_file = r"D:\Github\autogen-0.2.38\autogen\code_utils.py"

with open(code_file, "r", encoding="utf-8") as fp:
    all_codes = fp.read().strip()

structures, line_types = parse_python_code(all_codes)
code_lines = all_codes.splitlines()

length_rule = LengthRule(min_length=5)
duplicate_rule = DuplicateRule(threshold=0.8)
llm_rule = LLMRule(llm_config, gen_args)

result_list = []
comment_list = structures["comments"]
for i, comment in enumerate(comment_list):
    res = length_rule.check(comment["content"])
    comment["type"] = []
    if not res:
        comment["type"].append("注释太短")

comment_texts = [s["content"] for s in comment_list]
sim_idxs = duplicate_rule.check(comment_texts)
for idxs in sim_idxs:
    for i in idxs:
        comment_list[i]["type"].append("存在多处相似的注释")


# for comment in comment_list:
for comment in tqdm(comment_list, ncols=100):
    result = llm_rule.check(code_lines, comment, line_types)
    flag = result.get("result", "No").lower()
    if "yes" in flag:
        if result.get("type", ""):
            comment["type"].append(result.get("type"))
            comment["suggestion"] = result.get("suggestion")
            comment["proposal"] = result.get("proposal")
            
result_list = []
for comment in comment_list:
    if comment["type"]:
        comment["type"] = ", ".join(comment["type"])
        result_list.append(comment)

save_file = "test_reports.csv"
generate_pandas_report(result_list, save_file)
    


    





