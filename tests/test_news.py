# -*- coding: utf-8 -*-
"""Testing that news entries are well formed."""
import os
import re

import pytest

from xonsh.platform import scandir


NEWSDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "news")

CATEGORIES = frozenset(
    ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
)

single_grave_reg = re.compile(r"[^`]`[^`]+`[^`_]")


def check_news_file(fname):
    name = fname.name
    with open(fname.path) as f:
        lines = f.read().splitlines()
    form = ""
    for i, l in enumerate(lines):
        # search the graves
        if "`" in l and single_grave_reg.search(l):
            pytest.fail(
                f"{name}:{i + 1}: single grave accents are not valid rst",
                pytrace=True,
            )

        # determine the form of line
        if l.startswith("**"):
            cat = l[2:].rsplit(":")[0]
            if cat not in CATEGORIES:
                pytest.fail(
                    "{}:{}: {!r} not a proper category "
                    "must be one of {}"
                    "".format(name, i + 1, cat, list(CATEGORIES)),
                    pytrace=True,
                )
            form += "3" if l.endswith("None") else "2"
        elif l.startswith("* <news item>"):
            form += "4"
        elif l.startswith("* ") or l.startswith("- ") or l.startswith("  "):
            form += "1"
        elif l.strip() == "":
            form += "0"
        else:
            pytest.fail(f"{name}:{i + 1}: invalid rst", pytrace=True)
    # The file should have:
    #   empty lines around categories
    #   at least one content line in a non null category
    reg = re.compile(r"^(3(0|$)|20(1|4)(1|0|4)*0|204$)+$")
    if not reg.match(form):
        print(form)
        pytest.fail(f"{name}: invalid rst", pytrace=True)


@pytest.mark.parametrize("fname", list(scandir(NEWSDIR)))
def test_news(fname):
    base, ext = os.path.splitext(fname.path)
    assert "rst" in ext
    check_news_file(fname)
