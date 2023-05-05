from inspect import signature

from quart import request


class ParsedArg:
    pass


def url_params(func):
    async def wrapper(*args, **kwargs):
        func_signature = signature(func)
        params = {
            k: v
            for k, v in request.args.items()
            if k in func_signature.parameters
            and func_signature.parameters[k].annotation == ParsedArg
        }
        return await func(*args, **params, **kwargs)

    setattr(wrapper, "__name__", func.__name__)

    return wrapper
