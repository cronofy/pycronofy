all: test

clean:
	rm -rf build

install_dependencies:
	pip install --requirement requirements.txt --quiet

test: clean install_dependencies
	py.test pycronofy --cov=pycronofy -vv -s
	python -m flake8

release: test
	python setup.py sdist upload --repository pypi
