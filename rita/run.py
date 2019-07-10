import json
import argparse

import rita


def main():
    parser = argparse.ArgumentParser(description="Compile rita -> spaCy patterns")

    parser.add_argument("-f", help=".rita rules file")
    parser.add_argument("out", help="output .jsonl file to store rules")
    args = parser.parse_args()

    patterns = rita.compile(args.f)

    with open(args.out, "w") as f:
        for pattern in patterns:
            f.write(json.dumps(pattern) + "\n")
