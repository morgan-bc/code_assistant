import os
import warnings
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
from copy import deepcopy
from tqdm import tqdm
from code_assistant.parsers import parse_python_code, parse_multilang_code, find_lexer_by_extension
from code_assistant.suggestions import LLMRule, LengthRule, DuplicateRule


class CodeCommentAnalyzer:
    
    supported_langs = {
        ".py": "python",
    }


    def __init__(
        self, 
        min_length: int = 5,
        threshold: float = 0.8,
        num_workers: int = 1,
        llm_config: Dict = {},
        ):
        self.llm_config = llm_config
        self.length_rule = LengthRule(min_length=min_length) 
        self.duplicate_rule = DuplicateRule(threshold=threshold)
        llm_args, gen_args, api_type = self.parse_llm_config(llm_config)
        self.llm_rule = LLMRule(llm_config=llm_args, gen_args=gen_args, api_type=api_type)
        self.num_workers = num_workers
    
    def parse_llm_config(self, llm_config: Dict):
        gen_args = deepcopy(llm_config)
        llm_config = {}
        api_type = gen_args.pop("api_type", "openai")
        if api_type == "azure":
            basic_keys = ["api_key", "azure_endpoint",  "api_version"]
        else:
            basic_keys = ["api_key", "base_url"]
        
        for key in basic_keys:
            llm_config[key] = gen_args.pop(key)
        return llm_config, gen_args, api_type
        
    def detect_language(self, code_file: str):
        ext = os.path.splitext(code_file)[-1].lower()
        if ext == ".py" :
            return "python"
        else:
            lang = find_lexer_by_extension(ext)
        return lang
        
    
    def parse_code(self, code_file: str, lang):
        with open(code_file, "r", encoding="utf-8") as f:
            code = f.read().rstrip()
        if lang == "python":
            structures, line_types = parse_python_code(code)
        else:
            structures, line_types = parse_multilang_code(code, lang)
            
        code_lines = code.split("\n")
        return structures, line_types, code_lines

    def run(self, code_file: str, lang: str = None):
        structures, line_types, code_lines = self.parse_code(code_file, lang)
        comment_list = structures["comments"]
        
        for i, comment in enumerate(comment_list):
            res = self.length_rule.check(comment["content"])
            comment["type"] = []
            if not res:
                comment["type"].append("注释太短")

        comment_texts = [s["content"] for s in comment_list]
        sim_idxs = self.duplicate_rule.check(comment_texts)
        for idxs in sim_idxs:
            for i in idxs:
                comment_list[i]["type"].append("存在多处相似的注释")

        exe_func = functools.partial(self.llm_rule.check, code_lines=code_lines, line_types=line_types)
        batch_size = self.num_workers
        num_comments = len(comment_list)
        comment_results = []
        
        # debugs = ["# voting", "# check if the answer is correct"]
        # temp_list = []
        # for c in comment_list:
        #     for d in debugs:
        #         if d in c["content"]:
        #             temp_list.append(c)
        # comment_list = temp_list

        if batch_size <= 1:
            for comment in tqdm(comment_list, ncols=100):
                result = self.llm_rule.check(comment, code_lines, line_types)
                comment_results.append(result)
        else:
            for i in tqdm(range(0, num_comments, batch_size), ncols=100):
                batch = comment_list[i:i+batch_size]
                with ThreadPoolExecutor(max_workers=batch_size) as executor:
                    futures = [executor.submit(exe_func, comment) for comment in batch]
                    for f in futures:
                        comment_results.append(f.result())
            
                    
        for comment, result in zip(comment_list, comment_results):
            comment["code"] = result.get("code", "")
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

        return result_list