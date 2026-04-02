from typing import Dict, Any, Tuple
import ast

class ActionSpace:
    """
    Defines and validates agent actions.
    Actions: read_file, write_file, run_pytest
    """

    ALLOWED_ACTIONS = ["read_file", "write_file", "run_pytest"]

    def __init__(self, sandbox):
        """
        Initialize action space.
        
        Args:
            sandbox: Sandbox instance for execution
        """
        self.sandbox = sandbox

    def execute_action(self, action: str, params: Dict = None) -> Tuple[Any, Dict]:
        """
        Execute an action and return result.
        
        Args:
            action: Action name
            params: Action parameters
            
        Returns:
            Tuple of (result, info dict)
        """
        params = params or {}
        
        if action not in self.ALLOWED_ACTIONS:
            return None, {
                "error": f"Unknown action: {action}",
                "allowed": self.ALLOWED_ACTIONS
            }
        
        if action == "read_file":
            return self._execute_read_file(params)
        elif action == "write_file":
            return self._execute_write_file(params)
        elif action == "run_pytest":
            return self._execute_run_pytest(params)

    def _execute_read_file(self, params: Dict) -> Tuple[str, Dict]:
        """
        Read file action.
        
        Args:
            params: {"path": str}
            
        Returns:
            Tuple of (file content, info)
        """
        path = params.get("path")
        
        if not path:
            return None, {"error": "path parameter required"}
        
        try:
            content = self.sandbox.read_file(path)
            return content, {"success": True, "file": path}
        except Exception as e:
            return None, {"error": str(e)}

    def _execute_write_file(self, params: Dict) -> Tuple[bool, Dict]:
        """
        Write file action with validation.
        
        Args:
            params: {"path": str, "content": str}
            
        Returns:
            Tuple of (success, info)
        """
        path = params.get("path")
        content = params.get("content")
        
        if not path or content is None:
            return False, {"error": "path and content parameters required"}
        
        # Validate syntax if Python file
        if path.endswith(".py"):
            try:
                ast.parse(content)
            except SyntaxError as e:
                return False, {
                    "error": f"SyntaxError: {e}",
                    "line": e.lineno,
                    "offset": e.offset,
                }
        
        try:
            self.sandbox.write_file(path, content)
            return True, {"success": True, "file": path}
        except Exception as e:
            return False, {"error": str(e)}

    def _execute_run_pytest(self, params: Dict) -> Tuple[Dict, Dict]:
        """
        Run pytest action.
        
        Args:
            params: {} (no parameters)
            
        Returns:
            Tuple of (test results, info)
        """
        try:
            results = self.sandbox.run_pytest()
            return results, {"success": results["returncode"] == 0}
        except Exception as e:
            return None, {"error": str(e)}

    def validate_action(self, action: str, params: Dict) -> Tuple[bool, str]:
        """
        Validate action and parameters before execution.
        
        Args:
            action: Action name
            params: Parameters
            
        Returns:
            Tuple of (valid, message)
        """
        if action not in self.ALLOWED_ACTIONS:
            return False, f"Unknown action: {action}"
        
        if action == "read_file":
            if "path" not in params:
                return False, "read_file requires 'path' parameter"
        
        elif action == "write_file":
            if "path" not in params or "content" not in params:
                return False, "write_file requires 'path' and 'content' parameters"
        
        return True, "OK"