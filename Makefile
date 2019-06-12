CURRENT_VERSION:=$(shell grep "^Version: " PKG-INFO | cut -d" " -f2)
INIT_VERSION:=$(shell grep "__version__" pycronofy/__init__.py | cut -d"'" -f2)

.PHONY: all
all: test

.PHONY: clean
clean:
	rm -rf build

.PHONY: init
init:
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

.PHONY: test
test: clean init pytest checkversion

.PHONY: pytest
pytest:
	py.test pycronofy --cov=pycronofy -vv -s
	python -m flake8

.PHONY: release
release: test
	# Check pypi configured
	test -f ~/.pypirc
	python setup.py sdist upload --repository pypi
	git tag $(CURRENT_VERSION)
	git push --tags
	git push
