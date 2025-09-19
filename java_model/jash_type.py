from java_model.jash_type_parameter import JashTypeParameter


class JashType:
    def __init__(
            self,
            name: str = None,
            sub_type: "JashType" = None,
            implements: "JashType" = None,
            modifiers: list[str] = None,
            dimensions: list[int] = None,
            parameters: list[JashTypeParameter] = None
    ):
        self.parameters = parameters or []
        self.dimensions = dimensions or []
        self.modifiers = modifiers or []
        self.implements = implements
        self.sub_type = sub_type
        self.name = name or ""

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        return {
            "name": self.name,
            "sub_type": self.sub_type.to_dict() if self.sub_type else None,
            "implements": self.implements.to_dict() if self.implements else None,
            "modifiers": self.modifiers,
            "dimensions": self.dimensions,
            "parameters": [p.to_dict() for p in self.parameters],
        }
