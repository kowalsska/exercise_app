.PHONY: lint test setup

default: test

lint:
	black .
	
setup:
	pip install -r requirements.txt

test:
	PYTHONPATH=${PWD}/app python -m unittest discover -s ./app/ -p '*_test.py' -v
