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
