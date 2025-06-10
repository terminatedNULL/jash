import os
from collections import defaultdict
from typing import Any, List, Tuple, Dict, Iterator

Tree = Dict[str, Any]


def nested_defaultdict() -> defaultdict[str, Any]:
    """
    Creates a nested defaultdict structure that provides default nested defaultdicts indefinitely.

    Returns:
        A nested defaultdict providing other nested defaultdicts as default values.
    """
    return defaultdict(nested_defaultdict)


def insert_into_tree(tree: Tree, path_parts: List[str], filename: str) -> None:
    """
    Inserts a filename into a tree at the specified path.

    Args:
        tree: The tree to insert into.
        path_parts: The path, as a list, at which to insert the filename.
        filename: The filename to insert.
    """
    for part in path_parts:
        if part not in tree:
            tree[part] = {}
        tree = tree[part]
    tree.setdefault("_files", []).append(filename)


def remove_from_tree(tree: Tree, path_parts: List[str]) -> bool:
    """
    Removes the last element in path_parts from the tree.

    If the last element is a filename, removes it from the "files" list in the parent directory.
    If the last element is a directory, removes that directory subtree.

    Args:
        tree: The tree to remove from.
        path_parts: The path to the element to remove.

    Returns:
        True if removal was successful, False if path not found.
    """
    if not path_parts:
        return False  # Nothing to remove

    # Traverse down to the parent of the target
    node = tree
    for part in path_parts[:-1]:
        if part not in node or not isinstance(node[part], dict):
            return False
        node = node[part]

    last_part = path_parts[-1]

    # Try removing file
    files = node.get("_files", [])
    if last_part in files:
        files.remove(last_part)
        return True

    # Try removing directory
    if last_part in node:
        del node[last_part]
        return True

    return False


def ensure_files_keys(t: Tree) -> None:
    """
    Ensures each node in a tree has a "files" key.

    Args:
        t: The tree to walk through.
    """
    for v in t.values():
        if isinstance(v, dict):
            v.setdefault("_files", [])
            ensure_files_keys(v)


def tree_len(tree: Tree) -> int:
    """
    Recursively counts the number of files in the tree.

    Args:
        tree: The nested file tree.

    Returns:
        The total number of files in the tree.
    """
    total = len(tree.get("_files", []))
    for key, value in tree.items():
        if isinstance(value, dict):
            total += tree_len(value)
    return total


def path_exists(tree: Tree, path_parts: List[str]) -> bool:
    """
    Checks if a path exists in a tree.

    Args:
        tree: The tree to check.
        path_parts: The path to check.

    Returns:
        Whether the path exists in the tree.
    """
    node = tree
    for part in path_parts:
        if part == "_files":
            continue
        if part not in node or not isinstance(node[part], dict):
            return False
        node = node[part]
    return True


def keep_only_included(tree: Tree, includes: List[List[str]]) -> None:
    """
    Modifies `tree` in-place, keeping only paths that start with one of the include prefixes.
    Removes all other entries.
    """

    def path_starts_with_any(path: List[str], prefixes: List[List[str]]) -> bool:
        return any(path[:len(prefix)] == prefix for prefix in prefixes)

    def filter_tree(node: Tree, current_path: List[str]) -> bool:
        # Filter files
        if "_files" in node:
            node["_files"] = [f for f in node["_files"] if path_starts_with_any(current_path + [f], includes)]

        # Filter subdirectories recursively
        to_delete = []
        for key, subnode in node.items():
            if key == "_files":
                continue
            if not filter_tree(subnode, current_path + [key]):
                to_delete.append(key)

        for key in to_delete:
            del node[key]

        # Keep this node only if it has any files or subdirectories left
        return bool(node.get("_files")) or any(k != "_files" for k in node.keys())

    filter_tree(tree, [])


def build_java_file_tree(root_dir: str) -> Tuple[int, Tree]:
    """
    Recursively builds a file tree of all java files in a directory.

    The tree is structured as a nested dictionary where each node represents a directory.
    Each node also has a "files" key that contains a list of files in that directory.

    Args:
        root_dir: The root directory to start the walk from.

    Returns:
        The number of java files found and the file tree.
    """
    tree: Tree = {}
    file_count: int = 0

    for root, dirs, files in os.walk(root_dir):
        java_files = [f[:-5] for f in files if f.endswith(".java")]
        if java_files:
            rel_path = os.path.relpath(root, root_dir)
            path_parts = [] if rel_path == "." else rel_path.split(os.sep)
            for java_file in java_files:
                insert_into_tree(tree, path_parts, java_file)
            file_count += len(java_files)

    return file_count, tree


def iter_tree_files(tree: Tree, path=None) -> Iterator[Tuple[List[str], str]]:
    """
    Iterates over all files in the tree, yielding each file and its path as a list of strings.

    Args:
        tree: The nested tree to iterate.
        path: The current path (used internally during recursion).

    Yields:
        Tuples of (path, filename), where `path` is a list of strings representing directories.
    """
    if path is None:
        path = []

    for filename in tree.get("_files", []):
        yield path, filename

    for key, subtree in tree.items():
        if key == "_files":
            continue
        if isinstance(subtree, dict):
            yield from iter_tree_files(subtree, path + [key])
