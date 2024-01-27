from evenflow import flowable, compose_flow
from evenflow.compose import flow_topo_sort, build_exectuion_stages
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
    stages = build_exectuion_stages(components)
    # the stages are a list stages
    assert len(stages) == 1
    # each stage is a list of groups
    assert isinstance(stages[0],list)
    # each group is a list of functions
    assert isinstance(stages[0][0], list)
    assert callable(stages[0][0][0])
    assert type(stages)

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
        stages = build_exectuion_stages(components)
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
        stages = build_exectuion_stages(components)
        assert len(stages) == 3
        for stage in stages:
            assert isinstance(stage,list)
            for group in stage:
                assert isinstance(group,list)
                for item in group:
                    assert callable(item)
        assert stages[0][0].inputs[0] == 's_1'
        # oh are these also in the wrong order?!
        assert stages[-1][-1][-1].output == 'f'

