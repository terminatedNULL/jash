import generator
from java_model.jash_type_parameter import JashTypeParameter


import_map = {
    "List": "typing"
}


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

        if name != "":
            res = import_map.get(name, None)

            if res:
                generator.import_req.append(res)

    def __str__(self):
        return f"{self.name}"
