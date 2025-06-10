from typing import Any


def default(var: Any, val: Any, check_str: bool = False):
    """
    Handles default argument assignment, returning var is it != None,
    and val otherwise.

    Args:
        var: The variable to check for None.
        val: The default value.
        check_str: Whether to check for the string value "None".

    Returns:
        Any: The variable's value if != None, val otherwise.
    """
    if check_str:
        return var if var not in [None, "None"] else val
    return var if var is not None else val
