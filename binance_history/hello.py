def say_hello(name: str | None = None) -> str:
    msg: str
    if name:
        msg = f'hello, {name}!'
    else:
        msg = 'hello, stranger!'
    return msg
