import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.tools import read_file, write_file, get_file_path, validate_python_syntax

class TestTools:
    def test_get_file_path(self):
        path = get_file_path("test.py")
        assert "dummy_repo" in path
        assert path.endswith("test.py")
    
    def test_read_file(self):
        # Create a test file first
        test_path = get_file_path("test_read.txt")
        write_file(test_path, "Hello World")
        
        content = read_file(test_path)
        assert content == "Hello World"
        
        # Test non-existent file
        content = read_file("non_existent_file.txt")
        assert "ERROR" in content
    
    def test_write_file(self):
        test_path = get_file_path("test_write.txt")
        result = write_file(test_path, "Test Content")
        assert "SUCCESS" in result
        
        # Verify content was written
        content = read_file(test_path)
        assert content == "Test Content"