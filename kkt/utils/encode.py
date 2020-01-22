import base64
import gzip
from datetime import datetime
from typing import IO


def encode(io: IO) -> str:
    """
    Compress given stream with gzip and encode it to base64.

    >>> from io import BytesIO
    >>> io = BytesIO(b'abcd')
    >>> encoded = encode(io)

    """
    compressed = gzip.compress(io.read(), compresslevel=9)
    return base64.b64encode(compressed).decode("utf-8")
