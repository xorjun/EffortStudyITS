

execute_test_code = """
try:
    {test_name}()
    test_result = 1
    test_message = ""
except AssertionError as e:
    test_result = 0
    test_message = str(e)
    print(e)
"""

json_serialization = """
import json
def json_serialize(obj):
    if isinstance(obj, np.ndarray):
        #return obj.tolist()
        return np.array2string(obj)
    return obj

print("##!serialization!##")
print(json.dumps({{{serialization_args}}}, default=json_serialize))
print("##!serialization!##")
"""

plt_dummy = """
class dummy_plt():
    def __init__(self):
        self.plot_args = []

    def plot(self, *args, **kwargs):
        self.plot_args.append({'args': args, 'kwargs': kwargs})

    def show(self):
        pass

plt = dummy_plt()
"""

printIO_capture = """
import sys as unsafe_sys_import
from sys import __stdout__
from io import StringIO
submission_captured_output = StringIO()
unsafe_sys_import.stdout = submission_captured_output
"""

printIO_release = """
unsafe_sys_import.stdout = __stdout__
submission_captured_output = submission_captured_output.getvalue().strip()
"""

def format_json_returns(return_args):
    return json_serialization.format(serialization_args=", ".join([f"'{arg}': {return_args[arg]}" for arg in return_args]))

def getExecutableString_function(test_code, test_name, submission_code):
    # enter all values to be returned as json here as {returnName: returnVariable}. Those need to be set somewhere in the code.
    return_args = {
        "test_message": "test_message",
        "test_result": "test_result",
    }
    code_strings = [
        printIO_capture,
        submission_code,
        printIO_release,
        test_code,
        execute_test_code.format(test_name=test_name),
        format_json_returns(return_args),
    ]
    return "\n".join(code_strings)

def getExecutableString_plotFunction(test_code, test_name, submission_code):
    # enter all values to be returned as json here as {returnName: returnVariable}. Those need to be set somewhere in the code.
    return_args = {
        "plot_args": "plt.plot_args",
        "test_result": "test_result",
    }
    code_strings = [
        plt_dummy,
        submission_code.strip("import matplotlib.pyplot as plt"),
        test_code,
        execute_test_code.format(test_name=test_name),
        "plot_args = plt.plot_args",
        format_json_returns(return_args),
    ]
    return "\n".join(code_strings)


# These are for Runs

def getExecutableString_runFunction(submission_code, function_name, run_arguments):
    return_args = {
        "run_result": "run_result",
    }
    code_strings = [
        submission_code,
        f"run_result = {function_name}(**{run_arguments})",
        format_json_returns(return_args),
    ]
    return "\n".join(code_strings)

def getExecutableString_runPrint(submission_code, function_name, run_arguments):
    code_strings = [
        submission_code,
        #f"run_result = {function_name}(**{run_arguments})",
    ]
    return "\n".join(code_strings)

def getExecutableString_runPlot(submission_code, function_name, run_arguments):
    return_args = {
        "run_result": "run_result",
        "plot_args": "plt.plot_args",
    }
    code_strings = [
        plt_dummy,
        submission_code.strip("import matplotlib.pyplot as plt"),
        f"run_result = {function_name}(**{run_arguments})",
        "plot_args = plt.plot_args",
        format_json_returns(return_args),
    ]
    return "\n".join(code_strings)