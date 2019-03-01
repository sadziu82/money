all:

tests:
	python -m pytest -vvs --cov=money --cov-report=term-missing --disable-warnings

bdist_wheel:
	python setup.py bdist_wheel

build: bdist_wheel

.PHONY: all tests
