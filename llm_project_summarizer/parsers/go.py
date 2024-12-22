"""
Parser for Go source files.
Extracts symbols and relationships from Go code.
"""

import re
from typing import List, Optional, Match

from .base import LanguageParser, FileSymbols, CodeSymbol

class GoParser(LanguageParser):
    """Parses Go source files to extract symbols and relationships"""
    
    def can_parse(self, filename: str) -> bool:
        return filename.endswith('.go')
    
    def parse_file(self, filepath: str) -> FileSymbols:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract package name
        package = self._extract_package(content)
        
        # Extract imports
        imports = self._extract_imports(content)
        
        # Extract symbols
        symbols = []
        symbols.extend(self._extract_functions(content))
        symbols.extend(self._extract_types(content))
        symbols.extend(self._extract_interfaces(content))
        
        return FileSymbols(filepath, imports, symbols, package)
    
    def _extract_package(self, content: str) -> Optional[str]:
        """Extract the package name from Go source"""
        match = re.search(r'package\s+(\w+)', content)
        return match.group(1) if match else None
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract all imports from Go source"""
        imports = []
        
        # Match both single imports and import blocks
        import_matches = re.finditer(
            r'import\s+(?:\(\s*((?:[^)]+\s*)*)\)|([^\n]+))',
            content
        )
        
        for match in import_matches:
            if match.group(1):  # Multi-line import block
                imports.extend(re.findall(r'"([^"]+)"', match.group(1)))
            elif match.group(2):  # Single-line import
                imports.extend(re.findall(r'"([^"]+)"', match.group(2)))
        
        return imports
    
    def _extract_docstring(self, content: str, start_pos: int) -> Optional[str]:
        """Extract Go-style documentation comments"""
        # Look for comments before the given position
        end = start_pos
        while end > 0 and content[end-1].isspace():
            end -= 1
        
        lines = []
        pos = content.rfind('\n', 0, end)
        while pos != -1:
            line = content[pos+1:end].strip()
            if not line.startswith('//'):
                break
            lines.append(line[2:].strip())
            end = pos
            pos = content.rfind('\n', 0, end)
        
        return ' '.join(reversed(lines)) if lines else None
    
    def _extract_functions(self, content: str) -> List[CodeSymbol]:
        """Extract function declarations from Go source"""
        symbols = []
        
        # Match function declarations
        func_pattern = r'func\s+(?:\([^)]+\)\s+)?([^\s(]+)\s*\(([^{]*)\)'
        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            params = match.group(2)
            
            # Build full signature
            signature = f"func {name}({params})"
            
            # Extract docstring
            docstring = self._extract_docstring(content, match.start())
            
            symbols.append(CodeSymbol(
                name=name,
                kind='function',
                signature=signature.strip(),
                docstring=docstring
            ))
        
        return symbols
    
    def _extract_types(self, content: str) -> List[CodeSymbol]:
        """Extract type declarations from Go source"""
        symbols = []
        
        # Match type declarations
        type_pattern = r'type\s+([^\s{]+)\s+struct\s*{'
        for match in re.finditer(type_pattern, content):
            name = match.group(1)
            docstring = self._extract_docstring(content, match.start())
            
            symbols.append(CodeSymbol(
                name=name,
                kind='type',
                signature=f'type {name} struct',
                docstring=docstring
            ))
        
        return symbols
    
    def _extract_interfaces(self, content: str) -> List[CodeSymbol]:
        """Extract interface declarations from Go source"""
        symbols = []
        
        # Match interface declarations
        interface_pattern = r'type\s+([^\s{]+)\s+interface\s*{'
        for match in re.finditer(interface_pattern, content):
            name = match.group(1)
            docstring = self._extract_docstring(content, match.start())
            
            symbols.append(CodeSymbol(
                name=name,
                kind='interface',
                signature=f'type {name} interface',
                docstring=docstring
            ))
        
        return symbols
