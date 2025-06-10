import json
import os

from java_model.jash_type import JashType


class TypeResolver:
    def __init__(self, name = None):
        self.name = name or "default_resolver"
        self.type_map = {}
        self.builtins = {
            "byte": int,
            "short": int,
            "int": int,
            "long": int,
            "float": float,
            "double": float,
            "char": str,
            "String": str,
            "boolean": bool,
        }

    def load_from_file(self):
        if not os.path.exists(f"./types/{self.name}.json"):
            raise FileNotFoundError(f"Type file for resolver {self.name} not found.")

        with open(f"./types/{self.name}.json", "w") as f:
            obj = json.load(f)
            if "type_map" not in obj:
                raise ValueError(f"Type file for resolver {self.name} is missing required 'type_map' key.")
            self.type_map = obj["type_map"]

    def save_to_file(self):
        os.makedirs("./types/", exist_ok=True)
        with open(f"./types/{self.name}.json", "w") as f:
            pass

    def add_type(self, type_instance: JashType, location: str) -> None:
        self.type_map[location] = type_instance

    def resolve_type(self, type_name):
        """
        Attempts to resolve a given Java type to the equivalent Python or JASH type.

        Args:
            type_name: The name of the type to resolve.

        Returns:
            type | JashType: The resolved type, or None if the type could not be resolved.
        """
        if type_name in self.builtins:
            return self.builtins[type_name]
        if type_name in self.type_map:
            return self.type_map[type_name]
        return None