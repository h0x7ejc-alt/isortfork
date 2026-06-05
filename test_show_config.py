#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isort.settings import Config
from isort.main import _preconvert
import json

print("=== Current config ===")
config = Config()
print(f"Sources: {config.sources}")
print()

print("=== config.__dict__ ===")
config_dict = config.__dict__.copy()
# 过滤掉一些复杂属性，让输出更清晰
for key in list(config_dict.keys()):
    if key.startswith('_'):
        del config_dict[key]
print(json.dumps(config_dict, indent=4, separators=(",", ": "), default=_preconvert))
