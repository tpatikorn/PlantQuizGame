import tempfile
import os
from typing import List, Tuple

from models.db_models import TestCase


def check_equivalent(a: any, b: any, expected_type: type = float, tol: float = 1e-6):
    a = expected_type(a)
    b = expected_type(b)
    if expected_type == float:
        return abs(a - b) < tol
    else:
        return a == b


class SandboxPython:

    def __init__(self, base_restricted_functions=None, base_restricted_imports=None,
                 additional_restricted_functions=None, additional_restricted_imports=None):

        self.restricted_functions = base_restricted_functions or ['open', 'input']
        if additional_restricted_functions is not None:
            self.restricted_functions.extend(additional_restricted_functions)

        self.restricted_imports = base_restricted_imports or ['sys', 'os', 'subprocess']
        if additional_restricted_imports is not None:
            self.restricted_imports.extend(additional_restricted_imports)

    def construct_function(self, function_name):
        return lambda *_: self.raise_exception(function_name, *_)

    def raise_exception(self, func_name, *a):
        raise RuntimeError(f"can't call this function! '{func_name}' with arguments '{','.join(a)}'")

    def custom_import(self, name, custom_globals=None, custom_locals=None, fromlist=(), level=0):
        if name in self.restricted_imports:
            raise ImportError(f"Import of '{name}' module is not allowed")
        return __import__(name, custom_globals, custom_locals, fromlist, level)

    def run(self, code: str, test_cases: List[TestCase], result_only=False, verbose=False) -> \
            Tuple[List[Tuple[str, str, str]], int, int, int]:
        restricted_globals = {'__builtins__': {}}
        restricted_locals = {'__builtins__': {}}
        for fn in self.restricted_functions:
            restricted_globals[fn] = self.construct_function(fn)
        restricted_globals['__builtins__']['__import__'] = self.custom_import
        restricted_locals['__builtins__']['__import__'] = self.custom_import
        # Create a restricted environment
        results = []
        passed_count, failed_count, raised_count = 0, 0, 0
        print(len(test_cases))
        for test in test_cases:
            try:
                # Compile and execute the user's code within the restricted environment
                exec(code, restricted_globals, restricted_locals)
                # Execute the 'main' function with the provided arguments
                main_function = restricted_locals['main']
                current_output = main_function(*[float(_) for _ in test.test_inputs.split(',')])
                if check_equivalent(current_output, test.test_outputs) or result_only:
                    passed_count = passed_count + 1
                    if test.public:
                        if result_only:
                            results.append((test.test_inputs, "passed", current_output))
                        else:
                            results.append((test.test_inputs, "passed",
                                            f"Expected: {test.test_outputs}. Given: {current_output}"))
                else:
                    failed_count = failed_count + 1
                    if test.public:
                        results.append((test.test_inputs, "failed",
                                        f"Expected: {test.test_outputs}. Given: {current_output}"))
            except Exception as e:
                if verbose:
                    import traceback
                    print(traceback.format_exc())
                raised_count = raised_count + 1
                if test.public:
                    results.append((test.test_inputs, "raised", f"{type(e).__name__}: {str(e)}"))
        return results, passed_count, failed_count, raised_count


if __name__ == "__main__":
    sb = SandboxPython()
    # Python code as text
    test_code1 = """
import random
def main(arg):
    with open("app.py") as p:
        for l in p:
            print(l)
        return arg * 2
    """
    tc1 = TestCase(id=0, problem_id=0, test_inputs='5', test_outputs='10', public=True, active=True, problem=None)
    tc2 = TestCase(id=0, problem_id=0, test_inputs='6', test_outputs='12', public=True, active=True, problem=None)
    tc3 = TestCase(id=0, problem_id=0, test_inputs='7', test_outputs='14', public=False, active=True, problem=None)

    result = sb.run(code=test_code1, test_cases=[tc1, tc2, tc3])
    print(*result, sep="\n")
    test_code2 = """
def main(arg):
    return arg +5
    """
    sb2 = SandboxPython()
    result = sb2.run(code=test_code2, test_cases=[tc1, tc2, tc3])
    print(*result, sep="\n")
