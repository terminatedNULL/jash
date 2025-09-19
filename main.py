import argparse
import json
import os
import tempfile
import shutil

import generator
from generator.stdlib_generator import generate_stdlib, list_stdlib_versions, download_online_stdlib
from generator import propagate_java_data, collect_java_data, generate_python_files
from utils import tree, fio
from cli import progress_counter
from utils.fio import check_file_access

"""
Jython Advanced Syntax Highlighter (JASH)

A tool for generating typed python code stubs to
enable accurate syntax highlighting and autocompletion.
"""

STDLIB_PREFIX = "https://github.com/openjdk/"
STDLIB_POSTFIX = "/archive/master.zip"


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Jython Advanced Syntax Highlighter (JASH)")
    arg_parser.add_argument("-i", "--input", nargs="+", help="The jar files to generate stubs for.")
    arg_parser.add_argument("-o", "--output", help="The directory to generate the stubs to.")

    inc_ex_group = arg_parser.add_mutually_exclusive_group()
    inc_ex_group.add_argument("-ex", "--exclude", help="The exclude jar paths file to use during generation.")
    inc_ex_group.add_argument("-exl", "--exclude-list", nargs="+", help="List of internal jar directories to "
                                                                        "exclude during generation")
    inc_ex_group.add_argument("-inc", "--include", help="The include jar paths file to use during generation.")
    inc_ex_group.add_argument("-incl", "--include-list", nargs="+", help="List of internal jar directories "
                                                                         "to include during generation")

    arg_parser.add_argument("--stdlib", nargs="?", const="./", help="Generates all standard "
                                                                                  "library stubs to the specified directory, "
                                                                                  "defaults to jash's temp dir.")
    arg_parser.add_argument("--stdlib-source", nargs="?", const="jdk8", help="The location of "
                                                                                           "the java standard library to "
                                                                                           "download from, can be a URL, "
                                                                                           "path, or compatible version ("
                                                                                           "see --stdlib-list).")
    arg_parser.add_argument("--stdlib-dest", nargs="?", const="/tmp/jash/", help="The location to download "
                                                                                            "the standard library to.")
    arg_parser.add_argument("--stdlib-list", action="store_true", help="Lists all available standard library"
                                                                       " versions.")
    args = arg_parser.parse_args()

    # Create temp directory
    temp_dir = os.path.join(tempfile.gettempdir(), "jash")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    print(f"Using temp directory: {temp_dir}\n")

    if args.stdlib_list:
        versions = list_stdlib_versions()
        print("Available standard library versions:")
        for version in versions:
            print(f"\t- {version}")
        exit(1)

    stdlib_source_path = None
    if args.stdlib_source:
        if not args.stdlib_dest:
            args.stdlib_dest = temp_dir

        if args.stdlib_source.startswith("http"):                                       # Web download
            stdlib_source_path = download_online_stdlib(args.stdlib_source, args.stdlib_dest)
        elif args.stdlib_source.startswith("jdk"):                                      # Version download
            stdlib_source_path = download_online_stdlib(f"{STDLIB_PREFIX}{args.stdlib_source}{STDLIB_POSTFIX}", args.stdlib_dest)
        elif os.path.exists(args.stdlib_source) and os.path.isdir(args.stdlib_source):  # Local folder
            stdlib_source_path = args.stdlib_source
        else:
            raise Exception(f"The source '{args.stdlib_source}' is not a valid URL, directory, or version.")

    if args.stdlib:
        generate_stdlib(temp_dir if not args.stdlib else args.stdlib, args.output)
        exit(1)

    # Check for valid java installation
    code, output = fio.run_command(["java", "-version"])
    if code != 0 or "version" not in output.lower():
        raise Exception("Java is not installed or not properly configured.")

    if not args.input:
        exit(1)

    if not os.path.exists(args.output):
        os.mkdir(args.output)
        if not os.path.exists(args.output):
            raise Exception(f"The output directory '{args.output}' does not exist and could not be created.")

    # Decompile and generate jar stubs
    for jar in args.input:
        fio.check_file_access(jar)
        if os.path.splitext(jar)[1].lower() != ".jar":
            raise Exception(f"The file '{jar}' is not a jar file.")

        print(f"Decompiling {jar}...")
        code, _ = fio.run_command(["java", "-jar", "./third-party/jd-cli.jar", jar, "-od", temp_dir])
        if code != 0:
            raise Exception(f"Failed to decompile {jar}.")

        file_count, file_tree = tree.build_java_file_tree(temp_dir)
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
                if not tree.path_exists(file_tree, path):
                    raise Exception(f"The include path '{'.'.join(path)}' does not exist in {jar}.")

            tree.keep_only_included(file_tree, include_paths)
            include_num = len(include_paths)
            print(f"Applied {include_num} include path{'s' if include_num != 1 else ''} from {args.include}.")

        elif args.include_list:
            if not isinstance(args.exclude_list, list):
                args.exclude_list = [args.exclude_list]
            include_paths = [p.split(".") for p in args.include_list]

            for path in include_paths:
                if not tree.path_exists(file_tree, path):
                    raise Exception(f"The include path '{'.'.join(path)}' does not exist in {jar}.")

            tree.keep_only_included(file_tree, include_paths)
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
                if not tree.remove_from_tree(file_tree, path):
                    raise Exception(f"The exclude path '{'.'.join(path)}' does not exist in {jar}.")

            print(f"Applied {exclude_num} exclude path{'s' if exclude_num != 1 else ''} from {args.exclude}.")
        elif args.exclude_list:
            if not isinstance(args.exclude_list, list):
                args.exclude_list = [args.exclude_list]

            exclude_num = len(args.exclude_list)

            print(f"Parsing exclude paths...")
            for path in args.exclude_list:
                if not tree.remove_from_tree(file_tree, path.split(".")):
                    raise Exception(f"The exclude path '{path}' does not exist in {jar}.")

            print(f"Applied {exclude_num} exclude path{'s' if exclude_num != 1 else ''}.")

        t_len = tree.tree_len(file_tree)
        print(f"Total of {t_len} file{'s' if t_len != 1 else ''} from {jar} after filtering.")

        # Collect initial data
        print("Collecting initial java data...")
        counter = progress_counter.ProgressCounter(t_len)
        for path, file in tree.iter_tree_files(file_tree):
            collect_java_data(file, temp_dir, path)
            counter.increment()
        counter.complete()

        # Propagate known data to unknown references
        print("Propagating java data...")
        counter = progress_counter.ProgressCounter(t_len)
        for path, file in tree.iter_tree_files(file_tree):
            propagate_java_data()
            counter.increment()
        counter.complete()

        # Generate python stub files
        print("Generating python files...")
        generate_python_files(args.output)

        with open("type_resolver.json", "w") as f:
            f.write(json.dumps(generator.type_resolver.to_dict()))

        print(f"Successfully generated all files to {args.output}.")
