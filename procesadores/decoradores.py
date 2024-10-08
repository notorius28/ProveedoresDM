def multitab_property(value):
    def decorator(func):
        func.multitab = value
        return func
    return decorator

def dateontab_property(value):
    def decorator(func):
        func.dateontab = value
        return func
    return decorator