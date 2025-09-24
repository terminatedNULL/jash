import os
import shutil

import requests
import zipfile

from generator.generator import collect_java_data, generate_python_files
from utils import tree
from cli import progress_counter
from cli.byte_progress_counter import ByteProgressCounter

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


def list_stdlib_versions() -> list[str]:
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/orgs/openjdk/repos?per_page=100&page={page}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1
    return [repo['name'] for repo in repos if repo['name'].lower().startswith("jdk")]


def download_online_stdlib(source_url: str, target_dir: str) -> str:
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)

    print(f"Downloading Java stdlib from:\n\t- {source_url}")
    zip_path = os.path.join(target_dir, "stdlib.zip")

    with requests.get(source_url, stream=True) as res:
        if res.status_code != 200:
            raise Exception(f"Failed to download Java stdlib from {source_url}")

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
    dir_opts = os.listdir(extract_path)
    if not any(filename.lower().startswith("jdk") for filename in dir_opts):
        raise FileNotFoundError(f"Unable to find extracted Java stdlib at path '{extract_path}'.")

    jdk_dir = next((x for x in dir_opts if x.lower().startswith("jdk")), None)
    full_jdk_path_a = os.path.join(extract_path, jdk_dir, "jdk/src/")
    full_jdk_path_b = os.path.join(extract_path, jdk_dir, "src/")
    final_jdk_path = None

    if os.path.exists(full_jdk_path_a):
        final_jdk_path = full_jdk_path_a
    elif os.path.exists(full_jdk_path_b):
        final_jdk_path = full_jdk_path_b
    else:
        raise FileNotFoundError(f"Unable to find extracted Java stdlib at path '{full_jdk_path_a}' or '{full_jdk_path_b}'.")

    print(f"Stdlib verified, located at '{final_jdk_path}'.\n")
    return final_jdk_path

def generate_stdlib(source_dir: str, dest_dir: str) -> None:
    if not os.path.exists(source_dir):
        raise FileNotFoundError("Unable to find Java stdlib, please try re-downloading.")

    print("Generating stubs for Java stdlib...")
    file_count, file_tree = tree.build_java_file_tree(source_dir)
    print(f"Found {file_count} compatible files in stdlib.\n")

    t_len = tree.tree_len(file_tree)

    # Collect initial data
    print("Collecting initial java data...")
    counter = progress_counter.ProgressCounter(t_len)
    for path, file in tree.iter_tree_files(file_tree):
        if not file in STDLIB_INCOMPATIBLE:
            collect_java_data(file, source_dir, path)
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
    generate_python_files(dest_dir)

    print("Successfully generated all files.")

