import sys


class ProgressCounter:
    def __init__(self, max_value: int):
        if max_value <= 0:
            raise ValueError("max_value must be greater than 0")
        self.max_value = max_value
        self.current = 0

    def increment(self, step: int = 1):
        self.current += step
        if self.current > self.max_value:
            self.current = self.max_value
        self._display()

    def _display(self):
        percent = (self.current / self.max_value) * 100
        sys.stdout.write(f"\rProgress: {percent:.2f}%")
        sys.stdout.flush()

    def complete(self):
        self.current = self.max_value
        self._display()
        sys.stdout.write("\n")
