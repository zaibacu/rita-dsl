PYTHON=python

benchmark:
	${PYTHON} -m pytest --benchmark-only tests/ --benchmark-autosave
