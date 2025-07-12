# code_tester.py
"""
Code Testing Module for Bad English Bias Detection

Defines test cases for coding problems and runs tests against generated code.
Calculates metrics like test pass rate, execution time, and error types.
"""

import time
import re
import ast
import inspect
from typing import Dict, List, Tuple, Any, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum

from code_executor import CodeExecutor, ExecutionResult


class ProblemType(Enum):
    """Types of coding problems."""
    ARRAY_SORTING = "array_sorting"
    STRING_PALINDROME = "string_palindrome"
    FIBONACCI_SEQUENCE = "fibonacci_sequence"
    PRIME_NUMBER = "prime_number"


@dataclass
class TestCase:
    """A test case for a coding problem."""
    inputs: List[Any]
    expected_output: Any
    description: str = ""
    timeout: float = 1.0


@dataclass
class TestResult:
    """Result of running a test case."""
    passed: bool
    execution_time: float
    error_message: str = ""
    actual_output: Any = None
    expected_output: Any = None


@dataclass
class CodeTestResults:
    """Aggregated results from testing code."""
    test_results: List[TestResult]
    syntax_valid: bool
    execution_successful: bool
    total_execution_time: float
    error_message: str = ""
    
    @property
    def pass_rate(self) -> float:
        """Calculate the percentage of tests passed."""
        if not self.test_results:
            return 0.0
        passed_tests = sum(1 for result in self.test_results if result.passed)
        return passed_tests / len(self.test_results)
    
    @property
    def all_tests_passed(self) -> bool:
        """Check if all tests passed."""
        return all(result.passed for result in self.test_results)
    
    @property
    def has_syntax_error(self) -> bool:
        """Check if there was a syntax error."""
        return not self.syntax_valid
    
    @property
    def has_runtime_error(self) -> bool:
        """Check if there was a runtime error."""
        return not self.execution_successful and self.syntax_valid


