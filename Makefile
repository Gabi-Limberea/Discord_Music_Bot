VENV_ACTIVE=${VIRTUAL_ENV}
VENV_NAME=venv
IMG=bot-image

all: run

.PHONY: venv
venv:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		python3 -m venv venv; \
	fi

.PHONY: run
run:
	@if [ -z "$(VENV_ACTIVE)" ]; then \
		echo "ACTIVATE VIRTUAL ENVIRONMENT!"; \
		exit 1; \
	fi
	python3 ./src/main.py;

.PHONY: docker-build
docker-build:
	docker compose build

.PHONY: docker-run
docker-up:
	@if [ -z "$$(docker image ls | grep $(IMG))" ]; then \
		make docker-build; \
	fi
	docker compose up

.PHONY: docker-down
docker-down:
	docker compose down --remove-orphans 2> /dev/null

PHONY: docker-clean
docker-clean: docker-down
	docker image rm -f $(IMG) 2> /dev/null
	@docker image prune -f 2> /dev/null

.PHONY: gen-reqs
gen-reqs:
	@if [ -z "$(VENV_ACTIVE)" ]; then \
		echo "ACTIVATE VIRTUAL ENVIRONMENT!"; \
		exit 1; \
	fi
	pip freeze > ./config/requirements.txt

.PHONY: install-reqs
install-reqs: venv
	@if [ -z "$(VENV_ACTIVE)" ]; then \
		echo "ACTIVATE VIRTUAL ENVIRONMENT!"; \
		exit 1; \
	fi
	pip install -r ./config/requirements.txt
