import json
import argparse
import logging

import rita


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Compile rita -> spaCy patterns"
    )

    parser.add_argument("-f", help=".rita rules file")
    parser.add_argument(
        "out",
        help="output .jsonl file to store rules"
    )
    parser.add_argument("--debug", help="debug mode", action="store_true")
    parser.add_argument("--engine", help="Engine to use when compiling rules", default="spacy")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    patterns = rita.compile(args.f, use_engine=args.engine)

    logger.info("Compiling rules using {} engine".format(args.engine))

    with open(args.out, "w") as f:
        for pattern in patterns:
            f.write(json.dumps(pattern) + "\n")
