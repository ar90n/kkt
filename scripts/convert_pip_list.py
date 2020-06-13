import json
import sys

raw_str = sys.stdin.read()
hosted_pkgs = {r["name"]: r["version"] for r in json.loads(raw_str)}
print(f"DEFAULT_HOSTED_PKGS={hosted_pkgs}")
