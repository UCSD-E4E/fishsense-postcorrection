from examplePackage import exampleModule

def test_exampleFunction():
    """Tests that the example function completes successfully
    """
    exampleModule.exampleFunction()
    assert(True)

def test_exampleReturn():
    """Tests that the function returns something
    """
    retval = exampleModule.exampleReturningFunction()
    assert(retval is not None)