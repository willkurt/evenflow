from evenflow import flowable, compose_flow
from evenflow.compose import flow_topo_sort
from itertools import permutations
"""
Each test here tests a suite of behaviors against a DAG,
rather than testing each functionality seperately.
"""

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

