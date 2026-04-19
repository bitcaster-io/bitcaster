test:
	semgrep --test --trace ./

scan:
	semgrep scan \
		--config . \
		--metrics=off \
		--disable-version-check \
		--error \
		--exclude ../.semgrep/ \
		../src/
