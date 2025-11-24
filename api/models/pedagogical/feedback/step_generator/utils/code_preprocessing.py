import tokenize
import ast
from io import BytesIO
from collections import defaultdict
import re


def remove_comments(code):
    lines = code.split('\n')
    lines_to_remove = set()

    for i, line in enumerate(lines):
        if re.match(r'^\s*#', line): 
            lines_to_remove.add(i)
        elif '#' in line:
            lines[i] = line.split('#', 1)[0].rstrip()
    cleaned_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    return '\n'.join(cleaned_lines)

def remove_docstrings(code: str) -> str:
    docstring_pattern = re.compile(r'(^|\n)[ \t]*(("""(.*?)"""|\'\'\'(.*?)\'\'\'))', re.DOTALL)
    cleaned_code = re.sub(docstring_pattern, '', code)
    
    return cleaned_code


def remove_after_function_body(code):
    code_split = code.split("\n")
    code_split = [code if (code.startswith("    ") or code.startswith("  ") or code.startswith(" ") or code.startswith("def")) else "" for code in code_split]
    code = "\n".join(code_split)
    return(code)

def add_prefix(code, task_unique_name, task_prefix_dict):
    task_prefix = task_prefix_dict[task_unique_name]
    code = f"{task_prefix}{code}"
    return code


def add_pass_to_empty_blocks(code: str) -> str:
    lines = code.splitlines()
    output_lines = []  # To store the modified lines
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Check if it's a function, class, or control block (if, for, while)
        if stripped_line.endswith(':') and stripped_line and not line.strip().startswith('#'):
            indent_size = len(line) - len(stripped_line)
            
            # Check if the next line is empty or not indented correctly
            if i + 1 < len(lines) and lines[i + 1].strip() == '':
                output_lines.append(line)
                output_lines.append(' ' * (indent_size) + '    pass')
                continue
            elif i + 1 < len(lines):
                next_line = lines[i + 1]
                next_line_indent = len(next_line) - len(next_line.lstrip())
                next_line_stripped = next_line.strip()
                if next_line_indent <= indent_size and next_line_stripped != '':
                    output_lines.append(line)
                    output_lines.append(' ' * indent_size + '    pass')
                else:
                    output_lines.append(line)
                    continue
            elif i + 1 == len(lines):
                output_lines.append(line)
                output_lines.append(' ' * (indent_size) + '    pass')
            else:
                output_lines.append(line)
                continue
        else:
            output_lines.append(line)
    return '\n'.join(output_lines)


def detangle_keywords_from_blocks(code_str):
    """Desolves one-line blocks into keywords and proper blocks. Assumes that no comments are present."""
    colon_positions = []
    try:
        code_bytes = code_str.encode('utf-8')
        readline = BytesIO(code_bytes).readline
        for tok in tokenize.tokenize(readline):
            if tok.type == tokenize.OP and tok.string == ':':
                line_num = tok.start[0] - 1  # Convert to 0-based
                col_num = tok.start[1]
                colon_positions.append((line_num, col_num))
    except tokenize.TokenError as e:
        raise e

    colon_map = defaultdict(list)
    for line, col in colon_positions:
        colon_map[line].append(col)

    lines = code_str.splitlines()
    processed_lines = []
    for line_num, line in enumerate(lines):
        if line_num in colon_map:
            cols = colon_map[line_num]
            last_col = max(cols)
            before_colon = line[:last_col + 1]
            after_colon = line[last_col + 1:]
            if after_colon.strip() != "":
                leading_whitespace = re.match(r'^(\s*)', line).group(1)
                stripped_after = after_colon.lstrip()
                new_line = f"{before_colon}\n{leading_whitespace}    {stripped_after}"
                processed_lines.append(new_line)
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def convert_to_single_line_strings(code):
    bio = BytesIO(code.encode('utf-8'))
    tokens = list(tokenize.tokenize(bio.readline))
    new_tokens = []
    for tok in tokens:
        if tok.type == tokenize.STRING:
            s = tok.string
            if len(s) >= 6 and s.startswith("'''") or s.startswith('"""'):
                try:
                    content = s[3:-3]
                    content = content.replace('\n', '\\n')
                    if '"' not in content:
                        new_s = '"' + content.replace('"', '\\"') + '"'
                    elif "'" not in content:
                        new_s = "'" + content.replace("'", "\\'") + "'"
                    else:
                        new_s = '"' + content.replace('"', '\\"') + '"'
                    new_token = tokenize.TokenInfo(
                        type=tok.type,
                        string=new_s,
                        start=tok.start,
                        end=tok.end,
                        line=tok.line
                    )
                    new_tokens.append(new_token)
                except Exception:
                    new_tokens.append(tok)
            else:
                new_tokens.append(tok)
        else:
            new_tokens.append(tok)
    result_bytes = tokenize.untokenize(new_tokens)
    return result_bytes.decode('utf-8')

def preprocess_code(code, task_unique_name, task_prefix_dict, print_tasks):
    code = remove_comments(code)
    code = detangle_keywords_from_blocks(code)
    function_task = not (task_unique_name in print_tasks)
    if function_task:
        code = remove_after_function_body(code)
    if not code.startswith(f"def"):
        code = add_prefix(code, task_unique_name, task_prefix_dict)
    try:
        ast.parse(code)
    except Exception as e:
        if e.__class__.__name__ == "IndentationError":
            code_candidate = add_pass_to_empty_blocks(code)
            try:
                ast.parse(code_candidate)
                code = code_candidate
            except Exception as e:
                pass
    code = code.strip()
    return code

def remove_orphan_decorators(code: str) -> str:
    if is_valid(code):
        return code
    lines = code.splitlines(keepends=True)
    n = len(lines)
    for i in range(n):
        line = lines[i].lstrip()
        if line.startswith('@'):
            new_lines = lines[:i] + lines[i+1:]
            new_code = ''.join(new_lines)
            if is_valid(new_code):
                return new_code
    return code

def is_valid(code):
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def desolve_invalid_try(code):
    lines = code.splitlines(keepends=False)
    for i in range(len(lines)):
        line = lines[i]
        if line.strip().startswith('try:'):
            modified_lines = desolve_try(lines, i)
            modified_code = '\n'.join(modified_lines)
            try:
                ast.parse(modified_code)
                return modified_code
            except SyntaxError:
                pass
    return code

def desolve_try(lines, try_lineno):
    try_line = lines[try_lineno]
    try_indent = len(try_line[:len(try_line) - len(try_line.lstrip())])
    pre = lines[:try_lineno]
    post = lines[try_lineno + 1:]
    body = []
    remaining = []
    in_body = True
    dedent_amount = None
    
    for line in post:
        if not in_body:
            remaining.append(line)
            continue
        
        line_indent = len(line[:len(line) - len(line.lstrip())])
        if line_indent > try_indent:
            stripped = line.strip()
            if dedent_amount is None and stripped:
                dedent_amount = line_indent - try_indent
            if dedent_amount is not None:
                if len(line) >= dedent_amount:
                    dedented_line = line[dedent_amount:]
                else:
                    dedented_line = line.lstrip()
                body.append(dedented_line)
            else:
                body.append(line)
        else:
            in_body = False
            remaining.append(line)
    
    return pre + body + remaining
