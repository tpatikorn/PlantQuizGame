import tempfile
import os


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

    def custom_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        if name in self.restricted_imports:
            raise ImportError(f"Import of '{name}' module is not allowed")
        return __import__(name, globals, locals, fromlist, level)

    def run(self, code, test_inputs, test_outputs, verbose=False):
        restricted_globals = {'__builtins__': {}}
        restricted_locals = {'__builtins__': {}}
        for fn in self.restricted_functions:
            restricted_globals[fn] = self.construct_function(fn)
        # Create a restricted environment
        test_passed = []
        test_failed = []
        test_raised = []
        for test, expected_output in zip(test_inputs, test_outputs):
            try:
                # Compile and execute the user's code within the restricted environment
                exec(code, restricted_globals, restricted_locals)
                # Execute the 'main' function with the provided arguments
                main_function = restricted_locals['main']
                if main_function(*test) == expected_output:
                    test_passed.append(test)
                else:
                    test_failed.append(test)
            except Exception:
                if verbose:
                    import traceback
                    print(traceback.format_exc())
                test_raised.append(test)
        return test_passed, test_failed, test_raised


if __name__ == "__main__":
    sb = SandboxPython()
    # Python code as text
    test_code1 = """
def main(arg):
    with open("app.py") as p:
        for l in p:
            print(l)
        return arg * 2
    """
    passed, failed, raised = sb.run(test_code1, test_inputs=[[5], [6], [7]], test_outputs=[10, 12, 14])
    print(passed)
    print(failed)
    print(raised)
    test_code2 = """
def main(arg):
    return arg * 2
    """
    sb2 = SandboxPython()
    passed, failed, raised = sb2.run(test_code2, test_inputs=[[5], [6], [7]], test_outputs=[10, 12, 14])
    print(passed)
    print(failed)
    print(raised)
