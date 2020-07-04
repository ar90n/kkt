from typing import List
from pathlib import Path

from dataclasses import dataclass
import requests


@dataclass
class PackageLocation:
    url: str
    name: str


def fetch_packages(
    locations: List[PackageLocation], save_dir: Path, quiet: bool = False
) -> List[Path]:
    outfiles = []
    for loc in locations:
        response = requests.get(loc.url)
        outfile = save_dir / loc.name
        with outfile.open("wb") as out:
            out.write(response.content)
        outfiles.append(outfile)
        if not quiet:
            print("Output file downloaded to %s" % str(outfile))
    return outfiles
