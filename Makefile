.DEFAULT_GOAL := help
MAKEFLAGS += --warn-undefined-variables

ACTIVATE = poetry run

COL_WIDTH = 10
FORMAT_YELLOW = 33
FORMAT_BOLD_YELLOW = \e[1;$(FORMAT_YELLOW)m
FORMAT_END = \e[0m
FORMAT_UNDERLINE = \e[4m

define usage
@printf "Usage: make target\n\n"
@printf "$(FORMAT_UNDERLINE)target$(FORMAT_END):\n"
@grep -E "^[A-Za-z0-9_ -]*:.*#" $< | while read -r l; do printf "  $(FORMAT_BOLD_YELLOW)%-$(COL_WIDTH)s$(FORMAT_END)$$(echo $$l | cut -f2- -d'#')\n" $$(echo $$l | cut -f1 -d':'); done
endef

install: venv/touchfile .git/hooks/pre-commit
venv/touchfile: pyproject.toml
	@test -d venv || mkdir venv
	@poetry lock
	@poetry install --with dev
	@$(ACTIVATE) pre-commit install --hook-type pre-commit --hook-type pre-push
	@touch $@

.PHONY: help
help: Makefile  # Print this message
	$(call usage)

.PHONY: ruff
ruff:  # Auto-fix with Ruff
	@$(ACTIVATE) ruff . --fix

.PHONY: check
check: venv  # Run linters and formatters
	@$(ACTIVATE) pre-commit run --all-files --hook-stage=manual

.PHONY: test
test: venv  # Run tests
	@$(ACTIVATE) pytest

.PHONY: tox
tox: venv  # Run tests in all environments
	@$(ACTIVATE) tox

.PHONY: python
python: venv  # Python shell with API imported
	@$(ACTIVATE) python3 -i -c "from timeoff.__init__ import *"
