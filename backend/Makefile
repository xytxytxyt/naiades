ALLOWED_ORIGIN_HOSTS ?= localhost

lint-check:
	isort --check-only --diff --profile black naiades tests
	black --check --diff naiades tests
	flake8 --ignore E501 naiades tests

lint-fix:
	isort --profile black naiades tests
	black naiades tests

check-types:
	mypy --ignore-missing-imports --check-untyped-defs --install-types --non-interactive naiades tests

test:
	pytest -svv --log-cli-level=INFO tests

# remember to activate virtualenv
run:
	uvicorn naiades.server:app --reload --host 0.0.0.0 --port 8001 --reload-include '*.yaml'
