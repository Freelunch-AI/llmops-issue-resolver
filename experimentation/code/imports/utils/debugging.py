# from printing objects
def recursive_vars(obj):
    if isinstance(obj, list):
        return [recursive_vars(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: recursive_vars(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {key: recursive_vars(value) for key, value in vars(obj).items()}
    else:
        return obj