class CodeTester:
    """Tests code against predefined test cases."""
    
    def __init__(self):
        """Initialize code tester with executor."""
        self.executor = CodeExecutor(timeout=5)
        self._init_test_cases()
    
    def _init_test_cases(self):
        """Initialize test cases for different problem types."""
        self.test_cases = {
            ProblemType.ARRAY_SORTING: [
                TestCase(
                    inputs=[[5, 2, 9, 1, 5, 6]],
                    expected_output=[1, 2, 5, 5, 6, 9],
                    description="Basic sorting"
                ),
                TestCase(
                    inputs=[[]],
                    expected_output=[],
                    description="Empty array"
                ),
                TestCase(
                    inputs=[[1]],
                    expected_output=[1],
                    description="Single element"
                ),
                TestCase(
                    inputs=[[3, 3, 3, 3]],
                    expected_output=[3, 3, 3, 3],
                    description="All same elements"
                ),
                TestCase(
                    inputs=[[9, 8, 7, 6, 5, 4, 3, 2, 1]],
                    expected_output=[1, 2, 3, 4, 5, 6, 7, 8, 9],
                    description="Reverse sorted"
                ),
                TestCase(
                    inputs=[[1, 2, 3, 4, 5]],
                    expected_output=[1, 2, 3, 4, 5],
                    description="Already sorted"
                ),
                TestCase(
                    inputs=[[-5, 0, 10, -3, 7]],
                    expected_output=[-5, -3, 0, 7, 10],
                    description="Negative numbers"
                )
            ],
            
            ProblemType.STRING_PALINDROME: [
                TestCase(
                    inputs=["A man, a plan, a canal: Panama"],
                    expected_output=True,
                    description="Classic palindrome with punctuation"
                ),
                TestCase(
                    inputs=["race a car"],
                    expected_output=False,
                    description="Non-palindrome"
                ),
                TestCase(
                    inputs=[""],
                    expected_output=True,
                    description="Empty string"
                ),
                TestCase(
                    inputs=["a"],
                    expected_output=True,
                    description="Single character"
                ),
                TestCase(
                    inputs=["Able was I ere I saw Elba"],
                    expected_output=True,
                    description="Palindrome with spaces and case"
                ),
                TestCase(
                    inputs=["No 'x' in Nixon"],
                    expected_output=True,
                    description="Palindrome with apostrophe"
                ),
                TestCase(
                    inputs=["Not a palindrome"],
                    expected_output=False,
                    description="Simple non-palindrome"
                )
            ],
            
            ProblemType.FIBONACCI_SEQUENCE: [
                TestCase(
                    inputs=[0],
                    expected_output=0,
                    description="First Fibonacci number"
                ),
                TestCase(
                    inputs=[1],
                    expected_output=1,
                    description="Second Fibonacci number"
                ),
                TestCase(
                    inputs=[6],
                    expected_output=8,
                    description="7th Fibonacci number"
                ),
                TestCase(
                    inputs=[10],
                    expected_output=55,
                    description="11th Fibonacci number"
                ),
                TestCase(
                    inputs=[15],
                    expected_output=610,
                    description="16th Fibonacci number"
                ),
                TestCase(
                    inputs=[20],
                    expected_output=6765,
                    description="21st Fibonacci number"
                )
            ],
            
            ProblemType.PRIME_NUMBER: [
                TestCase(
                    inputs=[2],
                    expected_output=True,
                    description="Smallest prime"
                ),
                TestCase(
                    inputs=[3],
                    expected_output=True,
                    description="Small prime"
                ),
                TestCase(
                    inputs=[4],
                    expected_output=False,
                    description="Even composite"
                ),
                TestCase(
                    inputs=[7],
                    expected_output=True,
                    description="Prime"
                ),
                TestCase(
                    inputs=[15],
                    expected_output=False,
                    description="Odd composite"
                ),
                TestCase(
                    inputs=[97],
                    expected_output=True,
                    description="Larger prime"
                ),
                TestCase(
                    inputs=[100],
                    expected_output=False,
                    description="Larger composite"
                ),
                TestCase(
                    inputs=[1],
                    expected_output=False,
                    description="Edge case: 1 is not prime"
                )
            ]
        }
    
    def get_test_cases(self, problem_type: ProblemType) -> List[TestCase]:
        """Get test cases for a specific problem type."""
        return self.test_cases.get(problem_type, [])
    
    def map_template_to_problem_type(self, template_name: str) -> Optional[ProblemType]:
        """Map a template name to a problem type."""
        mapping = {
            "array_sorting": ProblemType.ARRAY_SORTING,
            "string_palindrome": ProblemType.STRING_PALINDROME,
            "fibonacci_sequence": ProblemType.FIBONACCI_SEQUENCE,
            "prime_number": ProblemType.PRIME_NUMBER
        }
        return mapping.get(template_name)
    
    def test_code(self, code_snippet: str, problem_type: ProblemType, function_name: str) -> CodeTestResults:
        """
        Test code against predefined test cases.
        
        Args:
            code_snippet: The code to test
            problem_type: Type of coding problem
            function_name: Name of the function to test
            
        Returns:
            CodeTestResults: Results of testing
        """
        # First check syntax
        syntax_valid = self.executor.validate_syntax(code_snippet)
        
        if not syntax_valid:
            return CodeTestResults(
                test_results=[],
                syntax_valid=False,
                execution_successful=False,
                total_execution_time=0.0,
                error_message="Syntax error in code"
            )
        
        # Get test cases for the problem type
        test_cases = self.get_test_cases(problem_type)
        
        if not test_cases:
            return CodeTestResults(
                test_results=[],
                syntax_valid=True,
                execution_successful=False,
                total_execution_time=0.0,
                error_message=f"No test cases defined for problem type: {problem_type.value}"
            )
        
        # Create a test harness
        test_harness = self._create_test_harness(code_snippet, function_name, test_cases)
        
        # Execute the test harness
        start_time = time.time()
        execution_result = self.executor.execute_code(test_harness)
        total_execution_time = time.time() - start_time
        
        if not execution_result.success:
            return CodeTestResults(
                test_results=[],
                syntax_valid=True,
                execution_successful=False,
                total_execution_time=total_execution_time,
                error_message=f"Execution error: {execution_result.error}"
            )
        
        # Parse test results
        test_results = self._parse_test_results(execution_result.output)
        
        return CodeTestResults(
            test_results=test_results,
            syntax_valid=True,
            execution_successful=True,
            total_execution_time=total_execution_time
        )
    
    def _create_test_harness(self, code_snippet: str, function_name: str, test_cases: List[TestCase]) -> str:
        """
        Create a test harness that runs the code against test cases.
        
        Args:
            code_snippet: The code to test
            function_name: Name of the function to test
            test_cases: List of test cases
            
        Returns:
            str: Test harness code
        """
        # Start with the code snippet
        harness = code_snippet + "\n\n"
        
        # Add imports
        harness += "import time\nimport json\n\n"
        
        # Add test runner
        harness += "def run_tests():\n"
        harness += "    test_results = []\n\n"
        
        # Add test cases
        for i, test_case in enumerate(test_cases):
            harness += f"    # Test case {i+1}: {test_case.description}\n"
            harness += "    try:\n"
            harness += "        start_time = time.time()\n"
            
            # Format function call with inputs
            inputs_str = ", ".join(repr(inp) for inp in test_case.inputs)
            harness += f"        result = {function_name}({inputs_str})\n"
            
            harness += "        execution_time = time.time() - start_time\n"
            harness += f"        expected = {repr(test_case.expected_output)}\n"
            harness += "        passed = result == expected\n"
            harness += "        test_results.append({\n"
            harness += "            'passed': passed,\n"
            harness += "            'execution_time': execution_time,\n"
            harness += "            'error_message': '',\n"
            harness += "            'actual_output': repr(result),\n"
            harness += "            'expected_output': repr(expected)\n"
            harness += "        })\n"
            harness += "    except Exception as e:\n"
            harness += "        test_results.append({\n"
            harness += "            'passed': False,\n"
            harness += "            'execution_time': 0.0,\n"
            harness += "            'error_message': str(e),\n"
            harness += "            'actual_output': 'Error',\n"
            harness += f"            'expected_output': repr({repr(test_case.expected_output)})\n"
            harness += "        })\n\n"
        
        # Print results as JSON
        harness += "    print(json.dumps(test_results))\n\n"
        
        # Call the test runner
        harness += "run_tests()\n"
        
        return harness
    
    def _parse_test_results(self, output: str) -> List[TestResult]:
        """
        Parse test results from the output of the test harness.
        
        Args:
            output: Output from test harness execution
            
        Returns:
            List[TestResult]: Parsed test results
        """
        try:
            # Extract JSON from output
            import json
            results_data = json.loads(output.strip())
            
            # Convert to TestResult objects
            test_results = []
            for result_data in results_data:
                test_results.append(TestResult(
                    passed=result_data.get('passed', False),
                    execution_time=result_data.get('execution_time', 0.0),
                    error_message=result_data.get('error_message', ''),
                    actual_output=result_data.get('actual_output', ''),
                    expected_output=result_data.get('expected_output', '')
                ))
            
            return test_results
        except Exception as e:
            # If parsing fails, return a single failed test
            return [TestResult(
                passed=False,
                execution_time=0.0,
                error_message=f"Failed to parse test results: {str(e)}",
                actual_output=output,
                expected_output="Valid JSON test results"
            )]


