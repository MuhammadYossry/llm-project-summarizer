"""
Parser for Python source files.
Uses the ast module for accurate symbol extraction.
"""

import ast
import logging
from typing import List, Set, Optional, Any

from .base import LanguageParser, FileSymbols, CodeSymbol

logger = logging.getLogger(__name__)

class PythonParser(LanguageParser):
    """Parses Python source files using the ast module"""
    
    def can_parse(self, filename: str) -> bool:
        return filename.endswith('.py')
    
    def parse_file(self, filepath: str) -> FileSymbols:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.error(f"Failed to parse {filepath}: {e}")
            return FileSymbols(filepath, [], [])
        
        imports = self._extract_imports(tree)
        symbols = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append(self._process_function(node))
            elif isinstance(node, ast.ClassDef):
                symbols.append(self._process_class(node))
            elif isinstance(node, ast.AsyncFunctionDef):
                symbols.append(self._process_async_function(node))
        
        return FileSymbols(filepath, imports, symbols)
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from an AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                imports.extend(f"{module}.{n.name}" for n in node.names)
        
        return imports
    
    def _format_expression(self, node: ast.AST) -> str:
        """Format an AST expression node as a string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._format_expression(node.value)}.{node.attr}"
        return "..."

    def _format_arguments(self, args: ast.arguments) -> str:
        """Format function arguments as a string"""
        parts = []
        
        # Add positional arguments
        parts.extend(arg.arg for arg in args.args)
        
        # Add varargs
        if args.vararg:
            parts.append(f"*{args.vararg.arg}")
        
        # Add keyword-only args
        if args.kwonlyargs:
            if not args.vararg:
                parts.append("*")
            parts.extend(arg.arg for arg in args.kwonlyargs)
        
        # Add kwargs
        if args.kwarg:
            parts.append(f"**{args.kwarg.arg}")
        
        return ", ".join(parts)
    
    def _format_decorators(self, decorators: List[ast.expr]) -> List[str]:
        """Format decorators as strings"""
        return [f"@{self._format_expression(d)}\n" for d in decorators]
    
    def _process_function(self, node: ast.FunctionDef) -> CodeSymbol:
        """Process a function definition"""
        args = self._format_arguments(node.args)
        decorators = self._format_decorators(node.decorator_list)
        signature = f"{''.join(decorators)}def {node.name}({args})"
        
        return CodeSymbol(
            name=node.name,
            kind='function',
            signature=signature,
            docstring=ast.get_docstring(node)
        )
    
    def _process_async_function(self, node: ast.AsyncFunctionDef) -> CodeSymbol:
        """Process an async function definition"""
        args = self._format_arguments(node.args)
        decorators = self._format_decorators(node.decorator_list)
        signature = f"{''.join(decorators)}async def {node.name}({args})"
        
        return CodeSymbol(
            name=node.name,
            kind='async_function',
            signature=signature,
            docstring=ast.get_docstring(node)
        )
    
    def _process_class(self, node: ast.ClassDef) -> CodeSymbol:
        """Process a class definition"""
        bases = [self._format_expression(b) for b in node.bases]
        base_str = f"({', '.join(bases)})" if bases else ""
        decorators = self._format_decorators(node.decorator_list)
        signature = f"{''.join(decorators)}class {node.name}{base_str}"
        
        return CodeSymbol(
            name=node.name,
            kind='class',
            signature=signature,
            docstring=ast.get_docstring(node)
        )