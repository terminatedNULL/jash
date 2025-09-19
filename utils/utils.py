import re
import uuid
from typing import Any


def str_default(var: Any, val: Any):
    """
    Handles default argument assignment, returning var is it != None or "None",
    and val otherwise.

    Args:
        var: The variable to check for None.
        val: The default value.

    Returns:
        Any: The variable's value if != None, val otherwise.
    """
    return var if var not in [None, "None"] else val


def remove_duplicates(l: list[Any]) -> list[Any]:
    """
    Removes all duplicate entries from a list using set comprehension.

    Args:
        l: The list to remove duplicates from.

    Returns:
        list[Any]: The list with duplicates removed.
    """
    seen = set()
    return [x for x in l if not (x in seen or seen.add(x))]


def condense_imports(import_list: list[tuple[str, str]]) -> dict[str, list[str]]:
    """

    Args:
        import_list:

    Returns:

    """
    import_map = {}
    for name, module in import_list:
        import_map.setdefault(module, []).append(name)
    return {module: remove_duplicates(names) for module, names in import_map.items()}

"""
TODO:
 - Code formatting for @code
 - @exception handling for typing
 - Groups @param into 'Args' block
 - Place @return under 'Returns' block at end
"""


import re

def format_documentation(doc: str) -> str:
    converted = '\t"""'
    params = []
    returns = ""
    tags_started = False
    lines = [l.strip() for l in doc.split("\n")]

    # Combine multi-line links into one line
    index = 0
    append_str = ""
    while index < len(lines):
        line = lines[index]

        if append_str == "" and "{@" in line and "}" not in line:
            keep, app = line.split("{@", maxsplit=1)
            append_str = "{@" + app
            lines[index] = keep.strip()
            index += 1
        elif append_str != "":
            append_str += " " + line.strip()
            if "}" in line:
                before, after = append_str.split("}", maxsplit=1)
                condensed = before + "}"
                lines[index] = after.strip()
                lines.insert(index, condensed.strip())
                append_str = ""
                index += 1
            else:
                lines.pop(index)
        else:
            index += 1

    for line in lines:
        temp = line
        temp = temp.removeprefix("/**").removesuffix("*/").lstrip("*").strip()
        if not temp:
            continue

        # Collect params
        match = re.match(r"@param\s+(.*)", temp)
        if match:
            params.append(match.group(1).strip())
            continue

        # Collect return
        if returns == "":
            match = re.match(r"@return\s+(.*)", temp)
            if match:
                returns = match.group(1).strip()
                continue

        # Collect other tags
        match = re.match(r"@(\w+)\s+(.*)", temp)
        if match:
            if not tags_started:
                converted += "\n"
                tags_started = True

            tag, content = match.groups()
            temp = f"{tag.capitalize()}: {content.strip()}"
            converted += f"\n\t{temp}\n"
            continue

        # Format inline code snippets
        temp = re.sub(r"\{@code\s+([^}]+)}", r"``\1``", temp)

        # Format inline links
        temp = re.sub(r"\{@link\s+([^}]+)}", r"`\1`", temp)

        converted += f"\n\t{temp}"

    if params:
        converted += "\n\tArgs:"
        for param in params:
            parts = param.split(" ", 1)
            if len(parts) == 2:
                name, desc = parts
            else:
                name, desc = parts[0], ""
            converted += f"\n\t\t{name}: {desc}\n"

    if returns:
        converted += f"\n\tReturns:\n\t\t{returns}\n"

    return converted + '\n\t"""'

METHOD_SIGNATURE_REGEX = re.compile(
    r"(?:public|protected|private|static|final|native|synchronized|abstract|default|strictfp|\s)*(?:<[^>]+>\s+)?(?:[A-Za-z0-9_<>\[\].]+)?\s+\b(?!if\b|for\b|while\b|switch\b|catch\b)[A-Za-z0-9_]+\s*\([^)]*\)(?:\s*throws\s+[A-Za-z0-9_.,\s]+)?\s*(?=\{)",
    re.DOTALL
)
""" A regex matching a java function signature. """

