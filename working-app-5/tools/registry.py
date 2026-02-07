TOOLS = {}

def register_tool(name):
    def wrapper(func):
        TOOLS[name] = func
        return func
    return wrapper

def get_tool(name):
    return TOOLS.get(name)
