from __future__ import annotations

import textwrap

from java_model.jash_annotation import JashAnnotation
from java_model.jash_method import JashMethod
from java_model.jash_type import JashType
from java_model.jash_variable import JashVariable
from utils.utils import default


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
        """
        Creates a new JashClass instance

        Args:
            _annotations: All class annotations.
            body: All definitions and declarations within the class.
            documentation: Any documentation comments on the class.
            extends: All types the class extends.
        """
        self.name = default(name, "")
        self.type_parameters = default(type_parameters, [])
        self.modifiers = default(modifiers, [])
        self.implements = implements
        self.extends = extends
        self.documentation = default(documentation, "", True)
        self.body = default(body, [])
        self.annotations = default(_annotations, [])

    def __str__(self):
        annotation_str = '\n'.join(str(a) for a in self.annotations).strip()
        body_decls = '\n\n'.join(textwrap.indent(str(b), "    ") for b in self.body).strip()
        doc = textwrap.indent(self.documentation.strip(), "    ") if self.documentation else ""

        lines = []

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
