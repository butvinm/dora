type StrAlias = str


def foo[T: StrAlias](x: T) -> T:
    return x
