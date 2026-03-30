# README +++
from .cli_hello import Hello


def test_hello_world():
    # for the example above that reverses the name
    o = Hello('hello', 1)
    assert o.reversed_name == 'olleh'


# README ---


def test_hello_world():
    o = Hello('hello', 1)
    assert o.name == 'hello'
    assert o.count == 1
