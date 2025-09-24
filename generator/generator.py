import enum
import os
import javalang.parse
<<<<<<< HEAD

from generator import generator_options
from java_model.jash_method import JashMethod
from utils.tree import iter_tree_files, Tree
from utils.utils import strip_method_bodies, fix_invalid_escapes, strip_all_comments, create_import_str
=======
import generator_options
from utils.utils import strip_method_bodies, fix_invalid_escapes, strip_all_comments
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce

try:
    import re2 as re
except ImportError:
    import re

<<<<<<< HEAD
from generator.generator_options import GeneratorOptions
=======
from generator_options import GeneratorOptions
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
from java_model.jash_expression import JashExpression
from java_model.jash_type import JashType
from java_model.jash_variable import JashVariable
from utils import fio
from java_model.jash_annotation import JashAnnotation
from java_model.jash_class import JashClass
from utils.type_resolver import TypeResolver

java_data = {}
<<<<<<< HEAD
imports = {}
=======
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
unknown_references = {}
type_resolver = TypeResolver()
options = GeneratorOptions()

<<<<<<< HEAD
=======
class DataType(enum.Enum):
    CLASS = 0
    FIELD = 1
    METHOD = 2

>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce

def collect_java_data(file: str, base_path: str, path: list[str]) -> None:
    """
    Collects all pertinent data from a given Java file.

<<<<<<< HEAD
    All data gathered is stored in ``java_data``.
=======
    All data gathered is stored in `java_data`.
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce

    Args:
        file: The name of the java file.
        base_path: The path to the temp starting directory.
        path: The path to the java file.
    """
    absolute_path = "/".join([base_path] + path + [file + ".java"])
    fio.check_file_access(absolute_path)
<<<<<<< HEAD

    with open(absolute_path, "r", encoding="utf-8", errors="replace") as f:
=======
    generator_options.import_req = {}

    with (open(absolute_path, "r", encoding="utf-8", errors="replace") as f):
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
        file_contents = f.read()

        # Remove inline comments
        file_contents = strip_all_comments(file_contents)

        # Replace invalid unicode characters
        file_contents = fix_invalid_escapes(file_contents)

        # Remove all function code
        file_contents = strip_method_bodies(file_contents)

        try:
<<<<<<< HEAD
            try: # Collect package
                package = re.search(r'^\s*package\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*;', file_contents).group(1).split(".")
=======
            try:
                package = re.search(r'^\s*package\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)*)\s*;', file_contents).group(1).split(".")
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
            except AttributeError:
                package = []

            # Map imports
<<<<<<< HEAD
            import_list = []
=======
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
            for match in re.finditer(r"(?<=import)\s+(?:static\s+)?(.*?)(?=\s*;)", file_contents):
                if len(match.groups()) < 1:
                    continue

                split_import = match.group(0).strip().split(".")
                import_path = split_import[:-1]
                import_name = split_import[-1]
<<<<<<< HEAD
                import_list.append([import_path, import_name])
                if import_name == "*":
                    continue

                if not type_resolver.resolve_type_details(import_name):
=======
                if import_path[-1] == "*":
                    continue

                if not type_resolver.resolve_type(import_name):
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
                    type_resolver.add_type(JashType(import_name), import_name, import_path)

            file_tree: javalang.parser.tree.CompilationUnit = javalang.parse.parse(file_contents)

<<<<<<< HEAD
            # Collect imports
            imports[file] = import_list

            file_tree = javalang.parse.parse(file_contents)
            classes = {}
            for node in getattr(file_tree, "types", []):  # top-level types
                classes.update(collect_types(node, package))
            java_data[file] = classes
=======

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
                    pass

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
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
        except javalang.parser.JavaSyntaxError as e:
            with open("error_file_content.java", "w") as file:
                file.write(file_contents)
            raise Exception(f"Syntax error encountered while parsing {absolute_path}.\n\t- {e.description} at {e.at}")
        except Exception as e:
            with open("error_file_content.java", "w") as file:
                file.write(file_contents)
            raise Exception(f"Unknown error encountered while parsing {absolute_path}.\n\t- {str(e)}")

<<<<<<< HEAD
def collect_types(node, package=None):
    package = package or []
    classes = {}

    # Only process nodes with a name (class/interface/enum/annotation)
    node_name = getattr(node, "name", None)
    if node_name:
        classes[node_name] = JashClass(
            name=node_name,
            _annotations=[JashAnnotation(a.name, a.element) for a in getattr(node, "annotations", [])],
            body=[],
            documentation=str(getattr(node, "documentation", "")),
            extends=getattr(node, "extends", None),
            implements=getattr(node, "implements", None),
            modifiers=list(getattr(node, "modifiers", []))
        )
        # Map type
        if not type_resolver.resolve_type_details(node_name):
            type_resolver.add_type(classes[node_name], node_name, package + [node_name])

    # Collect fields, constructors, methods
    for _, field_node in getattr(node, "filter", lambda x: [])(javalang.parser.tree.FieldDeclaration):
        for decl in field_node.declarators:
            classes[node_name].body.append(JashVariable(
                decl.name,
                JashType(str(getattr(field_node.type, "name", str(field_node.type)))),
                JashExpression(),
                list(field_node.modifiers),
                [JashAnnotation(a.name, a.element) for a in field_node.annotations],
                str(field_node.documentation)
            ))

    for _, ctor_node in getattr(node, "filter", lambda x: [])(javalang.parser.tree.ConstructorDeclaration):
        classes[node_name].body.append(JashMethod(
            "__init__",
            node_name,
            None,
            ctor_node.modifiers,
            [(p.type.name, p.name) for p in ctor_node.parameters]
        ))

    for _, method_node in getattr(node, "filter", lambda x: [])(javalang.parser.tree.MethodDeclaration):
        classes[node_name].body.append(JashMethod(
            method_node.name,
            node_name,
            getattr(method_node.return_type, "name", None),
            method_node.modifiers,
            [(p.type.name, p.name) for p in method_node.parameters]
        ))

    # Recurse into nested types
    for child in getattr(node, "body", []):
        if isinstance(child, (
            javalang.tree.ClassDeclaration,
            javalang.tree.InterfaceDeclaration,
            javalang.tree.EnumDeclaration,
            javalang.tree.AnnotationDeclaration
        )):
            classes.update(collect_types(child, package + [node_name]))

    return classes

def generate_python_files(save_dir: str, file_tree: Tree) -> None:
    os.makedirs(save_dir, exist_ok=True)

    print("Building file structure ...")
    written = 0

    for path, filename in iter_tree_files(file_tree):
        dir_path = os.path.join(save_dir, *path)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"{filename}.py")
        if filename not in java_data:
            print(f"⚠ Missing file '{filename}'")
            open(file_path, "w", encoding="utf-8").close()
            continue

        classes_str: str = "\n\n".join(str(cls) for cls in java_data[filename].values())
        if "@overload" in classes_str:
            imports[filename].append([["typing"], "overload"])

        imports_str = create_import_str(imports.get(filename, []))
        stub_str = imports_str + classes_str

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(stub_str)
        written += 1

    print(f"Wrote {written}/{len(java_data)} stubs)")
=======

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
>>>>>>> 229b316b13305f0f30de5d020d97aaa829200cce
