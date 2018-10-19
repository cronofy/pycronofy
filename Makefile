CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)
INIT_VERSION:=$(shell grep "__version__" pycronofy/__init__.py | cut -d"'" -f2)

all: test

clean:
	rm -rf build

install_dependencies:
	pip install --requirement requirements.txt --quiet

test: clean install_dependencies
	py.test pycronofy --cov=pycronofy -vv -s
	python -m flake8

version:
	@echo $(CURRENT_VERSION)

release: test
ifeq ($(CURRENT_VERSION),$(INIT_VERSION))
	python setup.py sdist upload --repository pypi
	git tag $(CURRENT_VERSION)
	git push --tags
	git push
else
	@echo "PKG-INFO and __init__.py disagree on Version"
	@exit 1
endif
