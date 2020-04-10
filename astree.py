"""A module to visualize Python AST."""

import ast
import inspect
import functools
import importlib
import json
import random
import re
from _ast import AST
import pydot_ng as pydot
from IPython.display import Image, display


# ~~~~~~~~~~~~~~~~~~ PARSING AST OBJ TO JSON ~~~~~~~~~~~~~~~~~~

def ast_parse(method):
    """Decorator to parse user input to JSON-AST object."""
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], str):
            ast_obj = ast.parse(args[0])  # i.e. a dec or exp
        else:
            obj = inspect.getsource(args[0])  # i.e. a method
            ast_obj = ast.parse(obj)
        json_parsed = method(ast_obj, **kwargs)
        parsed = json.loads(json_parsed)

        return parsed

    return wrapper


@ast_parse
def json_ast(node):
    """Parse an AST object into JSON."""
    def _format(_node):
        if isinstance(_node, AST):
            fields = [('_PyType', _format(_node.__class__.__name__))]
            fields += [(a, _format(b)) for a, b in iter_fields(_node)]
            return '{ %s }' % ', '.join(('"%s": %s' % field for field in fields))
        if isinstance(_node, list):
            return '[ %s ]' % ', '.join([_format(x) for x in _node])
        if isinstance(_node, bytes):
            return json.dumps(_node.decode("utf-8"))

        return json.dumps(_node)

    return _format(node)


def iter_fields(node):
    """Get attributes of a node."""
    try:
        for field in node._fields:
            yield field, getattr(node, field)
    except AttributeError:
        yield


# ~~~~~~~~~~~~~~~~~~~~~~~~ DRAWING AST ~~~~~~~~~~~~~~~~~~~~~~~~~

def grapher(graph, ast_nodes, parent_node='', node_hash='__init__'):
    """Recursively parse JSON-AST object into a tree."""
    if isinstance(ast_nodes, dict):
        for key, node in ast_nodes.items():
            if not parent_node:
                parent_node = node
                continue
            if key == '_PyType':
                node = graph_detail(node, ast_nodes)  # get node detail for graph
                node_hash = draw(parent_node, node, graph=graph, parent_hash=node_hash)
                parent_node = node  # once a child now parent
                continue
            # parse recursively
            if isinstance(node, dict):
                grapher(graph, node, parent_node=parent_node, node_hash=node_hash)
            if isinstance(node, list):
                [grapher(graph, item, parent_node=parent_node, node_hash=node_hash) for item in node]


def graph_detail(value, ast_scope):
    """Retrieve node details."""
    detail_keys = ('module', 'n', 's', 'id', 'name', 'attr', 'arg')
    for key in detail_keys:
        if not isinstance(dict.get(ast_scope, key), type(None)):
            value = f"{value}\n{key}: {ast_scope[key]}"

    return value


def clean_node(method):
    """Decorator to eliminate illegal characters, check type, and\n
    shorten lengthy child and parent nodes."""
    def wrapper(*args, **kwargs):
        parent_name, child_name = tuple('_node' if node == 'node' else node for node in args)
        illegal_char = re.compile(r'[,\\/]$')
        illegal_char.sub('*', child_name)
        if not child_name:
            return
        if len(child_name) > 2500:
            child_name = '~~~DOCS: too long to fit on graph~~~'
        args = (parent_name, child_name)

        return method(*args, **kwargs)

    return wrapper


@clean_node
def draw(parent_name, child_name, graph, parent_hash):
    """Draw parent and child nodes. Create and return new hash\n
    key declared to a child node."""
    parent_node = pydot.Node(parent_hash, label=parent_name, shape='box')
    child_hash = str(random.randint(1, 10e9))  # create hash key
    child_node = pydot.Node(child_hash, label=child_name, shape='box')

    graph.add_node(parent_node)
    graph.add_node(child_node)
    graph.add_edge(pydot.Edge(parent_node, child_node))

    return child_hash


# For jupyter notebooks
def view_tree(pdot):
    """Display tree onto console."""
    tree = Image(pdot.create_png())
    display(tree)


def parse_input(_input):
    """Parse user input and return an AST-compatible object."""
    try:
        if '.' in _input:
            mod, met = _input.split('.')  # handle modules and methods
            module = importlib.import_module(mod)
            method = getattr(module, met)
        else:
            module = importlib.import_module(_input)  # handle modules
            method = module
    except (ModuleNotFoundError):
        method = _input  # handle dec, exp

    return method


def main():
    """Take user input and draw an AST.\n
    Save file as PNG."""
    graph = pydot.Dot(graph_type='digraph', strict=True, constraint=True,
                      concentrate=True, splines='polyline')
    user_input = input('Input a method name, expression, etc.: ')
    parsed_input = parse_input(user_input)

    grapher(graph, json_ast(parsed_input))
    # view_tree(graph)
    if graph.write_png('astree.png'):
        print("Graph made successfully")


if __name__ == '__main__':
    main()
