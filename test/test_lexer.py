from pprint import pprint
from pygments.lexers import get_all_lexers, get_lexer_by_name, get_lexer_for_filename, find_lexer_class_for_filename


# for lexer in get_all_lexers():
#     print(lexer, type(lexer[0]), type(lexer[1]))

code_file = r"D:\Projects\aigc\test\http_conn.cpp"

lexer = get_lexer_for_filename(code_file)
print(lexer.__class__)

print(find_lexer_class_for_filename(code_file))

name = "ansys"
print(get_lexer_by_name(name))

# lexer = get_lexer_by_name("C++")
# with open(code_file, "r", encoding="utf-8") as f:
#     code = f.read().strip()

# structures, line_types = parse_cpp_code(code)
# pprint(structures)