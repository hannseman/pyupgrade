import ast
import functools
from typing import Iterable
from typing import Tuple

from tokenize_rt import Offset

from pyupgrade._ast_helpers import ast_to_offset
from pyupgrade._data import register
from pyupgrade._data import State
from pyupgrade._data import TokenFunc
from pyupgrade._token_helpers import replace_name

PEP585_BUILTINS = frozenset((
    'Dict', 'FrozenSet', 'List', 'Set', 'Tuple', 'Type',
))


@register(ast.Attribute)
def visit_Attribute(
        state: State,
        node: ast.Attribute,
        parent: ast.AST,
) -> Iterable[Tuple[Offset, TokenFunc]]:
    if (
            (
                state.settings.min_version >= (3, 9) or (
                    state.in_annotation and
                    'annotations' in state.from_imports['__future__']
                )
            ) and
            isinstance(node.value, ast.Name) and
            node.value.id == 'typing' and
            node.attr in PEP585_BUILTINS
    ):
        func = functools.partial(
            replace_name,
            name=node.attr,
            new=node.attr.lower(),
        )
        yield ast_to_offset(node), func


@register(ast.Name)
def visit_Name(
        state: State,
        node: ast.Name,
        parent: ast.AST,
) -> Iterable[Tuple[Offset, TokenFunc]]:
    if (
            (
                state.settings.min_version >= (3, 9) or (
                    state.in_annotation and
                    'annotations' in state.from_imports['__future__']
                )
            ) and
            node.id in state.from_imports['typing'] and
            node.id in PEP585_BUILTINS
    ):
        func = functools.partial(
            replace_name,
            name=node.id,
            new=node.id.lower(),
        )
        yield ast_to_offset(node), func
