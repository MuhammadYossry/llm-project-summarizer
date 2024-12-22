"""
Tests for the Go and Python parsers.
"""

import pytest
from llm_project_summarizer.parsers.go import GoParser
from llm_project_summarizer.parsers.python import PythonParser
from llm_project_summarizer.parsers.base import CodeSymbol, FileSymbols

def test_go_parser_can_parse():
    parser = GoParser()
    assert parser.can_parse("main.go") is True
    assert parser.can_parse("script.py") is False
    assert parser.can_parse("styles.css") is False

def test_python_parser_can_parse():
    parser = PythonParser()
    assert parser.can_parse("script.py") is True
    assert parser.can_parse("main.go") is False
    assert parser.can_parse("styles.css") is False

def test_go_parser_extracts_package(sample_go_file):
    parser = GoParser()
    result = parser.parse_file(str(sample_go_file))
    assert result.package == "main"

def test_go_parser_extracts_imports(sample_go_file):
    parser = GoParser()
    result = parser.parse_file(str(sample_go_file))
    assert "fmt" in result.imports
    assert "strings" in result.imports

def test_go_parser_extracts_interfaces(sample_go_file):
    parser = GoParser()
    result = parser.parse_file(str(sample_go_file))
    
    # Find UserService interface
    interface = next(s for s in result.symbols if s.name == "UserService")
    assert interface.kind == "interface"
    assert "handles user-related operations" in interface.docstring

def test_go_parser_extracts_structs(sample_go_file):
    parser = GoParser()
    result = parser.parse_file(str(sample_go_file))
    
    # Find User struct
    struct = next(s for s in result.symbols if s.name == "User")
    assert struct.kind == "type"
    assert "represents a system user" in struct.docstring.lower()

def test_go_parser_extracts_functions(sample_go_file):
    parser = GoParser()
    result = parser.parse_file(str(sample_go_file))
    
    # Find main function instead of NewUserService
    func = next(s for s in result.symbols if s.name == "main")
    assert func.kind == "function"
    

def test_python_parser_extracts_imports(sample_python_file):
    parser = PythonParser()
    result = parser.parse_file(str(sample_python_file))
    
    assert any("typing" in imp for imp in result.imports)
    assert any("datetime" in imp for imp in result.imports)

def test_python_parser_extracts_classes(sample_python_file):
    parser = PythonParser()
    result = parser.parse_file(str(sample_python_file))
    
    # Find User class
    user_class = next(s for s in result.symbols if s.name == "User")
    assert user_class.kind == "class"
    assert "Represents a user" in user_class.docstring

def test_python_parser_extracts_functions(sample_python_file):
    parser = PythonParser()
    result = parser.parse_file(str(sample_python_file))
    
    # Find process_user instead of process_users
    process_func = next(s for s in result.symbols if s.name == "process_user")
    assert process_func.kind == "function"
    assert "Process a user" in process_func.docstring
    
    # Find display_name method
    display_func = next(s for s in result.symbols if s.name == "display_name")
    assert display_func.kind == "function"
    assert "Get display name" in display_func.docstring

def test_python_parser_handles_invalid_file(tmp_path):
    parser = PythonParser()
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("this is not valid python")
    
    result = parser.parse_file(str(invalid_file))
    assert isinstance(result, FileSymbols)
    assert len(result.symbols) == 0
