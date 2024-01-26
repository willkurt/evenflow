from evenflow import flowable

def test_flowable():
    @flowable('demo')
    def demo_function(a, b, c):
        return f"{a}{b}{c}"
    
    assert all([arg in demo_function.inputs 
                for arg in ['a','b','c']])

