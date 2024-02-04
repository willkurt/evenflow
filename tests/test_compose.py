from evenflow import flowable, compose_flow
from evenflow.compose import flow_topo_sort, build_execution_stages
from itertools import permutations
"""
Each test here tests a suite of behaviors against a DAG,
rather than testing each functionality seperately.
"""

def test_dag_0a():
    """
    S_1
     |
     A
    """
    @flowable('a')
    def a(s_1):
        return 'a'
    components = [a]
    comp_func = compose_flow(components)
    assert comp_func.inputs[0] == 's_1'
    assert comp_func.output == 'a'
    stages = build_execution_stages(components)
    # the stages are a list stages
    assert len(stages) == 1
    # each stage is a list of groups
    assert isinstance(stages[0],list)
    # each group is a list of functions
    assert isinstance(stages[0][0], list)
    assert callable(stages[0][0][0])

def test_dag_0b():
    """
    S_1
     |
     A
     |
     B
    """
    @flowable('a')
    def a(s_1):
        return 'a'

    @flowable('b')
    def b(a):
        return 'b'
    components = [a,b]
    for perm in permutations(components):
        sorted_perm = flow_topo_sort(perm)
        assert sorted_perm.index(a) < sorted_perm.index(b)
        comp_func = compose_flow(perm)
        assert comp_func.inputs[0] == 's_1'
        assert comp_func.output == 'b'
        stages = build_execution_stages(components)
        assert len(stages) == 1
        assert stages[-1][-1][-1].output == 'b'
        assert isinstance(stages[0],list)
        # each group is a list of functions
        assert isinstance(stages[0][0], list)
        assert callable(stages[0][0][0])

def test_dag_0c():
    """
        S_1
         |
         A
        / \
       B   C
        \ /
         D
    """
    @flowable('a')
    def a(s_1):
        return 'a'
    @flowable('b')
    def b(a):
        return 'b'
    @flowable('c')
    def c(a):
        return 'c'
    @flowable('d')
    def d(b,c):
        return 'd'
    components = [a,b,c,d]
    for perm in permutations(components):
        sorted_perm = flow_topo_sort(perm)
        assert sorted_perm.index(a) < sorted_perm.index(b)
        assert sorted_perm.index(a) < sorted_perm.index(c)
        assert sorted_perm.index(b) < sorted_perm.index(d)
        assert sorted_perm.index(c) < sorted_perm.index(d)
        comp_func = compose_flow(perm)
        assert comp_func.inputs[0] == 's_1'
        assert comp_func.output == 'd'
        stages = build_execution_stages(components)
        assert len(stages) == 3
        assert stages[-1][-1][-1].output == 'd'
        assert isinstance(stages[0],list)
        # each group is a list of functions
        assert isinstance(stages[0][0], list)
        assert callable(stages[0][0][0])

def test_dag_0d():
    """
    S_1  S_2
     |    |
     A    |
      \  /
        B
        |
        C
    """ 
    @flowable('a')
    def a(s_1):
        return 'a'
    @flowable('b')
    def b(a,s_2):
        return 'b'
    @flowable('c')
    def c(b):
        return 'c'
    components = [a,b,c]
    for perm in permutations(components):
        sorted_perm = flow_topo_sort(perm)
        assert sorted_perm.index(a) < sorted_perm.index(b)
        assert sorted_perm.index(a) < sorted_perm.index(b)
        assert sorted_perm.index(b) < sorted_perm.index(c)
        comp_func = compose_flow(perm)
        assert all(val in ['s_1', 's_2'] for val in comp_func.inputs)
        assert comp_func.output == 'c'
        stages = build_execution_stages(components)
        assert len(stages) == 1
        assert stages[-1][-1][-1].output == 'c'
        assert isinstance(stages[0],list)
        # each group is a list of functions
        assert isinstance(stages[0][0], list)
        assert callable(stages[0][0][0])


def test_dag_1():
    """
       S_1
       / \
      A   B
      |   |
      C   |
      \   |
        D
    """
    @flowable('a')
    def a(s_1):
        return 'a'
    
    @flowable('b')
    def b(s_1):
        return 'b'
    
    @flowable('c')
    def c(a):
        return 'c'
    
    @flowable('d')
    def d(c,b):
        return 'd'
    
    components = [a,b,c,d]

    for perm in permutations(components):
        sorted_perm = flow_topo_sort(perm)
        assert sorted_perm.index(a) < sorted_perm.index(c)
        assert sorted_perm.index(c) < sorted_perm.index(d)
        assert sorted_perm.index(b) < sorted_perm.index(d)
        comp_func = compose_flow(perm)
        assert comp_func.inputs[0] == 's_1'
        assert comp_func.output == 'd'
        stages = build_execution_stages(components)
        # assert len(stages) == ?
        assert stages[-1][-1][-1].output == 'd'

