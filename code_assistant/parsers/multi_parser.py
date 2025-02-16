from pygments import lex
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.token import Token


def parse_multilang_code(code: str, lang):
    structures = {
    'classes': [],
    'functions': [],
    'comments': [],
    }


    lexer = get_lexer_by_name(lang)
    tokens = lex(code, lexer)

    last_lineno = 1
    in_class = False
    in_function = False

    for token_type, value in tokens:
        if '\n' in value:
            last_lineno += value.count('\n')
            
        # print(token_type, value)
        
        # 识别类定义
        if token_type is Token.Name.Class and value == 'class':
            class_name = value.strip()
            structures['classes'].append({
                'name': class_name,
                'start_line': last_lineno,
                'end_line': last_lineno  
            })
            in_class = True
        
        # 识别函数定义
        elif token_type is Token.Name.Function:
            func_name = value.strip()
            structures['functions'].append({
                'name': func_name,
                'start_line': last_lineno,
                'end_line': last_lineno 
            })
            in_function = True

        elif token_type in (Token.Comment, Token.Comment.Single, Token.Comment.Multiline):
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



def find_lexer_by_extension(ext: str):
    ext = ext.lower()
    name = None
    for item in get_all_lexers():
        for x in item[2]:
            if ext in x:
                name = item[1][0]
                break
        if name is not None:
            break
    return name
                

        