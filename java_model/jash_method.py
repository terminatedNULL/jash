from generator import generator
from java_model.jash_annotation import JashAnnotation


class JashMethod:
    def __init__(self, name: str, class_name: str | None, return_type: str,
                 modifiers: list[str]=None, parameters: list[tuple[str, str]]=None, annotations: list[JashAnnotation]=None) -> None:
        self.name = name
        self.class_name = class_name
        self.return_type = return_type
        self.modifiers = modifiers if modifiers else []
        self.parameters = parameters if parameters else []
        self.annotations = annotations if annotations else []

    def __str__(self):
        return (f"{"\n".join([str(a) for a in self.annotations])}{"\n" if self.annotations else ""}"
                f"def {self.name}({"self" if self.class_name else ""}{", " if self.parameters else ""}"
                f"{", ".join([f"{n}: {generator.type_resolver.resolve_type_name(t)}" for t, n in self.parameters])}) ->"
                f" {generator.type_resolver.resolve_type_name(self.return_type)}: ...\n")
