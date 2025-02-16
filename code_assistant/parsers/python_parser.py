from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token


def parse_python_code(code: str):
    structures = {
    'classes': [],
    'functions': [],
    'comments': [],
    }


    lexer = PythonLexer()
    tokens = lex(code, lexer)

    last_lineno = 1
    in_class = False
    in_function = False

    for token_type, value in tokens:
        if '\n' in value:
            last_lineno += value.count('\n')
        
        # 识别类定义
        if token_type is Token.Keyword and value == 'class':
            class_name = next((v for t, v in tokens if t is Token.Name.Class), 'UnknownClass')
            structures['classes'].append({
                'name': class_name,
                'start_line': last_lineno,
                'end_line': last_lineno  
            })
            in_class = True
        
        # 识别函数定义
        elif token_type is Token.Keyword and value == 'def':
            func_name = next((v for t, v in tokens if t is Token.Name.Function), 'UnknownFunction')
            structures['functions'].append({
                'name': func_name,
                'start_line': last_lineno,
                'end_line': last_lineno 
            })
            in_function = True

        elif token_type in (Token.Comment, Token.Literal.String.Doc, Token.Comment.Single, Token.Comment.Multiline):
            last_comment = structures['comments'][-1] if structures['comments'] else None
            if last_comment and last_comment['end_line'] == last_lineno - 1:
                last_comment['content'] += '\n' + value.strip()
                last_comment['end_line'] = last_lineno
            else:
                structures['comments'].append({
                    'content': value.strip(),
                    'start_line': last_lineno - value.count("\n"),
                    'end_line': last_lineno
                })
            
        

    code_lines = code.splitlines()
    num_lines = len(code_lines)
    line_types = ["null"] * num_lines
    for name, structure in structures.items():
        for s in structure:
            for i in range(s['start_line'] - 1, s['end_line']):
                line_types[i] = name
    
    for i in range(num_lines):
        if line_types[i] in ["functions", "classes"]:
            for j in range(i+1, num_lines):
                if not code_lines[j].strip() or line_types[j] != "null":
                    break
            for k in range(i, j):
                line_types[k] = line_types[i]
    
    for i in range(num_lines):
        if code_lines[i].strip() and line_types[i] == "null":
            line_types[i] = "code_blocks"
        if not code_lines[i].strip() and line_types[i] == "null":
            if i > 1 and line_types[i-1] == "comments":
                line_types[i] = "blank"

        
    return structures, line_types

