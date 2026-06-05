#!/usr/bin/env python3
"""Quick test for our enhancement"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isort.settings import Config
import json


def test_config_sources():
    # Test 1: Get default config sources
    print("Test 1: Default config sources")
    config1 = Config()
    print(f"Sources: {[s.get('source') for s in config1.sources]}")
    print()

    # Test 2: Get config from project
    print("Test 2: Using project config")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    config2 = Config(settings_path=project_dir)
    print(f"Sources: {[s.get('source') for s in config2.sources]}")
    print()

    # Test 3: With profile and runtime overrides
    print("Test 3: With runtime override")
    config3 = Config(settings_path=project_dir, line_length=150)
    print(f"Sources: {[s.get('source') for s in config3.sources]}")


def build_config_source_info(config):
    config_source_info = {}
    
    # Find config file
    config_file = None
    for source in config.sources:
        source_path = source.get("source", "")
        if source_path and source_path not in ("defaults", "runtime") and not source_path.endswith("profile"):
            config_file = source_path
            break
    if config_file:
        config_source_info["config_file"] = config_file
    
    # Find profile
    profile_name = None
    for source in config.sources:
        source_path = source.get("source", "")
        if source_path and source_path.endswith("profile"):
            profile_name = source_path.replace(" profile", "")
            break
    if profile_name:
        config_source_info["profile"] = profile_name
    
    # Check for runtime overrides
    has_runtime_override = False
    for source in config.sources:
        if source.get("source") == "runtime":
            has_runtime_override = True
            break
    config_source_info["has_runtime_override"] = has_runtime_override
    
    return config_source_info


if __name__ == "__main__":
    test_config_sources()
    print("\n=== Testing config source info extraction ===")
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    config = Config(settings_path=project_dir)
    info = build_config_source_info(config)
    print(f"config_source_info: {json.dumps(info, indent=2)}")
    
    config_with_override = Config(settings_path=project_dir, line_length=150)
    info_with_override = build_config_source_info(config_with_override)
    print(f"\nconfig_source_info with override: {json.dumps(info_with_override, indent=2)}")
