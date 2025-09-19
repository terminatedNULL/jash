# AbsentInformationException
class JashAnnotation:
    def __init__(self, name: str, elements: list[str]):
        self.name = name
        self.elements = elements

    def __str__(self):
        return f"@{self.name}"
