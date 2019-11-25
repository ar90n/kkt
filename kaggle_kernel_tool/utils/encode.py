import base64
import gzip
from pathlib import Path


def encode(path: Path) -> str:
    compressed = gzip.compress(path.read_bytes(), compresslevel=9)
    return base64.b64encode(compressed).decode("utf-8")
