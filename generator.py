import enum
import os
import javalang.parse
import generator_options
from utils.utils import strip_method_bodies, fix_invalid_escapes, strip_all_comments

try:
    import re2 as re
except ImportError:
    import re

from generator_options import GeneratorOptions
from java_model.jash_expression import JashExpression
from java_model.jash_type import JashType
from java_model.jash_variable import JashVariable
from utils import fio
from java_model.jash_annotation import JashAnnotation
from java_model.jash_class import JashClass
from utils.type_resolver import TypeResolver

java_data = {}
unknown_references = {}
type_resolver = TypeResolver()
options = GeneratorOptions()

class DataType(enum.Enum):
    CLASS = 0
    FIELD = 1
    METHOD = 2


def collect_java_data(file: str, base_path: str, path: list[str]) -> None:
    """
    Collects all pertinent data from a given Java file.

    All data gathered is stored in `java_data`.

    Args:
        file: The name of the java file.
        base_path: The path to the temp starting directory.
        path: The path to the java file.
    """
    absolute_path = "/".join([base_path] + path + [file + ".java"])
    fio.check_file_access(absolute_path)
    generator_options.import_req = {}

    with (open(absolute_path, "r", encoding="utf-8", errors="replace") as f):
        file_contents = f.read()

        # Remove inline comments
        file_contents = strip_all_comments(file_contents)

        # Replace invalid unicode characters
        file_contents = fix_invalid_escapes(file_contents)

        # Remove all function code
        file_contents = strip_method_bodies(file_contents)

        try:
            try:
                package = re.search(r'^\s*package\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;', file_contents).group(1).split(".")
            except AttributeError:
                package = []

            # Map imports
            for match in re.finditer(r"(?<=import)\s+(?:static\s+)?(.*?)(?=\s*;)", file_contents):
                if len(match.groups()) < 1:
                    continue

                split_import = match.group(0).strip().split(".")
                import_path = split_import[:-1]
                import_name = split_import[-1]
                if import_path[-1] == "*":
                    continue

                if not type_resolver.resolve_type(import_name):
                    type_resolver.add_type(JashType(import_name), import_name, import_path)

            file_tree: javalang.parser.tree.CompilationUnit = javalang.parse.parse(file_contents)


            # Collect classes
            classes = {}
            for path, node in file_tree.filter(javalang.parser.tree.ClassDeclaration):
                classes[node.name] = JashClass(
                    node.name,
                    [JashAnnotation(a.name, a.element) for a in node.annotations],
                    [],
                    str(node.documentation),
                    None,
                    None,
                    []
                )

                # Map type
                # TODO : Implement nested class handling
                class_obj = classes[node.name]
                if not type_resolver.resolve_type(class_obj.name):
                    type_resolver.add_type(class_obj., class_obj.name, path)

                # Member variables
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
                                        [JashAnnotation(a.name, a.element) for a in node.annotations],
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
            with open("error_file_content.java", "w") as file:
                file.write(file_contents)
            raise Exception(f"Syntax error encountered while parsing {absolute_path}.\n\t- {e.description} at {e.at}")
        except Exception as e:
            with open("error_file_content.java", "w") as file:
                file.write(file_contents)
            raise Exception(f"Unknown error encountered while parsing {absolute_path}.\n\t- {str(e)}")


def propagate_java_data():
    pass


def generate_python_files(save_dir: str):
    os.makedirs(save_dir, exist_ok=True)

    for file, data in java_data.items():
        with open(os.path.join(save_dir, file + ".py"), "w") as f:
            if file in data:
                f.write(str(data[file]))
            else:
                print(file)
