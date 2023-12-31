#!/usr/bin/env python3

import json
import textwrap

from argparse import ArgumentParser, FileType

parser = ArgumentParser(description="Process lighthouse JSON results")
parser.add_argument(
    "results_file", type=FileType("r"), help="a JSON-formatted file with lighthouse results"
)
# Parse command-line parameters
args = parser.parse_args()

text = "".join(args.results_file.readlines())
json_result = json.loads(text)

for category, category_results in json_result["categories"].items():
    score = category_results.get("score")
    score = f"{score * 100}%" if score else None
    info_line = textwrap.indent(f"{category}: {score}", "  ", predicate=None)
    print(info_line)
