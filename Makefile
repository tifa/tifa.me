.DEFAULT_GOAL := help
MAKEFLAGS += --warn-undefined-variables

ACTIVATE = . venv/bin/activate;

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

.PHONY: ruff
ruff:  # Auto-fix with Ruff
	@$(ACTIVATE) ruff . --fix

.PHONY: lint
lint: venv  # Run linters
	@$(ACTIVATE) ruff .

.PHONY: fmt
fmt: venv  # Run formatters
	@$(ACTIVATE) black .

.PHONY: check
check: lint fmt  # Run linters and formatters

.PHONY: python
python: venv  # Python shell with API imported
	@python3 -i -c "from timeoff.__init__ import *"