STR_INITIALIZATION_REGEX = re.compile(
    r'(?:String|var)\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:(?:"(?:\\.|[^"\\])*")|\s*\+\s*[A-Za-z_][A-Za-z0-9_]*)*\s*;',
    re.DOTALL
)
""" A regex matching a java string initialization line. """

def generate_unique_token() -> str:
    """
    Generates a unique token for use in text parsing.

    Returns:
        str: The unique token
    """
    return f"___{uuid.uuid4().hex.upper()}___"

def strip_method_bodies(code: str) -> str:
    """
    Clears the code from all function bodies in a java code snippet.

    Args:
        code (str): The java snippet to process.

    Returns:
        str: The processed java code snippet.
    """
    result = []
    token_map = {}
    last_index = 0
    i = 0

    # Tokenize string initializations
    for match in STR_INITIALIZATION_REGEX.finditer(code):
        start, end = match.start(), match.end()
        token = generate_unique_token()
        token_map[token] = code[start:end]
        result.append(code[last_index:start])
        result.append(token)
        last_index = end

    result.append(code[last_index:])
    result = ''.join(result)

    # Clear string literals
    result = re.sub(r'(?<!\')\"(?:\\.|[^\"\\])*\"', '""', result)

    # Clear char literals
    result = re.sub(r"'(?:\\.|[^'\\])'", "''", result)

    # Clear function bodies
    output = ""
    while i < len(result):
        m = METHOD_SIGNATURE_REGEX.search(result, i)
        if not m:
            output += result[i:]
            break

        output += result[i:m.end()]
        i = m.end()

        if i < len(result) and result[i] == "{":
            output += "{"
            brace_count = 1
            i += 1
            char = result[i]
            while i < len(result) and brace_count > 0:
                if result[i] == "{":
                    brace_count += 1
                elif result[i] == "}":
                    brace_count -= 1
                i += 1
                char = result[i]
            output += "}"

    # Replace string initializations
    for token in token_map:
        output = output.replace(token, token_map[token])

    return output

def fix_invalid_escapes(code: str) -> str:
    r"""
    Replaces ``\xNN`` Unicode characters with ``\u00NN`` characters.

    Args:
        code (str): The code snippet to fix.

    Returns:
        str: The fixed code snippet.
    """
    return ''.join(
        f'\\u{ord(c):04X}' if ord(c) >= 128 else c
        for c in code
    )

def strip_inline_comments(file_contents: str) -> str:
    """
    Replaces inline // comments inside block comments with tokens,
    removes standalone // lines, then restores the inline ones.
    """
    token_map = {}

    def replacer(match):
        prefix, inline_comment = match.groups()
        token = f"__INLINE_COMMENT_{uuid.uuid4().hex}__"
        token_map[token] = inline_comment
        return prefix + token

    inline_pattern = re.compile(r'(^\s*\*.*?)(//.*)', re.MULTILINE)
    file_contents = inline_pattern.sub(replacer, file_contents)

    file_contents = re.sub(r'\s*//.*', '', file_contents, flags=re.MULTILINE)

    for token, inline_comment in token_map.items():
        file_contents = file_contents.replace(token, inline_comment)

    return file_contents

def strip_all_comments(java_code: str) -> str:
    """
    Removes all Java comments (// and /* ... */), but preserves
    strings and char literals.

    Args:
        java_code (str): Java source code as a string.

    Returns:
        str: Java code with comments removed.
    """
    pattern = re.compile(
        r'("(\\"|[^"])*")|'      # string literals
        r'(\'(\\\'|[^\'])*\')|'         # char literals
        r'(/\*[\s\S]*?\*/)|'            # multi-line comments
        r'(//.*?$)',                    # single-line comments
        re.MULTILINE
    )

    def replacer(match):
        if match.group(1) or match.group(3):
            return match.group(0)
        return ''

    return pattern.sub(replacer, java_code)
