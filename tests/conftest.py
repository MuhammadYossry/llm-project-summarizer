"""
Pytest configuration and fixtures
"""

import os
import pytest
from pathlib import Path

@pytest.fixture
def sample_go_file(tmp_path):
    """Create a sample Go file for testing"""
    content = '''package main

import (
    "fmt"
    "strings"
)

// UserService handles user-related operations
type UserService interface {
    GetUser(id string) (*User, error)
    CreateUser(user *User) error
}

// User represents a system user
type User struct {
    ID   string
    Name string
}

func main() {
    fmt.Println("Hello")
}
'''
    file_path = tmp_path / "main.go"
    file_path.write_text(content)
    return file_path

@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing"""
    content = '''"""
Sample module for testing
"""
from typing import Optional
import datetime

class User:
    """Represents a user"""
    def __init__(self, name: str):
        self.name = name

    def display_name(self) -> str:
        """Get display name"""
        return self.name

def process_user(user: User) -> None:
    """Process a user"""
    print(user.display_name())
'''
    file_path = tmp_path / "users.py"
    file_path.write_text(content)
    return file_path

@pytest.fixture
def sample_project(tmp_path):
    """Create a sample project structure"""
    project_root = tmp_path / "sample_project"
    project_root.mkdir()
    
    # Create Go files
    (project_root / "src").mkdir()
    (project_root / "src" / "main.go").write_text('''
package main

func main() {
    println("Hello")
}
''')
    
    # Create Python files
    pkg_dir = project_root / "python_pkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").touch()
    (pkg_dir / "core.py").write_text('''
def main():
    print("Hello")
''')
    
    return project_root