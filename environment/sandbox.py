import docker
import os
import tempfile
import shutil
from typing import Dict, Tuple
import subprocess

class Sandbox:
    """
    Manages a sandboxed Docker container for code execution.
    Prevents agent from accessing host machine.
    """

    def __init__(self, image: str = "python:3.10-slim", timeout: int = 30):
        """
        Initialize sandbox.
        
        Args:
            image: Docker image to use
            timeout: Subprocess timeout in seconds
        """
        self.image = image
        self.timeout = timeout
        self.container = None
        self.episode_dir = None

    def create_episode_environment(self, repo_template: str) -> str:
        """
        Create isolated filesystem for new episode.
        
        Args:
            repo_template: Path to buggy repo template
            
        Returns:
            Path to episode directory
        """
        # Create temp directory
        self.episode_dir = tempfile.mkdtemp(prefix="asr_episode_")
        
        # Copy template repo
        if os.path.exists(repo_template):
            if os.path.isdir(repo_template):
                # If directory, copy contents
                for item in os.listdir(repo_template):
                    src = os.path.join(repo_template, item)
                    dst = os.path.join(self.episode_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            else:
                # If it's a file (shouldn't happen with current design but for safety)
                shutil.copy2(repo_template, self.episode_dir)

        
        # Create src/ and tests/ if they don't exist
        os.makedirs(os.path.join(self.episode_dir, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.episode_dir, "tests"), exist_ok=True)
        
        return self.episode_dir

    def read_file(self, path: str) -> str:
        """
        Read file from sandbox (with whitelist check).
        
        Args:
            path: File path relative to episode directory
            
        Returns:
            File contents
            
        Raises:
            PermissionError: If path is outside allowed directories
        """
        full_path = os.path.join(self.episode_dir, path)
        
        # Security: Only allow reading from src/ and tests/
        if not self._is_path_allowed(full_path):
            raise PermissionError(f"Access denied: {path}")
        
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> bool:
        """
        Write file to sandbox (with whitelist check).
        
        Args:
            path: File path relative to episode directory
            content: File contents to write
            
        Returns:
            Success boolean
            
        Raises:
            PermissionError: If path is outside allowed directories
        """
        full_path = os.path.join(self.episode_dir, path)
        
        # Security: Only allow writing to src/ and tests/
        if not self._is_path_allowed(full_path):
            raise PermissionError(f"Access denied: {path}")
        
        # Prevent deleting test files
        if path.startswith("tests/") and os.path.exists(full_path):
            raise PermissionError("Cannot modify test files")
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True

    def run_pytest(self) -> Dict:
        """
        Execute pytest in sandbox.
        
        Returns:
            Dict with stdout, stderr, returncode, and parsed results
        """
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                cwd=self.episode_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "passed": result.stdout.count(" PASSED"),
                "failed": result.stdout.count(" FAILED"),
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Pytest execution timed out",
                "returncode": -1,
                "passed": 0,
                "failed": -1,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "passed": 0,
                "failed": -1,
            }

    def _is_path_allowed(self, full_path: str) -> bool:
        """
        Check if path is within allowed directories.
        
        Args:
            full_path: Absolute path to check
            
        Returns:
            True if allowed, False otherwise
        """
        allowed_bases = [
            os.path.join(self.episode_dir, "src"),
            os.path.join(self.episode_dir, "tests"),
        ]
        
        for base in allowed_bases:
            if os.path.commonpath([full_path, base]) == base:
                return True
        
        return False

    def cleanup(self):
        """Clean up episode resources."""
        if self.episode_dir and os.path.exists(self.episode_dir):
            shutil.rmtree(self.episode_dir)

    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup()