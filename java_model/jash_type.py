from java_model.jash_type_parameter import JashTypeParameter
from utils.utils import default


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
        self.parameters = default(parameters, [])
        self.dimensions = default(dimensions, [])
        self.modifiers = default(modifiers, [])
        self.implements = implements
        self.sub_type = sub_type
        self.name = default(name, "")
