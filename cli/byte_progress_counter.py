import sys

class ByteProgressCounter:
    def __init__(self, total_bytes: int | None = None):
        self.total_bytes = total_bytes
        self.current = 0

    def increment(self, step: int = 1):
        self.current += step
        self._display()

    def _display(self):
        downloaded_mb = self.current / (1024 * 1024)
        if self.total_bytes:
            percent = (self.current / self.total_bytes) * 100
            sys.stdout.write(f"\r{downloaded_mb:.2f} MB ({percent:.2f}%)")
        else:
            sys.stdout.write(f"\r{downloaded_mb:.2f} MB")
        sys.stdout.flush()

    def complete(self):
        if self.total_bytes:
            self.current = self.total_bytes
        self._display()
        sys.stdout.write("\n")