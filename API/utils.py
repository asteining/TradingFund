import json, os, pathlib


def current_cfg():
    root = pathlib.Path(__file__).parents[1]
    return json.load(open(root / "config.json"))
