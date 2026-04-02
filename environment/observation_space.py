import os
from typing import Dict, Any
from environment.tree_sitter_parser import TreeSitterParser

class ObservationSpace:
    """
    Builds observations that agents see.
    Includes file tree, file content, parse trees, and terminal output.
    """

    def __init__(self, episode_dir: str):
        """
        Initialize observation builder.
        
        Args:
            episode_dir: Root directory of episode
        """
        self.episode_dir = episode_dir
        self.parser = TreeSitterParser()
        self.terminal_history = []

    def get_observation(self, current_file: str = None, last_test_output: Dict = None) -> Dict[str, Any]:
        """
        Build complete observation.
        
        Args:
            current_file: Path to file agent is 'looking at'
            last_test_output: Output from last pytest run
            
        Returns:
            Dict with all observation components
        """
        obs = {
            "file_tree": self._get_file_tree(),
            "current_file": self._get_current_file_content(current_file),
            "parse_tree": self._get_parse_tree(current_file),
            "last_output": self._get_last_output(),
            "test_results": last_test_output or {},
        }
        
        return obs

    def _get_file_tree(self) -> str:
        """
        Generate text representation of file tree.
        
        Returns:
            String representing directory structure
        """
        tree_lines = []
        
        for root, dirs, files in os.walk(self.episode_dir):
            level = root.replace(self.episode_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            rel_path = os.path.basename(root)
            tree_lines.append(f'{indent}{rel_path}/')
            
            subindent = ' ' * 2 * (level + 1)
            for file in sorted(files):
                if not file.startswith('.'):
                    tree_lines.append(f'{subindent}{file}')
        
        return '\n'.join(tree_lines)

    def _get_current_file_content(self, current_file: str = None) -> str:
        """
        Get content of current file with line numbers.
        
        Args:
            current_file: Path relative to episode directory
            
        Returns:
            File content with line numbers, or empty string
        """
        if current_file is None:
            return ""
        
        file_path = os.path.join(self.episode_dir, current_file)
        
        if not os.path.exists(file_path):
            return f"# File not found: {current_file}"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            numbered_lines = [
                f"{i+1:4d} | {line.rstrip()}"
                for i, line in enumerate(lines)
            ]
            
            return '\n'.join(numbered_lines)
        except Exception as e:
            return f"# Error reading file: {str(e)}"

    def _get_parse_tree(self, current_file: str = None) -> Dict[str, Any]:
        """
        Parse current file into AST.
        
        Args:
            current_file: Path relative to episode directory
            
        Returns:
            Parsed AST as dict
        """
        if current_file is None:
            return {}
        
        file_path = os.path.join(self.episode_dir, current_file)
        
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.parser.parse(code)
        except Exception as e:
            return {"error": str(e)}

    def _get_last_output(self, lines: int = 100) -> str:
        """
        Get last N lines of terminal output.
        
        Args:
            lines: Number of lines to return
            
        Returns:
            Recent terminal output
        """
        recent = self.terminal_history[-lines:] if self.terminal_history else []
        return '\n'.join(recent)

    def add_terminal_output(self, output: str):
        """
        Add terminal output to history.
        
        Args:
            output: Output string to add
        """
        lines = output.split('\n')
        self.terminal_history.extend(lines)
        
        # Keep last 1000 lines max
        if len(self.terminal_history) > 1000:
            self.terminal_history = self.terminal_history[-1000:]