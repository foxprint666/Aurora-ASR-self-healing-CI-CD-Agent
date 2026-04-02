"""
Dynamic Scenario Generator for Automated Software Repair.

Generates 500+ unique buggy code scenarios with controlled randomization.
Prevents overfitting by ensuring diverse bug patterns.
"""

import random
import os
import tempfile
import shutil
from typing import Dict, List, Tuple
import numpy as np


class BugTemplate:
    """Template for bug patterns."""
    
    def __init__(self, name: str, description: str, generator_func):
        """
        Initialize bug template.
        
        Args:
            name: Bug name
            description: Description of bug
            generator_func: Function to generate buggy code
        """
        self.name = name
        self.description = description
        self.generator_func = generator_func


class ScenarioGenerator:
    """
    Generates diverse bug scenarios for training.
    
    Ensures agent learns universal debugging principles,
    not specific bug patterns.
    """

    def __init__(self, seed: int = None):
        """
        Initialize scenario generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.seed = seed
        self.bug_templates = self._create_bug_templates()
        self.scenario_id = 0

    def _create_bug_templates(self) -> List[BugTemplate]:
        """
        Create library of bug templates.
        
        Returns:
            List of BugTemplate objects
        """
        templates = [
            BugTemplate(
                "undefined_variable",
                "Reference to undefined variable",
                self._gen_undefined_variable
            ),
            BugTemplate(
                "type_mismatch",
                "Type mismatch in operation",
                self._gen_type_mismatch
            ),
            BugTemplate(
                "missing_return",
                "Function missing return statement",
                self._gen_missing_return
            ),
            BugTemplate(
                "off_by_one",
                "Off-by-one error in indexing",
                self._gen_off_by_one
            ),
            BugTemplate(
                "null_reference",
                "Accessing None/null reference",
                self._gen_null_reference
            ),
            BugTemplate(
                "wrong_logic",
                "Incorrect conditional logic",
                self._gen_wrong_logic
            ),
            BugTemplate(
                "infinite_loop",
                "Unintended infinite loop",
                self._gen_infinite_loop
            ),
            BugTemplate(
                "import_error",
                "Missing or wrong import",
                self._gen_import_error
            ),
            BugTemplate(
                "indentation_error",
                "Incorrect indentation",
                self._gen_indentation_error
            ),
            BugTemplate(
                "scope_issue",
                "Variable scope issue",
                self._gen_scope_issue
            ),
        ]
        
        return templates

    def generate_scenario(self) -> Dict:
        """
        Generate a unique bug scenario.
        
        Returns:
            Dict with:
            - scenario_id: Unique ID
            - src/: Buggy source files
            - tests/: Test files (unchanged)
            - bug_info: Metadata about the bug
        """
        self.scenario_id += 1
        
        # Create temp directory
        scenario_dir = tempfile.mkdtemp(prefix=f"scenario_{self.scenario_id}_")
        
        # Create directory structure
        src_dir = os.path.join(scenario_dir, "src")
        tests_dir = os.path.join(scenario_dir, "tests")
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(tests_dir, exist_ok=True)
        
        # Select random bugs (1-3 per scenario)
        num_bugs = random.randint(1, 3)
        selected_bugs = random.sample(self.bug_templates, min(num_bugs, len(self.bug_templates)))
        
        # Generate buggy code
        buggy_code = self._generate_buggy_code(selected_bugs)
        
        # Write source files
        with open(os.path.join(src_dir, "main.py"), 'w') as f:
            f.write(buggy_code)
        
        # Generate corresponding tests
        test_code = self._generate_tests(selected_bugs)
        
        with open(os.path.join(tests_dir, "test_main.py"), 'w') as f:
            f.write(test_code)
        
        # Create pytest config
        with open(os.path.join(scenario_dir, "pytest.ini"), 'w') as f:
            f.write("[pytest]\ntestpaths = tests\n")
        
        bug_info = {
            "scenario_id": self.scenario_id,
            "bugs": [b.name for b in selected_bugs],
            "bug_descriptions": [b.description for b in selected_bugs],
            "scenario_dir": scenario_dir,
        }
        
        return bug_info

    def _generate_buggy_code(self, bugs: List[BugTemplate]) -> str:
        """
        Generate buggy Python code combining multiple bugs.
        
        Args:
            bugs: List of BugTemplate objects
            
        Returns:
            Python source code with bugs
        """
        code = '"""\nAuto-generated buggy module for repair testing.\n"""\n\n'
        
        for i, bug in enumerate(bugs):
            code += bug.generator_func(i)
            code += "\n\n"
        
        return code

    def _generate_tests(self, bugs: List[BugTemplate]) -> str:
        """
        Generate test file for buggy code.
        
        Args:
            bugs: List of BugTemplate objects
            
        Returns:
            Python test code
        """
        code = """import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import *