def test_dag_2():
    """
        S_1
        |
        A
       / \
      B   |
      |   C
      D   |
       \ /
        E
        |
        F
    """
    @flowable('a')
    def a(s_1):
        return 'a'

    @flowable('b')
    def b(a):
        return 'b'

    @flowable('c')
    def c(a):
        return 'c'

    @flowable('d')
    def d(b):
        return 'd'

    @flowable('e')
    def e(d,c):
        return 'e'

    @flowable('f')
    def f(e):
        return 'f'
    
    
    components = [a, b, c, d, e, f]

    for perm in permutations(components):
        sorted_perm = flow_topo_sort(perm)
        assert sorted_perm.index(a) < sorted_perm.index(c)
        assert sorted_perm.index(c) < sorted_perm.index(d)
        assert sorted_perm.index(b) < sorted_perm.index(d)
        comp_func = compose_flow(perm)
        assert comp_func.inputs[0] == 's_1'
        assert comp_func.output == 'f'
        stages = build_execution_stages(components)
        assert len(stages) == 3
        for stage in stages:
            assert isinstance(stage,list)
            for group in stage:
                assert isinstance(group,list)
                for item in group:
                    assert callable(item)
        assert stages[0][0][0].inputs[0] == 's_1'
        # oh are these also in the wrong order?!

        assert stages[-1][-1][-1].output == 'f'


def test_dag_3():
    """
        S_1  S_2
         |    |
         A    |
          \  /
         _ B
       /  /|\ 
      C  D E F
      |  | | |
      |  \ / |    
      |   G  H
       \   \ |
        \   I
         \  |
           J
    """
    @flowable('a')
    def a(s_1):
        return 'a'
    @flowable('b')
    def b(a,s_2):
        return 'b'
    @flowable('c')
    def c(b):
        return 'c'
    @flowable('d')
    def d(b):
        return 'd'
    @flowable('e')
    def e(b):
        return 'e'
    @flowable('f')
    def f(b):
        return 'f'
    @flowable('g')
    def g(d,e):
        return 'g'
    @flowable('h')
    def h(f):
        return 'h'
    @flowable('i')
    def i(g, h):
        return 'i'
    @flowable('j')
    def j(c,i):
        return 'j'
    components = [d,e,f,a,b,c,g,h,i,j]
    sorted_perm = flow_topo_sort(components)
    assert sorted_perm.index(a) < sorted_perm.index(b)
    assert sorted_perm.index(b) < sorted_perm.index(c)
    assert sorted_perm.index(b) < sorted_perm.index(d)
    assert sorted_perm.index(b) < sorted_perm.index(e)
    assert sorted_perm.index(b) < sorted_perm.index(f)
    comp_func = compose_flow(components)
    # this is interesting... not sure what
    # is correct... but they should potentially
    # be in topological order?
    assert comp_func.inputs[0] in ['s_1', 's_2']
    assert comp_func.output == 'j'
    stages = build_execution_stages(components)
    assert len(stages) == 5
    for stage in stages:
        assert isinstance(stage,list)
        for group in stage:
            assert isinstance(group,list)
            for item in group:
                assert callable(item)
    assert stages[0][0][0].inputs[0] == 's_1'
    # oh are these also in the wrong order?!

    assert stages[-1][-1][-1].output == 'j'

# Concurrency tests
def test_run_concur():
    import time
    from datetime import datetime
    """
        1
       / \
      2   3
       \ /
        4  
    """
    @flowable('x1')
    def step1(s):
        time.sleep(1)
        return 1 + s

    @flowable('x2')
    def step2(x1):
        time.sleep(1)
        return 1 + x1

    @flowable('x3')
    def step3(x1):
        time.sleep(1)
        return 1 + x1

    @flowable('x4')
    def step4(x2,x3):
        time.sleep(1)
        return 1 + x2 + x3
    

    components = [step1,step2,step3,step4]
    f_concur = compose_flow(components)
    start_t = datetime.now()
    result = f_concur(0)
    end_t = datetime.now()
    ts = (end_t - start_t).total_seconds()
    assert result == 5
    # only possible with concurreny happening
    assert ts < 3.10


def test_se_example():
    import numpy as np
    # Step 1
    @flowable('sample_mean')
    def calc_mean(samples):
        return np.mean(samples)

    # Step 2
    @flowable('square_distance')
    def calc_squares_distance(sample_mean, samples):
        return (samples-sample_mean)**2

    # Step 3
    @flowable('sum_of_squares')
    def calc_sum(square_distance):
        return np.sum(square_distance)

    # Step 4a - we'll need to get the n_samples (this will be useful in a bit)
    @flowable('n_samples')
    def calc_n_samples(samples):
        return len(samples)

    # Step 4b - This is just the calculation of the variance
    @flowable('var')
    def variance(sum_of_squares, n_samples):
            return sum_of_squares/n_samples
        
    # Step 5 - This is just calcuating the standard deviation from the variance
    @flowable('std_dev')
    def standard_deviation(var):
        return np.sqrt(var)

    @flowable('json_resp')
    def mock_endpoint(se):
        import json
        return json.dumps({
            'standard_error': se
        })

    @flowable('se')
    def standard_error(std_dev, n_samples):
        return std_dev/np.sqrt(n_samples)

    endpoint_components = [
        mock_endpoint, calc_mean, calc_squares_distance, standard_error, 
        calc_sum, calc_n_samples, variance, standard_deviation
    ]

    endpoint_v1 = compose_flow(endpoint_components)
    import json
    result = json.loads(endpoint_v1([1,2,3,4]))
    assert np.abs(result['standard_error'] - 0.5590169943749475) < 0.01
