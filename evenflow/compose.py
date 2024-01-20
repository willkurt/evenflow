from inspect import signature

def get_inputs(flow_elements):
    inputs = set()
    for element in flow_elements:
        inputs = inputs.union(element.inputs)
    return inputs

def get_terminals(flow_elements):
    inputs = get_inputs(flow_elements)
    terminals = []
    rest = []
    for element in flow_elements:
        if element.output in inputs:
            rest.append(element)
        else:
            terminals.append(element)
    return terminals, rest

def get_outputs(flow_elements):
    return set([element.output for element in flow_elements])

def get_start_elements(flow_elements):
    outputs = get_outputs(flow_elements)
    start = []
    rest = []
    for element in flow_elements:
        if not any([input in outputs 
                    for input in element.inputs]):
            start.append(element)
        else:
            rest.append(element)
    return start, rest

def flow_topo_sort(flow_elements):
    sorted = []
    starting, rest = get_start_elements(flow_elements)
    while len(starting) > 0:
        sorted.append(starting[0])
        starting = starting[1:]
        start, rest = get_start_elements(rest)
        starting += start
    return sorted

def top_level_args(flow_elements):
    inputs = get_inputs(flow_elements)
    outputs = get_outputs(flow_elements)
    return list(inputs.difference(outputs))

def unified_args(arg_names, args, kwargs):
    for i in range(len(args)):
        kwargs[arg_names[i]] = args[i]
    return kwargs

def call_with_args(func, args_dict):
    params = signature(func).parameters
    kwargs = {
        k: v for k,v in args_dict.items()
        if k in params
    }
    return func(**kwargs)

def compose_flow(flow_elements):
    terminals, _ = get_terminals(flow_elements)
    print(terminals)
    # later we can handle the cases of multiple terminal
    assert len(terminals) == 1, "flow must terminate in exactly 1 result"
    terminal_output = terminals[0].output
    arg_names = top_level_args(flow_elements)
    exec_order_funcs = flow_topo_sort(flow_elements)
    def f(*args, **kwargs):
        args_dict = unified_args(arg_names, args, kwargs)
        for func in exec_order_funcs:
            args_dict[func.output] = call_with_args(func, args_dict)
        return args_dict[terminal_output]
    f.flowable = True
    # Add logic for making it a flow
    return f