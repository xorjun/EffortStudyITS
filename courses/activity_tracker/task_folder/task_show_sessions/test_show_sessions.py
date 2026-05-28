from example_solution import show_sessions as show_sessions
#!cut_imports!#
import sys
from io import StringIO

def test_show_sessions():
    captured_output = StringIO()
    sys.stdout = captured_output
    show_sessions([["Mathematics", 45], ["Physics", 30]])
    sys.stdout = sys.__stdout__
    captured_output = captured_output.getvalue().strip()
    expected_output = "Subject: Mathematics, Duration: 45 minutes\nSubject: Physics, Duration: 30 minutes"
    assert captured_output == expected_output, "Print one formatted line for each session in the list."

    captured_output = StringIO()
    sys.stdout = captured_output
    show_sessions([])
    sys.stdout = sys.__stdout__
    assert captured_output.getvalue().strip() == "", "For an empty list, the function should not print any session lines."