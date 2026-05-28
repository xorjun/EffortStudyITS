from example_solution import remember_subject as remember_subject
#!cut_imports!#

def test_remember_subject():
    assert remember_subject("Mathematics") == "Mathematics", "Return the subject that was stored in the variable."
    assert remember_subject("Computer Science") == "Computer Science", "The function should work for different subject names."