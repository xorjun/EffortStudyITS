from example_solution import welcome_message as welcome_message
#!cut_imports!#
import sys
from io import StringIO

def test_create_function():
    captured_output = StringIO()
    sys.stdout = captured_output
    welcome_message()
    sys.stdout = sys.__stdout__
    result = captured_output.getvalue().strip()
    assert result == "Welcome to Activity Tracker", "The function should print exactly 'Welcome to Activity Tracker'."
