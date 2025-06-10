from __future__ import annotations

import textwrap

from java_model.jash_annotation import JashAnnotation
from java_model.jash_method import JashMethod
from java_model.jash_type import JashType
from java_model.jash_variable import JashVariable
from utils.utils import str_default
from utils.utils import condense_imports
from generator_options import import_req


class JashClass:
    def __init__(
            self,
            name: str = "",
            _annotations: list[JashAnnotation] = None,
            body: list[JashMethod | JashVariable] = None,
            documentation: str = None,
            extends: JashType = None,
            implements: JashType = None,
            modifiers: list[str] = None,
            type_parameters: list[JashType] = None
    ):
        self.name = name or ""
        self.type_parameters = type_parameters or []
        self.modifiers = modifiers or []
        self.implements = implements
        self.extends = extends
        self.documentation = str_default(documentation, "")
        self.body = body or []
        self.annotations = _annotations or []

    def __str__(self):
        annotation_str = "\n".join(str(a) for a in self.annotations).strip()
        body_decls = "\n".join(textwrap.indent(str(b), "    ") for b in self.body).strip()
        doc = textwrap.indent(self.documentation.strip(), "    ") if self.documentation else ""
        import_str = "\n".join([f"from {key} import {','.join(value)}"
                                for key, value in condense_imports(import_req).items()])

        lines = []

        if import_str:
            lines.append(import_str)

        if annotation_str:
            lines.append(annotation_str)

        class_def = f"class {self.name}: "
        lines.append(class_def)

        if doc:
            lines.append(doc)

        if body_decls:
            lines.append(body_decls)
        else:
            lines.append("    pass")

        return '\n\n' + '\n'.join(lines) + '\n'
