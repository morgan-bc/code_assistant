
def extract_xml(text: str, tag):
    p1 = text.find(f'<{tag}>')
    p2 = text.find(f'</{tag}>')
    if p1 == -1 or p2 == -1:
        return ''
    p1 = p1 + len(f'<{tag}>')
    return text[p1:p2].strip()
    