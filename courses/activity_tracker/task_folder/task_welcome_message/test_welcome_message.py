from example_solution import welcome_message as welcome_message
#!cut_imports!#
import sys
from io import StringIO

def test_welcome_message():
    captured_output = StringIO()
    sys.stdout = captured_output
    welcome_message()
    sys.stdout = sys.__stdout__
    captured_output = captured_output.getvalue().strip()
    assert captured_output == "Welcome to Study Tracker", "The function should print exactly 'Welcome to Study Tracker'."