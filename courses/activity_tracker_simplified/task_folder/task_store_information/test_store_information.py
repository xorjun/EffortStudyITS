from example_solution import remember_subject as remember_subject
#!cut_imports!#
import sys
from io import StringIO

def test_store_information():
    captured = StringIO()
    sys.stdout = captured
    remember_subject("Python")
    sys.stdout = sys.__stdout__
    assert captured.getvalue().strip() == "Python", "The function should print 'Python' when called with 'Python'."

    captured2 = StringIO()
    sys.stdout = captured2
    remember_subject("Mathematics")
    sys.stdout = sys.__stdout__
    assert captured2.getvalue().strip() == "Mathematics", "The function should print whatever subject is passed in."
