import os
import shutil

import requests
import zipfile

from generator import collect_java_data, propagate_java_data, generate_python_files
from utils import tree
from cli import progress_counter
from cli.byte_progress_counter import ByteProgressCounter

STDLIB_URL = "https://github.com/openjdk/jdk8/archive/master.zip"

STDLIB_INCOMPATIBLE = [
    "module-info",
    "AbstractChronology",
    "Map",
    "TreeMap",
    "Comparator",
    "ConcurrentSkipListMap",
    "DoublePipeline",
    "Collectors",
    "SliceOps",
    "LongPipeline",
    "ReferencePipeline",
    "IntPipeline",
    "IBM964",
    "IBM33722",
    "CollationData_ja",
    "CollationData_ko",
    "CollationData_zh",
    "CollationData_zh_TW"
]


def download_stdlib(target_dir: str) -> None:
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    print(f"Downloading Java stdlib from:\n\t- {STDLIB_URL}")
    zip_path = os.path.join(target_dir, "stdlib.zip")

    with requests.get(STDLIB_URL, stream=True) as res:
        if res.status_code != 200:
            raise Exception(f"Failed to download Java stdlib from {STDLIB_URL}")

        content_length = res.headers.get("content-length")
        total_size = int(content_length) if content_length else None

        progress = ByteProgressCounter(total_size)
        chunk_size = 8192

        with open(zip_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.increment(len(chunk))
        progress.complete()
        print()

    print("Extracting archive...")
    extract_path = os.path.join(target_dir, "stdlib")
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
    os.remove(zip_path)
    print("Successfully downloaded and extracted Java stdlib.")

    print("Verifying extracted Java stdlib...")
    if not os.path.exists(os.path.join(extract_path, "jdk8-master/jdk/src/share/classes")):
        raise FileNotFoundError("Unable to find extracted Java stdlib.")
    print("Stdlib verified.\n")


def generate_stdlib(target_dir: str) -> None:
    stdlib_path = os.path.join(target_dir, "stdlib/jdk8-master/jdk/src/share/classes")
    if not os.path.exists(stdlib_path):
        raise FileNotFoundError("Unable to find Java stdlib, please try re-downloading.")

    print("Generating stubs for Java stdlib...")
    file_count, file_tree = tree.build_java_file_tree(stdlib_path)
    print(f"Found {file_count} compatible files in stdlib.\n")

    t_len = tree.tree_len(file_tree)

    # Collect initial data
    print("Collecting initial java data...")
    counter = progress_counter.ProgressCounter(t_len)
    for path, file in tree.iter_tree_files(file_tree):
        if not file in STDLIB_INCOMPATIBLE:
            collect_java_data(file, stdlib_path, path)
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
    generate_python_files("./test_dir/")

    print("Successfully generated all files.")

