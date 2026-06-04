#!/usr/bin/env python3
import sys
from io import StringIO
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, '/app/isortfork')

import isort
from isort import identify, api

def test_identify():
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
    print("Testing with stdin-like data:")
    print("-" * 50)
    
    # Test using identify module directly
    input_stream = StringIO(test_code)
    identified = list(identify.imports(input_stream))
    
    print(f"Found {len(identified)} imports:\n")
    
    # Convert to JSON
    import_list = []
    for imp in identified:
        imp_dict = imp._asdict()
        if imp_dict.get('file_path') is not None:
            imp_dict['file_path'] = str(imp_dict['file_path'])
        import_list.append(imp_dict)
    
    print(json.dumps(import_list, indent=4, separators=(",", ": ")))

def test_with_file():
    print("\n\nTesting with test_imports.py:")
    print("-" * 50)
    identified = list(api.find_imports_in_file("/app/isortfork/test_imports.py"))
    import_list = []
    for imp in identified:
        imp_dict = imp._asdict()
        if imp_dict.get('file_path') is not None:
            imp_dict['file_path'] = str(imp_dict['file_path'])
        import_list.append(imp_dict)
    print(json.dumps(import_list, indent=4, separators=(",", ": ")))

if __name__ == "__main__":
    test_identify()
    test_with_file()
