import json
import os
import tempfile

import pytest

from isort import main


def test_show_config_includes_source_info(capsys, tmpdir):
    """Test that show-config now includes config_source with file, profile, and override info"""
    # Create a config file
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
profile=hug
"""
    )
    
    # Run show-config
    main.main([str(tmpdir), "--show-config"])
    out, error = capsys.readouterr()
    
    # Verify output
    assert not error
    config = json.loads(out)
    assert "config_source" in config
    config_source = config["config_source"]
    
    # Verify config source information
    assert config_source["config_file"] == str(config_file)
    assert config_source["profile"] == "hug"
    assert config_source["has_runtime_override"] == False


def test_show_config_with_runtime_override(capsys, tmpdir):
    """Test that show-config indicates when there are runtime overrides"""
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
profile=hug
line_length=100
"""
    )
    
    # Run with a runtime override
    main.main([str(tmpdir), "--show-config", "--line-length=150"])
    out, error = capsys.readouterr()
    
    assert not error
    config = json.loads(out)
    assert "config_source" in config
    config_source = config["config_source"]
    
    assert config_source["config_file"] == str(config_file)
    assert config_source["profile"] == "hug"
    assert config_source["has_runtime_override"] == True


def test_show_config_without_config_file(capsys, tmpdir):
    """Test show-config works when there's no config file"""
    # Run show-config in a directory without config
    main.main([str(tmpdir), "--show-config"])
    out, error = capsys.readouterr()
    
    assert not error
    config = json.loads(out)
    assert "config_source" in config
    config_source = config["config_source"]
    
    # No config file found
    assert "config_file" not in config_source
    # No profile
    assert "profile" not in config_source
    assert config_source["has_runtime_override"] == False


def test_show_config_with_profile_only(capsys, tmpdir):
    """Test show-config when only a profile is specified on command line"""
    # Run show-config with a profile from CLI
    main.main([str(tmpdir), "--show-config", "--profile=black"])
    out, error = capsys.readouterr()
    
    assert not error
    config = json.loads(out)
    assert "config_source" in config
    config_source = config["config_source"]
    
    # Profile should be detected even though it's from CLI
    assert config_source["profile"] == "black"
    assert config_source["has_runtime_override"] == True  # because we set --profile


def test_existing_show_config_still_works(capsys, tmpdir):
    """Test that existing functionality of show-config is still intact"""
    # This is essentially the same as the existing test_main.test_main's test
    config_file = tmpdir.join(".isort.cfg")
    config_file.write(
        """
[settings]
profile=hug
verbose=true
"""
    )
    
    # Run show-config
    config_args = ["--settings-path", str(config_file), "--show-config"]
    main.main(config_args)
    out, error = capsys.readouterr()
    
    # Verify existing data is still there
    config = json.loads(out)
    assert config["profile"] == "hug"
    assert config["verbose"] == True
    assert "config_source" in config  # Plus our new data
