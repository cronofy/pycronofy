CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)
SETUP_VERSION:=$(shell grep "version='" setup.py | cut -d"'" -f2)

all: test

clean:
	rm -rf build

install_dependencies:
	pip install --requirement requirements.txt --quiet

test: clean install_dependencies
	py.test pycronofy --cov=pycronofy -vv -s
	python -m flake8

release: test
ifeq ($(CURRENT_VERSION),$(SETUP_VERSION))
	python setup.py sdist upload --repository pypi
	git tag $(CURRENT_VERSION)
	git push --tags
else
	@echo "PKG-INFO and setup.py disagree on Version"
	@exit 1
endif
