#!/usr/bin/env python
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isort.settings import Config
from isort.main import _preconvert

# 模拟 main.py 中我们添加的逻辑
def get_enhanced_config_dict(config):
    # 复制配置字典用于输出
    output_dict = config.__dict__.copy()
    
    # 添加配置源信息
    config_source_info = {}
    
    # 查找配置文件路径
    config_file = None
    for source in config.sources:
        source_path = source.get("source", "")
        if source_path and source_path not in ("defaults", "runtime") and not source_path.endswith("profile"):
            config_file = source_path
            break
    if config_file:
        config_source_info["config_file"] = config_file
    
    # 查找 profile
    profile_name = None
    for source in config.sources:
        source_path = source.get("source", "")
        if source_path and source_path.endswith("profile"):
            profile_name = source_path.replace(" profile", "")
            break
    if profile_name:
        config_source_info["profile"] = profile_name
    
    # 检查是否有 runtime 覆盖
    has_runtime_override = False
    for source in config.sources:
        if source.get("source") == "runtime":
            has_runtime_override = True
            break
    config_source_info["has_runtime_override"] = has_runtime_override
    
    # 添加到输出字典
    output_dict["config_source"] = config_source_info
    
    return output_dict

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
