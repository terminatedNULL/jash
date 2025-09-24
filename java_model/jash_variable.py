from generator import generator
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
        annotation_str = '\n'.join(str(a) for a in self.annotations).rstrip()
        variable_str = (
            f"{self.name}"
            f"{f': {generator.type_resolver.resolve_type_name(self.type.name)}' if generator.options.typed else ''}"
            f"{' = None # TODO : Initializer' if self.initializer is not None else ''}"
        )
        return f"{annotation_str}\n{variable_str}\n" if annotation_str else f"{variable_str}\n"