"""
        
        test_id = 1
        for bug in bugs:
            if bug.name == "undefined_variable":
                code += f"""def test_undefined_var_{test_id}():
    \"\"\"Test handles undefined variable.\"\"\"
    result = add_numbers(5, 3)
    assert result == 8

"""
            elif bug.name == "type_mismatch":
                code += f"""def test_type_mismatch_{test_id}():
    \"\"\"Test handles type mismatch.\"\"\"
    result = multiply_values(4, 5)
    assert result == 20

"""
            elif bug.name == "missing_return":
                code += f"""def test_missing_return_{test_id}():
    \"\"\"Test detects missing return.\"\"\"
    result = divide_numbers(10, 2)
    assert result == 5.0

"""
            elif bug.name == "off_by_one":
                code += f"""def test_off_by_one_{test_id}():
    \"\"\"Test off-by-one errors.\"\"\"
    result = get_element([1, 2, 3], 0)
    assert result == 1

"""
            elif bug.name == "null_reference":
                code += f"""def test_null_reference_{test_id}():
    \"\"\"Test null reference handling.\"\"\"
    result = process_list([1, 2, 3])
    assert result == 6

"""
            elif bug.name == "wrong_logic":
                code += f"""def test_wrong_logic_{test_id}():
    \"\"\"Test logical errors.\"\"\"
    result = is_even(4)
    assert result == True

"""
            
            test_id += 1
        
        return code

    # Bug generation methods
    
    def _gen_undefined_variable(self, idx: int) -> str:
        """Generate undefined variable bug."""
        var_name = random.choice(['x', 'y', 'z', 'temp', 'value'])
        return f"""def add_numbers(a, b):
    \"\"\"Bug: uses undefined variable {var_name}.\"\"\"
    return a + b + {var_name}  # {var_name} is not defined!
"""

    def _gen_type_mismatch(self, idx: int) -> str:
        """Generate type mismatch bug."""
        return """def multiply_values(a, b):
    \"\"\"Bug: tries to multiply string and int.\"\"\"
    return "result: " + (a * b)  # String concatenation with int
"""

    def _gen_missing_return(self, idx: int) -> str:
        """Generate missing return bug."""
        return """def divide_numbers(a, b):
    \"\"\"Bug: missing return statement.\"\"\"
    result = a / b
    # Missing: return result
"""

    def _gen_off_by_one(self, idx: int) -> str:
        """Generate off-by-one error."""
        return """def get_element(lst, index):
    \"\"\"Bug: off-by-one error in list access.\"\"\"
    return lst[index + 1]  # Should be lst[index]
"""

    def _gen_null_reference(self, idx: int) -> str:
        """Generate null reference bug."""
        return """def process_list(items):
    \"\"\"Bug: accesses None.\"\"\"
    result = None
    for item in items:
        result = result + item  # result is None!
    return result
"""

    def _gen_wrong_logic(self, idx: int) -> str:
        """Generate logical error bug."""
        return """def is_even(n):
    \"\"\"Bug: wrong logic for even check.\"\"\"
    return n % 2 == 1  # Should be n % 2 == 0
"""

    def _gen_infinite_loop(self, idx: int) -> str:
        """Generate infinite loop bug."""
        return """def sum_to_n(n):
    \"\"\"Bug: infinite loop.\"\"\"
    total = 0
    i = 0
    while i < n:
        total += i
        # i is never incremented!
    return total
"""

    def _gen_import_error(self, idx: int) -> str:
        """Generate import error."""
        return """def use_math():
    \"\"\"Bug: uses math without importing.\"\"\"
    return math.sqrt(16)  # math not imported
"""

    def _gen_indentation_error(self, idx: int) -> str:
        """Generate indentation error."""
        return """def check_value(x):
    \"\"\"Bug: incorrect indentation.\"\"\"
    if x > 0:
    return "positive"  # Wrong indentation
    else:
        return "non-positive"
"""

    def _gen_scope_issue(self, idx: int) -> str:
        """Generate scope issue."""
        return """global_var = 10

def modify_global():
    \"\"\"Bug: tries to modify global without keyword.\"\"\"
    global_var = 20  # Creates local, doesn't modify global
    return global_var
"""

    def generate_batch(self, num_scenarios: int) -> List[Dict]:
        """
        Generate multiple scenarios.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario info dicts
        """
        scenarios = []
        for _ in range(num_scenarios):
            scenario = self.generate_scenario()
            scenarios.append(scenario)
        
        return scenarios

    def cleanup_scenario(self, scenario_dir: str):
        """
        Clean up scenario directory.
        
        Args:
            scenario_dir: Path to scenario directory
        """
        if os.path.exists(scenario_dir):
            shutil.rmtree(scenario_dir)

    def get_statistics(self) -> Dict:
        """Get statistics about generated scenarios."""
        return {
            "total_scenarios_generated": self.scenario_id,
            "num_bug_templates": len(self.bug_templates),
            "seed": self.seed,
            "bug_types": [b.name for b in self.bug_templates],
        }