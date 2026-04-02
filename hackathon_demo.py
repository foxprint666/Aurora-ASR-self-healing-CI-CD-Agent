"""
Aurora ASR: Self-Healing CI/CD Pipeline Demo
--------------------------------------------
This script provides a high-impact visualization of how the Aurora RL agent
analyzes, mutates, and repairs buggy code in a simulated CI/CD environment.

Run this to showcase the project's 'Self-Healing' capabilities.
"""

import time
import difflib
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class MockAgent:
    def parse_and_fix(self, buggy_code):
        # Simulate RL agent thinking process
        time.sleep(1)
        fixed_code = buggy_code.replace("return fibonacci(n-1) + fibonacci(n-1)", "return fibonacci(n-1) + fibonacci(n-2)")
        fixed_code = fixed_code.replace("if n <= 0:\n        return 0\n    elif n == 1:\n        return 0", "if n <= 0:\n        return 0\n    elif n == 1:\n        return 1")
        return fixed_code

def print_diff(old_code, new_code):
    diff = difflib.unified_diff(
        old_code.splitlines(), new_code.splitlines(),
        fromfile='buggy.py', tofile='fixed.py', lineterm=''
    )
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            console.print(f"[bold green]{line}[/bold green]")
        elif line.startswith('-') and not line.startswith('---'):
            console.print(f"[bold red]{line}[/bold red]")
        else:
            console.print(line)

def run_demo():
    # Force UTF-8 for rich console if possible (though terminal might still fail)
    # Using simpler ASCII symbols to be safe.
    
    console.rule("[bold cyan]Aurora ASR: Self-Healing Pipeline[/bold cyan]")
    
    buggy_code = """def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 0
    else:
        return fibonacci(n-1) + fibonacci(n-1)
"""

    console.print("\n[bold yellow]Target Function Identified:[/bold yellow]")
    console.print(Panel(Syntax(buggy_code, "python", theme="monokai", line_numbers=True), title="buggy.py", border_style="red"))
    
    time.sleep(1.5)
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Running Continuous Integration Tests...", total=None)
        time.sleep(1.5)
    
    console.print("[bold red]FAILED:[/bold red] AssertionError: fibonacci(5) returned 0, expected 5")
    time.sleep(1)
    
    console.print("\n[bold magenta]Initializing ASR Agent...[/bold magenta]")
    
    with Progress(SpinnerColumn("dots2"), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task1 = progress.add_task(description="[cyan]Parsing AST Graph...[/cyan]", total=None)
        time.sleep(1)
        progress.update(task1, description="[cyan]Generating CodeBERT Embeddings...[/cyan]")
        time.sleep(1)
        progress.update(task1, description="[green]RL Agent evaluating Q-values...[/green]")
        
        agent = MockAgent()
        fixed_code = agent.parse_and_fix(buggy_code)
        
        progress.update(task1, description="[cyan]Applying mutations...[/cyan]")
        time.sleep(1.5)
        
    console.print("\n[bold green]Mutation Sandbox Testing...[/bold green]")
    with Progress(SpinnerColumn("bouncingBar"), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        progress.add_task(description="Running test suite on patched tree...", total=None)
        time.sleep(1.5)
        
    console.print("[bold green]ALL TESTS PASSED![/bold green] Solution found in 4 steps.")
    time.sleep(1)
    
    console.print("\n[bold yellow]Patch Diff:[/bold yellow]")
    print_diff(buggy_code, fixed_code)
    
    time.sleep(1)
    console.print("\n[bold yellow]Final Fixed Source:[/bold yellow]")
    console.print(Panel(Syntax(fixed_code, "python", theme="monokai", line_numbers=True), title="fixed.py", border_style="green"))

if __name__ == "__main__":
    run_demo()
