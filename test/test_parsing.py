#!/usr/bin/env python3


import sys
sys.path.append("..")
import pyrandr
import pytest


filenames = ["a.txt", "b.txt"]


@pytest.mark.parametrize("filename", filenames)
def test_parse(filename):
    with open("test-cases/" + filename) as f:
        text = f.read()
    screens = list(pyrandr.parse_screens(text.splitlines()))
    assert len(screens) > 0
