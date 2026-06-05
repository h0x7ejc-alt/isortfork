#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入并运行我们的测试
from test_enhanced_config import get_enhanced_config_dict
from isort.settings import Config
import json

print("=== Testing Enhanced Show Config ===")
print()

# 测试 1：默认配置
print("1. Testing default config...")
config1 = Config()
output1 = get_enhanced_config_dict(config1)
print(f"   Sources: {[s.get('source') for s in config1.sources]}")
print(f"   Config source info: {json.dumps(output1['config_source'], indent=2)}")
print()

# 测试 2：使用当前项目的配置
print("2. Testing with project config...")
config2 = Config(settings_path=os.path.dirname(os.path.abspath(__file__)))
output2 = get_enhanced_config_dict(config2)
print(f"   Sources: {[s.get('source') for s in config2.sources]}")
print(f"   Config source info: {json.dumps(output2['config_source'], indent=2)}")
print()

# 测试 3：带有 runtime 覆盖的配置
print("3. Testing with runtime override...")
config3 = Config(settings_path=os.path.dirname(os.path.abspath(__file__)), line_length=120)
output3 = get_enhanced_config_dict(config3)
print(f"   Sources: {[s.get('source') for s in config3.sources]}")
print(f"   Config source info: {json.dumps(output3['config_source'], indent=2)}")
print()

print("=== Test Complete ===")
