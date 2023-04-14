# -*- coding: utf-8 -*-
"""Implements the xonsh parser for Python v3.6."""
import xonsh.ast as ast
from xonsh.parsers.v35 import Parser as ThreeFiveParser
from xonsh.parsers.base import store_ctx, ensure_has_elts, lopen_loc


class Parser(ThreeFiveParser):
    """A Python v3.6 compliant parser for the xonsh language."""

    def p_comp_for(self, p):
        """comp_for : FOR exprlist IN or_test comp_iter_opt"""
        targs, it, p5 = p[2], p[4], p[5]
        targ = targs[0] if len(targs) == 1 else ensure_has_elts(targs)
        store_ctx(targ)
        # only difference with base should be the is_async=0
        comp = ast.comprehension(target=targ, iter=it, ifs=[], is_async=0)
        comps = [comp]
        p0 = {"comps": comps}
        if p5 is not None:
            comps += p5.get("comps", [])
            comp.ifs += p5.get("if", [])
        p[0] = p0

    def p_expr_stmt_annassign(self, p):
        """expr_stmt : testlist_star_expr COLON test EQUALS test"""
        p1 = p[1][0]
        lineno, col = lopen_loc(p1)
        if len(p[1]) > 1 or not isinstance(p1, ast.Name):
            loc = self.currloc(lineno, col)
            self._parse_error("only single target can be annotated", loc)
        store_ctx(p1)
        p[0] = ast.AnnAssign(
            target=p1,
            annotation=p[3],
            value=p[5],
            simple=1,
            lineno=lineno,
            col_offset=col,
        )
