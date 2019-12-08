PYTHON=python

build-pkg:
	${PYTHON} setup.py sdist bdist_wheel

publish: build-pkg
	 twine upload dist/*

benchmark:
	${PYTHON} -m pytest --benchmark-only tests/ --benchmark-autosave
