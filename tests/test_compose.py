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
    assert(True)