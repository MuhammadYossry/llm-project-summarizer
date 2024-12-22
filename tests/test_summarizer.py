"""
Tests for the main project summarizer functionality.
"""

import os
import pytest
from pathlib import Path
from llm_project_summarizer.summarizer import ProjectSummarizer

def test_summarizer_processes_project(sample_project):
    summarizer = ProjectSummarizer()
    results = summarizer.summarize_project(str(sample_project))
    
    # Check if both Go and Python files were processed
    file_paths = [os.path.basename(f) for f in results.keys()]
    assert "main.go" in file_paths
    assert "core.py" in file_paths

def test_summarizer_respects_exclusions(sample_project):
    summarizer = ProjectSummarizer()
    
    # Add some files that should be excluded
    (sample_project / "node_modules").mkdir()
    (sample_project / "node_modules/test.js").write_text("console.log('test');")
    (sample_project / ".git").mkdir()
    (sample_project / ".git/config").write_text("git config")
    
    results = summarizer.summarize_project(
        str(sample_project),
        exclusions=["node_modules/*", ".git/*"]
    )
    
    # Check that excluded files were not processed
    file_paths = [str(p) for p in results.keys()]
    assert not any("node_modules" in p for p in file_paths)
    assert not any(".git" in p for p in file_paths)

def test_summarizer_writes_summary(sample_project, tmp_path):
    summarizer = ProjectSummarizer()
    results = summarizer.summarize_project(str(sample_project))
    
    output_file = tmp_path / "summary.md"
    summarizer.write_summary(str(sample_project), results, str(output_file))
    
    # Check if summary file was created and contains expected sections
    assert output_file.exists()
    content = output_file.read_text()
    
    assert "# Project Summary" in content
    assert "## Project Architecture" in content
    assert "### Package Structure" in content

def test_summarizer_handles_empty_project(tmp_path):
    empty_project = tmp_path / "empty"
    empty_project.mkdir()
    
    summarizer = ProjectSummarizer()
    results = summarizer.summarize_project(str(empty_project))
    
    assert len(results) == 0

def test_summarizer_generates_mermaid_diagram(sample_project, tmp_path):
    summarizer = ProjectSummarizer()
    results = summarizer.summarize_project(str(sample_project))
    
    output_file = tmp_path / "summary.md"
    summarizer.write_summary(str(sample_project), results, str(output_file))
    
    content = output_file.read_text()
    assert "```mermaid" in content
    assert "graph TD" in content
