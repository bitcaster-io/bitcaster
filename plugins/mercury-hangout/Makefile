develop: .setup-git
	@pip install -U pip setuptools
	pip install -e .[test]

test:
	py.test

qa:
	flake8 src/ tests/
	isort -rc src/ --check-only
	check-manifest

clean:
	@rm -fr .pytest_cache *.egg-info ~build .coverage .tox dist
	@find . -name __pycache__ -o -name "*.py?" -o -name "*.orig" -prune | xargs rm -rf

fullclean:
	@rm -fr .tox .cache
	@$(MAKE) clean
