#!/usr/bin/env python3
import sys
from io import StringIO
import json

# Add the project root to the path
sys.path.insert(0, '/app/isortfork')

from isort.main import identify_imports_main

# Test 1: Test with file path
print("Test 1: Testing with file path test_imports.py")
print("-" * 50)
try:
    identify_imports_main(['--json', 'test_imports.py'])
except Exception as e:
    print(f"Error: {e}")
print("\n" + "=" * 50 + "\n")

# Test 2: Test with stdin
print("Test 2: Testing with stdin")
print("-" * 50)
test_code = """
import os
import sys
from pathlib import Path

def test_function():
    import math
    from typing import List, Dict

cimport numpy as np
"""
stdin_buf = StringIO(test_code)
try:
    identify_imports_main(['--json', '-'], stdin=stdin_buf)
except Exception as e:
    print(f"Error: {e}")
