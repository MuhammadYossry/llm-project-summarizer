"""
Base classes and data structures for language parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Set

@dataclass
class CodeSymbol:
    """Represents a code symbol (function, class, interface, etc.)"""
    name: str
    kind: str  # 'function', 'class', 'interface', 'struct', etc.
    signature: str
    docstring: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)

@dataclass
class FileSymbols:
    """Contains all symbols found in a single file"""
    filepath: str
    imports: List[str]
    symbols: List[CodeSymbol]
    package: Optional[str] = None

class LanguageParser(ABC):
    """Abstract base class for language-specific parsers"""
    
    @abstractmethod
    def can_parse(self, filename: str) -> bool:
        """Determines if this parser can handle the given file"""
        pass
    
    @abstractmethod
    def parse_file(self, filepath: str) -> FileSymbols:
        """Parses a file and returns its symbols"""
        pass
    
    def _sanitize_docstring(self, docstring: Optional[str]) -> Optional[str]:
        """Cleans up a docstring for consistent formatting"""
        if not docstring:
            return None
        
        # Remove common indentation
        lines = docstring.split('\n')
        if len(lines) == 1:
            return lines[0].strip()
        
        # Find minimum indentation
        indents = [len(line) - len(line.lstrip()) 
                  for line in lines[1:] if line.strip()]
        if indents:
            min_indent = min(indents)
            lines = [lines[0].strip()] + [
                line[min_indent:] if line.strip() else ''
                for line in lines[1:]
            ]
        
        return '\n'.join(line.rstrip() for line in lines).strip()
