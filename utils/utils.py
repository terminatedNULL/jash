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