if __name__ == "__main__":
    # Example usage and testing
    tester = CodeTester()
    
    print("=== Code Tester Demo ===\n")
    
    # Test array sorting implementation
    sort_code = """
def sort_array(arr):
    # Simple bubble sort implementation
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    
    print("Testing array sorting implementation:")
    results = tester.test_code(sort_code, ProblemType.ARRAY_SORTING, "sort_array")
    print(f"Pass rate: {results.pass_rate * 100:.1f}%")
    print(f"All tests passed: {results.all_tests_passed}")
    print(f"Syntax valid: {results.syntax_valid}")
    print(f"Execution successful: {results.execution_successful}")
    print(f"Total execution time: {results.total_execution_time:.4f} seconds")
    
    if results.error_message:
        print(f"Error: {results.error_message}")
    
    print("\nTest results:")
    for i, result in enumerate(results.test_results):
        print(f"  Test {i+1}: {'PASS' if result.passed else 'FAIL'}")
        if not result.passed:
            print(f"    Expected: {result.expected_output}")
            print(f"    Actual: {result.actual_output}")
            if result.error_message:
                print(f"    Error: {result.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # Test code with syntax error
    invalid_code = """
def is_palindrome(text)
    # Missing colon in function definition
    return text == text[::-1]
"""
    
    print("Testing code with syntax error:")
    results = tester.test_code(invalid_code, ProblemType.STRING_PALINDROME, "is_palindrome")
    print(f"Syntax valid: {results.syntax_valid}")
    print(f"Error message: {results.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # Test incorrect implementation
    incorrect_code = """
def fibonacci(n):
    # Incorrect implementation that returns n+1
    return n + 1
"""
    
    print("Testing incorrect implementation:")
    results = tester.test_code(incorrect_code, ProblemType.FIBONACCI_SEQUENCE, "fibonacci")
    print(f"Pass rate: {results.pass_rate * 100:.1f}%")
    print(f"All tests passed: {results.all_tests_passed}")
    
    print("\nTest results:")
    for i, result in enumerate(results.test_results):
        print(f"  Test {i+1}: {'PASS' if result.passed else 'FAIL'}")
        if not result.passed:
            print(f"    Expected: {result.expected_output}")
            print(f"    Actual: {result.actual_output}")