import textwrap
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from typing import List, Dict

from .llm import chat_complete, azure_chat_complete
from .uitls import extract_xml
from .prompt import RelevanceDetectionPrompt


class LengthRule:
    def __init__(self, min_length=5):
        self.min_length = min_length

    def check(self, text: str):
        chinese_characters = re.findall(r'[\u4e00-\u9fff]', text)
        if len(chinese_characters) > 0:
            return len(text) >= self.min_length
        else:
            words = text.split(" ")
            chars = set(text)
            return len(words) >= self.min_length or len(chars) >= self.min_length*2
    
    
class DuplicateRule:
    
    def __init__(self, threshold=0.8):
        self.threshold = threshold
       
    def check(self, comments):
        tfidf = TfidfVectorizer().fit_transform(comments)
        similarity_matrix: csr_matrix  = tfidf * tfidf.T
        similar_idxs = []
        walked = set()
        for i, row in enumerate(similarity_matrix):
            if i in walked: 
                continue
            idxs = (row > self.threshold).nonzero()[1]
            if len(idxs) > 1:
                similar_idxs.append(idxs)
                walked.update(idxs)
        return similar_idxs


class LLMRule:
    
    def __init__(self, llm_config={}, gen_args={}, api_type="openai"):
        self.llm_config = llm_config
        self.gen_args = gen_args
        self.api_type = api_type
        
    def check(self, comment, code_lines, line_types):
        comment_text = comment["content"]
        start_line = comment["start_line"] - 1
        end_line = comment["end_line"] - 1
        num_line = len(code_lines)

        for i in range(start_line - 1, 1, -1):
            if line_types[i] in ["null", "code_blocks"]:
                start_line = i + 1
                break
            
        for i in range(end_line + 1, min(num_line, end_line+20)):
            if line_types[i] in ["null", "comments"]:
                end_line = i - 1
                break
        end_line = min(end_line + 3, num_line)

        code = "\n".join(code_lines[start_line:end_line+1])
        user_text = f"代码和注释如下\n<commnet>\n{comment_text}\n</comment>\n<code>\n```\n{code}\n```\n</code>\n"
        user_text += "请帮我分析注释是否合理，并给出分析和修改建议"
        messages = [
            {"role": "system", "content": RelevanceDetectionPrompt},
            {"role": "user", "content": user_text}
        ]
        
        if self.api_type == "azure":
            response = azure_chat_complete(messages, self.llm_config, self.gen_args)
        else:
            response = chat_complete(messages, self.llm_config, self.gen_args)
        keys = ["analysis", "result", "type", "suggestion", "proposal"]
        result = {}
        for key in keys: 
            result[key] = extract_xml(response, key)
        result["code"] = code
        # result["proposal"] = result["proposal"].replace("```python", "").replace("```", "")
        return result
    
        