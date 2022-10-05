from typing import List

def exampleFunction() -> None:
    """Example function that prints out a message
    """
    print("This is a function that does something")

def exampleReturningFunction() -> str:
    """Example function that returns a value

    Returns:
        str: Example return value
    """
    return "This function returned a string"

def exampleComplexFunction(a: int, b: List[str]) -> str:
    """Example function that does something complex with a function

    Args:
        a (int): Number to insert between strings
        b (List[str]): Strings to combine

    Returns:
        str: String in b concatenated using the string representation of a
    """
    return f'{a}'.join(b)

def exampleEntryPoint() -> None:
    """Example entry point that exersizes all of the module's functions
    """
    exampleFunction()
    print(exampleReturningFunction())
    print(f"This is a complex function: {exampleComplexFunction(3, ['asdf', 'foo', 'bar'])}")

if __name__ == "__main__":
    exampleEntryPoint()