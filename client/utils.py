"""A collection of various utility functions."""


def insert_str(target: str, string: str, index: int):
    """Insert a string into another string"""
    return target[:index] + string + target[index:]


def del_char(string: str, index: int):
    """Remove a character from a string"""
    return string[: index - 1] + string[index:]


def divide_size(size, chunk_size):
    """
    I can't explain this one so here you go:

    Example:
        params:
            size: 1234
            chunk_size: 100
        yields:
            100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 34
    """
    while size > 0:
        yield min(size, chunk_size)
        size -= min(size, chunk_size)
