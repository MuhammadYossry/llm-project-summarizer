"""
Main module for project summarization functionality.
"""

import os
import logging
from typing import Dict, List, Optional

from .parsers.base import FileSymbols
from .parsers.go import GoParser
from .parsers.python import PythonParser

logger = logging.getLogger(__name__)

class ProjectSummarizer:
    """Main class for summarizing a project's structure"""
    
    def __init__(self):
        self.parsers = [
            GoParser(),
            PythonParser()
        ]
    
    def summarize_project(self, project_path: str, exclusions: Optional[List[str]] = None) -> Dict[str, FileSymbols]:
        """Summarize all supported files in the project"""
        if exclusions is None:
            exclusions = ['.git', '__pycache__', '*.pyc', '*.pyo']
        
        results = {}
        
        for root, dirs, files in os.walk(project_path):
            # Apply directory exclusions
            dirs[:] = [d for d in dirs if not any(
                os.path.join(root, d).startswith(excl) for excl in exclusions
            )]
            
            for file in files:
                filepath = os.path.join(root, file)
                
                # Skip excluded files
                if any(os.path.join(root, file).startswith(excl) for excl in exclusions):
                    continue
                
                # Find appropriate parser
                parser = next((p for p in self.parsers if p.can_parse(file)), None)
                if parser:
                    try:
                        results[filepath] = parser.parse_file(filepath)
                    except Exception as e:
                        logger.error(f"Error parsing {filepath}: {e}")
        
        return results
    
    def write_summary(self, project_path: str, results: Dict[str, FileSymbols], output_file: str):
        """Write the project summary to a file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Project Summary\n\n")
            
            # Project Overview
            f.write("## Project Architecture\n")
            f.write("This is a ")
            if os.path.exists(os.path.join(project_path, 'go.mod')):
                f.write("Go")
            elif os.path.exists(os.path.join(project_path, 'setup.py')) or \
                 os.path.exists(os.path.join(project_path, 'pyproject.toml')):
                f.write("Python")
            else:
                f.write("mixed-language")
            f.write(" project with the following structure:\n\n")
            
            # Package Structure
            f.write("### Package Structure\n")
            for filepath, file_symbols in sorted(results.items()):
                rel_path = os.path.relpath(filepath, project_path)
                f.write(f"\n#### {rel_path}\n")
                
                if file_symbols.package:
                    f.write(f"Package: {file_symbols.package}\n")
                
                if file_symbols.symbols:
                    f.write("\nSymbols:\n")
                    for symbol in sorted(file_symbols.symbols, key=lambda s: s.name):
                        f.write(f"\n  {symbol.kind}: {symbol.signature}\n")
                        if symbol.docstring:
                            f.write(f"    {symbol.docstring}\n")
                        if symbol.dependencies:
                            f.write(f"    Dependencies: {', '.join(sorted(symbol.dependencies))}\n")
            
            # Dependency Graph
            f.write("\n### Dependencies\n")
            f.write("```mermaid\ngraph TD\n")
            for filepath, file_symbols in results.items():
                pkg_name = file_symbols.package or os.path.basename(os.path.dirname(filepath))
                for imp in file_symbols.imports:
                    f.write(f"    {pkg_name}-->{imp}\n")
            f.write("```\n")
