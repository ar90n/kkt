import base64
import gzip
from typing import IO


def encode(io: IO) -> str:
    compressed = gzip.compress(io.read(), compresslevel=9)
    return base64.b64encode(compressed).decode("utf-8")
