VENV_ACTIVE=${VIRTUAL_ENV}
VENV_NAME=venv
BOT_IMAGE=bot-image

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
	docker build -f=./config/Dockerfile -t bot-image .

.PHONY: docker-run
docker-run:
	@if [ -z "$$(docker image ls | grep $(BOT_IMAGE))" ]; then \
		make docker-build; \
	fi
	docker run -d bot-image

.PHONY: gen-reqs
gen-reqs:
	pipreqs ./src --force --savepath ./config/requirements.txt

.PHONY: install-reqs
install-reqs: venv
	pip install -r ./config/requirements.txt
