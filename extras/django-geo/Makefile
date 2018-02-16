requirements:
	@pip-compile src/requirements/testing.in \
		--upgrade \
		--rebuild \
		--no-header \
		--no-emit-trusted-host \
		--no-index -o src/requirements/testing.pip
	@pip-compile src/requirements/develop.in \
		src/requirements/install.pip \
		src/requirements/testing.pip \
		--upgrade \
		--rebuild \
		--no-header \
		--no-emit-trusted-host \
		--no-index -o src/requirements/develop.pip
