#!/usr/bin/env python3
import sys
from io import StringIO
import json
from pathlib import Path
sys.path.insert(0, '/app/isortfork')

import isort
from isort import identify

test_code = """
import os
import sys
from pathlib import Path
from collections import defaultdict as dd
import json as js

def test_function():
    import math
    from typing import List, Dict

cimport numpy as np
"""

input_stream = StringIO(test_code)
identified = list(identify.imports(input_stream))

print("Testing JSON conversion logic:")
print("=" * 50)

# Test our conversion logic
import_list = []
for identified_import in identified:
    import_dict = identified_import._asdict()
    if import_dict.get("file_path") is not None:
        import_dict["file_path"] = str(import_dict["file_path"])
    import_list.append(import_dict)

# Preconvert function from main.py
def _preconvert(item):
    if isinstance(item, (set, frozenset)):
        return list(item)
    if isinstance(item, Path):
        return str(item)
    if callable(item) and hasattr(item, "__name__"):
        return str(item.__name__)
    raise TypeError(f"Unserializable object {item} of type {type(item)}")

# Test dumping
json_output = json.dumps(import_list, indent=4, separators=(",", ": "), default=_preconvert)
print(json_output)
print("\n" + "=" * 50)
print("✅ JSON conversion works!")
