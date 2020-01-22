from typing import Dict


def merge(source: Dict, destination: Dict) -> Dict:
    """
    Merge given dictionaries recursively.
    Reference: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data

    >>> a = { 'a' : { 'b' : { 'd' : 1, 'e' : 2 } } }
    >>> b = { 'a' : { 'b' : { 'f' : 3, 'g' : 4 } } }
    >>> merge(a, b)
    {'a': {'b': {'f': 3, 'g': 4, 'd': 1, 'e': 2}}}

    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            if key not in destination:
                destination[key] = value

    return destination
