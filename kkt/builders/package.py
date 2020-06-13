from dataclasses import dataclass


@dataclass
class Package:
    name: str
    content: bytes
