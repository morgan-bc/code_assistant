import pandas as pd

def add_line_breaks(text):
    return text.replace('\n', '<br>')

def generate_pandas_report(data, save_file: str):
    if not isinstance(data, pd.DataFrame):
        df = pd.DataFrame(data)
    else:
        df = data
    if save_file.endswith(".xlsx"):
        df.to_excel(save_file, index=False)
    elif save_file.endswith(".md"):
        with open(save_file, "w") as fp:
            fp.write(df.to_markdown())
    elif save_file.endswith(".html"):
        formatters = {
            "code": add_line_breaks,
            "proposal": add_line_breaks,
            "suggestion": add_line_breaks,
            "content": add_line_breaks,
        }
        with open(save_file, "w") as fp:
            html = df.to_html(escape=False, formatters=formatters)
            fp.write(html)
    else:
        df.to_csv(save_file, index=False)
            