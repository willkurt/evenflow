# Even Flow: Creating Self-Organizing Python Functions

"Thoughts arrive like butterflies..."

Even flow is an attempt to create a frame work for *self-organizng* python code composed from a series of function with clearly defined inputs and a single output. The programmer only has to concern themselves with defining tiny pieces of a larger program and `evenflow` will automatically compose that program in the form of another `flowable` function.

The original intent of this package was to create a frame work for compostion **LLM Agents** but it turned otu it works for simple python functions as well.

## Usage

`evenflow` only uses two essential functions: 

- `flowable` a dectorator to annotate your functions
- `compose_flow` which takes a list of *flowable* functions and builds a new, also flowble, function.

## Example 1: Hello World

In this example we'll create a function that will print "Hello <name> in the <department>!" from an email address. The email address can be used to look up the `name` and `department` seperately. This, fo course, is a toy problem, but it is meant to be similar to a common pattern that comes up with using Retrieval Augmented Generation (RAG) using LLM agents.

Let's start by thinking about our program from a top-down perspective, something that is made very easy by `evenflow`. We know in the end we want to take two inputs and return an output. Here is our base function with uses the `flowable` decorator:

```python
from evenflow import flowable, compose_flow

@flowable('hello_statement')
def say_hello(name, department):
    return f"Hello {name} from the {department} dept!"
```
Names are important for `evenflow`, in our decorator we will specify the return value of our flowable function. This name can should match the parameters taken by other arguments.

Next let's build a simple function that looks up a name based on a email address:

```python
@flowable('name')
def lookup_name(email):
    name_dict = {
        "will@countbayesie.com": "Will Kurt",
        "emil@notreal.xyz": "Emil Cioran",
        "sogol@daumal.net": "Professor Sogol"
    }
    return name_dict.get(email,"unknown")
```

When creating a `flowable` function the only the the programmer needs to worry about is being consistent with names of inputs (parameters) and output (argument to flowable).

Next we'll build a similar function for looking updepartment:

```python
@flowable('department')
def lookup_department(email):
    dept_dict = {
        "will@countbayesie.com": "English",
        "emil@notreal.xyz": "Philosophy",
        "sogol@daumal.net": "Logic"
    }
    return dept_dict.get(email,"unknown")
```

Now we need only one other function, `compose_flow`, to put this all together to make a `hello_world` function. `compose_flow` just takes in a list of function you want to use a building block and *automatically assembles them into another function*. The order *does not matter* since `evenflow` figures out the necessary order for you.

```python
hello_world = compose_flow([say_hello, lookup_name, lookup_department])
```

We know have a regular Python function, self-assembled from flowable parts:

```python
hello_world("will@countbayesie.com")

# 'Hello Will Kurt from the English dept!'
```

When building complex systems of interacting agents (or really just functions) it can be hard to imagine the *entire system*, but often easy to know what inputs you want at each stage. `evenflow` makes buiding complex, agent based systems easier by leaving you to only worry about the inputs and outputs at each section.
