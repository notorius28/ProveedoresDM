def multitab_property(value):
    def decorator(func):
        func.multitab = value
        return func
    return decorator