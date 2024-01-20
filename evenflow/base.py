from inspect import signature


def flowable(output_name):
    """
    Essential decorator
    """
    def flow_f(func):
        # TODO: add check if already
        # flowable then return
        def f(*args, **kwargs):
            val = func(*args, **kwargs)
            return val
        f.__qualname__ = func.__name__
        f.__signature__ = signature(func)
        f.flowable = True
        f.inputs = [k for 
                    k in signature(func).parameters]
        f.output = output_name
        return f
    return flow_f

