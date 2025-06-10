import enum
import os

import javalang.parse

from generator_options import GeneratorOptions
from java_model.jash_expression import JashExpression
from java_model.jash_type import JashType
from java_model.jash_variable import JashVariable
from utils import fio
from java_model.jash_annotation import JashAnnotation
from java_model.jash_class import JashClass

java_data = {}
unknown_references = {}

options = GeneratorOptions()
import_req = []


class DataType(enum.Enum):
    CLASS = 0
    FIELD = 1
    METHOD = 2


def collect_java_data(file: str, temp_path: str, path: list[str]) -> None:
    """
    Collects all pertinent data from a given Java file.

    All data gathered is stored in `java_data`.

    Args:
        file: The name of the java file.
        temp_path: The path to the temp file directory.
        path: The path to the java file.
    """
    absolute_path = "/".join([temp_path] + path + [file + ".java"])
    fio.check_file_access(absolute_path)

    file_tree = None
    with (open(absolute_path, "r") as f):
        try:
            file_tree: javalang.parser.tree.CompilationUnit = javalang.parse.parse(f.read())

            classes = {}

            for path, node in file_tree.filter(javalang.parser.tree.ClassDeclaration):

                # General class data
                classes[node.name] = JashClass(
                    node.name,
                    [JashAnnotation(a) for a in node.annotations],
                    [],
                    str(node.documentation),
                    None,
                    None,
                    []
                )

                # Member variable
                for path, node in file_tree.filter(javalang.parser.tree.FieldDeclaration):
                    class_name = None
                    for ancestor in reversed(path):
                        if isinstance(ancestor, javalang.parser.tree.ClassDeclaration):
                            class_name = ancestor.name
                            break

                    if class_name:
                        for decl in node.declarators:
                            if class_name in classes:
                                classes[class_name].body.append(
                                    JashVariable(
                                        str(decl.name),
                                        JashType(str(getattr(node.type, 'name', str(node.type)))),
                                        JashExpression(),
                                        [str(m) for m in list(node.modifiers)],
                                        [JashAnnotation(str(a)) for a in node.annotations],
                                        str(node.documentation)
                                    )
                                )
                                continue

                            # Handle class not found case
                            # if class_name not in unknown_references:
                            #     unknown_references[class_name] = []
                            # unknown_references[class_name].append({
                            #     "file": file,
                            #     "path": path,
                            #     "inner_path": [
                            #         (class_name, DataType.CLASS),
                            #         (field_info["name"], DataType.FIELD)
                            #     ]
                            # })

            #
            # # Constructors
            # for path, node in file_tree.filter(javalang.parser.tree.ConstructorDeclaration):
            #     class_name = None
            #     for ancestor in reversed(path):
            #         if isinstance(ancestor, javalang.parser.tree.ClassDeclaration):
            #             class_name = ancestor.name
            #             break
            #     if class_name is None:
            #         continue
            #
            #     classes[class_name]["constructors"].append({
            #         "class": class_name,
            #         "name": "__init__",
            #         "return_type": None,
            #         "modifiers": node.modifiers,
            #         "parameters": [(param.type.name, param.name) for param in node.parameters],
            #         "position": node.position
            #     })
            #
            # # Methods
            # for path, node in file_tree.filter(javalang.parser.tree.MethodDeclaration):
            #     class_name = None
            #     for ancestor in reversed(path):
            #         if isinstance(ancestor, javalang.parser.tree.ClassDeclaration):
            #             class_name = ancestor.name
            #             break
            #     if class_name is None:
            #         continue  # skip if no class found
            #     classes[class_name]["methods"].append({
            #         "class": class_name,
            #         "name": node.name,
            #         "return_type": node.return_type.name if node.return_type else 'void',
            #         "modifiers": node.modifiers,
            #         "parameters": [(param.type.name, param.name) for param in node.parameters],
            #         "position": node.position
            #     })

                java_data[file] = classes
        except javalang.parser.JavaSyntaxError as e:
            raise Exception(f"Syntax error encountered while parsing {file}.java.\n\t- {e}")
        except Exception as e:
            raise Exception(f"Unknown error encountered while parsing {file}.java.\n\t- {e}")


def propagate_java_data():
    pass


def generate_python_files(save_dir: str):
    os.makedirs(save_dir, exist_ok=True)

    for file, data in java_data.items():
        with open(os.path.join(save_dir, file + ".py"), "w") as f:
            f.write(str(data[file]))
