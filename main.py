import argparse
import os
import tempfile
import shutil
from typing import List

import fio
import tree
from fio import check_file_access

"""
Jython Advanced Syntax Highlighter (JASH)

A tool used to generate typed python code stubs to
enable accurate syntax highlighting and autocompletion.
"""


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Jython Advanced Syntax Highlighter (JASH)")
    arg_parser.add_argument("-i", "--input", nargs="+", help="The jar file to generate stubs for.")

    inc_ex_group = arg_parser.add_mutually_exclusive_group()
    inc_ex_group.add_argument("-ex", "--exclude", help="The exclude jar paths file to use during generation.")
    inc_ex_group.add_argument("-exl", "--exclude-list", nargs="+", help="List of internal jar directories to exclude during generation")
    inc_ex_group.add_argument("-inc", "--include", help="The include jar paths file to use during generation.")
    inc_ex_group.add_argument("-incl", "--include-list", nargs="+", help="List of internal jar directories to include during generation")

    args = arg_parser.parse_args()

    # Create temp directory
    temp_dir = os.path.join(tempfile.gettempdir(), "jash")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    print(f"Using temp directory: {temp_dir}\n")

    # Check for valid java installation
    code, output = fio.run_command(["java", "-version"])
    if code != 0 or "version" not in output.lower():
        raise Exception("Java is not installed or not properly configured.")

    # Decompile and generate jar stubs
    for jar in args.input:
        fio.check_file_access(jar)
        if os.path.splitext(jar)[1].lower() != ".jar":
            raise Exception(f"The file '{jar}' is not a jar file.")

        print(f"Decompiling {jar}...")
        code, _ = fio.run_command(["java", "-jar", "./third-party/jd-cli.jar", jar, "-od", temp_dir])
        if code != 0:
            raise Exception(f"Failed to decompile {jar}.")

        file_count, file_map = tree.build_java_file_tree(temp_dir)
        print(f"Found {file_count} compatible files in {jar}.\n")

        # Mutually include or exclude files from the tree.py
        if args.include:
            check_file_access(args.include)

            include_paths = []
            print(f"Parsing include paths from {args.include}...")
            with open(args.include, "r") as f:
                for line in f:
                    line = line.strip()
                    include_paths.append(line.split("."))

            for path in include_paths:
                if not tree.path_exists(file_map, path):
                    raise Exception(f"The include path '{'.'.join(path)}' does not exist in {jar}.")

            tree.keep_only_included(file_map, include_paths)
            include_num = len(include_paths)
            print(f"Applied {include_num} include path{'s' if include_num != 1 else ''} from {args.include}.")

        elif args.include_list:
            if not isinstance(args.exclude_list, list):
                args.exclude_list = [args.exclude_list]
            include_paths = [p.split(".") for p in args.include_list]

            for path in include_paths:
                if not tree.path_exists(file_map, path):
                    raise Exception(f"The include path '{'.'.join(path)}' does not exist in {jar}.")

            tree.keep_only_included(file_map, include_paths)
            include_num = len(include_paths)
            print(f"Applied {include_num} include path{'s' if include_num != 1 else ''}.")

        elif args.exclude:
            fio.check_file_access(args.exclude)

            exclude_num = 0
            exclude_paths = []

            print(f"Parsing exclude paths from {args.exclude}...")
            with open(args.exclude, "r") as f:
                for line in f:
                    line = line.strip()
                    exclude_paths.append(line.split("."))
            exclude_num = len(exclude_paths)

            for path in exclude_paths:
                if not tree.remove_from_tree(file_map, path):
                    raise Exception(f"The exclude path '{'.'.join(path)}' does not exist in {jar}.")

            print(f"Applied {exclude_num} exclude path{"s" if exclude_num != 1 else ""} from {args.exclude}.")
        elif args.exclude_list:
            if not isinstance(args.exclude_list, list):
                args.exclude_list = [args.exclude_list]

            exclude_num = len(args.exclude_list)

            print(f"Parsing exclude paths...")
            for path in args.exclude_list:
                if not tree.remove_from_tree(file_map, path.split(".")):
                    raise Exception(f"The exclude path '{path}' does not exist in {jar}.")

            print(f"Applied {exclude_num} exclude path{"s" if exclude_num != 1 else ""}.")

        t_len = tree.tree_len(file_map)
        print(f"Total of {t_len} file{'s' if t_len != 1 else ''} from {jar} after filtering.")

        # print(f"Generating stubs for {jar}...")
        # print(f" - Generating stubs for {file}...")