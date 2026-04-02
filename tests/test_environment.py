"""
Unit tests for ASR environment components.
"""

import unittest
import tempfile
import os
from environment.sandbox import Sandbox
from environment.tree_sitter_parser import TreeSitterParser
from environment.observation_space import ObservationSpace
from environment.action_space import ActionSpace


class TestSandbox(unittest.TestCase):
    """Test Sandbox functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.sandbox = Sandbox()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        self.sandbox.cleanup()

    def test_create_episode_environment(self):
        """Test episode environment creation."""
        episode_dir = self.sandbox.create_episode_environment(self.temp_dir)
        self.assertTrue(os.path.exists(episode_dir))
        self.assertTrue(os.path.exists(os.path.join(episode_dir, "src")))
        self.assertTrue(os.path.exists(os.path.join(episode_dir, "tests")))


class TestTreeSitterParser(unittest.TestCase):
    """Test Tree-sitter parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = TreeSitterParser()

    def test_parse_function(self):
        """Test parsing function definition."""
        code = "def foo(x): return x + 1"
        tree = self.parser.parse(code)
        self.assertIsNotNone(tree)

    def test_parse_class(self):
        """Test parsing class definition."""
        code = "class MyClass:\n    def method(self): pass"
        tree = self.parser.parse(code)
        self.assertIsNotNone(tree)


class TestActionSpace(unittest.TestCase):
    """Test action space."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sandbox = Sandbox()
        self.sandbox.create_episode_environment(self.temp_dir)
        self.action_space = ActionSpace(self.sandbox)

    def test_read_file(self):
        """Test read_file action."""
        # Create test file
        test_file = os.path.join(self.sandbox.episode_dir, "src", "test.py")
        with open(test_file, 'w') as f:
            f.write("print('hello')")
        
        # Read file
        result, info = self.action_space.execute_action(
            "read_file",
            {"path": "src/test.py"}
        )
        
        self.assertEqual(result, "print('hello')")


if __name__ == '__main__':
    unittest.main()