include Make.defs

.git/hooks/pre-commit:
	$(ACTIVATE) pre-commit install
	@touch $@

venv: venv/touchfile .git/hooks/pre-commit
venv/touchfile: requirements.txt
	test -d venv || virtualenv venv
	$(ACTIVATE) pip install -Ur requirements.txt
	touch $@

.PHONY: help
help: Makefile  # Print this message
	$(call usage)

.PHONY: lint
lint: venv  # Run linters
	$(ACTIVATE) ruff . --fix

.PHONY: fmt
fmt: venv  # Run formatters
	$(ACTIVATE) black .

.PHONY: check
check: lint fmt  # Run linters and formatters
