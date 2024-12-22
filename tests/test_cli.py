"""
Tests for the command-line interface.
"""

import pytest
from click.testing import CliRunner
from llm_project_summarizer.cli import main

def test_cli_basic_usage(sample_project):
    runner = CliRunner()
    result = runner.invoke(main, [str(sample_project)])
    
    assert result.exit_code == 0
    assert "Project summary written to" in result.output

def test_cli_custom_output(sample_project, tmp_path):
    output_file = tmp_path / "custom_summary.md"
    runner = CliRunner()
    
    result = runner.invoke(main, [
        str(sample_project),
        '--output', str(output_file)
    ])
    
    assert result.exit_code == 0
    assert output_file.exists()

def test_cli_with_exclusions(sample_project):
    runner = CliRunner()
    result = runner.invoke(main, [
        str(sample_project),
        '--exclude', '*.pyc',
        '--exclude', '__pycache__'
    ])
    
    assert result.exit_code == 0

def test_cli_invalid_project_path():
    runner = CliRunner()
    result = runner.invoke(main, ['/nonexistent/path'])
    
    assert result.exit_code != 0
    assert "Error" in result.output

def test_cli_handles_config_file(sample_project, tmp_path):
    # Create a config file
    config_file = tmp_path / "config.yaml"
    config_file.write_text('''
exclude:
  - "*.pyc"
  - "__pycache__"
output: "custom_summary.md"
''')
    
    runner = CliRunner()
    result = runner.invoke(main, [
        str(sample_project),
        '--config', str(config_file)
    ])
    
    assert result.exit_code == 0
