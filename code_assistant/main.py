import os
import argparse
import pandas as pd
from .reports  import generate_pandas_report
from .app import CodeCommentAnalyzer

def parse_args():
    parser = argparse.ArgumentParser(description='The code to be analyzed')
    parser.add_argument('--input', "-i", type=str, help='input file or directory', required=True)
    parser.add_argument('--output', "-o", type=str, help='output file or directory', required=True)
    parser.add_argument('--num-workers', type=int, help="num workers to analyze code", default=1, required=False)
    parser.add_argument('--llm-provider', type=str, help="llm provider [azure_openai, modelscope]", default="modelscope", required=False)
    parser.add_argument('--lang', type=str, help='language. if lang is not specified, it will be inferred from the file extension')
    args = parser.parse_args()
    return args

def find_all_files(directory):
    code_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            code_files.append(os.path.join(root, file))
    return code_files


def get_llm_config(llm_provider: str):
    if llm_provider == "modelscope":
        llm_config = {
            "base_url": "https://api-inference.modelscope.cn/v1/",
            "api_key": os.environ.get("MODELSCOPE_API_KEY"),
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "temperature": 0.8,  
            "api_type": "openai"
        }
    elif llm_provider == "azure_openai":
        llm_config = {
            "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "api_version": "2023-05-15",
            "model": "gpt-35-turbo",
            "temperature": 0.8,  
            "api_type": "azure",
        }
    else:
        raise ValueError("Invalid llm provider")

    return llm_config


def main():
    args = parse_args()
    if os.path.isdir(args.input):
        code_files = find_all_files(args.input)
    else:
        code_files = [args.input]
    out_files = []
    if os.path.isdir(args.output):
        assert os.path.isdir(args.output), "output must be a directory"
    for code_file in code_files:
        if os.path.isdir(args.output):
            if os.path.isdir(args.input):
                out_files.append(code_file.replace(args.input, args.output))
            else:
                out_files.append(os.path.join(args.output, os.path.basename(code_file))+".html")
        else:
            if args.output.endswith(".html"):
                out_files.append(args.output)
            else:
                out_files.append(args.output)
        

    llm_config = get_llm_config(args.llm_provider)
    
    comment_analyzer = CodeCommentAnalyzer(
        min_length=5,
        threshold=0.9,
        num_workers=args.num_workers,
        llm_config=llm_config,
    )
    lang = args.lang.lower() if args.lang else None
    for code_file, out_file in zip(code_files, out_files):
        code_lang = comment_analyzer.detect_language(code_file)
        if code_lang is None:
            print(f"{code_file} is not a supported language")
            continue
        else:
            if lang is not None and lang != code_lang:
                print(f"{code_file} is not a {lang} file")
                continue
        result_list = comment_analyzer.run(code_file, lang=code_lang)
        # for res in result_list:
        #     res.pop("content")
        df = pd.DataFrame(result_list)
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        generate_pandas_report(df, out_file)
        csv_file = out_file.replace(".html", ".csv")
        generate_pandas_report(df, csv_file)
        
                
if __name__ == "__main__":
    main()
    
