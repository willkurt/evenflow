from inspect import (
    signature,
    Parameter,
    Signature
    )
from collections import defaultdict
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def get_nodes_children(dag):
    nodes = {
        node.output: node
        for node in dag
    }
    children = defaultdict(list)
    for node in dag:
        for input in node.inputs:
            children[input].append(node.output)
    return nodes, children

def build_execution_stages(dag_components):
    # I want a copy of this for now since
    # I'll be using .pop() 
    dag = [node for node in
           flow_topo_sort(dag_components)]
    nodes, children = get_nodes_children(dag)
    seen = {}
    start_nodes = top_level_args(dag)
    def non_start_inputs(node):
        return [val for val in node.inputs
                if not val in start_nodes]
    # internal since it requires all these 
    # variables
    def group_nodes(node, group,sid):
        # this need rethinking 
        # case where one start input and
        # one or more inputs
        # for just this example we'll
        # assume only 1 start
        if node.output in seen:
            return group
        if(len(children[node.output]) > 1):
            if any([seen.get(child,sid+1) >= sid for child in children[node.output]]):
                return group
        if all([input in start_nodes for input in node.inputs]):
            result = [node] + group
        elif len(non_start_inputs(node)) > 1:
            result = [node] + group
        elif len(children[non_start_inputs(node)[0]]) > 1:
            result = [node] + group
        else:
            # at this point we must have only one parent
            # and if you have one parent
            # you can be rolled up with it.
            result = group_nodes(
                nodes[non_start_inputs(node)[0]],
                [node]+group, sid)
        seen[node.output] = sid
        return result
    # this section build the stages
    # by walking the dag backwards
    stages = []
    stage_id = 0
    while(len(dag)) > 0:
        node = dag.pop()
        stage = []
        if (node.output in seen) and (len(non_start_inputs(node)) <= 1):
            continue
        elif len(non_start_inputs(node)) > 1:
            if not node.output in seen:
                stages.append([[node]])
                seen[node.output] = stage_id
                stage_id += 1
            for input in non_start_inputs(node):
                stage.append(group_nodes(nodes[input],[],stage_id))
        else:
            stage.append(group_nodes(node,[],stage_id))
        stages.append(stage)
        stage_id += 1
    # the end up in reverse order
    stages.reverse()
    return stages

def group_to_func(group):
    def func(env):
        for func in group:
            env[func.output] = call_with_args(func, env)
        return env
    # don't think this needs to be flowable...
    return func

def execute_stage(stage, env):
    with ThreadPoolExecutor(max_workers=10) as executor:
        # right now each stages is mutating the same dictionary..
        # which seems wrong/risky
        # maybe create a deep copy for each group?
        result_env = deepcopy(env)
        futures = [executor.submit(group_to_func(group), env) for group in stage]
        for future in as_completed(futures):
            result_env.update(future.result())
    return result_env

def execute_stages(stages, init_env):
    for stage in stages:
        init_env = execute_stage(stage, init_env)
    return init_env

def compose_flow(flow_elements):
    terminals, _ = get_terminals(flow_elements)
    # later we can handle the cases of multiple terminal
    assert len(terminals) == 1, "flow must terminate in exactly 1 result"
    terminal_output = terminals[0].output
    arg_names = top_level_args(flow_elements)
    stages = build_execution_stages(flow_elements)
    def f(*args, **kwargs):
        args_dict = unified_args(arg_names, args, kwargs)
        args_dict = execute_stages(stages, args_dict)
        return args_dict[terminal_output]
    f.inputs = arg_names
    f.output = terminal_output
    f.flowable = True
    f.__qualname__ = f"compute_{terminal_output}"
    params = [Parameter(arg, Parameter.POSITIONAL_OR_KEYWORD)
              for arg in arg_names]
    f.__signature__ = Signature(params)
    return f

def _compose_flow(flow_elements):
    terminals, _ = get_terminals(flow_elements)
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
    f.inputs = arg_names
    f.output = terminal_output
    f.flowable = True
    f.__qualname__ = f"compute_{terminal_output}"
    params = [Parameter(arg, Parameter.POSITIONAL_OR_KEYWORD)
              for arg in arg_names]
    f.__signature__ = Signature(params)
    return f