# -*- coding: utf-8 -*-
"""Arithmetic Expression Parser.

This module uses the py_expression_parser from AxiaCore S.A.S., found in
https://github.com/Axiacore/py-expression-eval. py_expression_parser is b ased on
js-expression-eval, by Matthew Crumley (email@matthewcrumley.com,
http://silentmatt.com/) https://github.com/silentmatt/js-expression-eval
Ported to Python and modified by Vera Mazhuga (ctrl-alt-delete@live.com,
http://vero4ka.info/)

"""
__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import itertools
import re
from typing import Any, Dict, Match, Optional
import py_expression_eval
from nemoa.base import stype
from nemoa.types import AnyOp

OptVars = Optional[stype.Frame]
Expr = Any # TODO: Use py_expression_eval.Expression when typeshed is ready

def parse(expr: str, variables: OptVars = None) -> Expr:
    """ """
    if variables:
        vmap = get_var_mapping(expr, variables)
        expr = substitute(expr, vmap)

    return py_expression_eval.Parser().parse(expr).simplify({})

def get_var_mapping(expr: str, variables: OptVars = None) -> dict:
    """ """
    if not variables:
        return {}

    # Create an operator that checks, if a given variable name <var> is
    # already occupied by the expression. Thereby ignore appearances within
    # quoted (single or double) terms.
    quoted = "\"[^\"]+\"|'[^']+'" # RegEx for quoted terms
    raw = quoted + "|(?P<var>{var})" # Unformated RegEx for matches
    fmt: AnyOp = lambda var: raw.format(var=re.escape(var))
    matches: AnyOp = lambda var: re.finditer(fmt(var), expr)
    hit: AnyOp = lambda obj: obj.group('var') # Test if match is a var
    occupied: AnyOp = lambda var: any(map(hit, matches(var)))

    # Use the operator to create a field mapping from the set of field IDs
    # in the frame to valid variable names.
    fields = set(variables)
    mapping: Dict[stype.FieldID, str] = {}
    var_counter = itertools.count()
    next_var: AnyOp = lambda: 'X{i}'.format(i=next(var_counter))
    for field in fields:
        if isinstance(field, str) and field.isidentifier():
            mapping[field] = field
            continue
        var_name = next_var()
        while occupied(var_name):
            var_name = next_var()
        mapping[field] = var_name

    # Create and return variable mapping
    get_var: AnyOp = lambda field: mapping.get(field, '')
    return dict(zip(variables, map(get_var, variables)))

def substitute(expr: str, mapping: dict) -> str:
    """ """
    # Declare replacement function
    def repl(mo: Match) -> str:
        if mo.group('var'):
            return mapping.get(mo.group('var'), mo.group('var'))
        if mo.group('str2'):
            return mo.group('str2')
        return mo.group('str1')

    # Build operator that creates an regex pattern for a given field ID
    re_str1 = "(?P<str1>\"[^\"]+\")" # RegEx for double quoted terms
    re_str2 = "(?P<str2>'[^']+')" # RegEx for single quoted terms
    re_var = "(?P<var>{var})" # Unformated RegEx for variable
    raw = '|'.join([re_str1, re_str2, re_var]) # Unformated RegEx
    pattern: AnyOp = lambda var: raw.format(var=re.escape(var))

    # Iterate all field ids and succesively replace invalid variable names
    new_expr = expr
    for field, var in mapping.items():
        if field == var:
            continue
        new_expr = re.sub(pattern(field), repl, new_expr)

    return new_expr
