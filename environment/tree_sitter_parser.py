import tree_sitter
from tree_sitter import Language, Parser
import json
from typing import Dict, List, Any

class TreeSitterParser:
    """
    Parses Python code into structured AST representation.
    Helps agent 'see' code as syntax trees, not just text.
    """

    def __init__(self):
        """Initialize Tree-sitter parser for Python."""
        try:
            PY_LANGUAGE = Language("tree_sitter_python.so", "python")
            self.parser = Parser()
            self.parser.set_language(PY_LANGUAGE)
        except Exception as e:
            print(f"Warning: Tree-sitter initialization failed: {e}")
            print("Falling back to basic parsing")
            self.parser = None

    def parse(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code into structured representation.
        
        Args:
            code: Python source code
            
        Returns:
            Dict with AST structure and metadata
        """
        if self.parser is None:
            return self._fallback_parse(code)
        
        try:
            tree = self.parser.parse(code.encode('utf-8'))
            return self._extract_tree_info(tree.root_node, code)
        except Exception as e:
            print(f"Parse error: {e}")
            return self._fallback_parse(code)

    def _extract_tree_info(self, node, code: str) -> Dict[str, Any]:
        """
        Recursively extract tree information.
        
        Args:
            node: Tree-sitter node
            code: Source code (for text extraction)
            
        Returns:
            Structured representation of AST
        """
        info = {
            "type": node.type,
            "text": code[node.start_byte:node.end_byte] if node.start_byte < len(code) else "",
            "start": {"line": node.start_point[0], "column": node.start_point[1]},
            "end": {"line": node.end_point[0], "column": node.end_point[1]},
        }

        # Extract specific node types
        if node.type == "function_definition":
            info.update(self._extract_function(node, code))
        elif node.type == "class_definition":
            info.update(self._extract_class(node, code))
        elif node.type == "assignment":
            info.update(self._extract_assignment(node, code))

        # Add children
        if node.child_count > 0:
            info["children"] = [
                self._extract_tree_info(child, code)
                for child in node.children
                if child.type not in ["NEWLINE", "INDENT", "DEDENT"]
            ]

        return info

    def _extract_function(self, node, code: str) -> Dict[str, Any]:
        """Extract function definition details."""
        info = {}
        
        for child in node.children:
            if child.type == "identifier":
                info["name"] = code[child.start_byte:child.end_byte]
            elif child.type == "parameters":
                info["parameters"] = self._extract_parameters(child, code)
        
        return info

    def _extract_class(self, node, code: str) -> Dict[str, Any]:
        """Extract class definition details."""
        info = {}
        
        for child in node.children:
            if child.type == "identifier":
                info["name"] = code[child.start_byte:child.end_byte]
        
        return info

    def _extract_assignment(self, node, code: str) -> Dict[str, Any]:
        """Extract assignment details."""
        info = {}
        
        for i, child in enumerate(node.children):
            if child.type == "identifier":
                info["variable"] = code[child.start_byte:child.end_byte]
            elif child.type == ":" and i + 1 < len(node.children):
                info["value"] = code[node.children[i + 1].start_byte:node.children[i + 1].end_byte]
        
        return info

    def _extract_parameters(self, node, code: str) -> List[str]:
        """Extract function parameters."""
        params = []
        
        for child in node.children:
            if child.type == "identifier":
                params.append(code[child.start_byte:child.end_byte])
        
        return params

    def _fallback_parse(self, code: str) -> Dict[str, Any]:
        """
        Fallback parsing without Tree-sitter.
        Basic extraction of functions, classes, and assignments.
        """
        import ast
        
        try:
            tree = ast.parse(code)
            return {
                "type": "module",
                "functions": [
                    {"name": node.name, "lineno": node.lineno}
                    for node in ast.walk(tree)
                    if isinstance(node, ast.FunctionDef)
                ],
                "classes": [
                    {"name": node.name, "lineno": node.lineno}
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ClassDef)
                ],
                "code": code,
            }
        except SyntaxError as e:
            return {
                "type": "module",
                "syntax_error": str(e),
                "code": code,
            }

    def get_function_body(self, code: str, function_name: str) -> str:
        """
        Extract specific function body.
        
        Args:
            code: Source code
            function_name: Name of function to extract
            
        Returns:
            Function source code
        """
        import ast
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    lines = code.split('\n')
                    start = node.lineno - 1
                    end = node.end_lineno
                    return '\n'.join(lines[start:end])
        except:
            pass
        
        return ""