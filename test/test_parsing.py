#!/usr/bin/env python3

import pytest

import pathlib
test_root =pathlib.Path(__file__).parent.resolve()

import sys
sys.path.append(str(test_root.parent))

import pyrandr

filenames = ["a.txt", "b.txt"]
filenames = [
    test_root / "test-cases" / filename
    for filename in filenames
]


@pytest.mark.parametrize("filename", filenames)
def test_parse(filename):
    with open(filename) as f:
        text = f.read()
    screens = list(pyrandr.parse_screens(text.splitlines()))
    assert len(screens) > 0
