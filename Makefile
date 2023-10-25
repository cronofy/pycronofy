CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)
INIT_VERSION:=$(shell grep "version" ./pyproject.toml | cut -d"=" -f2 | tr -d '"[:blank:]' )


.PHONY: all
all: test

.PHONY: clean
clean:
	rm -rf build

.PHONY: init_ci
init_ci:
	python -m pip install --upgrade pip
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
test_ci: clean init_ci pytest checkversion

.PHONY: test
test: clean init pytest checkversion

.PHONY: pytest
pytest:
	python -m pytest pycronofy --cov=pycronofy -vv -s
	python -m flake8

.PHONY: release
release: test
	# Check pypi configured
	test -f ~/.pypirc
	pythom -m build
	twine upload -r testpypi dist/*
	# twine upload -r pypi dist/*
	git tag $(CURRENT_VERSION)
	git push --tags
	git push
