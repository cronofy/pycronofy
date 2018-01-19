CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)

all: test

clean:
	rm -rf build

install_dependencies:
	pip install --requirement requirements.txt --quiet

test: clean install_dependencies
	py.test pycronofy --cov=pycronofy -vv -s
	python -m flake8

release: test
	git tag $(CURRENT_VERSION)
	git push --tags
	python setup.py sdist upload --repository pypi
