from example_solution import apply_mask as apply_mask
#!cut_imports!#
def test_apply_mask():
    # Test is arbitrary, but you should use assert.
    assert apply_mask("input1") == "something1", "Message1"
    assert apply_mask("input2") == "something2", "Message2"