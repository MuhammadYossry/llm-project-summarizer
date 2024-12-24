"""
summarizer with Mermaid graph generation.
"""

import os
import re
import logging
from typing import Dict, List, Optional, Set, Tuple

# Import the parsers explicitly
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

    def _sanitize_node_id(self, name: str) -> str:
        """
        Convert package name to valid Mermaid node ID.
        Removes special characters and ensures valid Mermaid ID format.
        """
        # Replace invalid characters with underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'pkg_' + sanitized
        return sanitized

    def _get_package_display_name(self, filepath: str, file_symbols: FileSymbols) -> str:
        """Get a human-readable package name for display"""
        if file_symbols.package:
            return file_symbols.package
        # Extract meaningful name from filepath
        parts = os.path.normpath(filepath).split(os.sep)
        # Use parent directory + filename without extension
        if len(parts) >= 2:
            return f"{parts[-2]}/{os.path.splitext(parts[-1])[0]}"
        return os.path.splitext(parts[-1])[0]

    def _extract_dependencies(self, results: Dict[str, FileSymbols]) -> Tuple[List[str], Set[Tuple[str, str]]]:
        """
        Extract nodes and edges for the dependency graph.
        Returns:
            - List of (node_id, display_name) tuples
            - Set of (from_node, to_node) edges
        """
        nodes = []
        edges = set()
        node_ids = {}  # Maps display names to node IDs
        # First pass: Create nodes
        for filepath, file_symbols in results.items():
            display_name = self._get_package_display_name(filepath, file_symbols)
            node_id = self._sanitize_node_id(display_name)
            node_ids[display_name] = node_id
            nodes.append((node_id, display_name))
        # Second pass: Create edges
        for filepath, file_symbols in results.items():
            from_pkg = self._get_package_display_name(filepath, file_symbols)
            from_id = node_ids[from_pkg]
            for imp in file_symbols.imports:
                # If import matches a known package, add edge
                if imp in node_ids:
                    edges.add((from_id, node_ids[imp]))
                # For external imports, create new nodes
                else:
                    ext_id = self._sanitize_node_id(imp)
                    if (ext_id, imp) not in nodes:
                        nodes.append((ext_id, imp))
                    edges.add((from_id, ext_id))
        return nodes, edges

    def _generate_mermaid_graph(self, results: Dict[str, FileSymbols]) -> str:
        """Generate a properly formatted Mermaid dependency graph."""
        nodes, edges = self._extract_dependencies(results)
        # Build the Mermaid graph
        lines = ['graph LR;', '    %% Nodes']
        # Add nodes with proper styling
        for node_id, display_name in nodes:
            lines.append(f'    {node_id}["{display_name}"];')
        # Add relationship lines
        if edges:
            lines.append('    %% Dependencies')
            for from_node, to_node in sorted(edges):
                lines.append(f'    {from_node} --> {to_node};')
        return '\n'.join(lines)

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

            # Dependency Graph with improved Mermaid syntax
            f.write("\n### Dependencies\n")
            f.write("```mermaid\n")
            f.write(self._generate_mermaid_graph(results))
            f.write("\n```\n")