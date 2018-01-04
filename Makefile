all: test

install_dependencies:
	pip install --requirement requirements.txt --quiet

test: install_dependencies
	py.test pycronofy --cov=pycronofy -v

release: test
	python setup.py sdist upload --repository pypi
