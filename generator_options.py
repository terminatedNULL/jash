import_req: list[tuple[str, str]] = []
"""
Stores the list of required imports for the generated python code.

Stored as tuples of (obj_name, module).
"""

class GeneratorOptions:
    typed = True
    """
    Whether to provide type hints in the python code produced.
    """
