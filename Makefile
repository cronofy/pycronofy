CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)
INIT_VERSION:=$(shell grep "__version__" pycronofy/__init__.py | cut -d"'" -f2)

.PHONY: all
all: test

.PHONY: clean
clean:
	rm -rf dist

.PHONY: init_ci
init_ci:
	python -m pip install --upgrade pip build
	pip install --requirement requirements-ci.txt

.PHONY: init
init:
	python -m pip install --upgrade pip build
	pip install --requirement requirements.txt

.PHONY: version
version:
	@echo $(CURRENT_VERSION)

.PHONY: checkversion
checkversion:
ifeq ($(CURRENT_VERSION),$(INIT_VERSION))
	@echo "Versions match"
else
	@echo "PKG-INFO and __init__.py disagree on Version"
	@exit 1
endif

.PHONY: test_ci
test_ci: clean init_ci build pytest checkversion

.PHONY: test
test: clean init build pytest checkversion

.PHONY: build
build:
	python -m build

.PHONY: pytest
pytest:
	python -m pytest pycronofy --cov=pycronofy -vv -s
	python -m flake8

.PHONY: release
release: test
	# Check pypi configured
	test -f ~/.pypirc
	twine upload -r pypi dist/*
	git tag $(CURRENT_VERSION)
	git push --tags
	git push
