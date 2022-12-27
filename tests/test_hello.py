from binance_history.hello import say_hello


def test_say_hello():
    word = "hello"
    assert say_hello() == "hello, stranger!"
    assert say_hello("xzmeng") == "hello, xzmeng!"
    assert say_hello("python") == "hello, python!"
