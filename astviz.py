"""A module to fetch and vizualize Python AST"""

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


def parse_inspect(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], str):
            p_func = ast.parse(args[0])
        else:
            _func = inspect.getsource(args[0])
            p_func = ast.parse(_func)
        de_parsed = method(p_func, **kwargs)
        json_parsed = json.loads(de_parsed)

        return json_parsed

    return wrapper


@parse_inspect
def ast_json(node):
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
    try:
        for field in node._fields:
            yield field, getattr(node, field)
    except AttributeError:
        yield


def key_append(value, dictionary):
    esc_keys = ('module', 'n', 's', 'id', 'name', 'attr', 'arg')
    for i in esc_keys:
        if not isinstance(dict.get(dictionary, i), type(None)):
            value = f"{value}\n{i}: {dictionary[i]}"

    return value


def _grapher(graph, dictionary, _node_from='', hash_node='__init__'):
    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            if not _node_from:
                _node_from = value
                continue
            if key == '_PyType':
                value = key_append(value, dictionary)
                hash_node = draw(_node_from, value, graph=graph, parent_hash=hash_node)
                _node_from = value
                continue
            if isinstance(value, dict):
                _grapher(graph, value, _node_from=_node_from, hash_node=hash_node)
            if isinstance(value, list):
                [_grapher(graph, item, _node_from=_node_from, hash_node=hash_node) for item in value]


def draw_filter(method):
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


@draw_filter
def draw(parent_name, child_name, graph, parent_hash):
    parent_node = pydot.Node(parent_hash, label=parent_name, shape='box')
    child_hash = str(random.randint(1, 10e9))
    child_node = pydot.Node(child_hash, shape='box', label=child_name)
    graph.add_node(parent_node)
    graph.add_node(child_node)
    graph.add_edge(pydot.Edge(parent_node, child_node))

    return child_hash


def view_pydot(pdot):
    plt = Image(pdot.create_png())
    display(plt)


def main():
    graph = pydot.Dot(graph_type='digraph', strict=True, constraint=True, concentrate=True, splines='polyline')
    user_input = input('input a func name or declaration: ')
    try:
        if '.' in user_input:
            m, o = user_input.split('.')
            mod = importlib.import_module(m)
            met = getattr(mod, o)
        else:
            m = importlib.import_module(user_input)
            met = m
    except (ModuleNotFoundError):
        met = user_input
    _grapher(graph, ast_json(met))
    # view_pydot(graph)
    if graph.write_png('test.png'):
        print("Graph made successfully")


if __name__ == '__main__':
    main()
