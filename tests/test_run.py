import sys

from rita.run import main


def test_simple_compile(mocker):
    sys.argv = [
        "rita-dsl",
        "-f",
        "examples/cheap-phones.rita",
        "output.jsonl"
    ]
    main()

