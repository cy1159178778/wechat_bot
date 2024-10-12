current_plugins = []


def append_plugin(item):

    def decorator(func):
        item.insert(1, func)
        current_plugins.append(item)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def on_regex(pattern, priority=1, block=False, chat_level=1):
    item = [priority, "on_regex", pattern, block, chat_level]
    return append_plugin(item)


def on_full_match(pattern, priority=1, block=False, chat_level=1):
    item = [priority, "on_full_match", pattern, block, chat_level]
    return append_plugin(item)
