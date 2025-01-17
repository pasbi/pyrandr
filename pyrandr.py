#!/usr/bin/env python3

import sys
from dataclasses import dataclass
import subprocess
import re
import argparse


class FPS:
    pattern = re.compile(r"^(\d+.\d+)(\s?)(\*?)(\+?)$")

    def __init__(self, code):
        matches = FPS.pattern.match(code)
        assert matches is not None, f"Unexpected line for FPS: {code}"
        self.value = float(matches.group(1))
        self.asterisk = matches.group(2) != ""
        self.plus = matches.group(3) != ""

    def __repr__(self):
        return f"{self.value}{'*' if self.asterisk else ''}{'+' if self.plus else ''}"


def split_fps(code):
    tokens = code.split()
    codes = []
    number_pattern = re.compile(r"^\d+.\d+$")
    for token in codes:
        if number_pattern.match(token) or len(codes) == 0:
            codes.append(token)
        else:
            codes[-1] += token
    return codes


class Mode:
    pattern = re.compile(r"^\s*(\d+)x(\d+)(i?)((\s+\d+.\d+\s?\*?\+?)+)\s*$")

    def __init__(self, code):
        matches = Mode.pattern.match(code)
        assert matches is not None, f"Unexpected line for Mode: {code}"
        self.width = int(matches.group(1))
        self.height = int(matches.group(2))
        self.interlaced = matches.group(3) != ""
        self.fps = [FPS(s) for s in split_fps(matches.group(4))]

    def __repr__(self):
        return f"{self.width}x{self.height}{'i' if self.interlaced else ''} {self.fps}"

    def area(self):
        return self.width * self.height

    def to_tuple(self):
        """used for sorting"""
        return (self.area(), self.width, self.height, self.fps, not self.interlaced)

    def __lt__(self, other):
        return self.to_tuple() < other.to_tuple()


class Screen:
    def __init__(self, name: str, connected: bool):
        self.name = name
        self.connected = connected
        self.modes: list[Mode] = []

    def preferred_mode(self):
        if len(self.modes) == 0:
            return None
        return max(self.modes)

    def __repr__(self):
        return (
            f"Screen[{self.name} {'connected' if self.connected else 'disconnected'}]"
        )


def find_name(line):
    return line.split()[0]


def parse_screens(lines):
    current_screen = None
    for line in lines:
        is_disconnected = " disconnected " in line
        is_connected = " connected " in line
        is_headline = is_disconnected or is_connected

        if is_headline:
            if current_screen is not None:
                yield current_screen
            current_screen = Screen(name=find_name(line), connected=is_connected)
        elif current_screen is not None:
            current_screen.modes.append(Mode(line))

    if current_screen is not None:
        yield current_screen


def assemble_command(screens):
    pos_x = 0
    for screen in screens:
        yield ["--output", screen.name]
        if not screen.connected:
            yield ["--off"]
        else:
            mode = screen.preferred_mode()
            yield [
                "--mode",
                f"{mode.width}x{mode.height}",
                "--pos",
                f"{pos_x}x{0}",
                "--rotate",
                "normal",
            ]
            pos_x += mode.width


def format_command(command):
    lines = []
    for token in command:
        if token == "--output":
            lines.append(token)
        elif len(lines) == 0:
            lines.append(token)
        else:
            lines[-1] += " " + token

    return "\\\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pyrandr", description="Convenient xrandr wrapper for special cases"
    )
    parser.add_argument(
        "screens",
        nargs="*",
        help="The sequence of screens from left to right. "
        "Screens that are not specified here will be turned off. "
        "Regex to match screen names is supported. "
        "An empty list places all connected screens next to each other.",
    )
    args = parser.parse_args()

    listing_result = subprocess.run(["xrandr"], capture_output=True)
    screens = list(parse_screens(listing_result.stdout.decode("utf-8").splitlines()))
    screen_regex_sequence = [re.compile(pattern) for pattern in sys.argv[1:]]

    def screen_position(screen: Screen):
        if screen.connected:
            if len(screen_regex_sequence) == 0:
                return 0
            for i, regex in enumerate(screen_regex_sequence):
                if regex.match(screen.name):
                    return i
        screen.connected = False
        return -1

    screens.sort(key=screen_position)
    command = assemble_command(screens)
    command = ["xrandr"] + [v for vs in command for v in vs]

    print(format_command(command))
    subprocess.run(command)
