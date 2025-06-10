import generator
from java_model.jash_annotation import JashAnnotation
from java_model.jash_expression import JashExpression
from java_model.jash_type import JashType


class JashVariable:
    def __init__(
        self,
        name: str = None,
        _type: JashType = None,
        initializer: JashExpression = None,
        modifiers: list[str] = None,
        annotations: list[JashAnnotation] = None,
        documentation: str = None
    ):
        self.name = name or ""
        self.type = _type
        self.initializer = initializer
        self.modifiers = modifiers or []
        self.annotations = annotations or []
        self.documentation = documentation or ""

    def __str__(self):
        annotation_str = '\n'.join(str(a) for a in self.annotations).strip()
        return (f"{annotation_str}{self.name}{f': {self.type}' if generator.options.typed else ''}"
                f"{f' = 42' if self.initializer is not None else ''}\n")
