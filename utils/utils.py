import re
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

import re

def format_documentation(doc: str) -> str:
    converted = '\t"""'
    params = []
    returns = ""
    tags_started = False

    lines = [l.strip() for l in doc.split("\n")]
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
