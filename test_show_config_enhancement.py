#!/usr/bin/env python3
"""Test for show-config enhancement"""

import json
import os
import tempfile
from io import StringIO
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from isort import main
from isort.settings import Config


def test_show_config_enhancement():
    """Test that show-config now includes config_source information"""
    
    # Create a temporary directory with a config file
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, ".isort.cfg")
        with open(config_file, "w") as f:
            f.write("""
[settings]
profile=hug
line_length=120
""")
        
        # Test 1: Show config without runtime overrides
        from contextlib import redirect_stdout
        f = StringIO()
        
        with redirect_stdout(f):
            main.main([str(tmpdir), "--show-config"])
        
        output = f.getvalue()
        config = json.loads(output)
        
        # Verify config_source exists
        assert "config_source" in config
        config_source = config["config_source"]
        assert config_source["config_file"] == config_file
        assert config_source["profile"] == "hug"
        assert config_source["has_runtime_override"] == False
        
        # Test 2: Show config with runtime overrides
        f = StringIO()
        
        with redirect_stdout(f):
            main.main([str(tmpdir), "--show-config", "--line-length=150"])
        
        output = f.getvalue()
        config = json.loads(output)
        
        # Verify config_source exists and has_runtime_override is True
        assert "config_source" in config
        config_source = config["config_source"]
        assert config_source["has_runtime_override"] == True


if __name__ == "__main__":
    test_show_config_enhancement()
    print("All tests passed!")
