from example_solution import print_welcome as print_welcome
#!cut_imports!#
import sys
from io import StringIO

def test_print_welcome():
    captured_output = StringIO()
    sys.stdout = captured_output
    print_welcome()
    sys.stdout = sys.__stdout__
    result = captured_output.getvalue().strip()
    assert result == "Welcome to Activity Tracker", "The function should print exactly 'Welcome to Activity Tracker'."
