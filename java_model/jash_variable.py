from java_model.jash_annotation import JashAnnotation
from java_model.jash_type import JashType


class JashVariable:
    def __init__(
        self,
        name: str,
        type: JashType,
        initializer: 'JashExpression' = None,
        modifiers: list[str] = None,
        annotations: list['JashAnnotation'] = None,
        documentation: str = None
    ):
        self.name = name
        self.type = type
        self.initializer = initializer
        self.modifiers = modifiers or []
        self.annotations = annotations or []
        self.documentation = documentation
