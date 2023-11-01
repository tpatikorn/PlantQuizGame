import json
from functools import partial
from typing import List, Tuple, Dict
from pebble import ProcessPool
from models.db_models import TestCase, Problem


def check_equivalent(a: any, b: any, expected_type: type = float, tol: float = 1e-6):
    a = expected_type(a)
    b = expected_type(b)
    if expected_type == float:
        return abs(a - b) < tol
    else:
        return a == b


def convert(value_dict: Dict[str, any], type_dict: Dict[str, str]):
    for k, v in value_dict.items():
        match type_dict[k]:
            case "float":
                value_dict[k] = float(v)
            case "int":
                value_dict[k] = int(v)
            case "list_float":
                value_dict[k] = [float(_) for _ in v]
            case "list_int":
                value_dict[k] = [int(_) for _ in v]
            case _:
                value_dict[k] = str(v)
    return value_dict


class SandboxPython:

    def __init__(self, base_restricted_functions=None, base_restricted_imports=None,
                 additional_restricted_functions=None, additional_restricted_imports=None, timeout=1):
        self.timeout = timeout
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

    # run the code in the sandbox
    def test_target_code(self, target_test: TestCase, target_code, result_only):
        try:
            restricted_globals = {'__builtins__': {}}
            restricted_locals = {'__builtins__': {}}
            for fn in self.restricted_functions:
                restricted_globals[fn] = self.construct_function(fn)
            restricted_globals['__builtins__']['__import__'] = self.custom_import
            restricted_locals['__builtins__']['__import__'] = self.custom_import

            # Compile and execute the user's code within the restricted environment
            exec(target_code, restricted_globals, restricted_locals)
            # Execute the 'main' function with the provided arguments
            main_function = restricted_locals['main']
            input_format = json.loads(target_test.problem.input_format)
            test_inputs = convert(value_dict=json.loads(target_test.test_inputs), type_dict=input_format)
            current_output = main_function(**test_inputs)
            if check_equivalent(current_output, target_test.test_outputs) or result_only:
                if target_test.public:
                    if result_only:
                        return target_test.test_inputs, "passed", current_output
                    else:
                        return target_test.test_inputs, "passed", \
                            f"Expected: {target_test.test_outputs}. Given: {current_output}"
                else:
                    return None, "passed", None
            else:
                if target_test.public:
                    return target_test.test_inputs, "failed", \
                        f"Expected: {target_test.test_outputs}. Given: {current_output}"
                else:
                    return None, "failed", None
        except Exception as e:
            if target_test.public:
                return target_test.test_inputs, "raised", f"{type(e).__name__}: {str(e)}"
            else:
                return None, "raised", None

    # actually run the code against the TestCases
    def run(self, code: str, test_cases: List[TestCase], result_only=False) -> \
            Tuple[List[Tuple[str, str, str]], int, int, int, int]:

        # Create a restricted environment
        results = []
        passed_counts, failed_counts, raised_counts, timed_counts = 0, 0, 0, 0
        with ProcessPool() as pool:
            mapped_pool = pool.map(
                partial(self.test_target_code, target_code=code, result_only=result_only),
                test_cases, timeout=self.timeout)
            iterator = mapped_pool.result()
            while True:
                try:
                    test_inputs, status, message = next(iterator)
                    print(test_inputs, status, message)
                    if message is not None:
                        results.append((test_inputs, status, message))
                    if status == "passed":
                        passed_counts = passed_counts + 1
                    elif status == "failed":
                        failed_counts = failed_counts + 1
                    else:
                        raised_counts = raised_counts + 1
                except TimeoutError:
                    timed_counts = timed_counts + 1
                except StopIteration:
                    break
        print(results)
        return results, passed_counts, failed_counts, raised_counts, timed_counts


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
    p = Problem.create_mock_problem(problem_id=0, input_format='{"arg":"int"}', output_format="int")
    tc1 = TestCase(id=0, problem_id=0, test_inputs='{"arg":5}', test_outputs='10', public=True, active=True,
                   problem=p)
    tc2 = TestCase(id=0, problem_id=0, test_inputs='{"arg":6}', test_outputs='12', public=True, active=True,
                   problem=p)
    tc3 = TestCase(id=0, problem_id=0, test_inputs='{"arg":7}', test_outputs='14', public=False, active=True,
                   problem=p)

    result = sb.run(code=test_code1, test_cases=[tc1, tc2, tc3])
    print(*result, sep="\n")
    test_code2 = """
def main(arg):
    return arg +5
    """
    sb2 = SandboxPython()
    result = sb2.run(code=test_code2, test_cases=[tc1, tc2, tc3])
    print(*result, sep="\n")
