# astree
### Visualize abstract syntax trees of methods, declarations, expressions, etc.

```astree.py``` combines the Python <a href=https://docs.python.org/3.8/library/ast.html>```ast```</a> module with
<a href=https://github.com/pydot/pydot-ng>```pydot_ng```</a> to draw abstract syntax trees specified in DOT language scripts.
An <a href=https://en.wikipedia.org/wiki/Abstract_syntax_tree> abstract syntax tree</a> is a tree representation of the abstract
syntactic structure of source code written in a programming language (e.g. Python).<br>
<hr>
  
<b>Jumpstart</b> -- running the program:
1) Clone repository
2) ```$ pip install -r requirements.txt```<br>
3) ```$ python astree.py```

Input modules, methods, declarations, statements, expressions, etc.<br>
View video example <a href="https://i.imgur.com/C43Mn6p.mp4">here</a>.<br>

For example, let's look at the ```requests.get``` method:<br>
```>>> Input a method name, expression, etc.:```<br>
```requests.get```<br>

<p align = 'center'>
<img src=https://i.imgur.com/41FcAwg.png alt="AST visualize requests.get"
    width=800><br>
</p>
<br>
Note: please report bugs to <a href="https://github.com/irahorecka/astree/issues">issues</a>.
